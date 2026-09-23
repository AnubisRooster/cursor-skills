---
name: latc-confluence-daily-digest
description: >
  Daily LATC Confluence digest for Mike Fink's personal space (~mfink). Runs as
  a Windows Scheduled Task weekdays at 8:00 AM Eastern. Uses the Cursor SDK
  (model grok-4.6) to scrape LATC Confluence updates across ALL pillars plus
  ATP, score/cluster them, join Jira where possible, publish a dated digest
  under the LATC Daily Digest hub in Mike Fink's writing-voice (formal
  Confluence), and point the hub Latest link. Use when setting up,
  troubleshooting, or changing digest format, cadence, filters, voice, ATP
  section, or schedule.
---

# latc-confluence-daily-digest

Personal weekday **reader's digest** of significant LATC Confluence activity
across all pillars and ATP. Not an Infrastructure-only brief.

| Item | Value |
|---|---|
| Hub | pageId `684280623` |
| Style reference | pageId `684280624` (2026-09-03 sample) |
| Home | pageId `685742313` |
| Publish space | `~mfink` |
| Source space | `LATC` |
| Schedule | Mon–Fri 8:00 AM Eastern |
| Task name | `LATC Confluence Daily Digest` |
| Model | `grok-4.6` |
| Scope lock | 2026-09-23: all pillars + ATP section |

## Cadence

| Run day | Window |
|---|---|
| Monday | Fri + Sat + Sun |
| Tuesday–Friday | Prior calendar day only |

## Approved page structure

1. Meta  
2. Pulse (all-pillar + ATP skim)  
3. Connect the dots  
4. Roadmap implications  
5. Decisions / asks for you (≤5)  
6. Clustered updates  
7. **ATP projects / updates / proposals** (required; project-first table)  
8. Weekly status rollup — Infra, Eval, Models, DCM, Runtime, R&O / HiVE  
9. Jira map  
10. Noise / filter log  
11. Evidence  

## ATP section (required)

Heading exactly: `ATP projects / updates / proposals`

| Column | Meaning |
|---|---|
| Project / proposal | Plexus, Sphere, HiVE / AI Forge, P-Cube, 2nd Brain, GLT, Hybrid Router, coding-agent, HiVE Bench, Ecosystem, etc. |
| What moved | Substance this window |
| Owner | Named people |
| Lens | Architecture \| Prototyping \| Ecosystem when known |
| Watch / ask | Dated risk or decision |

Collapse individual `ATP Weekly Update — Name` shells into this table by
**project**, not by author. Do not dump ATP weeklies into Noise.

Every run also does an **ATP CQL pass** (title ~ ATP / Plexus / Sphere /
P-Cube / HiVE Bench / 2nd-Brain / GLT, etc.) so Infra-heavy windows cannot
starve the section.

## Signal score + hard cap

Prefer new pages, decisions/architecture/eval/proposal language, substantial
diffs, then Jira keys. Hard cap **8–12** Pulse clusters (Monday up to **15**).
ATP table separately capped ~**8–12** project rows.

## Voice

**Required.** Before drafting, the agent must read
`C:\Users\mfink\.cursor\skills\writing-voice\SKILL.md` and apply formal
Confluence channel rules (problem/ask/risk shape, sentence cadence, ban list).

Title format: `YYYY-MM-DD | LATC Confluence Digest`

## Files

```
latc-confluence-daily-digest/
├── SKILL.md
├── latc_confluence_daily_digest.py       # prompt + runner (RUNTIME for task)
├── run_digest_via_herdr.ps1              # scheduled entry (Herdr + Python fallback)
├── setup_latc_daily_digest_task.ps1
└── _win_bridge_patch.py
```

Scheduled task runs the **skill folder** copy via Herdr. Keep
`pillars/scripts/latc_confluence_daily_digest.py` in sync when editing the
prompt.

## Setup (one-time)

```powershell
pip install cursor-sdk
setx CURSOR_API_KEY "cursor_your_key_here"
# new terminal
cd C:\Users\mfink\.claude\skills\latc-confluence-daily-digest
# task already points at run_digest_via_herdr.ps1
python latc_confluence_daily_digest.py                 # smoke today
python latc_confluence_daily_digest.py --date YYYY-MM-DD   # backfill
```

## How it works

```
Windows Task Scheduler (Mon-Fri 08:00 Eastern)
  └── run_digest_via_herdr.ps1
        └── latc_confluence_daily_digest.py
              └── Agent.prompt(..., model="grok-4.6")
                    ├── confluence_search (LATC window + ATP pass)
                    ├── confluence_get_page / get_page_diff
                    ├── jira_get_issue / jira_search
                    ├── confluence_create/update dated digest under hub
                    └── confluence_update hub Latest pointer
```

Success requires first-line sentinel:

```
PUBLISHED: <full Confluence page URL>
```

Missing sentinel counts as failure. The runner retries once.

## Customisation

| To change | Edit |
|---|---|
| Page sections / ATP / filter rules | `DIGEST_PROMPT_TEMPLATE` in `latc_confluence_daily_digest.py` |
| Style reference page | `REFERENCE_PAGE_ID` (default `684280624`) |
| Hub | `HUB_PAGE_ID` (default `684280623`) |
| Model | `model=` in `AgentOptions` |
| Schedule | Task Scheduler action / `setup_latc_daily_digest_task.ps1` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| DNS / xpaas unreachable | Connect Lenovo VPN; re-run |
| Agent status=error empty result | Confirm `grok-4.6` still works; try direct python |
| Herdr workspace create fails | Wrapper falls back to direct python; start `herdr server` |
| Bridge WinError 10061 | Cursor agent bridge down; retry later |
| WinError 10038 | Ensure `_win_bridge_patch` imports before `cursor_sdk` |
| Digest is Infra-only | ATP pass / all-pillars scope skipped; re-run with updated prompt |
| ATP weeklies listed as Noise | Collapse into ATP section by project |
| Task Last Result != 0 | Read `~/.herdr-pilot/digest-*.log` and skill `logs/` |
