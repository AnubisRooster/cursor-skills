# Metron ops cheat sheet — extract / edit / filter

Verified live **2026-08-05** with manager session (`ops_verify.json`: extract JSON **15/15** core APIs OK; safe no-op PATCH **6/6** OK; SSR pages **9/9** load; export `deps/resources/roadmap` OK, `risks` empty CSV, `chains` 400).

Auth header for all examples:

```powershell
$BASE = "https://latc.lenovo.com"
# From C:\Users\mfink\.cursor\secrets\metron.env
$COOKIE = "<METRON_COOKIE>"
$H = @{ Cookie = $COOKIE; Accept = "application/json" }
```

`SC` in the app = `fetch` with `credentials:"include"` against `/metron` + path. Same cookie works from scripts.

**Never mutate production without explicit user ask.** Examples below that write were verified as **no-op round-trips** (PATCH same values).

---

## Capability matrix

| Page | Extract | Filter / navigate | Edit |
|---|---|---|---|
| Overview | SSR HTML | `?range=week\|month\|3m\|6m` | — |
| Team | JSON + SSR org | `period=` on APIs; org click in UI | — (read-only) |
| Program · Summary | JSON | — | POST/PATCH/DELETE findings |
| Program · DAG | SSR/client | click nodes | — |
| Program · Chains | JSON | — | POST/PATCH/DELETE |
| Program · Deps | JSON / CSV | pillar filters in UI | POST/PATCH/DELETE |
| Program · Risks | JSON | — | annotate POST/DELETE |
| Program · Blockers | JSON + SSR Jira | — | manual blockers + annotations |
| Program · Resources | JSON / CSV | — | PATCH/DELETE rows |
| Program · By Initiative | SSR only | filter box | — |
| Program · Teams & Capacity | JSON | — | PATCH team-meta |
| Program · Roadmap | JSON / CSV (**auth**) | — | PATCH full row (**auth**) |
| Jira Cadence | SSR | `?range=` | — |
| CTOO | SSR read | region/category UI | POST/PATCH ATP (no GET list API) |
| AI ROI | SSR | `?range=` | — |
| Contributors | SSR | `?range=` · `?manager=` | — |
| Activity | SSR | client source filter | — |
| Sync Jobs | SSR | — | — |

---

## Shared: session

```powershell
Invoke-RestMethod -Headers $H "$BASE/metron/api/auth/session"
# expect user.email, role, expires
```

Re-login: `Downloads/metron-explore/metron_login.py` → refresh `METRON_COOKIE`.

---

## Overview — extract / filter

```powershell
# HTML/RSC (no JSON API)
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/dashboard?range=week" -o overview.html
# KPIs in page text: ACTIVE USERS, AI ADOPTION, AI SPEND
```

| Action | How |
|---|---|
| Extract | Parse HTML/RSC or Playwright `main` text |
| Filter | `?range=week\|month\|3m\|6m` (+ Custom in UI) |
| Edit | Not supported |

---

## Team Dashboard — extract / filter

```powershell
# Compliance map (all people)
Invoke-RestMethod -Headers $H "$BASE/metron/api/team/compliance?period=Month"

# Rollup for one or many emails (comma-separated)
$emails = [uri]::EscapeDataString("mfink@lenovo.com")
Invoke-RestMethod -Headers $H "$BASE/metron/api/team/details?emails=$emails&period=Month"
```

`period`: `Week` | `Month` | `Quarter` | `Half` | `Year` | `All`

**details** keys: `total`, `byStatus` (`todo`/`prog`/`done`), `byProject`, `byPillar`, `trend`, `trendUnit`, `tickets`, `confluence`, `calorie`.

| Action | How |
|---|---|
| Extract | APIs above; org tree/roster from SSR `/metron/dashboard/team` |
| Filter | Change `period`; pass team emails in `emails=` (UI builds list from org selection) |
| Edit | Not supported (metrics are ingested) |

---

## Program — extract

```powershell
$paths = @(
  "findings","chains","item-deps","schedule-risks","resources","team-meta",
  "manual-blockers","blocker-annotations","manual-risks","risk-annotations","roadmap"
)
foreach ($p in $paths) {
  Invoke-RestMethod -Headers $H "$BASE/metron/api/program/$p" | ConvertTo-Json -Depth 2 | Out-File "program-$p.json"
}

# CSV export (auth)
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/api/program/export?tab=deps" -o deps.csv
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/api/program/export?tab=resources" -o resources.csv
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/api/program/export?tab=roadmap" -o roadmap.csv
# tab=risks → 200 empty; tab=chains → 400
```

**By Initiative (RBS):** no JSON route — open `/metron/dashboard/program` (tab `rbs`) via Playwright/HTML.

**Findings history:** `GET /metron/api/program/findings/{id}/history`

---

## Program — edit (verified patterns)

All use `Content-Type: application/json` + session cookie. Confirm with user before write.

### Roadmap (full row required) — **verified**

