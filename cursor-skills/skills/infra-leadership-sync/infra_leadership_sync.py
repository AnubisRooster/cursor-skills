#!/usr/bin/env python3
"""
Infrastructure Leadership Sync - weekly Confluence notes
--------------------------------------------------------
Scrapes recent LATC Jira (Operations & Infrastructure), writes a dated notes
page under the Infrastructure Leadership Sync hub, and updates the hub
"Latest notes" link. Ops (Non-Tech) is not a primary scrape; include it only
when it is a real cross-team dependency.

Runs via Windows Task Scheduler every Wednesday at 3:00 PM Eastern.

Setup:
  pip install cursor-sdk
  CURSOR_API_KEY must be a persistent user environment variable
  Run setup_infra_leadership_sync_task.ps1 once to register the scheduled task.

Approved page style (2026-09-02, pageId=681704768): Summary (Activities /
Blockers / Upcoming priorities), In Progress only for ongoing work and
roadmap, plain human prose (writing-voice; no em dashes or brochure labels).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import date, timedelta
from logging.handlers import RotatingFileHandler

# time is used for retry backoff between Agent.prompt attempts

# Windows compatibility shim for cursor-sdk 0.1.6 - fixes the bridge-discovery
# selector bug (WinError 10038). No-op on non-Windows. Must precede cursor_sdk.
import _win_bridge_patch  # noqa: F401

try:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions, CursorAgentError
except ImportError:
    print("ERROR: cursor-sdk not installed. Run: pip install cursor-sdk", file=sys.stderr)
    sys.exit(1)


HUB_PAGE_ID = "679722190"
TEMPLATE_PAGE_ID = "679722196"
REFERENCE_PAGE_ID = "681704768"
SPACE_KEY = "LATC"
FACILITATOR = "Mike Fink"
ATTENDEES = "Chris, Duncan, Qigang, Amardeep, Aaron"
NOTES_OWNER = "Mike Fink"
INFRA_INTAKE = "Aaron / Anusha / Gus"


def _build_logger() -> logging.Logger:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "infra_leadership_sync.log")

    logger = logging.getLogger("infra-leadership-sync")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=12, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    return logger


LOG = _build_logger()


SYNC_PROMPT = """\
Create this week's Infrastructure Leadership Sync notes page in LATC Confluence.
This is an unattended scheduled run. Publish the page. Do not wait for human
approval. Use the mcp-atlassian server (Jira Data Center + Confluence DC).

Match the APPROVED style from reference pageId={reference}
(2026-09-02 | Infrastructure Leadership Sync). That page is the style source of
truth. Prefer it over any older Pre-read template. Also read template
pageId={template} for roster defaults only.

**Page contract**
- Space: LATC
- Hub (parent): pageId={hub}  title "Infrastructure Leadership Sync"
  https://km.xpaas.lenovo.com/pages/viewpage.action?pageId={hub}
- Template: pageId={template}
- Reference (style source of truth): pageId={reference}
- New page title MUST be exactly:  YYYY-MM-DD | Infrastructure Leadership Sync
  where YYYY-MM-DD is today's date (the Wednesday of this run).
- Labels on the dated page: infra, meeting-notes, leadership-sync
- content_format: markdown

**Standing roster (prefill on new pages)**
- Facilitator: {facilitator}
- Attendees: {attendees}
- Notes owner: {notes_owner}
- Default Infra intake owners for unassigned cross-team Infra asks: {infra_intake}

**Idempotency and preserve in-room edits**
1. confluence_get_page_children on parent_id={hub} (limit 50).
2. If a child already has today's title, UPDATE that page (do not create a duplicate).
3. Otherwise confluence_create_page with space_key=LATC, parent_id={hub}.
4. When UPDATING an existing dated page, first confluence_get_page it. Preserve:
   - Facilitator / Attendees / Notes owner if they are already real names
     (not "[Name]" / "Infra Pillar leadership")
   - Any non-empty Roadmap "Notes" or "Why it matters" cells edited in the room
   - Decisions and Actions if they contain real content (not only the
     placeholder follow-up row / "Capture in the room")
   Refresh Summary, ongoing work, roadmap rows, blockers, and cross-team
   dependencies from Jira.

**Step 1 - Date**
Determine today's date in America/New_York as YYYY-MM-DD. Use that as the page
title date.

**Step 2 - Scrape Jira DC (project LATC)**
Primary component is **Operations & Infrastructure** only. Do not scrape
Operations (Non-Tech) as a source list. Use jira_search.
fields: summary,status,issuetype,assignee,priority,updated,created,components,labels
limit: 25 (paginate only if you need a second page for Blocked).

Run these JQLs:
A. Recently updated open Infra:
   project = LATC AND component = "Operations & Infrastructure"
   AND updated >= -14d AND statusCategory != Done ORDER BY updated DESC
