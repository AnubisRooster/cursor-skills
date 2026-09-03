#!/usr/bin/env python3
"""
LATC Confluence Daily Digest
----------------------------
Scrapes LATC Confluence updates for the configured window, publishes a dated
digest under Mike Fink's personal space hub (LATC Daily Digest), and updates
the hub Latest link.

Cadence (America/New_York):
  Monday     -> Fri + Sat + Sun
  Tue-Friday -> prior calendar day only

Runs via Windows Task Scheduler weekdays at 8:00 AM Eastern.

Setup:
  pip install cursor-sdk
  CURSOR_API_KEY must be a persistent user environment variable
  Run setup_latc_daily_digest_task.ps1 once to register the scheduled task.

Approved page style: sample pageId=684280624 (2026-09-03 | LATC Confluence Digest).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import date, timedelta
from logging.handlers import RotatingFileHandler

# Windows compatibility shim for cursor-sdk — must precede cursor_sdk.
import _win_bridge_patch  # noqa: F401

try:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions, CursorAgentError
except ImportError:
    print("ERROR: cursor-sdk not installed. Run: pip install cursor-sdk", file=sys.stderr)
    sys.exit(1)


HUB_PAGE_ID = "684280623"
REFERENCE_PAGE_ID = "684280624"
HOME_PAGE_ID = "685742313"
SPACE_KEY = "~mfink"
SOURCE_SPACE = "LATC"


def _build_logger() -> logging.Logger:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "latc_confluence_daily_digest.log")

    logger = logging.getLogger("latc-confluence-daily-digest")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=30, encoding="utf-8"
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


def compute_window(run_date: date) -> tuple[date, date, date]:
    """Return (window_start, window_end_inclusive, window_end_exclusive).

    Monday: Fri–Sun (run_date-3 .. run_date-1).
    Tue–Sun: prior calendar day only (scheduled runs are weekdays only).
    """
    if run_date.weekday() == 0:  # Monday
        start = run_date - timedelta(days=3)
        end = run_date - timedelta(days=1)
    else:
        start = end = run_date - timedelta(days=1)
    return start, end, end + timedelta(days=1)


DIGEST_PROMPT_TEMPLATE = """\
Create today's LATC Confluence Daily Digest page in personal space ~mfink.
This is an unattended scheduled run. Publish the page. Do not wait for human
approval. Use the mcp-atlassian server (Jira Data Center + Confluence DC).

Match the APPROVED style from reference pageId={reference}
(2026-09-03 | LATC Confluence Digest). That page is the style source of truth.
Also read hub pageId={hub} for cadence, filter rules, and roadmap watchlist.

**Page contract**
- Space: {space}  (personal space; quote as "~mfink" in CQL)
- Hub (parent): pageId={hub}  title "LATC Daily Digest"
  https://km.xpaas.lenovo.com/pages/viewpage.action?pageId={hub}
- Home (grandparent): pageId={home}
- Reference (style source of truth): pageId={reference}
- New page title MUST be exactly:  {run_date} | LATC Confluence Digest
- content_format: markdown
- table_layout: wide

**Run date and scrape window (America/New_York) — use these exact dates**
- Run date (page title date): {run_date}
- Window start (inclusive): {window_start}
- Window end (inclusive): {window_end}
- Window end exclusive (for CQL upper bound): {window_end_excl}
- Cadence rule applied: {cadence_note}

**Idempotency**
1. confluence_get_page_children on parent_id={hub} (limit 50).
2. If a child already has title "{run_date} | LATC Confluence Digest", UPDATE
   that page (do not create a duplicate).
3. Otherwise confluence_create_page with space_key={space}, parent_id={hub}.

**Step 1 - Scrape LATC Confluence**
Use confluence_search with spaces_filter empty string (or LATC) and CQL:

A. Modified in window (paginate with limit=50 as needed; aim to cover the set):
   type=page AND space=LATC AND lastModified >= "{window_start}"
   AND lastModified < "{window_end_excl}" ORDER BY lastModified DESC

B. Created in window (new-page preference):
   type=page AND space=LATC AND created >= "{window_start}"
   AND created < "{window_end_excl}" ORDER BY created DESC