```powershell
$row = Invoke-RestMethod -Headers $H "$BASE/metron/api/program/roadmap" |
  Where-Object { $_.item_id -eq "INF-001" }
# mutate fields on $row, then:
Invoke-RestMethod -Method PATCH -Headers ($H + @{ "Content-Type"="application/json" }) `
  -Body ($row | ConvertTo-Json -Depth 6) `
  "$BASE/metron/api/program/roadmap/$($row.item_id)"
```

### Findings — **verified**

```text
POST   /metron/api/program/findings
       body: { priority, title, description, added_date }
PATCH  /metron/api/program/findings/{id}
       body: { priority, title, description, added_date, sort_order? }
DELETE /metron/api/program/findings/{id}
```

`sort_order` is accepted on PATCH (verified 2026-08-05) — use it to keep weekly cards at the top of Executive Summary.

### Chains — **verified**

```text
POST   /metron/api/program/chains
       body: { name, phase, target, steps[], sort_order }
PATCH  /metron/api/program/chains/{id}
       body: { name, phase, target, steps:[{id,label,pillar}] }
DELETE /metron/api/program/chains/{id}
```

### Item deps — **verified**

```text
POST   /metron/api/program/item-deps
       body: { from_key, to_key, rel_type, from_label, to_label, pillars, notes, risk_label, sort_order, … }
PATCH  /metron/api/program/item-deps/{id}
DELETE /metron/api/program/item-deps/{id}
```

### Team meta — **verified**

```text
PATCH /metron/api/program/team-meta/{pillar_code}
body: { lead, fte_needed, fte_gap, notes, roles_override: string[] }
```

### Resources — **verified**

```text
PATCH  /metron/api/program/resources/{id}   # send full/near-full row
DELETE /metron/api/program/resources/{id}   # UI supports; confirm before use
POST   /metron/api/program/resources        # create (bundle)
```

### Blockers / risks annotations (bundle; not no-op tested)

```text
POST   /metron/api/program/manual-blockers
PATCH  /metron/api/program/manual-blockers/{id}
DELETE /metron/api/program/manual-blockers/{id}
POST   /metron/api/program/blocker-annotations
       body includes issue_key, is_resolved, resolved_note, …
POST   /metron/api/program/manual-risks
POST   /metron/api/program/risk-annotations
       body: { risk_key, … }
DELETE /metron/api/program/risk-annotations/{risk_key}
```

---

## Jira Cadence — extract / filter

```powershell
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/dashboard/jira-cadence?range=3m" -o cadence.html
```

| Action | How |
|---|---|
| Extract | SSR — compliance tables + weekly chart in HTML |
| Filter | `?range=` |
| Edit | — |

---

## CTOO Partnerships — extract / edit

**Read:** SSR only (`AtpView` `data` prop). `GET /api/program/atp` → 404.

```powershell
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/dashboard/ctoo-ecosystem-partnerships" -o ctoo.html
# or Playwright: filter All/ROW/PRC + Startups/Academia/Industry/Internal
```

**Write** (auth; do not create junk without ask):

```text
POST   /metron/api/program/atp/projects
       body: { epic_key, name, status_override }   # e.g. status_override:"new"
PATCH  /metron/api/program/atp/projects/{id}
       body: { …fields, epic_key }
PATCH  /metron/api/program/atp/partners/{epicKey}
       body: partner fields
DELETE (bundle supports partner/project delete — confirm in UI before scripting)
```

`POST /atp/projects` returns **405** on GET (write-only collection). After write, UI calls `router.refresh()` (SSR reload).

---

## AI ROI — extract / filter

```powershell
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/dashboard/ai-adoption?range=3m" -o ai-roi.html
```

Parse funnel + person table from HTML/Playwright. No JSON API.

---

## Contributors — extract / filter

```powershell
curl.exe -s -H "Cookie: $COOKIE" `
  "$BASE/metron/dashboard/contributors?range=3m&manager=en%3Aanwar+ghuloum" -o contrib.html