B. Recently created Infra:
   project = LATC AND component = "Operations & Infrastructure"
   AND created >= -14d ORDER BY created DESC
C. Open Infra Initiative / Epic / Feature:
   project = LATC AND component = "Operations & Infrastructure"
   AND issuetype in (Initiative, Epic, Feature)
   AND statusCategory != Done ORDER BY updated DESC
D. Currently Blocked Infra:
   project = LATC AND component = "Operations & Infrastructure"
   AND status = Blocked AND statusCategory != Done
   ORDER BY priority DESC, updated DESC
E. Highest / Critical open Infra (Story, Task, Epic, Initiative, Feature only):
   project = LATC AND component = "Operations & Infrastructure"
   AND statusCategory != Done AND priority in (Highest, Critical)
   AND issuetype in (Story, Task, Epic, Initiative, Feature)
   ORDER BY priority DESC, updated DESC

**Step 3 - Leadership filter (do not dump the board)**
Open Infra is large. Keep the page to items leadership should discuss this week.

Include:
- Currently Blocked Infra tickets
- In Progress Core Infra / Landing Zone / ClearML / identity / network /
  security / Developer Portal work that leadership owns
- Highest / Critical items that are In Progress or true blockers
- Brand-new cross-pillar asks on Infra (DCM, HiVE, Eval) when they need a room
  decision

Exclude:
- Anything not In Progress from sections "1. Ongoing work" and "2. Roadmap"
  (To Do / Backlog alone is not enough unless it is Blocked and belongs under
  Blockers)
- Ticket laundry lists with no why-it-matters sentence
- Sub-task noise unless the parent is the discussion item
- Ops (Non-Tech) PKB / meeting / hardware-loan / calendar / Slack tickets
- Hiring written-test tickets unless staffing is the point of the sync
- Regional / PRC OSC / FOSSA / China-ops detail unless leadership asked for it
  this week (default: leave it off this page)

Ops (Non-Tech) may appear only in Cross-team dependencies when it is a real
dependency.

**Step 4 - Voice and formatting (required)**
Write like a human meeting note, not an AI brief. Follow writing-voice:
- Short to medium sentences. Next sentence same length or shorter.
- Formal Confluence. Complete sentences. No chat openers.
- Problem / ask / risk shape where useful. No brochure language.
- Do NOT use em dashes or en dashes as ornament. Use plain hyphen, comma,
  period, or pipe.
- Do NOT use labels like "So what:" or "Key takeaways". Put the implication
  in a plain second sentence.
- Do NOT bold every phrase. One bold run per bullet max (topic title only).
- Do NOT start three bullets with the same verb rhythm.
- Ban: leverage, synergy, landscape, robust, seamless, holistic, utilize,
  Additionally, Furthermore, Moreover, Going forward, comprehensive overview.
- Evidence line uses plain pipes, not middots or fancy separators.

**Step 5 - Page body**
Required sections (use these headings exactly):

1) One-row meta table:
   Date | Facilitator | Attendees | Notes owner
   (Date = today; roster as above unless preserving existing names)

2) Heading: Summary
   Three subheadings exactly:
   ### Activities
   ### Blockers
   ### Upcoming priorities
   Each is 3-5 short bullets. No Jira key spam here. Name the work and the
   consequence. This replaces any "Pre-read" section. Do not create Pre-read.

   After Summary, one related-update link to the latest written weekly update
   under parent 653003208.

3) "1. Ongoing work and status updates"
   Bullets with Jira key links (https://jira.xpaas.lenovo.com/browse/LATC-NNNN).
   **In Progress only.** Each bullet: bold topic title, then keys/owners, then
   one plain sentence on why it matters for LATC / HiVE / ML. Cap at about 7
   bullets.

4) "2. Roadmap items and upcoming priorities"
   Intro line: "In Progress only. Highest / Critical noted where set."
   Compact table columns:
   Item | Type | Status | Owner | Why it matters
   **In Progress rows only.** No To Do epics. Cap at about 8 rows.

5) "3. Blockers and risks"
   Table: Item | Impact | Owner | Needed
   Keep to the blockers and live risks leadership must clear.

6) "4. Cross-team dependencies"
   Table: Dependency | What is needed | Other team | Owner
   Only active asks that need another pillar this week. Cap at about 5 rows.
   If Infra-side owner is Unassigned, put {infra_intake}.

7) "Decisions"
   Line: "Capture in the room:" then a numbered list of 3-5 concrete questions
   (who / date / path). Link Jira keys in the questions.

8) "Actions"
   Empty table with one [Follow-up] placeholder row unless preserving real
   actions. Columns: Action | Owner | Due

9) Evidence line:
   Evidence: [Weekly update] | [Infra Jira component] | [Work Map]
   Work Map: https://km.xpaas.lenovo.com/pages/viewpage.action?pageId=672837246
   Infra Jira: component Operations & Infrastructure, not Done.

