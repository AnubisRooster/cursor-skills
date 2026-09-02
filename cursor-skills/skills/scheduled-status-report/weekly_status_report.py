#!/usr/bin/env python3
"""
Weekly LATC Status Reports
---------------------------
Generates weekly status reports for three pillars and publishes them to Confluence:
  1. Operations & Infrastructure  (parent: 628270579 — 00-Regular Updates - INFRA)
  2. Evaluation & Benchmarking    (parent: 630655592 — 00-Regular Updates - EVAL)
  3. Models                       (parent: 636192034 — 00-Regular Updates - MODELS)

Each pillar also gets a condensed one-screen "Weekly Pillar Update" (per the
[Template] pages David Richardson set up under "Weekly Pillar Lead Updates -
<Pillar>"), published alongside the detailed report:
  1. Operations & Infrastructure  (parent: 653003208)
  2. Evaluation & Benchmarking    (parent: 653003209)
  3. Models                       (parent: 653003206)

Runs via Windows Task Scheduler every Monday at 9:00 AM Eastern.

Setup:
  pip install cursor-sdk
  set CURSOR_API_KEY=cursor_...   (or add to system environment variables)
  Run setup_scheduled_task.ps1 once to register the scheduled task.
"""

import argparse
import logging
import os
import sys
import time
from datetime import date, timedelta
from logging.handlers import RotatingFileHandler

# Windows compatibility shim for cursor-sdk 0.1.6 — fixes the bridge-discovery
# selector bug (WinError 10038). No-op on non-Windows. Must precede cursor_sdk.
import _win_bridge_patch  # noqa: F401

try:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions, CursorAgentError
except ImportError:
    print("ERROR: cursor-sdk not installed. Run: pip install cursor-sdk", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Logging — writes to scripts/logs/weekly_status_report.log (rotating) and,
# when run interactively, also echoes to the console.
# ---------------------------------------------------------------------------

def _build_logger() -> logging.Logger:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "weekly_status_report.log")

    logger = logging.getLogger("weekly-status")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1 MB per file, keep 12 backups (~3 months of weekly runs + headroom).
    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=12, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    # Force UTF-8 on the console stream so agent tails with arrows/emoji
    # don't crash the handler on Windows cp1252 consoles (logging error only;
    # the file handler already uses utf-8 and is unaffected).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    return logger


LOG = _build_logger()


# ---------------------------------------------------------------------------
# Report prompt — mirrors the format established in the three existing pages
# under parent 628270579 (Weekly Status updates → 00-Regular Updates - INFRA)
# ---------------------------------------------------------------------------

