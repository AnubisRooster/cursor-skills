---
name: infra-leadership-sync
description: >
  Weekly Infrastructure Leadership Sync notes for LATC. Runs as a Windows
  Scheduled Task every Wednesday at 3:00 PM Eastern. Uses the Cursor SDK
  (model grok-4.5) to scrape Jira Operations & Infrastructure, publish a dated
  Confluence notes page under the Infrastructure Leadership Sync hub, and point
  the hub Latest notes link. Use when setting up, troubleshooting, or changing
  the sync page format, schedule, or leadership filter.
---

# infra-leadership-sync

Weekly notes for the Infrastructure Leadership Sync.

| Item | Value |
|---|---|
| Hub | pageId `679722190` |
| Template | pageId `679722196` |
| Style reference | pageId `681704768` (2026-09-02 approved) |
| Space | `LATC` |
| Schedule | Wednesday 3:00 PM Eastern |
| Task name | `LATC Infra Leadership Sync` |
| Model | `grok-4.5` |

## Approved page style (2026-09-02)

This is the format for every future dated page. Do not revert to Pre-read.

### Structure

1. Meta table: Date | Facilitator | Attendees | Notes owner
2. **Summary** with three subheads only:
   - Activities
   - Blockers
   - Upcoming priorities
3. **1. Ongoing work and status updates** (In Progress only)
4. **2. Roadmap items and upcoming priorities** (In Progress only)
5. **3. Blockers and risks**
6. **4. Cross-team dependencies**
7. **Decisions** (numbered questions for the room)
8. **Actions**
9. Evidence line with plain pipes

### Content rules

- Ongoing work and Roadmap: **In Progress only**. No To Do / Backlog rows.
- Each ongoing bullet needs a plain second sentence on why it matters.
- Roadmap table column is **Why it matters**, not empty Notes.
- Summary is the leadership skim. No Jira key spam there.
- Keep blockers and cross-team asks tight. Cap the page to what leadership
  should discuss this week.
- Default: leave regional PRC OSC / FOSSA / China-ops detail off unless the
  room asked for it that week.
- Ops (Non-Tech) is not a primary scrape. It may appear only as a real
  cross-team dependency.

### Voice rules (writing-voice)

- Short to medium sentences. Next sentence same length or shorter.
- Formal Confluence. Complete sentences. No chat openers.
- No em dashes or ornamental en dashes. Use hyphen, comma, period, or pipe.
- No labels like "So what:" or "Key takeaways". Put the implication in prose.
- One bold run per bullet max (topic title only).
- No parallel verb-rhythm bullet stacks.
- Ban brochure words: leverage, synergy, landscape, robust, seamless,
  holistic, utilize, Additionally, Furthermore, Moreover, Going forward.

Title format: `YYYY-MM-DD | Infrastructure Leadership Sync`

## Files

```
infra-leadership-sync/
├── SKILL.md
├── infra_leadership_sync.py              # prompt + runner
├── setup_infra_leadership_sync_task.ps1  # Wednesday 3:00 PM Eastern
└── _win_bridge_patch.py                  # cursor-sdk Windows selector fix
```

Runtime copy used by the scheduled task:

`C:\Users\mfink\Downloads\pillars\scripts\infra_leadership_sync.py`

Keep the skill folder copy in sync when publishing.

## Setup (one-time)

```powershell
pip install cursor-sdk
setx CURSOR_API_KEY "cursor_your_key_here"
# new terminal
cd C:\Users\mfink\Downloads\pillars\scripts
.\setup_infra_leadership_sync_task.ps1
python infra_leadership_sync.py                 # smoke this week
python infra_leadership_sync.py --date YYYY-MM-DD   # backfill
```

## How it works

```
Windows Task Scheduler (Wed 15:00 Eastern)
  └── infra_leadership_sync.py
        └── Agent.prompt(..., model="grok-4.5")
              ├── jira_search (Ops & Infra window + Blocked)
              ├── confluence_create/update dated notes page
              └── confluence_update hub Latest notes pointer
```

Success requires first-line sentinel:

```
PUBLISHED: <full Confluence URL>
```

Missing sentinel counts as failure. The runner retries once.

## Customisation

| To change | Edit |
|---|---|
| Page sections / style rules | `SYNC_PROMPT` in `infra_leadership_sync.py` |
| Style reference page | `REFERENCE_PAGE_ID` (default `681704768`) |
| Confluence template page | pageId `679722196` |
| Roster | `FACILITATOR` / `ATTENDEES` / `NOTES_OWNER` |
| Model | `model=` in `AgentOptions` |
| Schedule | `setup_infra_leadership_sync_task.ps1` trigger, then re-register |

## Troubleshooting

| Symptom | Fix |
|---|---|
| DNS / xpaas unreachable | Connect Lenovo VPN; re-run |
| Agent status=error empty result | Confirm `grok-4.5` still works |
| Bridge WinError 10061 | Cursor agent bridge down; retry later |
| WinError 10038 | Ensure `_win_bridge_patch` imports before `cursor_sdk` |
| Page looks like a ticket dump | Leadership filter / In Progress rule skipped; re-run |
| Em dashes / So what labels | Voice rules skipped; rewrite to writing-voice |
| Task Last Result != 0 | Read `logs/infra_leadership_sync.log` |
