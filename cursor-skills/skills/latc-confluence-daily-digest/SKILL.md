---
name: latc-confluence-daily-digest
description: >
  Daily LATC Confluence digest for Mike Fink's personal space (~mfink). Runs as
  a Windows Scheduled Task weekdays at 8:00 AM Eastern. Uses the Cursor SDK
  (model grok-4.5) to scrape LATC Confluence updates, score/cluster them, join
  Jira where possible, publish a dated digest under the LATC Daily Digest hub
  in Mike Fink's writing-voice (formal Confluence), and point the hub Latest
  link. Use when setting up, troubleshooting, or changing digest format,
  cadence, filters, voice, or schedule.
---

# latc-confluence-daily-digest

Personal weekday briefing of LATC Confluence activity.

| Item | Value |
|---|---|
| Hub | pageId `684280623` |
| Style reference | pageId `684280624` (2026-09-03 sample) |
| Home | pageId `685742313` |
| Publish space | `~mfink` |
| Source space | `LATC` |
| Schedule | Mon–Fri 8:00 AM Eastern |
| Task name | `LATC Confluence Daily Digest` |
| Model | `grok-4.5` |

## Cadence

| Run day | Window |
|---|---|
| Monday | Fri + Sat + Sun |
| Tuesday–Friday | Prior calendar day only |

## Approved page structure

1. Meta  
2. Pulse (cluster-first)  
3. Connect the dots  
4. Roadmap implications (watchlist from high-signal themes)  
5. Decisions / asks for you (≤5; owner + risk if silent)  
6. Clustered updates  
7. Weekly status rollup — one section for Infra, Eval, Models, DCM, Runtime, R&O  
8. Jira map  
9. Noise / filter log  
10. Evidence  

## Signal score + hard cap

Prefer new pages, decisions/architecture/eval language, substantial diffs, then Jira keys. Hard cap **8–12** (Monday up to **15**). Collapse individual weekly shells into the pillar rollup.

## Voice

**Required.** Before drafting, the agent must read
`C:\Users\mfink\.cursor\skills\writing-voice\SKILL.md` and apply formal
Confluence channel rules (problem/ask/risk shape, sentence cadence, ban list).
This is Mike's personal briefing, not a generic AI summary.

Title format: `YYYY-MM-DD | LATC Confluence Digest`

## Files

```
latc-confluence-daily-digest/
├── SKILL.md
├── latc_confluence_daily_digest.py       # prompt + runner
├── setup_latc_daily_digest_task.ps1      # Mon-Fri 8:00 AM Eastern
└── _win_bridge_patch.py                  # cursor-sdk Windows selector fix
```

Runtime copy used by the scheduled task:

`C:\Users\mfink\Downloads\pillars\scripts\latc_confluence_daily_digest.py`

Keep the skill folder copy in sync when publishing.

## Setup (one-time)

```powershell
pip install cursor-sdk
setx CURSOR_API_KEY "cursor_your_key_here"
# new terminal
cd C:\Users\mfink\Downloads\pillars\scripts
.\setup_latc_daily_digest_task.ps1
python latc_confluence_daily_digest.py                 # smoke today
python latc_confluence_daily_digest.py --date YYYY-MM-DD   # backfill
```

## How it works

```
Windows Task Scheduler (Mon-Fri 08:00 Eastern)
  └── latc_confluence_daily_digest.py
        └── Agent.prompt(..., model="grok-4.5")
              ├── confluence_search (LATC window)
              ├── confluence_get_page / get_page_diff (high-signal)
              ├── jira_get_issue / jira_search (join keys)
              ├── confluence_create/update dated digest under hub
              └── confluence_update hub Latest pointer
```

Success requires first-line sentinel:

```
PUBLISHED: <full Confluence URL>
```

Missing sentinel counts as failure. The runner retries once.

## Customisation

| To change | Edit |
|---|---|
| Page sections / filter rules | `DIGEST_PROMPT_TEMPLATE` in `latc_confluence_daily_digest.py` |
| Style reference page | `REFERENCE_PAGE_ID` (default `684280624`) |
| Hub | `HUB_PAGE_ID` (default `684280623`) |
| Model | `model=` in `AgentOptions` |
| Schedule | `setup_latc_daily_digest_task.ps1` trigger, then re-register |

## Troubleshooting

| Symptom | Fix |
|---|---|
| DNS / xpaas unreachable | Connect Lenovo VPN; re-run |
| Agent status=error empty result | Confirm `grok-4.5` still works |
| Bridge WinError 10061 | Cursor agent bridge down; retry later |
| WinError 10038 | Ensure `_win_bridge_patch` imports before `cursor_sdk` |
| Digest is a changelog | Signal score / hard cap skipped; re-run |
| Weekly pages listed individually | Pillar rollup rule skipped; rewrite |
| Task Last Result != 0 | Read `logs/latc_confluence_daily_digest.log` |