REPORT_PROMPT = """\
Generate the weekly Operations & Infrastructure status report for the LATC \
Confluence space. Follow every step exactly. The page MUST be published in \
Confluence STORAGE format (XHTML) so the native chart macros render.

**Step 1 — Date range**
Determine today's date in YYYY-MM-DD format. The reporting window is the \
7 days ending today (from 7 days ago through today, inclusive).

**Step 2 — Fetch completed issues**
Call jira_search with:
  JQL:    component = "Operations & Infrastructure" AND status changed TO Done \
DURING ("<7-days-ago>", "<today>") ORDER BY assignee ASC
  fields: summary,status,assignee,issuetype,created,resolutiondate,customfield_10006
  limit:  50
If the returned total exceeds 50, paginate with start_at (50, 100, …) until \
every issue is retrieved.

**Step 3 — Resolve Epic names**
Collect every unique Epic key found in customfield_10006 (skip nulls and \
"(This issue is an Epic)" entries). Run a single jira_search:
  JQL:    key in (KEY1, KEY2, …)
  fields: summary,issuetype
Build a lookup map: epic_key → epic_summary. When you label an epic in the
report, ALWAYS use the form "<short epic name> (<EPIC-KEY>)" — e.g.
"5.27 Container Image Updates (LATC-813)" — so charts and tables are
self-describing.

**Step 4 — Check for completed Epics**
Call jira_search with:
  JQL: issuetype = Epic AND component = "Operations & Infrastructure" AND \
status changed TO Done DURING ("<7-days-ago>", "<today>")
Record any epics that closed this window (key, summary, assignee).

**Step 5 — Component health snapshot (for the KPI header + completion pie)**
Run these count-only jira_search calls (limit 1 is fine; read `total`):
  a. component = "Operations & Infrastructure"                              -> total_scope
  b. component = "Operations & Infrastructure" AND statusCategory = Done    -> done_total
  c. component = "Operations & Infrastructure" AND statusCategory = "To Do" -> todo_total
  d. component = "Operations & Infrastructure" AND statusCategory = "In Progress" -> inprog_total
open_total = todo_total + inprog_total.

**Step 6 — Build per-contributor narratives**
Group all completed issues alphabetically by assignee display_name. For each:
  1. Write a 2–4 sentence narrative paragraph describing what they accomplished
     thematically — explain why the work matters, what problem it solves, or
     how the pieces relate. Do NOT simply restate ticket titles.
  2. Follow with a bullet list of their tickets:
       <li><strong>LATC-XXXX</strong> | Epic: <resolved epic name (KEY) or "No Epic linked"> | <summary></li>

**Step 7 — Compute stats and chart tallies**
From the completed-issue set, tally:
  - completed_total (issues moved to Done this window)
  - velocity_per_week = completed_total / 1   (one-week window)
  - by_type:        count of completed issues per issuetype (Task/Story/Bug/Test/…)
  - by_epic:        count of completed issues per epic (use "name (KEY)" labels),
                    sorted desc; group epics with a single completion into
                    "Other (N epics, 1 each)".
  - by_contributor: count of completed issues per assignee, sorted desc; group
                    the long tail of single-ticket assignees into
                    "Other (N contributors, 1 each)".
  - per_epic_velocity = (completed count for that epic) / 1   (issues/week)
  - cycle time (created → resolutiondate): median and mean in days, noting any
    long-lived outliers that skew the mean.
Also use Step-5 numbers for the completion pie and the open-by-status bar.

**Step 7b — Per-epic completion (for the %-complete chart and column)**
For each REAL epic that had at least one completion this period (skip the
"No Epic linked" and "Other (…)" buckets), measure overall progress across ALL
of that epic's child issues (not just this window, and not limited to the
component — this reflects true epic progress):
  total_e = jira_search `"Epic Link" = <EPIC-KEY>`                          (read total)
  done_e  = jira_search `"Epic Link" = <EPIC-KEY> AND statusCategory = Done` (read total)
  open_e  = total_e - done_e
  pct_e   = round(100 * done_e / total_e)   (0 if total_e == 0)
Use limit=1 on these (you only need the `total`). Keep the same "name (KEY)"
labels. Sort the epics for the chart by pct_e ascending (least-complete first)
so the bars that need attention sit at the top.

**Step 8 — Publish to Confluence (STORAGE format)**
Before creating the page, call confluence_search or an equivalent lookup for a \
page titled exactly "Weekly Status - <today YYYY-MM-DD>" in space LATC. If it \
already exists (e.g. from a retried run), call confluence_update_page on that \
existing page instead of creating a duplicate. Otherwise, call \
confluence_create_page with EXACTLY these parameters:
  space_key:             LATC
  title:                 Weekly Status - <today YYYY-MM-DD>
  parent_id:             628270579
  content_format:        storage
  content: (full storage XHTML — see template below)

CRITICAL chart-macro rules (Confluence DC renders these server-side):
  * Every bar chart MUST include BOTH of these parameters or the category
    (epic/contributor/status) names will NOT appear on the axis:
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="orientation">horizontal</ac:parameter>
    - dataOrientation=vertical  -> first table COLUMN is the category labels
      (DC default is "horizontal" = rows-as-series, which hides your labels).
    - orientation=horizontal    -> those category labels sit on the vertical
      (Y) axis with bars extending right (best for long epic names).
  * Title each axis: xLabel = the category ("Epic"/"Contributor"/"Status"),
    yLabel = the measure ("Issues completed"/"Issues open").
  * The FIRST COLUMN of each data table holds the labels; value columns follow.
  * Pies do not need orientation; keep them as <type>pie</type>.

---
STORAGE TEMPLATE (fill in all <placeholders>; keep the macro parameters verbatim):

<p><strong>Component:</strong> Operations &amp; Infrastructure<br/><strong>Reporting Window:</strong> <start> to <today> &middot; <strong>Generated:</strong> <today></p>

<h2>Project Snapshot</h2>
<table><tbody>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Component scope</td><td><total_scope> issues</td></tr>
<tr><td>Overall completion</td><td><strong><done_total> / <total_scope> Done (<pct>%)</strong></td></tr>
<tr><td>Open remaining</td><td><open_total> issues (<todo_total> To Do, <inprog_total> In Progress)</td></tr>
<tr><td>Completed this period</td><td><completed_total> issues</td></tr>
<tr><td>Contributors active (this period)</td><td><N> named + unassigned</td></tr>
<tr><td>Velocity (this period)</td><td>~<velocity_per_week> issues/wk</td></tr>
<tr><td>Cycle time, open&rarr;done</td><td>Median ~<median> days, mean ~<mean> days</td></tr>
<tr><td>Completed Epics this period</td><td><N or 0></td></tr>
</tbody></table>

<h2>Progress Charts</h2>
<table><tbody><tr>
<td><ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">pie</ac:parameter><ac:parameter ac:name="title">Component Completion (all <total_scope>)</ac:parameter><ac:parameter ac:name="legend">true</ac:parameter><ac:parameter ac:name="width">360</ac:parameter><ac:parameter ac:name="height">300</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Status</th><th>Issues</th></tr><tr><td>Done</td><td><done_total></td></tr><tr><td>Open</td><td><open_total></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro></td>
<td><ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">pie</ac:parameter><ac:parameter ac:name="title">Completed This Period by Type</ac:parameter><ac:parameter ac:name="legend">true</ac:parameter><ac:parameter ac:name="width">360</ac:parameter><ac:parameter ac:name="height">300</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Type</th><th>Count</th></tr><!-- one <tr><td>Type</td><td>N</td></tr> per by_type entry --></tbody></table></ac:rich-text-body></ac:structured-macro></td>
</tr></tbody></table>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Status</ac:parameter><ac:parameter ac:name="yLabel">Issues open</ac:parameter><ac:parameter ac:name="title">Open Work Remaining by Status</ac:parameter><ac:parameter ac:name="width">520</ac:parameter><ac:parameter ac:name="height">280</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Status</th><th>Issues</th></tr><tr><td>To Do</td><td><todo_total></td></tr><tr><td>In Progress</td><td><inprog_total></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Epic</ac:parameter><ac:parameter ac:name="yLabel">Issues completed</ac:parameter><ac:parameter ac:name="title">Completed This Period by Epic</ac:parameter><ac:parameter ac:name="width">820</ac:parameter><ac:parameter ac:name="height">380</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Epic</th><th>Completed</th></tr><!-- one row per by_epic entry, label = "name (KEY)" --></tbody></table></ac:rich-text-body></ac:structured-macro>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Epic</ac:parameter><ac:parameter ac:name="yLabel">% complete</ac:parameter><ac:parameter ac:name="title">Epic % Complete (all child issues)</ac:parameter><ac:parameter ac:name="rangeMax">100</ac:parameter><ac:parameter ac:name="width">820</ac:parameter><ac:parameter ac:name="height">420</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Epic</th><th>% Complete</th></tr><!-- one row per epic from Step 7b (sorted by pct_e asc): <td>name (KEY) — done_e/total_e</td><td>pct_e</td> --></tbody></table></ac:rich-text-body></ac:structured-macro>
<p><em>Bar = overall epic completion (Done child issues / all child issues, point-in-time across the full epic, not just this window). Bars are comparable regardless of epic size; absolute Done/Total appear in each label and in the table below.</em></p>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Contributor</ac:parameter><ac:parameter ac:name="yLabel">Issues completed</ac:parameter><ac:parameter ac:name="title">Completed This Period by Contributor</ac:parameter><ac:parameter ac:name="width">760</ac:parameter><ac:parameter ac:name="height">420</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Contributor</th><th>Completed</th></tr><!-- one row per by_contributor entry --></tbody></table></ac:rich-text-body></ac:structured-macro>

<h2>Epic Activity &amp; Velocity (this period)</h2>
<table><tbody>
<tr><th>Epic</th><th>Completed (this wk)</th><th>Velocity (/wk)</th><th>Epic % Complete</th></tr>
<!-- one row per epic with completions: <td>name &middot; <a href="https://jira.xpaas.lenovo.com/browse/KEY">KEY</a></td><td>N</td><td>N.N</td><td>pct_e% (done_e/total_e)</td> ; use "—" in the % cell for the "Other (…)" bucket -->
<tr><td><strong>Total</strong></td><td><strong><completed_total></strong></td><td><strong><velocity_per_week></strong></td><td><strong>&mdash;</strong></td></tr>
</tbody></table>
<p><em>Velocity = issues moved to Done during the window. Epic % Complete = Done child issues / all child issues of that epic (overall progress, point-in-time), so it does not sum and is independent of this window's throughput.</em></p>

<h2>Completed Epics (Done in period)</h2>
<!-- If none: <p>No Epics in <code>Operations &amp; Infrastructure</code> were moved to Done during this reporting window.</p>
     If any: a <table> with columns Epic | Epic Name | Assignee -->

<h2>Executive Summary</h2>
<ul>
<li><strong>Total issues moved to Done:</strong> <completed_total> across <N> contributors</li>
<li><strong>Completed Epics in this window:</strong> <N or 0></li>
<li><strong>Velocity:</strong> ~<velocity_per_week> tickets/week</li>
<li><strong>Key themes this window:</strong> <1–2 sentences></li>
</ul>

<h2>Completed Work by Epic</h2>
<p><em>What moved this period, grouped by epic.</em></p>
<!-- per epic that had completions (sorted by completed count desc): a <h3>name (KEY) &mdash; N done this period &middot; pct_e% complete overall</h3> followed by a 1–2 sentence thematic <p> describing what was accomplished and why it matters (do NOT just list ticket titles). Cover the "No Epic linked" bucket last as a single paragraph if non-trivial. -->

<h2>Contributor Summaries</h2>
<p><em>Each section includes a narrative of what the contributor accomplished, followed by their closed tickets.</em></p>
<!-- per assignee: <h3>Name (N tickets)</h3><p>narrative</p><ul>...ticket <li>s...</ul> -->

<h2>Notes</h2>
<ul>
<li>Report scope is based on Jira issues that <strong>changed to Done</strong> during <start> through <today> and include component <strong>Operations &amp; Infrastructure</strong>.</li>
<li>Epic names are resolved from Epic Link (<code>customfield_10006</code>) where available.</li>
<li>Charts are a point-in-time snapshot generated from Jira via MCP. For always-current charts see the live charts on the parent <em>00-Regular Updates - INFRA</em> page.</li>
</ul>
END TEMPLATE

**Step 9 — Publish condensed Weekly Pillar Update**
Using the SAME underlying data already gathered in Steps 2–7b, also publish a \
decision-grade one-screen executive summary. Pattern reference (approved \
2026-09-02): "so what" pulse + Good/Watch/Bad workstreams + concrete risks \
and leadership asks — NOT a ticket laundry list. Before creating, check \
whether a page titled exactly "<today YYYY-MM-DD> | Infrastructure & \
Operations Weekly Update" already exists under parent_id 653003208 in space \
LATC. If it exists, call confluence_update_page on it instead of creating a \
duplicate. Otherwise call confluence_create_page with:
  space_key:      LATC
  title:          <today YYYY-MM-DD> | Infrastructure & Operations Weekly Update
  parent_id:      653003208
  content_format: storage
  content: (storage XHTML — see CONDENSED TEMPLATE below)

CONDENSED QUALITY RULES (mandatory):
1. Executive pulse MUST have three short blocks: Pillar week / Tech-delivery \
   week (include Done count, velocity, component % Done) / So what (who can \
   do what now that they could not last week, or what remains gated).
2. Stand-up MUST be 2–3 workstream ROWS (not one mega-cell of 3 bullets). \
   Default Infra workstreams: (a) MLOps / ClearML &amp; AI Builder \
   (b) Core Infra / Network / Identity (c) Platform ops / toolchain. Drop a \
   row only if that stream had no material signal this window.
3. Inside each "What we completed" cell, use explicit labels \
   <strong>Good:</strong> / <strong>Watch:</strong> / \
   <strong>Bad / actionable:</strong> with outcomes + evidence (epic % or \
   ticket link). Prefer outcome → proof → who cares over epic title lists.
4. Leadership ask MUST be a concrete decision, date owner, or escalation when \
   ANY gate is evident (Security, Direct Connect, ClearML install, capacity, \
   identity). Use "TBD — pillar lead to confirm" ONLY when no gate is \
   visible in the data. Never invent a person's name.
5. Top risk MUST name impact + mitigation owner. Status column uses single \
   letters G / A / R only (never YellowAMBER / GreenGREEN).
6. Keep to one screen. Do not paste the detailed report.

---
CONDENSED TEMPLATE (storage XHTML; fill in all <placeholders>):

<p><em>Condensed summary — see the <a href="<detailed report URL from Step 8>">full weekly report</a> for charts and ticket-level detail.</em></p>

<h1>Infrastructure &amp; Operations &mdash; Weekly Update</h1>
<table><tbody>
<tr><th>Week of</th><th>Pillar Lead</th><th>Overall Status</th><th>Last Updated</th></tr>
<tr><td><today></td><td>TBD &mdash; pillar lead to confirm</td><td>Green / Amber / Off Track</td><td><today></td></tr>
</tbody></table>

<h2>Executive pulse</h2>
<p><strong>Pillar week:</strong> <2–4 short sentences: narrative leadership should hear — platforms stood up, gates, demos, cross-region teaming></p>
<p><strong>Tech / delivery week:</strong> <completed_total> issues Done (~<velocity_per_week>/wk), <N> epics closed, component <strong><done_total> / <scope_total> Done (<pct>%)</strong>. <one sentence on where schedule risk sits></p>
<p><strong>So what:</strong> <1–3 short sentences naming who is unblocked or still gated and why it matters></p>

<h2>Stand-up</h2>
<table><tbody>
<tr><th>What we completed</th><th>What is next</th><th>Blockers / help needed</th></tr>
<tr>
<td><p><em><strong>MLOps / ClearML &amp; AI Builder.</strong></em> <strong>Good:</strong> [outcome + evidence/link]. <strong>Watch:</strong> [metric or % still thin]. <strong>Bad / actionable:</strong> [concrete slip risk or write "None"].</p></td>
<td>[Next measurable outcomes + links; max 3 short sentences]</td>
<td>[Blocker + impact + owner, or "None blocking coding." plus any schedule risk]</td>
</tr>
<tr>
<td><p><em><strong>Core Infra / Network / Identity.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
<tr>
<td><p><em><strong>Platform ops / toolchain.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> [… or None].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
</tbody></table>

<h2>Interfaces, Risks &amp; Asks</h2>
<table><tbody>
<tr><th>Dependency / contract</th><th>What is needed</th><th>Owner / date</th><th>Status</th></tr>
<tr><td>[Security, datacenter/xCloud, Runtime/Models, DCM, Evaluation, BU]</td><td>[Capacity, circuit, checklist, telemetry, identity, or SLA]</td><td>[Name / date or TBD]</td><td>G / A / R</td></tr>
<!-- up to 3 rows; only dependencies evident this window -->
</tbody></table>
<ul>
<li><strong>Top risk:</strong> [Risk + delivery/business impact + mitigation owner]</li>
<li><strong>Leadership ask:</strong> [Concrete decision / date owner / escalation — or TBD only if none evident]</li>
<li><strong>Reusability check:</strong> [Shared-platform assets vs one-off requests this week]</li>
</ul>

<p><strong>Evidence:</strong> <a href="<detailed report URL from Step 8>">Full weekly report</a> &middot; <a href="https://jira.xpaas.lenovo.com/issues/?jql=component%3D%22Operations%20%26%20Infrastructure%22">Jira board</a> &middot; Roadmap &middot; Capacity / operations dashboard</p>
END CONDENSED TEMPLATE

Style reference — prior pages under the same parent (628270579):
  Biweekly Status - 2026-05-13  (ID 628270599)
  Biweekly Status - 2026-05-27  (ID 628270580)
  Biweekly Status - 2026-06-05  (ID 632542390)
  Weekly Status - 2026-06-12    (ID — today's run)
Match their structure, chart set, and narrative depth exactly.

**FINAL MESSAGE REQUIREMENT (mandatory — the script checks this):**
After confluence_create_page succeeds for the Step 8 detailed report, the \
very first line of your final response MUST be exactly:
  PUBLISHED: <full Confluence page URL of the Step 8 detailed report>
If you were unable to publish the Step 8 report for ANY reason (MCP \
unavailable, API error, page already exists, missing data, etc.) the very \
first line MUST be:
  FAILED: <one-line reason>
The SECOND line MUST report the Step 9 condensed summary page:
  SUMMARY: <full Confluence page URL of the Step 9 condensed page>
or, if Step 9 could not be completed:
  SUMMARY: FAILED: <one-line reason>
Do NOT include any other text before these two sentinel lines.
"""


