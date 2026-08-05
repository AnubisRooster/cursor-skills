# Metron — detailed site & API reference

Explored 2026-08-05 against `https://latc.lenovo.com/metron` (authenticated manager session + guest probes).

## App facts

- Stack: Next.js App Router, `basePath: /metron`
- Auth: Auth.js credentials (`/metron/api/auth/*`); session cookie `__Secure-authjs.session-token`
- Theme: `localStorage.metron-theme` = `dark` | light
- Most non-Program pages are **RSC/SSR** (`text/x-component` flights). Client JSON APIs are concentrated under `/metron/api/program/*` and `/metron/api/team/*`.

## Routes

| Path | Component (bundle) | Notes |
|---|---|---|
| `/metron` | redirect | → dashboard when authed |
| `/metron/login` | login | Authed users bounce to Overview |
| `/metron/dashboard` | Overview | `?range=week\|month\|3m\|6m` |
| `/metron/dashboard/team` | `TeamDashboard` | Client period; APIs use `period=` |
| `/metron/dashboard/program` | `ProgramDashboard` | In-page tabs |
| `/metron/dashboard/jira-cadence` | Jira Cadence | `?range=` |
| `/metron/dashboard/ctoo-ecosystem-partnerships` | `AtpView` | SSR data + ATP write API |
| `/metron/dashboard/ai-adoption` | AI ROI | `?range=` |
| `/metron/dashboard/contributors` | `ContributorsTable` | `?range=` · `?manager=en%3A…` |
| `/metron/dashboard/activity` | `ActivityFeed` | Client source filter |
| `/metron/dashboard/sync-jobs` | Sync Jobs | Last 200 runs |

## Query params (SSR pages)

| Page | Param | Values / examples |
|---|---|---|
| Overview, Jira Cadence, AI ROI, Contributors | `range` | `week`, `month`, `3m`, `6m` (+ Custom UI) |
| Contributors | `manager` | `en%3Aanwar+ghuloum` (URL-encoded `en:anwar ghuloum`) |
| Team | *(URL usually unchanged)* | Period sent to API as `period=Week\|Month\|Quarter\|Half\|Year\|All` |

## Client JSON API catalog

All paths below are under `https://latc.lenovo.com/metron`.

### Auth

| Method | Path | Notes |
|---|---|---|
| GET | `/api/auth/session` | `null` or `{ user, expires }` |
| GET | `/api/auth/csrf` | `{ csrfToken }` |
| GET | `/api/auth/providers` | credentials provider metadata |
| POST | `/api/auth/callback/credentials` | login |

### Team

| Method | Path | Notes |
|---|---|---|
| GET | `/api/team/details?emails=a@x,b@y&period=Month` | Rollup object |
| GET | `/api/team/compliance?period=Month` | `Record<email, Compliance>` |

**`team/details` keys:** `total`, `byStatus` (`todo`/`prog`/`done`), `byProject[]`, `byPillar[]`, `trend`, `trendUnit`, `tickets[]`, `confluence` (`edits`,`pages`,`recent`), `calorie` (`latestWeek`,`total`,`average`,`contributors`,`components`,`byPerson`,`trend`,`trendUnit`,`benchmark`,`subject`,`teamBenchmark`).

**`team/compliance` value:** `{ updates, lastUpdate, daysSince, status }` with `status` like `compliant` | `lapsed`.

**Team UI period map (client):**

| Button | days | unit | label |
|---|---|---|---|
| Week | 7 | day | Last 7 days |
| Month | 30 | day | Last 30 days |
| Quarter | 92 | week | Last quarter |
| Half | 183 | week | Last 6 months |
| Year | 365 | month | Last 12 months |
| All | null | month | All time |

