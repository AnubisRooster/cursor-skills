---
name: scheduled-status-report
description: >
  Automated weekly LATC pillar status reports (Ops & Infra, Evaluation, Models).
  Runs as a Windows Scheduled Task every Monday at 9:00 AM Eastern — uses the
  Cursor SDK (model grok-4.5) to query Jira for Done issues in the last 7 days,
  publish a detailed Confluence report with native chart macros, and publish a
  decision-grade condensed Weekly Pillar Update (so-what pulse, Good/Watch/Bad
  workstreams, concrete risks/asks). Use when setting up, troubleshooting, or
  changing the automated weekly status report format or schedule.
---

# scheduled-status-report

Automated weekly status reports for three LATC Jira components:

| Pillar | Detailed parent | Condensed parent |
|---|---|---|
| Operations & Infrastructure | `628270579` | `653003208` |
| Evaluation | `630655592` | `653003209` |
| Models | `636192034` | `653003206` |

A Python script runs on a schedule, invokes the Cursor SDK, and the agent
publishes both a detailed report and a condensed Weekly Pillar Update — no
manual steps when VPN/DNS and MCP are healthy.

## Schedule

- **When:** every **Monday at 9:00 AM Eastern**
- **Task name:** `LATC Weekly Status Report`
- **Reporting window:** 7 days ending on run day (`today-7` → `today`)
- **Next setup:** re-run `setup_scheduled_task.ps1` after editing the trigger
- **Note:** Sep 7 2026 is Labor Day — confirm machine is on VPN if the run must fire that morning

## What it produces

### 1) Detailed weekly report (`Weekly Status - …`)

- Project Snapshot KPIs (scope, % Done, velocity, cycle time)
- Native Confluence `chart` macros (completion, by-type, by-epic, by-contributor)
- Epic Activity & Velocity table
- Completed-work narratives + contributor summaries

### 2) Condensed Weekly Pillar Update (decision-grade, one screen)

**Approved pattern (2026-09-02)** — Infra reference draft style. Do **not**
emit a ticket laundry list.

| Section | Required content |
|---|---|
| Header table | Week of · Pillar Lead · Overall Status (Green/Amber/Off Track) · Last Updated |
| Executive pulse | **Pillar week** · **Tech / delivery week** (Done count, velocity, component % Done, where risk sits) · **So what** (who is unblocked or still gated) |
| Stand-up | **2–3 workstream rows** (not one mega-cell). Each completed cell uses **Good:** / **Watch:** / **Bad / actionable:** with outcome + evidence |
| Interfaces, Risks & Asks | Up to 3 dependency rows; status **G / A / R** only |
| Top risk | Impact + mitigation owner |
| Leadership ask | Concrete decision/date owner when a gate is evident; `TBD — pillar lead to confirm` only if none |
| Reusability check | Shared-platform assets vs one-offs |
| Evidence | Link to detailed report + Jira board |

**Default Infra workstreams:**

1. MLOps / ClearML & AI Builder  
2. Core Infra / Network / Identity  
3. Platform ops / toolchain  

Eval/Models use analogous workstreams defined in their Step 9 prompts.

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9+ | In `PATH` |
| `cursor-sdk` | `pip install cursor-sdk` |
| `CURSOR_API_KEY` | Persistent **user** env var |
| `mcp-atlassian` | In `%USERPROFILE%\.cursor\mcp.json` with `JIRA_*` + `CONFLUENCE_*` |
| Lenovo VPN / corporate DNS | `*.xpaas.lenovo.com` must resolve at run time |
| Windows Task Scheduler | `setup_scheduled_task.ps1` once |

## Files

```
scheduled-status-report/
├── SKILL.md
├── weekly_status_report.py     ← prompts + runner (source of truth in pillars/scripts/)
├── setup_scheduled_task.ps1    ← Monday 9:00 AM Eastern trigger
├── _win_bridge_patch.py        ← cursor-sdk Windows selector fix
└── logs/weekly_status_report.log
```

Runtime copy used by the scheduled task lives at:

`C:\Users\mfink\Downloads\pillars\scripts\weekly_status_report.py`

Keep the skill folder copy in sync when publishing.

## Setup (one-time)

```powershell
pip install cursor-sdk
setx CURSOR_API_KEY "cursor_your_key_here"
# new terminal
cd C:\Users\mfink\Downloads\pillars\scripts
.\setup_scheduled_task.ps1
python weekly_status_report.py          # smoke all pillars
python weekly_status_report.py --pillar infra --date YYYY-MM-DD   # backfill
```

## How it works

```
Windows Task Scheduler (Mon 09:00 Eastern)
  └── weekly_status_report.py
        └── cursor_sdk.Agent.prompt(..., model="grok-4.5")
              ├── jira_search (Done in window)
              ├── epic resolve + % complete
              ├── confluence_create/update (detailed, storage XHTML)
              └── confluence_create/update (condensed Weekly Pillar Update)
```

Success requires first-line sentinels:

```
PUBLISHED: <detailed URL>
SUMMARY: <condensed URL>
```

Missing sentinels count as failure; the runner retries once.

## Customisation

| To change | Edit |
|---|---|
| Condensed format / quality rules | Step 9 + `CONDENSED TEMPLATE` in each prompt |
| Detailed charts / sections | Step 8 STORAGE TEMPLATE |
| Model | `model=` in `AgentOptions` (currently `grok-4.5`) |
| Schedule | `setup_scheduled_task.ps1` trigger → re-register |
| Single pillar / backfill | `--pillar infra|eval|models` and/or `--date YYYY-MM-DD` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| DNS NXDOMAIN / xpaas unreachable | Connect Lenovo VPN; re-run |
| Agent `status=error` empty result | Confirm `grok-4.5` still works; fall back only if needed |
| Bridge WinError 10061 | Cursor agent bridge down — retry later |
| WinError 10038 | Ensure `_win_bridge_patch.py` imports before `cursor_sdk` |
| Condensed looks like a ticket dump | Step 9 QUALITY RULES were skipped — tighten prompt / re-run pillar |
| Charts missing axis labels | `dataOrientation=vertical` + `orientation=horizontal` on bar macros |
| Task Last Result ≠ 0 | Read `logs/weekly_status_report.log` |

## Scope

- "Completed" = status **changed to Done** in the window (not merely currently Done).
- Epic % Complete = Done children / all children (point-in-time).
- Condensed pages are leadership-facing; detailed pages hold ticket-level evidence.