EVAL_REPORT_PROMPT = """\
Generate the weekly Evaluation & Benchmarking status report for the LATC \
Confluence space. Follow every step exactly. The page MUST be published in \
Confluence STORAGE format (XHTML) so the native chart macros render.

**Step 1 — Date range**
Determine today's date in YYYY-MM-DD format. The reporting window is the \
7 days ending today (from 7 days ago through today, inclusive).

**Step 2 — Fetch completed issues**
Call jira_search with:
  JQL:    component = "Evaluation" AND status changed TO Done \
DURING ("<7-days-ago>", "<today>") ORDER BY assignee ASC
  fields: summary,status,assignee,issuetype,created,resolutiondate,customfield_10006
  limit:  50
If the returned total exceeds 50, paginate with start_at (50, 100, …) until \
every issue is retrieved.

**Step 3 — Resolve Epic names**
Collect every unique Epic key found in customfield_10006 (skip nulls and \
"(This issue is an Epic)" entries). Run a single jira_search:
  JQL:    key in (KEY1, KEY2, …)
  fields: summary,issuetype
Build a lookup map: epic_key → epic_summary. When you label an epic in the
report, ALWAYS use the form "<short epic name> (<EPIC-KEY>)" — e.g.
"5.27 Container Image Updates (LATC-813)" — so charts and tables are
self-describing.

**Step 4 — Check for completed Epics**
Call jira_search with:
  JQL: issuetype = Epic AND component = "Evaluation" AND \
status changed TO Done DURING ("<7-days-ago>", "<today>")
Record any epics that closed this window (key, summary, assignee).

**Step 5 — Component health snapshot (for the KPI header + completion pie)**
Run these count-only jira_search calls (limit 1 is fine; read `total`):
  a. component = "Evaluation"                              -> total_scope
  b. component = "Evaluation" AND statusCategory = Done    -> done_total
  c. component = "Evaluation" AND statusCategory = "To Do" -> todo_total
  d. component = "Evaluation" AND statusCategory = "In Progress" -> inprog_total
open_total = todo_total + inprog_total.

**Step 6 — Build per-contributor narratives**
Group all completed issues alphabetically by assignee display_name. For each:
  1. Write a 2–4 sentence narrative paragraph describing what they accomplished
     thematically — explain why the work matters, what problem it solves, or
     how the pieces relate. Do NOT simply restate ticket titles.
  2. Follow with a bullet list of their tickets:
       <li><strong>LATC-XXXX</strong> | Epic: <resolved epic name (KEY) or "No Epic linked"> | <summary></li>

**Step 7 — Compute stats and chart tallies**
From the completed-issue set, tally:
  - completed_total (issues moved to Done this window)
  - velocity_per_week = completed_total / 1   (one-week window)
  - by_type:        count of completed issues per issuetype (Task/Story/Bug/Test/…)
  - by_epic:        count of completed issues per epic (use "name (KEY)" labels),
                    sorted desc; group epics with a single completion into
                    "Other (N epics, 1 each)".
  - by_contributor: count of completed issues per assignee, sorted desc; group
                    the long tail of single-ticket assignees into
                    "Other (N contributors, 1 each)".
  - per_epic_velocity = (completed count for that epic) / 1   (issues/week)
  - cycle time (created → resolutiondate): median and mean in days, noting any
    long-lived outliers that skew the mean.
Also use Step-5 numbers for the completion pie and the open-by-status bar.

**Step 7b — Per-epic completion (for the %-complete chart and column)**
For each REAL epic that had at least one completion this period (skip the
"No Epic linked" and "Other (…)" buckets), measure overall progress across ALL
of that epic's child issues (not just this window, and not limited to the
component — this reflects true epic progress):
  total_e = jira_search `"Epic Link" = <EPIC-KEY>`                          (read total)
  done_e  = jira_search `"Epic Link" = <EPIC-KEY> AND statusCategory = Done` (read total)
  open_e  = total_e - done_e
  pct_e   = round(100 * done_e / total_e)   (0 if total_e == 0)
Use limit=1 on these (you only need the `total`). Keep the same "name (KEY)"
labels. Sort the epics for the chart by pct_e ascending (least-complete first)
so the bars that need attention sit at the top.

**Step 8 — Publish to Confluence (STORAGE format)**
Before creating the page, call confluence_search or an equivalent lookup for a \
page titled exactly "Weekly Status - Evaluation - <today YYYY-MM-DD>" in space \
LATC. If it already exists (e.g. from a retried run), call \
confluence_update_page on that existing page instead of creating a duplicate. \
Otherwise, call confluence_create_page with EXACTLY these parameters:
  space_key:             LATC
  title:                 Weekly Status - Evaluation - <today YYYY-MM-DD>
  parent_id:             630655592
  content_format:        storage
  content: (full storage XHTML — see template below)

CRITICAL chart-macro rules (Confluence DC renders these server-side):
  * Every bar chart MUST include BOTH of these parameters or the category
    (epic/contributor/status) names will NOT appear on the axis:
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="orientation">horizontal</ac:parameter>
    - dataOrientation=vertical  -> first table COLUMN is the category labels
      (DC default is "horizontal" = rows-as-series, which hides your labels).
    - orientation=horizontal    -> those category labels sit on the vertical
      (Y) axis with bars extending right (best for long epic names).
  * Title each axis: xLabel = the category ("Epic"/"Contributor"/"Status"),
    yLabel = the measure ("Issues completed"/"Issues open").
  * The FIRST COLUMN of each data table holds the labels; value columns follow.
  * Pies do not need orientation; keep them as <type>pie</type>.

---
STORAGE TEMPLATE (fill in all <placeholders>; keep the macro parameters verbatim):

<p><strong>Component:</strong> Evaluation<br/><strong>Reporting Window:</strong> <start> to <today> &middot; <strong>Generated:</strong> <today></p>

<h2>Project Snapshot</h2>
<table><tbody>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Component scope</td><td><total_scope> issues</td></tr>
<tr><td>Overall completion</td><td><strong><done_total> / <total_scope> Done (<pct>%)</strong></td></tr>
<tr><td>Open remaining</td><td><open_total> issues (<todo_total> To Do, <inprog_total> In Progress)</td></tr>
<tr><td>Completed this period</td><td><completed_total> issues</td></tr>
<tr><td>Contributors active (this period)</td><td><N> named + unassigned</td></tr>
<tr><td>Velocity (this period)</td><td>~<velocity_per_week> issues/wk</td></tr>
<tr><td>Cycle time, open&rarr;done</td><td>Median ~<median> days, mean ~<mean> days</td></tr>
<tr><td>Completed Epics this period</td><td><N or 0></td></tr>
</tbody></table>

<h2>Progress Charts</h2>
<table><tbody><tr>
<td><ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">pie</ac:parameter><ac:parameter ac:name="title">Component Completion (all <total_scope>)</ac:parameter><ac:parameter ac:name="legend">true</ac:parameter><ac:parameter ac:name="width">360</ac:parameter><ac:parameter ac:name="height">300</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Status</th><th>Issues</th></tr><tr><td>Done</td><td><done_total></td></tr><tr><td>Open</td><td><open_total></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro></td>
<td><ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">pie</ac:parameter><ac:parameter ac:name="title">Completed This Period by Type</ac:parameter><ac:parameter ac:name="legend">true</ac:parameter><ac:parameter ac:name="width">360</ac:parameter><ac:parameter ac:name="height">300</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Type</th><th>Count</th></tr><!-- one <tr><td>Type</td><td>N</td></tr> per by_type entry --></tbody></table></ac:rich-text-body></ac:structured-macro></td>
</tr></tbody></table>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Status</ac:parameter><ac:parameter ac:name="yLabel">Issues open</ac:parameter><ac:parameter ac:name="title">Open Work Remaining by Status</ac:parameter><ac:parameter ac:name="width">520</ac:parameter><ac:parameter ac:name="height">280</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Status</th><th>Issues</th></tr><tr><td>To Do</td><td><todo_total></td></tr><tr><td>In Progress</td><td><inprog_total></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Epic</ac:parameter><ac:parameter ac:name="yLabel">Issues completed</ac:parameter><ac:parameter ac:name="title">Completed This Period by Epic</ac:parameter><ac:parameter ac:name="width">820</ac:parameter><ac:parameter ac:name="height">380</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Epic</th><th>Completed</th></tr><!-- one row per by_epic entry, label = "name (KEY)" --></tbody></table></ac:rich-text-body></ac:structured-macro>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Epic</ac:parameter><ac:parameter ac:name="yLabel">% complete</ac:parameter><ac:parameter ac:name="title">Epic % Complete (all child issues)</ac:parameter><ac:parameter ac:name="rangeMax">100</ac:parameter><ac:parameter ac:name="width">820</ac:parameter><ac:parameter ac:name="height">420</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Epic</th><th>% Complete</th></tr><!-- one row per epic from Step 7b (sorted by pct_e asc): <td>name (KEY) — done_e/total_e</td><td>pct_e</td> --></tbody></table></ac:rich-text-body></ac:structured-macro>
<p><em>Bar = overall epic completion (Done child issues / all child issues, point-in-time across the full epic, not just this window). Bars are comparable regardless of epic size; absolute Done/Total appear in each label and in the table below.</em></p>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Contributor</ac:parameter><ac:parameter ac:name="yLabel">Issues completed</ac:parameter><ac:parameter ac:name="title">Completed This Period by Contributor</ac:parameter><ac:parameter ac:name="width">760</ac:parameter><ac:parameter ac:name="height">420</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Contributor</th><th>Completed</th></tr><!-- one row per by_contributor entry --></tbody></table></ac:rich-text-body></ac:structured-macro>

<h2>Epic Activity &amp; Velocity (this period)</h2>
<table><tbody>
<tr><th>Epic</th><th>Completed (this wk)</th><th>Velocity (/wk)</th><th>Epic % Complete</th></tr>
<!-- one row per epic with completions: <td>name &middot; <a href="https://jira.xpaas.lenovo.com/browse/KEY">KEY</a></td><td>N</td><td>N.N</td><td>pct_e% (done_e/total_e)</td> ; use "—" in the % cell for the "Other (…)" bucket -->
<tr><td><strong>Total</strong></td><td><strong><completed_total></strong></td><td><strong><velocity_per_week></strong></td><td><strong>&mdash;</strong></td></tr>
</tbody></table>
<p><em>Velocity = issues moved to Done during the window. Epic % Complete = Done child issues / all child issues of that epic (overall progress, point-in-time), so it does not sum and is independent of this window's throughput.</em></p>

<h2>Completed Epics (Done in period)</h2>
<!-- If none: <p>No Epics in <code>Evaluation &amp; Benchmarking</code> were moved to Done during this reporting window.</p>
     If any: a <table> with columns Epic | Epic Name | Assignee -->

<h2>Executive Summary</h2>
<ul>
<li><strong>Total issues moved to Done:</strong> <completed_total> across <N> contributors</li>
<li><strong>Completed Epics in this window:</strong> <N or 0></li>
<li><strong>Velocity:</strong> ~<velocity_per_week> tickets/week</li>
<li><strong>Key themes this window:</strong> <1–2 sentences></li>
</ul>

<h2>Completed Work by Epic</h2>
<p><em>What moved this period, grouped by epic.</em></p>
<!-- per epic that had completions (sorted by completed count desc): a <h3>name (KEY) &mdash; N done this period &middot; pct_e% complete overall</h3> followed by a 1–2 sentence thematic <p> describing what was accomplished and why it matters (do NOT just list ticket titles). Cover the "No Epic linked" bucket last as a single paragraph if non-trivial. -->

<h2>Contributor Summaries</h2>
<p><em>Each section includes a narrative of what the contributor accomplished, followed by their closed tickets.</em></p>
<!-- per assignee: <h3>Name (N tickets)</h3><p>narrative</p><ul>...ticket <li>s...</ul> -->

<h2>Notes</h2>
<ul>
<li>Report scope is based on Jira issues that <strong>changed to Done</strong> during <start> through <today> and include component <strong>Evaluation</strong>.</li>
<li>Epic names are resolved from Epic Link (<code>customfield_10006</code>) where available.</li>
<li>Charts are a point-in-time snapshot generated from Jira via MCP. For always-current charts see the live charts on the parent <em>00-Regular Updates - EVAL</em> page.</li>
</ul>
END TEMPLATE

**Step 9 — Publish condensed Weekly Pillar Update**
Using the SAME underlying data already gathered in Steps 2–7b, also publish a \
decision-grade one-screen executive summary. Follow the Infra condensed QUALITY \
pattern (approved 2026-09-02): Pillar week / Tech-delivery week / So what; \
2–3 workstream rows with Good / Watch / Bad·actionable; concrete leadership \
asks when gates are evident; status G/A/R only. Before creating, check whether \
a page titled exactly "<today YYYY-MM-DD> | Evaluation Weekly Update" already \
exists under parent_id 653003209 in space LATC. If it exists, call \
confluence_update_page on it instead of creating a duplicate. Otherwise call \
confluence_create_page with:
  space_key:      LATC
  title:          <today YYYY-MM-DD> | Evaluation Weekly Update
  parent_id:      653003209
  content_format: storage
  content: (storage XHTML — see CONDENSED TEMPLATE below)

Do NOT fabricate a Pillar Lead name. Leadership ask = concrete decision/date \
owner when a gate is evident; otherwise "TBD — pillar lead to confirm". \
Keep to one screen.

---
CONDENSED TEMPLATE (storage XHTML; fill in all <placeholders>):

<p><em>Condensed summary — see the <a href="<detailed report URL from Step 8>">full weekly report</a> for charts and ticket-level detail.</em></p>

<h1>Evaluation &mdash; Weekly Update</h1>
<table><tbody>
<tr><th>Week of</th><th>Pillar Lead</th><th>Overall Status</th><th>Last Updated</th></tr>
<tr><td><today></td><td>TBD &mdash; pillar lead to confirm</td><td>Green / Amber / Off Track</td><td><today></td></tr>
</tbody></table>

<h2>Executive pulse</h2>
<p><strong>Pillar week:</strong> <narrative leadership should hear></p>
<p><strong>Tech / delivery week:</strong> <completed_total> Done (~<velocity_per_week>/wk), <N> epics closed, component <strong><done_total> / <scope_total> Done (<pct>%)</strong>. <where risk sits></p>
<p><strong>So what:</strong> <who is unblocked or still gated; include numbers when available></p>

<h2>Stand-up</h2>
<table><tbody>
<tr><th>What we completed</th><th>What is next</th><th>Blockers / help needed</th></tr>
<tr>
<td><p><em><strong>Benchmarks / datasets.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
<tr>
<td><p><em><strong>Harness / tooling / SDK.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
<tr>
<td><p><em><strong>Cross-pillar gates.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
</tbody></table>

<h2>Interfaces, Risks &amp; Asks</h2>
<table><tbody>
<tr><th>Dependency / contract</th><th>What is needed</th><th>Owner / date</th><th>Status</th></tr>
<tr><td>[Models, R&amp;O, Runtime, DCM, Infra, BU, or CTO validation]</td><td>[Scenario, metric, dataset, environment, or sign-off]</td><td>[Name / date]</td><td>G / A / R</td></tr>
</tbody></table>
<ul>
<li><strong>Top risk:</strong> [Risk + impact + mitigation owner]</li>
<li><strong>Leadership ask:</strong> [Concrete ask, or TBD only if none evident]</li>
<li><strong>Reusability check:</strong> [Shared eval assets vs one-offs]</li>
</ul>

<p><strong>Evidence:</strong> <a href="<detailed report URL from Step 8>">Full weekly report</a> &middot; <a href="https://jira.xpaas.lenovo.com/issues/?jql=component%3D%22Evaluation%22">Jira board</a> &middot; Roadmap &middot; Evaluation report / benchmark</p>
END CONDENSED TEMPLATE

This is the first report for this pillar; no prior style-reference pages exist yet.

**FINAL MESSAGE REQUIREMENT (mandatory — the script checks this):**
After confluence_create_page succeeds for the Step 8 detailed report, the \
very first line of your final response MUST be exactly:
  PUBLISHED: <full Confluence page URL of the Step 8 detailed report>
If you were unable to publish the Step 8 report for ANY reason (MCP \
unavailable, API error, page already exists, missing data, etc.) the very \
first line MUST be:
  FAILED: <one-line reason>
The SECOND line MUST report the Step 9 condensed summary page:
  SUMMARY: <full Confluence page URL of the Step 9 condensed page>
or, if Step 9 could not be completed:
  SUMMARY: FAILED: <one-line reason>
Do NOT include any other text before these two sentinel lines.
"""