### Program

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/api/program/findings` | Guest | Executive Summary |
| GET/POST… | `/api/program/findings/` | Auth | Mutations (trailing slash variants in bundle) |
| GET | `/api/program/chains` | Guest | Delivery chains |
| GET | `/api/program/item-deps` | Guest | Cross-item deps |
| GET | `/api/program/schedule-risks` | Guest | Conflicts + staffing gaps |
| GET | `/api/program/resources` | Guest | Resource registry |
| GET | `/api/program/team-meta` | Guest | Teams & Capacity |
| GET | `/api/program/manual-blockers` | Guest | Manual blockers |
| GET | `/api/program/blocker-annotations` | Guest | Annotations |
| GET | `/api/program/manual-risks` | Guest | Manual risks |
| GET | `/api/program/risk-annotations` | Guest | Risk annotations |
| GET | `/api/program/roadmap` | **Auth** | Gantt rows (~151) |
| PATCH | `/api/program/roadmap/{item_id}` | **Auth** | **Full row required** |
| GET | `/api/program/export?tab=` | **Auth** | CSV; tabs: `deps`,`resources`,`roadmap`,`risks` ( `chains` may 400) |
| POST | `/api/program/atp/projects` | **Auth** | CTOO add project |
| (SSR) | ATP partnership tree | — | Read via page `data` prop; bare GET `/api/program/atp` may 404 |

## Program tab switch (client)

```text
summary → Executive Summary
dag     → Pillar Dependency DAG
chains  → Critical Delivery Chains
deps    → Item-Level Dependencies
risks   → Schedule Risks
blockers→ Active Blockers
resources→ Resources
rbs     → By Initiative
teams   → Teams & Capacity
roadmap → Roadmap   // auth-gated data
```

## Pillar codes & colors

| code | Label | Color |
|---|---|---|
| `infra` | Infrastructure | `#3b82f6` |
| `models` | Models | `#8b5cf6` |
| `dcm` | Data, Context & Memory | `#10b981` |
| `ro` | Reasoning & Orchestration | `#f97316` |
| `runtime` | Runtime | `#f59e0b` |
| `eval` | Evaluation | `#ec4899` |

DAG also shows **HiVE / BU Products**. Filter chips: Infra, Models, DCM, R&O, Runtime, Eval.

FY26 Roadmap months: index `1..12` → Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,Jan,Feb,Mar.

## Schedule risk levels

**Inversion**, **Late Prereq**, **Overlap** (tight), **Enabler**; plus manual risks. Annotation statuses: Open · Acknowledged · Mitigating · Accepted · Resolved.

## API field shapes (Program)

### `GET /metron/api/program/findings` → `Finding[]`

```json
{
  "id": "uuid",
  "priority": "critical|high|medium|low",
  "title": "string",
  "description": "string",
  "added_date": "YYYY-MM-DD",
  "sort_order": 0,
  "created_by": "string",
  "updated_by": "string",
  "created_at": "ISO",
  "updated_at": "ISO"
}
```

### `GET /metron/api/program/item-deps` → `Dep[]`

Key fields: `from_key`, `from_label`, `from_pillar`, `rel_type` (e.g. Prerequisite), `to_key`, `to_label`, `to_pillar`, `risk_label`, `from_start_month`, `from_end_month`, `to_start_month`, `to_end_month`, `schedule_risk_days`, plus live Jira status/due on endpoints.

Work-item IDs: `INF-001`, `DAT-004`, `MDL-002`, `ROO-001`, …

### `GET /metron/api/program/schedule-risks`

```json
{
  "conflicts": [ { "provider_id", "consumer_id", "level", "months", "source", "…" } ],
  "staffing_gaps": [ { "item_id", "has_gap", "gap_note", "blocked", "…" } ],
  "summary": { "inversion", "late_prereq", "overlap", "enabler", "total", "staffing_gaps", "critical" }
}
```

### `GET /metron/api/program/chains`

Delivery-chain objects with phases, step IDs, Jira-linked status, `health`, `done_count`, `at_risk_count`, `blocked_count`, `total_steps`.

### `GET /metron/api/program/resources`

Roster (~314). Keys: `id`, `pillar`, `pillar_code`, `display_name`, `it_code`, `email`, `category`, `role`, `primary_project`, `domain`, `manager`, `fte`, `notes`, `status`. Categories include Regular vs C&O; open roles feed the Resources badge.

### `GET /metron/api/program/team-meta`

Per-pillar: `pillar_code`, `lead`, `fte_needed`, `fte_gap`, `notes`, `roles_override`, `updated_at`, `updated_by`.

### `GET /metron/api/program/roadmap` (auth)

```json
{
  "item_id": "INF-001",
  "pillar": "Infrastructure",
  "pillar_code": "infra",
  "name": "GPU Compute Cluster",
  "priority": "P0",
  "status": "in_progress",
  "start_month": 1,
  "end_month": 9,
  "resources": "…",
  "fte": "5.0",
  "has_gap": false,
  "gap_note": null,
  "blocked": false,
  "dependencies": [],
  "notes": null,
  "jira_url": "https://jira.xpaas.lenovo.com/browse/LATC-6576"
}
```