For high-signal candidates, confluence_get_page (markdown). When version jumped
hard (roughly +3 or more in-window, or a known long page with large edit), use
confluence_get_page_diff for from_version -> to_version and summarize WHAT
CHANGED, not the whole page.

**Step 2 - Signal score and hard cap (required)**
Prefer, in order:
1. New pages
2. Decision / architecture / evaluation / recommendation / RFC / roadmap language
3. Substantial version diffs
4. Jira key / Epic / Initiative mentions
5. Parent path under known hubs (Infra, Eval, Models, Plexus, HiVE, identity)

Hard cap: **8-12** high-signal items. On Monday weekend packs, up to **15**.
Cluster first. Do not emit a chronological laundry list.

Exclude / demote:
- Empty or nearly empty folder pages
- Cosmetic-only bumps
- Attachment OCR, comment-thread dumps
- Full CN->EN translation (English summary + keep Chinese title and link)

**Weekly status pages**
Titles matching YYYYMM-Name or similar individual weekly shells must NOT be
listed one-by-one. Collapse into **one Weekly status rollup** covering pillars:
Infra | Eval | Models | DCM | Runtime | R&O
Surface blockers, decisions, and cross-pillar asks only.

**Step 3 - Join Jira where possible**
Extract LATC-\\d+ (and other project keys if clearly relevant) from titles,
bodies, and links. Resolve with jira_get_issue or jira_search:
fields summary,status,assignee,issuetype,updated,priority
Flag Confluence-only proposals with no Jira as a governance gap.

**Step 4 - Roadmap watchlist**
Score implications against themes derived from high-signal content this window.
Seed list (refresh if new clusters repeat):
- Corporate IdP / SSO / AWS Identity Center
- Plexus / HiVE RA / Metron dogfooding
- Hybrid Agent Routing SDK / Model Router / cache-aware routing
- Eval benches, golden datasets, Sphere / quality trackers
- GPU / ClearML / capacity (when pages score high)
- China OSC / PRC packaging only when it gates ROW delivery

**Step 5 - Voice (MANDATORY: writing-voice skill)**
Before drafting any page body, READ the full skill file:
  C:\\Users\\mfink\\.cursor\\skills\\writing-voice\\SKILL.md
(and examples.md beside it if present). This digest is published as Mike Fink
in Confluence. Write in that voice. Do not invent a generic AI brief tone.

Confluence channel rules from the skill (enforce all of them):
- Formal Confluence. Complete sentences. Capitalize. Headings. No chat openers.
- Sentence length usually matches the previous sentence, or shorter.
- Problem / ask / risk shape. Lead with the situation. Then the ask. Then the
  cost of waiting. Do not slap "Problem:" / "Ask:" labels on every bullet;
  put the shape in the prose and in the Asks table.
- No em dashes or ornamental en dashes. Use hyphen, comma, period, or pipe.
- No brochure language or AI tells from the skill ban list (leverage, synergy,
  landscape, robust, seamless, holistic, utilize, Additionally, Furthermore,
  Moreover, Going forward, Key takeaways, comprehensive overview, etc.).
- One bold run per bullet max (topic title only). Usually none elsewhere.
- Do not start three bullets with the same verb rhythm.
- Concrete nouns: people, dates, teams, tickets, regions. Not vague
  "stakeholders" / "alignment."
- Optimize for Mike's jobs: Infra leadership, roadmap collisions, cross-pillar
  asks, identity/security, capacity. Default demote pure China weekly detail
  unless it creates an Infra/Eval/Models/DCM/Runtime/R&O dependency.

**Step 6 - Page body (required headings)**
Use these sections in order:

1) Meta table:
   Window | Source | High-signal clusters | Weekly status | Jira joined

2) Pulse
   5-8 bullets. Cluster-first skim. What moved, who owns it, why it matters.

3) Connect the dots
   Table: Theme | Belong together | Why it matters

4) Roadmap implications
   Numbered list mapped to the watchlist themes that scored this window.

