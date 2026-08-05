---
name: metron-program-dashboard
description: >
  Navigate and operate the live Metron Engineering Intel portal at
  https://latc.lenovo.com/metron — all sidebar pages (Overview, Team,
  Program, Jira Cadence, CTOO Partnerships, AI ROI, Contributors, Activity,
  Sync Jobs) plus Program Roadmap / FY26 pillar dependency tabs. Use when the
  user mentions Metron, LATC Engineering Intel, Program Roadmap, Team Calorie,
  Jira Cadence, CTOO/ATP partnerships, AI ROI/adoption, Contributors
  leaderboard, Activity Feed, Sync Jobs, or latc.lenovo.com/metron.
---

# Metron — Engineering Intel (full portal)

Live Next.js App Router site: **Metron — Engineering Intel** at `https://latc.lenovo.com/metron`.

Base path is always `/metron` (pages, assets, APIs). Auth.js credentials login at `/metron/login`.

**Per-page extract / edit / filter recipes (verified):** [ops.md](ops.md) · **API field shapes:** [reference.md](reference.md)

## Auth & secrets

| Mode | Access |
|---|---|
| **Guest** | Most SSR pages readable; most Program tab GETs work; **Roadmap + export** blocked |
| **Signed in** | Edit controls; Roadmap; Team details refresh; CTOO mutations |

Agent credentials (local only — never paste into chat/commits):

`C:\Users\mfink\.cursor\secrets\metron.env`

- `METRON_BASE=https://latc.lenovo.com`
- `METRON_COOKIE=...` (includes `__Secure-authjs.session-token`)
- optional `METRON_EMAIL` / `METRON_PASSWORD` for re-login via `Downloads/metron-explore/metron_login.py`

Probe:

```powershell
curl.exe -s -H "Cookie: <METRON_COOKIE>" -H "Accept: application/json" `
  "https://latc.lenovo.com/metron/api/auth/session"