**Step 6 - Hub pointer**
confluence_get_page page_id={hub}. Then confluence_update_page on the hub:
keep the existing cadence/agenda/related text, but set "Latest notes" to the
dated page you just published. Do not change the hub title.

**Step 7 - Labels**
confluence_add_label on the dated page for: infra, meeting-notes, leadership-sync
(skip if already present).

**Final response - first lines MUST be exactly one of:**
  PUBLISHED: <full Confluence page URL>
or
  FAILED: <one-line reason>
Do NOT include any other text before that sentinel line.
""".format(
    hub=HUB_PAGE_ID,
    template=TEMPLATE_PAGE_ID,
    reference=REFERENCE_PAGE_ID,
    facilitator=FACILITATOR,
    attendees=ATTENDEES,
    notes_owner=NOTES_OWNER,
    infra_intake=INFRA_INTAKE,
)


def _run_sync(prompt: str, api_key: str) -> bool:
    LOG.info("-" * 60)
    LOG.info("Starting Infrastructure Leadership Sync notes")
    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model="grok-4.5",
                local=LocalAgentOptions(
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    setting_sources=["all"],
                ),
            ),
        )
    except CursorAgentError as err:
        LOG.error(
            "Agent FAILED to start: %s (retryable=%s)",
            err.message, err.is_retryable,
        )
        return False
    except Exception as err:  # noqa: BLE001
        LOG.exception("Unexpected error launching agent: %s", err)
        return False

    summary = (result.result or "").strip()

    if result.status == "error":
        detail = summary[-500:] if summary else "(no result text returned)"
        LOG.error(
            "Agent run completed with ERRORS. Run ID: %s  detail: %s",
            result.id, detail,
        )
        return False
    if summary:
        tail = summary if len(summary) <= 500 else summary[-500:]
        LOG.info("Agent final message (tail): %s", tail)

    lines = [ln.strip() for ln in (summary.splitlines() if summary else []) if ln.strip()]
    published_line = next((ln for ln in lines if ln.upper().startswith("PUBLISHED:")), "")
    failed_line = next((ln for ln in lines if ln.upper().startswith("FAILED:")), "")

    if published_line:
        LOG.info(
            "Sync DONE: status=%s  run_id=%s  url=%s",
            result.status, result.id, published_line.split(":", 1)[1].strip(),
        )
        return True
    if failed_line:
        LOG.error(
            "Sync FAILED (agent reported failure): reason=%s  run_id=%s",
            failed_line.split(":", 1)[1].strip(), result.id,
        )
        return False

    first_line = lines[0] if lines else ""
    LOG.error(
        "Sync FAILED (missing PUBLISHED/FAILED sentinel): run_id=%s  "
        "status=%s  first_line=%r",
        result.id, result.status, first_line[:120],
    )
    return False


def _inject_date_override(prompt: str, today: date) -> str:
    override = (
        f"NOTE - BACKFILL RUN: Treat {today.isoformat()} as 'today' for ALL date "
        f"calculations in this prompt. The Jira window is the 14 days ending "
        f"{today.isoformat()}. Do NOT use the actual current date.\n\n"
    )
    return override + prompt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Weekly Infrastructure Leadership Sync Confluence notes"
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help=(
            "Backfill date: treat this date as 'today' for the page title and "
            "Jira window. Omit for the normal current-week run."
        ),
    )
    args = parser.parse_args()

    LOG.info("=" * 70)

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        LOG.error(
            "CURSOR_API_KEY environment variable is not set. "
            "Add it as a persistent user environment variable and retry."
        )
        sys.exit(1)

    if args.date:
        try:
            today = date.fromisoformat(args.date)
        except ValueError:
            LOG.error("Invalid --date value %r - expected YYYY-MM-DD", args.date)
            sys.exit(1)
        LOG.info("Infrastructure Leadership Sync - backfill run (--date %s)", today)
        prompt = _inject_date_override(SYNC_PROMPT, today)
    else:
        today = date.today()
        LOG.info("Infrastructure Leadership Sync - run starting (%s)", today)
        prompt = SYNC_PROMPT

    window_start = today - timedelta(days=14)
    LOG.info("Jira window: %s -> %s", window_start, today)

    ok = False
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        ok = _run_sync(prompt, api_key)
        if ok:
            break
        if attempt < max_attempts:
            LOG.warning("Retrying - attempt %d/%d failed", attempt, max_attempts)
            time.sleep(15)

    LOG.info("=" * 70)
    if not ok:
        LOG.error("Run finished with FAILURE")
        sys.exit(2)

    LOG.info("Leadership sync notes published SUCCESSFULLY.")
    sys.exit(0)


if __name__ == "__main__":
    main()