5) Decisions / asks for you
   Table: # | Ask | Owner signal | Risk if silent
   Cap at **5** asks. Every ask needs owner signal and risk if silent.

6) Clustered updates
   Theme subheadings with links. Not chronological.

7) Weekly status rollup (all pillars)
   Table: Pillar | What moved | Watch
   Rows for: Infra, Eval, Models, DCM, Runtime, R&O
   Mention weekly authors collapsed (names only), do not expand each page.

8) Jira map
   Table: Key | Summary | Status | Assignee | Surfaced from
   Note any Confluence-only gaps.

9) Noise / filter log
   Brief: what was excluded or collapsed and why.

10) Evidence
    CQL window, page counts, note that format follows reference {reference}.

**Step 7 - Hub pointer**
confluence_get_page page_id={hub}. Then confluence_update_page on the hub:
keep cadence / filter / watchlist / automation text, but set **Latest** to the
dated page you just published (title + URL). Do not change the hub title.

**Final response - first lines MUST be exactly one of:**
  PUBLISHED: <full Confluence page URL>
or
  FAILED: <one-line reason>
Do NOT include any other text before that sentinel line.
"""


def build_prompt(run_date: date) -> str:
    start, end, end_excl = compute_window(run_date)
    if run_date.weekday() == 0:
        cadence_note = (
            f"Monday run: weekend pack covering {start.isoformat()} through "
            f"{end.isoformat()} (Fri+Sat+Sun)."
        )
    else:
        cadence_note = (
            f"Weekday run: prior day only ({start.isoformat()})."
        )
    return DIGEST_PROMPT_TEMPLATE.format(
        hub=HUB_PAGE_ID,
        reference=REFERENCE_PAGE_ID,
        home=HOME_PAGE_ID,
        space=SPACE_KEY,
        source=SOURCE_SPACE,
        run_date=run_date.isoformat(),
        window_start=start.isoformat(),
        window_end=end.isoformat(),
        window_end_excl=end_excl.isoformat(),
        cadence_note=cadence_note,
    )


def _run_digest(prompt: str, api_key: str) -> bool:
    LOG.info("-" * 60)
    LOG.info("Starting LATC Confluence Daily Digest")
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
            "Digest DONE: status=%s  run_id=%s  url=%s",
            result.status, result.id, published_line.split(":", 1)[1].strip(),
        )
        return True
    if failed_line:
        LOG.error(
            "Digest FAILED (agent reported failure): reason=%s  run_id=%s",
            failed_line.split(":", 1)[1].strip(), result.id,
        )
        return False

    first_line = lines[0] if lines else ""
    LOG.error(
        "Digest FAILED (missing PUBLISHED/FAILED sentinel): run_id=%s  "
        "status=%s  first_line=%r",
        result.id, result.status, first_line[:120],
    )
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LATC Confluence Daily Digest (personal space ~mfink)"
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help=(
            "Backfill / override: treat this date as the run date for the page "
            "title and window calculation. Omit for today's Eastern calendar date."
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
            run_date = date.fromisoformat(args.date)
        except ValueError:
            LOG.error("Invalid --date value %r - expected YYYY-MM-DD", args.date)
            sys.exit(1)
        LOG.info("LATC Daily Digest - backfill/override run (--date %s)", run_date)
    else:
        # Local machine is Eastern; date.today() matches Task Scheduler local time.
        run_date = date.today()
        LOG.info("LATC Daily Digest - run starting (%s)", run_date)

    start, end, end_excl = compute_window(run_date)
    LOG.info(
        "Window: %s -> %s (CQL upper bound %s)",
        start, end, end_excl,
    )

    prompt = build_prompt(run_date)

    ok = False
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        ok = _run_digest(prompt, api_key)
        if ok:
            break
        if attempt < max_attempts:
            LOG.warning("Retrying - attempt %d/%d failed", attempt, max_attempts)
            time.sleep(15)

    LOG.info("=" * 70)
    if not ok:
        LOG.error("Run finished with FAILURE")
        sys.exit(2)

    LOG.info("LATC Confluence Daily Digest published SUCCESSFULLY.")
    sys.exit(0)


if __name__ == "__main__":
    main()