```

Expect `user.email` + `role` (e.g. `manager`). Session expiry ~30 days from login. On 401 for roadmap, re-login and refresh cookie.

**Mutations:** never POST/PATCH/DELETE unless the user explicitly asks. Confirm the intended edit first.

## Architecture (important)

Two data patterns coexist:

1. **SSR / RSC** — Overview, Jira Cadence, AI ROI, Contributors, Activity, Sync Jobs, CTOO (read), Program **By Initiative** / much of Blockers. Data is embedded in the HTML/`text/x-component` flight. Changing filters often does a **soft navigation with query params** (no JSON API).
2. **Client JSON APIs** — Program interactive tabs (`/metron/api/program/*`), Team rollups (`/metron/api/team/*`), CTOO writes (`/metron/api/program/atp...`).

Prefer JSON APIs when they exist. For SSR-only pages, use authenticated Playwright or fetch the HTML/RSC page with the session cookie and parse visible text — do not invent endpoints that 404.

## Sidebar (global)

| Label | Route | Primary data mode |
|---|---|---|
| Overview | `/metron/dashboard` | SSR + `?range=` |
| Team Dashboard | `/metron/dashboard/team` | SSR org + client `/api/team/*` |
| **Program** | `/metron/dashboard/program` | Client Program APIs (+ SSR for RBS) |
| Jira Cadence | `/metron/dashboard/jira-cadence` | SSR + `?range=` |
| CTOO Partnerships | `/metron/dashboard/ctoo-ecosystem-partnerships` | SSR read; ATP write API |
| AI ROI | `/metron/dashboard/ai-adoption` | SSR + `?range=` |
| Contributors | `/metron/dashboard/contributors` | SSR + `?range=` / `?manager=` |
| Activity Feed | `/metron/dashboard/activity` | SSR (client filter) |
| Sync Jobs | `/metron/dashboard/sync-jobs` | SSR |

Dark mode: sidebar footer (`localStorage` key `metron-theme`). Signed-in users see **Sign out**.

---

## Overview — `/metron/dashboard`

**Title:** Executive Summary  
**Greeting:** “Welcome back, {name}. Showing {range}.”

| Control | Behavior |
|---|---|
| This week / This month / Last 3M / Last 6M / Custom | Navigates `?range=week\|month\|3m\|6m` (Custom date UI) |

**KPIs (buttons):** Active Users (avg/period) · AI Adoption (score/100) · AI Spend (USD total)  
**Chart:** Active Users Trend for selected range.

No dedicated public JSON API — re-fetch the page with the desired `range` query.

---

## Team Dashboard — `/metron/dashboard/team`

**Subtitle:** Org chart · team & individual work rollups · Jira Projects & Pillars · Confluence activity

### UI sections
- **Organization** — expandable tree (default root e.g. Tolga Kurtoglu); pick a manager node
- **Manager view** — Direct reports vs Whole team counts; Cadence %
- **Range:** Week · Month · Quarter · Half · Year · All (client state; refreshes APIs with `period=`)
- **Team Calorie** + **Manager Calorie Benchmark** (percentile vs other teams)
- **Jira Update Compliance** · **Team Jira Summary**
- **Projects (Initiatives)** · **Pillars (Components)**
- **Jira · Team Ticket Activity** · **Confluence Activity**
- **Team Roster**

### Client APIs

| Endpoint | Query | Returns |
|---|---|---|
| `GET /metron/api/team/details` | `emails=` (comma list) + `period=Week\|Month\|Quarter\|…` | `{ total, byStatus, byProject, byPillar, trend, trendUnit, tickets, confluence, calorie }` |
| `GET /metron/api/team/compliance` | `period=` optional | Map `email → { updates, lastUpdate, daysSince, status }` where status ∈ compliant/lapsed/… |

`byStatus` keys: `todo`, `prog`, `done`. Calorie object includes `benchmark`, `teamBenchmark`, `byPerson`, etc.

Org tree + roster identity data are SSR; changing period/emails triggers the JSON calls above.

---

## Program — `/metron/dashboard/program`

**Title:** LATC Pillar Dependency Map — FY26  
**Sources:** FY26 Roadmap · LATC Resource Registry  
**KPI strip:** Pillars · Work Items · Mapped Dependencies · Critical Blockers · High-Risk Gaps

### In-page tabs (`tab` ids)

| UI | id | Guest | Notes |
|---|---|---|---|
| Executive Summary | `summary` | Yes | Findings cards; edit when signed in |
| Pillar Dependency DAG | `dag` | Yes | SVG pillar graph |
| Critical Delivery Chains | `chains` | Yes | Live Jira step health |
| Item-Level Dependencies | `deps` | Yes | Table + CSV export |
| Schedule Risks | `risks` | Yes | Inversions / late prereqs / overlaps + staffing |
| Active Blockers | `blockers` | Yes | Jira blocked + manual; badge count |
| Resources | `resources` | Yes | Roster; open-gap badge; inline edit when signed in |
| By Initiative | `rbs` | Yes | Live Jira INIT→epic→task RBS (SSR; ~55 initiatives) |
| Teams & Capacity | `teams` | Yes | Per-pillar FTE need/gap |
| **Roadmap** | `roadmap` | **Auth** | FY26 Gantt; guest → login |

Many tabs: **↓ Export CSV** → `/metron/api/program/export?tab=<id>` (auth). Known good tabs: `deps`, `resources`, `roadmap`, `risks`. `chains` may 400.

### Roadmap (auth)

- FY26 months `1..12` = Apr’26 → Mar’27
- Pillar codes: `infra`, `models`, `dcm`, `ro`, `runtime`, `eval`
- Fields: name, priority P0–P3, status, start/end month, resources, fte, has_gap, gap_note, blocked, dependencies[], notes, jira_url
- **PATCH** `/metron/api/program/roadmap/{item_id}` requires the **full row** (partial body can coerce numbers to `NaN` and 500)

### Program JSON APIs

Prefix: `https://latc.lenovo.com/metron/api/program/`

| Path | Auth | Shape |
|---|---|---|
| `findings` | Guest GET | Finding[] |
| `chains` | Guest GET | Chain[] |
| `item-deps` | Guest GET | Dep[] (~39) |
| `schedule-risks` | Guest GET | `{ conflicts, staffing_gaps, summary }` |
| `resources` | Guest GET | Roster[] (~300+) |
| `team-meta` | Guest GET | Pillar capacity[] |
| `manual-blockers` / `blocker-annotations` | Guest GET | overlays |
| `manual-risks` / `risk-annotations` | Guest GET | overlays |
| `roadmap` | **Auth** | RoadmapItem[] (~151) |
| `export?tab=` | **Auth** | CSV |
| `atp` / `atp/projects` | Auth write | CTOO (see below) |

Field-level shapes: [reference.md](reference.md).

---

## Jira Cadence — `/metron/dashboard/jira-cadence`

How regularly people keep Jira updated, rolled up by manager org.

- Range pills → `?range=` (same vocabulary as Overview)
- Compliance target chips: Weekly / Bi-weekly / Monthly
- KPIs: Org compliance %, People tracked, Lapsed (no update in 7d), No updates in range
- **Weekly Update Activity** chart (distinct updaters / ISO week; from Jira changelog)
- Table **Compliance by Manager Org**: Manager, Org size, Compliance, Lapsed, None
- Table **People — Update Cadence**: Person, Updates, Active wks, Last, Status

SSR-only for agents (no dedicated cadence JSON API discovered).

---

## CTOO Partnerships — `/metron/dashboard/ctoo-ecosystem-partnerships`

Component: `AtpView`. Live from Jira **LATC · atp-ep** (partner = Epic, project = Story).

- Region filters: All · ROW · PRC (client filter; PRC preference key `atp-partnerships:prc`)
- Categories: Startups · Academia · Industry · Internal
- KPIs: Partners, Projects, On track, In pilot, Need attention, Kept warm, Complete
- Partner cards with project rows + status chips: on-track, at-risk, blocked, pilot, warm, new, done
- Signed-in: **+ Add project** → `POST /metron/api/program/atp/projects` (form includes Jira key placeholder `LATC-0000`)
- Bare `GET /metron/api/program/atp` may 404; **read path is SSR `data` prop**, writes go through ATP API

---

## AI ROI — `/metron/dashboard/ai-adoption`

**Subtitle:** Token burn → code output · {range}

- Range pills → `?range=`
- Score card: AI Adoption Score + Adoption rate / Accept rate / AI code ratio
- Spend: team total, LATC-ROW vs LATC-PRC, per active user, AI requests, active users
- Trends: Adoption Score + Team spend (ROW vs PRC)
- **Adoption Funnel:** engineers tracked → AI-active (≥1 Cursor request/week) → AI-attributed MRs → AI CI pass rate
- Tables: AI weeks vs non-AI weeks metrics; per-person (AI requests, accepted lines, AI code %, accept rate, MRs, commits, spend, efficiency)

SSR-only for agents.

---

## Contributors — `/metron/dashboard/contributors`

Sortable leaderboard for selected range.

- Range pills → `?range=`
- Org `<select>` → `?manager=en%3A{name}` (e.g. `en%3Aanwar+ghuloum`)
- Columns: Person, MRs, Commits, Reviews, AI Requests, Accept Rate, Issues, Doc Edits (plus GitLab/Cursor/Jira/Confluence group headers)
- Click column headers to sort

SSR-only for agents.

---

## Activity Feed — `/metron/dashboard/activity`

Live GitLab / Jira / Confluence activity (UI copy: refresh ~5 minutes).

- Filters (client): All · GitLab · Confluence · Jira
- Grouped buckets: Today / Yesterday / This week / Older
- **Load 40 more events**
- Event types include issue updated, page edited, etc.

SSR seed + client filtering; no dedicated `/api/activity` JSON route found.

---

## Sync Jobs — `/metron/dashboard/sync-jobs`

Ingest pipeline history — last 200 runs.

- KPIs: Total runs, Success rate, Errors, Last run
- **Source Status** cards — observed sources include: calorie, Confluence, Cursor, Cursor (team 2), GitLab LATC, Jira, Jira (instance 2), Jira activity (+ instance 2), …
- **Run History** table: Source, Status, Started, Duration, Rows, Watermark, Error

SSR-only.

---

## How the agent should operate

1. **Identify the page** from the sidebar table; Program work is only under `/dashboard/program`.
2. **Roadmap / export / ATP writes / Team details refresh:** require session cookie.
3. **Read data:**
   - Program / Team → JSON APIs above
   - Everything else → open page (Playwright or HTML fetch) with cookie; use `?range=` / `?manager=` where documented
4. **Metron month index** on Roadmap: `1=Apr’26 … 12=Mar’27`.
5. **Roadmap PATCH:** send full item row, not a partial patch.
6. **PII:** Team, Contributors, Cadence, Resources, Activity embed names/emails — treat as internal.
7. Offline twin: personal `roadmap-dashboard-html` skill ≈ Program tabs only; Metron is the live hosted system.
8. For concrete curl/Playwright/PATCH payloads, follow [ops.md](ops.md). Re-verify with `Downloads/metron-explore/verify_ops.py` when the site changes.

## Quick verification

```bash
curl -s  -H "Cookie: $METRON_COOKIE" "$BASE/metron/api/auth/session"
curl -s  -H "Cookie: $METRON_COOKIE" "$BASE/metron/api/program/roadmap" | head
curl -s  -H "Cookie: $METRON_COOKIE" "$BASE/metron/api/team/compliance?period=Month" | head
curl -sI "$BASE/metron/dashboard?range=week"
```

Exploration artifacts (screenshots, DOM dumps, API probes): `Downloads/metron-explore/full-explore/`.