MODELS_REPORT_PROMPT = """\
Generate the weekly Models status report for the LATC Confluence space. \
Follow every step exactly. The page MUST be published in Confluence STORAGE \
format (XHTML) so the native chart macros render.

**Step 1 — Date range**
Determine today's date in YYYY-MM-DD format. The reporting window is the \
7 days ending today (from 7 days ago through today, inclusive).

**Step 2 — Fetch completed issues**
Call jira_search with:
  JQL:    component = "Models" AND status changed TO Done \
DURING ("<7-days-ago>", "<today>") ORDER BY assignee ASC
  fields: summary,status,assignee,issuetype,created,resolutiondate,customfield_10006
  limit:  50
If the returned total exceeds 50, paginate with start_at (50, 100, …) until \
every issue is retrieved.

**Step 3 — Resolve Epic names**
Collect every unique Epic key found in customfield_10006 (skip nulls and \
"(This issue is an Epic)" entries). Run a single jira_search:
  JQL:    key in (KEY1, KEY2, …)
  fields: summary,issuetype
Build a lookup map: epic_key → epic_summary. When you label an epic in the
report, ALWAYS use the form "<short epic name> (<EPIC-KEY>)" — e.g.
"5.27 Container Image Updates (LATC-813)" — so charts and tables are
self-describing.

**Step 4 — Check for completed Epics**
Call jira_search with:
  JQL: issuetype = Epic AND component = "Models" AND \
status changed TO Done DURING ("<7-days-ago>", "<today>")
Record any epics that closed this window (key, summary, assignee).

**Step 5 — Component health snapshot (for the KPI header + completion pie)**
Run these count-only jira_search calls (limit 1 is fine; read `total`):
  a. component = "Models"                              -> total_scope
  b. component = "Models" AND statusCategory = Done    -> done_total
  c. component = "Models" AND statusCategory = "To Do" -> todo_total
  d. component = "Models" AND statusCategory = "In Progress" -> inprog_total
open_total = todo_total + inprog_total.

**Step 6 — Build per-contributor narratives**
Group all completed issues alphabetically by assignee display_name. For each:
  1. Write a 2–4 sentence narrative paragraph describing what they accomplished
     thematically — explain why the work matters, what problem it solves, or
     how the pieces relate. Do NOT simply restate ticket titles.
  2. Follow with a bullet list of their tickets:
       <li><strong>LATC-XXXX</strong> | Epic: <resolved epic name (KEY) or "No Epic linked"> | <summary></li>

**Step 7 — Compute stats and chart tallies**
From the completed-issue set, tally:
  - completed_total (issues moved to Done this window)
  - velocity_per_week = completed_total / 1   (one-week window)
  - by_type:        count of completed issues per issuetype (Task/Story/Bug/Test/…)
  - by_epic:        count of completed issues per epic (use "name (KEY)" labels),
                    sorted desc; group epics with a single completion into
                    "Other (N epics, 1 each)".
  - by_contributor: count of completed issues per assignee, sorted desc; group
                    the long tail of single-ticket assignees into
                    "Other (N contributors, 1 each)".
  - per_epic_velocity = (completed count for that epic) / 1   (issues/week)
  - cycle time (created → resolutiondate): median and mean in days, noting any
    long-lived outliers that skew the mean.
Also use Step-5 numbers for the completion pie and the open-by-status bar.

**Step 7b — Per-epic completion (for the %-complete chart and column)**
For each REAL epic that had at least one completion this period (skip the
"No Epic linked" and "Other (…)" buckets), measure overall progress across ALL
of that epic's child issues (not just this window, and not limited to the
component — this reflects true epic progress):
  total_e = jira_search `"Epic Link" = <EPIC-KEY>`                          (read total)
  done_e  = jira_search `"Epic Link" = <EPIC-KEY> AND statusCategory = Done` (read total)
  open_e  = total_e - done_e
  pct_e   = round(100 * done_e / total_e)   (0 if total_e == 0)
Use limit=1 on these (you only need the `total`). Keep the same "name (KEY)"
labels. Sort the epics for the chart by pct_e ascending (least-complete first)
so the bars that need attention sit at the top.

**Step 8 — Publish to Confluence (STORAGE format)**
Before creating the page, call confluence_search or an equivalent lookup for a \
page titled exactly "Weekly Status - Models - <today YYYY-MM-DD>" in space \
LATC. If it already exists (e.g. from a retried run), call \
confluence_update_page on that existing page instead of creating a duplicate. \
Otherwise, call confluence_create_page with EXACTLY these parameters:
  space_key:             LATC
  title:                 Weekly Status - Models - <today YYYY-MM-DD>
  parent_id:             636192034
  content_format:        storage
  content: (full storage XHTML — see template below)

CRITICAL chart-macro rules (Confluence DC renders these server-side):
  * Every bar chart MUST include BOTH of these parameters or the category
    (epic/contributor/status) names will NOT appear on the axis:
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="orientation">horizontal</ac:parameter>
    - dataOrientation=vertical  -> first table COLUMN is the category labels
      (DC default is "horizontal" = rows-as-series, which hides your labels).
    - orientation=horizontal    -> those category labels sit on the vertical
      (Y) axis with bars extending right (best for long epic names).
  * Title each axis: xLabel = the category ("Epic"/"Contributor"/"Status"),
    yLabel = the measure ("Issues completed"/"Issues open").
  * The FIRST COLUMN of each data table holds the labels; value columns follow.
  * Pies do not need orientation; keep them as <type>pie</type>.

---
STORAGE TEMPLATE (fill in all <placeholders>; keep the macro parameters verbatim):

<p><strong>Component:</strong> Models<br/><strong>Reporting Window:</strong> <start> to <today> &middot; <strong>Generated:</strong> <today></p>

<h2>Project Snapshot</h2>
<table><tbody>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Component scope</td><td><total_scope> issues</td></tr>
<tr><td>Overall completion</td><td><strong><done_total> / <total_scope> Done (<pct>%)</strong></td></tr>
<tr><td>Open remaining</td><td><open_total> issues (<todo_total> To Do, <inprog_total> In Progress)</td></tr>
<tr><td>Completed this period</td><td><completed_total> issues</td></tr>
<tr><td>Contributors active (this period)</td><td><N> named + unassigned</td></tr>
<tr><td>Velocity (this period)</td><td>~<velocity_per_week> issues/wk</td></tr>
<tr><td>Cycle time, open&rarr;done</td><td>Median ~<median> days, mean ~<mean> days</td></tr>
<tr><td>Completed Epics this period</td><td><N or 0></td></tr>
</tbody></table>

<h2>Progress Charts</h2>
<table><tbody><tr>
<td><ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">pie</ac:parameter><ac:parameter ac:name="title">Component Completion (all <total_scope>)</ac:parameter><ac:parameter ac:name="legend">true</ac:parameter><ac:parameter ac:name="width">360</ac:parameter><ac:parameter ac:name="height">300</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Status</th><th>Issues</th></tr><tr><td>Done</td><td><done_total></td></tr><tr><td>Open</td><td><open_total></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro></td>
<td><ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">pie</ac:parameter><ac:parameter ac:name="title">Completed This Period by Type</ac:parameter><ac:parameter ac:name="legend">true</ac:parameter><ac:parameter ac:name="width">360</ac:parameter><ac:parameter ac:name="height">300</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Type</th><th>Count</th></tr><!-- one <tr><td>Type</td><td>N</td></tr> per by_type entry --></tbody></table></ac:rich-text-body></ac:structured-macro></td>
</tr></tbody></table>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Status</ac:parameter><ac:parameter ac:name="yLabel">Issues open</ac:parameter><ac:parameter ac:name="title">Open Work Remaining by Status</ac:parameter><ac:parameter ac:name="width">520</ac:parameter><ac:parameter ac:name="height">280</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Status</th><th>Issues</th></tr><tr><td>To Do</td><td><todo_total></td></tr><tr><td>In Progress</td><td><inprog_total></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Epic</ac:parameter><ac:parameter ac:name="yLabel">Issues completed</ac:parameter><ac:parameter ac:name="title">Completed This Period by Epic</ac:parameter><ac:parameter ac:name="width">820</ac:parameter><ac:parameter ac:name="height">380</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Epic</th><th>Completed</th></tr><!-- one row per by_epic entry, label = "name (KEY)" --></tbody></table></ac:rich-text-body></ac:structured-macro>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Epic</ac:parameter><ac:parameter ac:name="yLabel">% complete</ac:parameter><ac:parameter ac:name="title">Epic % Complete (all child issues)</ac:parameter><ac:parameter ac:name="rangeMax">100</ac:parameter><ac:parameter ac:name="width">820</ac:parameter><ac:parameter ac:name="height">420</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Epic</th><th>% Complete</th></tr><!-- one row per epic from Step 7b (sorted by pct_e asc): <td>name (KEY) — done_e/total_e</td><td>pct_e</td> --></tbody></table></ac:rich-text-body></ac:structured-macro>
<p><em>Bar = overall epic completion (Done child issues / all child issues, point-in-time across the full epic, not just this window). Bars are comparable regardless of epic size; absolute Done/Total appear in each label and in the table below.</em></p>

<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="orientation">horizontal</ac:parameter><ac:parameter ac:name="dataOrientation">vertical</ac:parameter><ac:parameter ac:name="legend">false</ac:parameter><ac:parameter ac:name="xLabel">Contributor</ac:parameter><ac:parameter ac:name="yLabel">Issues completed</ac:parameter><ac:parameter ac:name="title">Completed This Period by Contributor</ac:parameter><ac:parameter ac:name="width">760</ac:parameter><ac:parameter ac:name="height">420</ac:parameter><ac:rich-text-body><table><tbody><tr><th>Contributor</th><th>Completed</th></tr><!-- one row per by_contributor entry --></tbody></table></ac:rich-text-body></ac:structured-macro>

<h2>Epic Activity &amp; Velocity (this period)</h2>
<table><tbody>
<tr><th>Epic</th><th>Completed (this wk)</th><th>Velocity (/wk)</th><th>Epic % Complete</th></tr>
<!-- one row per epic with completions: <td>name &middot; <a href="https://jira.xpaas.lenovo.com/browse/KEY">KEY</a></td><td>N</td><td>N.N</td><td>pct_e% (done_e/total_e)</td> ; use "—" in the % cell for the "Other (…)" bucket -->
<tr><td><strong>Total</strong></td><td><strong><completed_total></strong></td><td><strong><velocity_per_week></strong></td><td><strong>&mdash;</strong></td></tr>
</tbody></table>
<p><em>Velocity = issues moved to Done during the window. Epic % Complete = Done child issues / all child issues of that epic (overall progress, point-in-time), so it does not sum and is independent of this window's throughput.</em></p>

<h2>Completed Epics (Done in period)</h2>
<!-- If none: <p>No Epics in <code>Models</code> were moved to Done during this reporting window.</p>
     If any: a <table> with columns Epic | Epic Name | Assignee -->

<h2>Executive Summary</h2>
<ul>
<li><strong>Total issues moved to Done:</strong> <completed_total> across <N> contributors</li>
<li><strong>Completed Epics in this window:</strong> <N or 0></li>
<li><strong>Velocity:</strong> ~<velocity_per_week> tickets/week</li>
<li><strong>Key themes this window:</strong> <1–2 sentences></li>
</ul>

<h2>Completed Work by Epic</h2>
<p><em>What moved this period, grouped by epic.</em></p>
<!-- per epic that had completions (sorted by completed count desc): a <h3>name (KEY) &mdash; N done this period &middot; pct_e% complete overall</h3> followed by a 1–2 sentence thematic <p> describing what was accomplished and why it matters (do NOT just list ticket titles). Cover the "No Epic linked" bucket last as a single paragraph if non-trivial. -->

<h2>Contributor Summaries</h2>
<p><em>Each section includes a narrative of what the contributor accomplished, followed by their closed tickets.</em></p>
<!-- per assignee: <h3>Name (N tickets)</h3><p>narrative</p><ul>...ticket <li>s...</ul> -->

<h2>Notes</h2>
<ul>
<li>Report scope is based on Jira issues that <strong>changed to Done</strong> during <start> through <today> and include component <strong>Models</strong>.</li>
<li>Epic names are resolved from Epic Link (<code>customfield_10006</code>) where available.</li>
<li>Charts are a point-in-time snapshot generated from Jira via MCP. For always-current charts see the live charts on the parent <em>00-Regular Updates - MODELS</em> page.</li>
</ul>
END TEMPLATE

**Step 9 — Publish condensed Weekly Pillar Update**
Using the SAME underlying data already gathered in Steps 2–7b, also publish a \
decision-grade one-screen executive summary. Follow the Infra condensed QUALITY \
pattern (approved 2026-09-02): Pillar week / Tech-delivery week / So what; \
2–3 workstream rows with Good / Watch / Bad·actionable; concrete leadership \
asks when gates are evident; status G/A/R only. Before creating, check whether \
a page titled exactly "<today YYYY-MM-DD> | Models Weekly Update" already \
exists under parent_id 653003206 in space LATC. If it exists, call \
confluence_update_page on it instead of creating a duplicate. Otherwise call \
confluence_create_page with:
  space_key:      LATC
  title:          <today YYYY-MM-DD> | Models Weekly Update
  parent_id:      653003206
  content_format: storage
  content: (storage XHTML — see CONDENSED TEMPLATE below)

Do NOT fabricate a Pillar Lead name. Leadership ask = concrete decision/date \
owner when a gate is evident; otherwise "TBD — pillar lead to confirm". \
Keep to one screen.

---
CONDENSED TEMPLATE (storage XHTML; fill in all <placeholders>):

<p><em>Condensed summary — see the <a href="<detailed report URL from Step 8>">full weekly report</a> for charts and ticket-level detail.</em></p>

<h1>Models &mdash; Weekly Update</h1>
<table><tbody>
<tr><th>Week of</th><th>Pillar Lead</th><th>Overall Status</th><th>Last Updated</th></tr>
<tr><td><today></td><td>TBD &mdash; pillar lead to confirm</td><td>Green / Amber / Off Track</td><td><today></td></tr>
</tbody></table>

<h2>Executive pulse</h2>
<p><strong>Pillar week:</strong> <narrative leadership should hear></p>
<p><strong>Tech / delivery week:</strong> <completed_total> Done (~<velocity_per_week>/wk), <N> epics closed, component <strong><done_total> / <scope_total> Done (<pct>%)</strong>. <where risk sits></p>
<p><strong>So what:</strong> <who is unblocked or still gated; include numbers when available></p>

<h2>Stand-up</h2>
<table><tbody>
<tr><th>What we completed</th><th>What is next</th><th>Blockers / help needed</th></tr>
<tr>
<td><p><em><strong>Training / Model Factory.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
<tr>
<td><p><em><strong>Optimization / edge / quantization.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
<tr>
<td><p><em><strong>Safety / eval integration / cross-pillar.</strong></em> <strong>Good:</strong> […]. <strong>Watch:</strong> […]. <strong>Bad / actionable:</strong> […].</p></td>
<td>[…]</td>
<td>[…]</td>
</tr>
</tbody></table>

<h2>Interfaces, Risks &amp; Asks</h2>
<table><tbody>
<tr><th>Dependency / contract</th><th>What is needed</th><th>Owner / date</th><th>Status</th></tr>
<tr><td>[DCM, R&amp;O, Runtime, Evaluation, Infra, or BU]</td><td>[Dataset, behavior, package, hardware envelope, benchmark, or capacity]</td><td>[Name / date]</td><td>G / A / R</td></tr>
</tbody></table>
<ul>
<li><strong>Top risk:</strong> [Risk + impact + mitigation owner]</li>
<li><strong>Leadership ask:</strong> [Concrete ask, or TBD only if none evident]</li>
<li><strong>Reusability check:</strong> [Shared model/platform output vs bespoke asks]</li>
</ul>

<p><strong>Evidence:</strong> <a href="<detailed report URL from Step 8>">Full weekly report</a> &middot; <a href="https://jira.xpaas.lenovo.com/issues/?jql=component%3D%22Models%22">Jira board</a> &middot; Roadmap &middot; Model registry / evaluation evidence</p>
END CONDENSED TEMPLATE

This is the first report for this pillar; no prior style-reference pages exist yet.

**FINAL MESSAGE REQUIREMENT (mandatory — the script checks this):**
After confluence_create_page succeeds for the Step 8 detailed report, the \
very first line of your final response MUST be exactly:
  PUBLISHED: <full Confluence page URL of the Step 8 detailed report>
If you were unable to publish the Step 8 report for ANY reason (MCP \
unavailable, API error, page already exists, missing data, etc.) the very \
first line MUST be:
  FAILED: <one-line reason>
The SECOND line MUST report the Step 9 condensed summary page:
  SUMMARY: <full Confluence page URL of the Step 9 condensed page>
or, if Step 9 could not be completed:
  SUMMARY: FAILED: <one-line reason>
Do NOT include any other text before these two sentinel lines.
"""