```

| Action | How |
|---|---|
| Extract | SSR leaderboard table |
| Filter | `?range=` · `?manager=en%3A{lowercase+name}` |
| Edit | — |

---

## Activity Feed — extract / filter

```powershell
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/dashboard/activity" -o activity.html
```

Client filters: All / GitLab / Confluence / Jira (no durable query param required). Paginate with **Load 40 more** in UI/Playwright.

---

## Sync Jobs — extract

```powershell
curl.exe -s -H "Cookie: $COOKIE" "$BASE/metron/dashboard/sync-jobs" -o sync.html
```

Source status cards + Run History table (last 200). No JSON API / no edits.

---

## Playwright recipe (SSR pages)

```python
from playwright.sync_api import sync_playwright
# add METRON_COOKIE cookies for latc.lenovo.com, then:
page.goto("https://latc.lenovo.com/metron/dashboard/ai-adoption?range=3m")
page.wait_for_load_state("networkidle")
text = page.locator("main").first.inner_text()
tables = page.eval_on_selector_all("table", """els => els.map(t => ({
  headers: [...t.querySelectorAll('th')].map(th => th.innerText.trim()),
  rows: [...t.querySelectorAll('tbody tr')].map(tr =>
    [...tr.querySelectorAll('td')].map(td => td.innerText.trim()))
}))""")
```

---

## Verification checklist (re-run)

Script: `Downloads/metron-explore/verify_ops.py` → `full-explore/ops_verify.json`

Expect:

| Check | Pass bar |
|---|---|
| Core GET APIs | 200 |
| Roadmap/findings/chains/deps/team-meta/resources PATCH no-op | 200 |
| SSR page loads | 200 + title markers |
| export deps/resources/roadmap | 200 + bytes > 0 |
| ATP GET | 404/405 (expected) |

---

## Weekly Executive Summary refresh (Confluence → findings)

**Never write findings without explicit user approval.** Curate a draft first; then POST/PATCH.

### Card model

Keep existing strategic findings. Maintain exactly **two** weekly cards (upsert by theme substring):

| Theme substring | Title pattern | Typical priority |
|---|---|---|
| `Cross-pillar & BU delivery risks` | `Week of YYYY-MM-DD — Cross-pillar & BU delivery risks` | `high` (or `critical` if Off Track / hard delivery block) |
| `Major milestones & near-term targets` | `Week of YYYY-MM-DD — Major milestones & near-term targets` | `medium` or `high` if a hard executive date |

`added_date` = newest pillar week-of date in the pack. After upsert, PATCH `sort_order` so weekly cards are **0** and **1**, then shift strategic cards to 2+.

Description format (plain text only — UI is `whitespace-pre-wrap`, not markdown):

```text
PILLAR · Project/epic
Risk: …   (or Target:/Landed: for milestones)
Impact: … (or Value: for milestones — quantify dates, %, ticket counts, slip windows)
```

Blank line between items. 5–8 items max. **No Confluence/source links and no Jira issue keys/URLs** (keep project names only). Pillar labels in CAPS (or `PILLAR · Project`) for scanability — `**bold**` will not render.

### Confluence hubs (LATC)

Hubs are indexes — use **latest dated child**, skip `[Template]` and “To be updated…” placeholders.

| Pillar / BU | Hub pageId | Lead / notes hub |
|---|---|---|
| Infra | `653003208` | — |
| Models | `636192034` | Lead updates `653003206` (prefer dated `| Models Weekly Update`) |
| Eval | `630655592` | Lead updates `653003209` |
| DCM | `622810939` | Lead updates `653003204` |
| R&O | `653003205` | — |
| Runtime | `653003207` | Also search title `Runtime Weekly` (latest may live outside hub children) |
| Horizontal BU | `616881999` | Nested: Qira `616882011`, Tianxi `616882012`, SSG `616882014`, DTIT `616882015` → `632545983` / bi-weekly `625865518`, Enterprise AI `551397641` |

### Extract fields (pillar template)

From each latest page: Overall Status · Executive pulse · Stand-up “What is next” · Top risk · amber/red deps · Leadership ask (decision/escalation only) · Evidence URL + Jira keys.

**Skip:** reusability checklists, ticket laundry lists, placeholder pulses, stale BU syncs (>~3 weeks).

### Tooling (manual)

1. Confluence MCP: `confluence_get_page_children` → `confluence_get_page` (markdown).
2. Draft pack (example: `Downloads/metron-explore/exec_summary_weekly_draft.md`).
3. On approval: `GET /metron/api/program/findings` → POST new or PATCH matching theme → PATCH `sort_order` for full list.
4. Helper script (optional): `Downloads/metron-explore/apply_weekly_findings.py`.
5. Verify UI: `/metron/dashboard/program` → Executive Summary.

### Scheduled job (Windows Task Scheduler — Monday 09:00 Eastern)

Installed task name: **`MetronWeeklyExecSummary`** (next run Monday 09:00 local; host timezone = Eastern).

| Piece | Path |
|---|---|
| Job script | `Downloads/metron-explore/weekly_exec_summary_refresh.py` |
| Wrapper | `Downloads/metron-explore/run_weekly_exec_summary.ps1` |
| Installer | `Downloads/metron-explore/install_weekly_task.ps1` |
| Logs | `Downloads/metron-explore/logs/` |

Auth: Confluence PAT from `~/.cursor/mcp.json` (`mcp-atlassian`); Metron cookie from `~/.cursor/secrets/metron.env`.

```powershell
# Dry-run (harvest + draft only)
python "$env:USERPROFILE\Downloads\metron-explore\weekly_exec_summary_refresh.py" --dry-run

# Run once for real
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\Downloads\metron-explore\run_weekly_exec_summary.ps1"

# Reinstall / inspect
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\Downloads\metron-explore\install_weekly_task.ps1"
Get-ScheduledTask -TaskName MetronWeeklyExecSummary | Get-ScheduledTaskInfo
```

Keep Metron cookie fresh (re-login via `metron_login.py` if Monday runs start failing auth). PC must be on / awake at 09:00 (task has `StartWhenAvailable`).

---

## Safety

1. Mutations only after explicit user approval.
2. Roadmap PATCH = **entire row** (partial → `NaN` / 500).
3. Prefer no-op PATCH or dry-run GET before real edits.
4. Do not POST ATP projects / DELETE chains/deps in “tests.”
5. Treat Resources, Team, Contributors, Cadence as **PII-bearing**.