## Program tab UX notes

### Executive Summary
- Cards with CRITICAL / HIGH / … chips; Added / Edited timestamps
- `+ Add Finding`, `↺ Refresh` (signed-in)
- API: `findings`

### Pillar Dependency DAG
- **Pillar-Level Dependency Graph**
- Layers: Foundation → Core → Enabling → Orchestration (+ HiVE/BU)
- Click node → detail; hover highlights edges

### Critical Delivery Chains
- Expandable chains with phase + done/total
- `+ Add Delivery Chain` (signed-in)
- API: `chains`

### Item-Level Dependencies
- Headers: FROM ID, WORK ITEM, PILLAR, RELATIONSHIP, TO ID, WORK ITEM, PILLAR, SCHEDULE RISK
- Filters: All + per-pillar + “Schedule risks only”
- API: `item-deps`

### Schedule Risks
- Subfilters: All · Date Conflicts · Staffing / Blocked · Manual Risks
- APIs: `schedule-risks`, `risk-annotations`, `manual-risks`

### Active Blockers
- Counts: jira blocked / manual / overdue (badge can show large Jira-blocked counts)
- Project filter + search; resolve/delete when signed-in
- Jira blocked list largely SSR; overlays via `manual-blockers` + `blocker-annotations`

### Resources
- Totals: roster / filled / regular / C&O / open gap / FTE
- Grouped by pillar / initiative; search + filters
- Inline edit/delete when signed-in
- API: `resources`

### By Initiative
- Banner example: live LATC Jira plan — initiatives · epics · assigned tasks · people
- Hierarchy from Epic Link + Parent Link; expandable INIT rows (WBS titles)
- Legend: Done / In progress / To do
- Filter: “Filter initiatives…”
- **No dedicated `/api/program/rbs` JSON** — rendered from SSR

### Teams & Capacity
- Cards: FTE Needed, Staff Gap, Total Items, P0–P3 counts
- Saves via `team-meta` when signed-in

### Roadmap
- Guest → `/metron/login?callbackUrl=%2Fdashboard%2Fprogram`
- Auth: FY26 Gantt, dependency arrows, inline edit; PATCH full row

## Other pages — UI detail

### Overview
- KPIs: Active Users, AI Adoption score, AI Spend
- Chart: Active Users Trend

### Team
- Org rooted at leadership (e.g. Tolga Kurtoglu); Entire team vs Direct reports
- Calorie percentile vs ~31 teams
- Compliance statuses styled: Compliant / Lapsed / …

### Jira Cadence
- Tables: Compliance by Manager Org (Manager, Org, Compliance, Lapsed, None); People (Person, Updates, Active wks, Last, Status)
- Chart: Weekly Update Activity from `issue_updated` changelog events

### CTOO / ATP
- Status map: on-track, at-risk, blocked, pilot, warm, new, done
- Region: all / row / prc
- Categories: Startups, Academia, Industry, Internal
- Add project → `POST /api/program/atp/projects`

### AI ROI
- Funnel steps: Engineers tracked → AI-active → AI-attributed MRs → AI CI pass rate
- Person table columns: AI requests, Accepted lines, AI code %, Accept rate, MRs merged, Commits, Spend, Efficiency (MRs/100 req)

### Contributors
- Columns: Person, MRs, Commits, Reviews, AI Requests, Accept Rate, Issues, Doc Edits
- Org filter via `manager` query

### Activity
- Source filters: all / gitlab / confluence / jira
- Time buckets: Today, Yesterday, This week, Older
- Pagination: Load 40 more events

### Sync Jobs
- Source status cards + Run History (Source, Status, Started, Duration, Rows, Watermark, Error)
- Sources observed: calorie, Confluence, Cursor (+ team 2), GitLab LATC, Jira (+ instance 2), Jira activity (+ instance 2), …

## Agent exploration cache

Local dumps from the full-site crawl (screenshots, `pw_pages.json`, API probes):

`C:\Users\mfink\Downloads\metron-explore\full-explore\`

## Related local skill

`roadmap-dashboard-html` ≈ offline Program twin. Prefer Metron for live Jira-synced state; prefer the HTML skill for shareable XLSX-derived artifacts.