def _run_report(prompt: str, label: str, api_key: str) -> bool:
    """Run a single pillar report. Returns True on success, False on failure."""
    LOG.info("-" * 60)
    LOG.info("Starting report: %s", label)
    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                # Configured model: Grok 4.5 (SDK id grok-4.5). Prefer this over
                # auto-smart / claude-sonnet-4-5 — the latter returned status=error.
                model="grok-4.5",
                local=LocalAgentOptions(
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    setting_sources=["all"],
                ),
            ),
        )
    except CursorAgentError as err:
        LOG.error(
            "Agent FAILED to start (%s): %s (retryable=%s)",
            label, err.message, err.is_retryable,
        )
        return False
    except Exception as err:  # noqa: BLE001
        LOG.exception("Unexpected error launching agent (%s): %s", label, err)
        return False

    summary = (result.result or "").strip()

    if result.status == "error":
        detail = summary[-500:] if summary else "(no result text returned)"
        LOG.error(
            "Agent run completed with ERRORS (%s). Run ID: %s  detail: %s",
            label, result.id, detail,
        )
        return False
    if summary:
        tail = summary if len(summary) <= 500 else summary[-500:]
        LOG.info("Agent final message (%s, tail): %s", label, tail)

    # Validate the mandatory sentinel line so a "finished" agent that never
    # published still counts as a failure (prevents silent no-ops).
    # Scan all lines — agents sometimes put a short preamble before PUBLISHED:.
    lines = [ln.strip() for ln in (summary.splitlines() if summary else []) if ln.strip()]
    published_line = next((ln for ln in lines if ln.upper().startswith("PUBLISHED:")), "")
    failed_line = next((ln for ln in lines if ln.upper().startswith("FAILED:")), "")
    summary_line = next((ln for ln in lines if ln.upper().startswith("SUMMARY:")), "")

    def _log_summary_line() -> None:
        if not summary_line:
            LOG.warning("Condensed Weekly Pillar Update sentinel missing (%s)", label)
            return
        if summary_line.upper().startswith("SUMMARY: FAILED:"):
            LOG.warning("Condensed Weekly Pillar Update FAILED (%s): %s",
                        label, summary_line.split(":", 2)[2].strip())
        else:
            LOG.info("Condensed Weekly Pillar Update published (%s): %s",
                     label, summary_line.split(":", 1)[1].strip())

    if published_line:
        LOG.info("Report DONE: %s  status=%s  run_id=%s  url=%s",
                 label, result.status, result.id,
                 published_line.split(":", 1)[1].strip())
        _log_summary_line()
        return True
    elif failed_line:
        LOG.error("Report FAILED (agent reported failure): %s  reason=%s  run_id=%s",
                  label, failed_line.split(":", 1)[1].strip(), result.id)
        return False
    else:
        # Agent finished but did not emit the required sentinel — treat as failure.
        first_line = lines[0] if lines else ""
        LOG.error(
            "Report FAILED (missing PUBLISHED/FAILED sentinel): %s  run_id=%s  "
            "status=%s  first_line=%r",
            label, result.id, result.status, first_line[:120],
        )
        return False


def _inject_date_override(prompt: str, today: date) -> str:
    """Prepend a date-override instruction so the agent uses the backfill date."""
    window_start = today - timedelta(days=7)
    override = (
        f"NOTE — BACKFILL RUN: Treat {today.isoformat()} as 'today' for ALL date "
        f"calculations in this prompt. The reporting window is "
        f"{window_start.isoformat()} to {today.isoformat()}. "
        f"Do NOT use the actual current date.\n\n"
    )
    return override + prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly LATC Status Reports")
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help=(
            "Backfill date: treat this date as 'today' for the reporting window "
            "(window = date-7 through date). Omit for the normal current-week run."
        ),
    )
    parser.add_argument(
        "--pillar",
        choices=["infra", "eval", "models"],
        help="Run only the specified pillar report (default: all three).",
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
            LOG.error("Invalid --date value %r — expected YYYY-MM-DD", args.date)
            sys.exit(1)
        LOG.info("Weekly LATC status reports - backfill run (--date %s)", today)
    else:
        today = date.today()
        LOG.info("Weekly LATC status reports - run starting")

    window_start = today - timedelta(days=7)
    LOG.info("Reporting window: %s -> %s", window_start, today)

    all_reports = [
        (REPORT_PROMPT,        "Operations & Infrastructure", "infra"),
        (EVAL_REPORT_PROMPT,   "Evaluation & Benchmarking",  "eval"),
        (MODELS_REPORT_PROMPT, "Models",                     "models"),
    ]

    if args.pillar:
        all_reports = [(p, l, k) for p, l, k in all_reports if k == args.pillar]

    MAX_ATTEMPTS = 2  # 1 retry — most failures observed so far are transient
    failures = []
    for prompt, label, _key in all_reports:
        if args.date:
            prompt = _inject_date_override(prompt, today)
        ok = False
        for attempt in range(1, MAX_ATTEMPTS + 1):
            ok = _run_report(prompt, label, api_key)
            if ok:
                break
            if attempt < MAX_ATTEMPTS:
                LOG.warning(
                    "Retrying report (%s) — attempt %d/%d failed",
                    label, attempt, MAX_ATTEMPTS,
                )
                time.sleep(15)
        if not ok:
            failures.append(label)

    LOG.info("=" * 70)
    if failures:
        LOG.error("Run finished with FAILURES: %s", ", ".join(failures))
        sys.exit(2)

    LOG.info("All reports completed SUCCESSFULLY.")
    sys.exit(0)


if __name__ == "__main__":
    main()
