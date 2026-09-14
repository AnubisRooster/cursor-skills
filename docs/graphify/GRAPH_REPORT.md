# Graph Report - cursor-skills  (2026-09-14)

## Corpus Check
- 106 files · ~164,460 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 116 nodes · 138 edges · 21 communities (12 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- weekly_status_report.py
- latc_confluence_daily_digest.py
- infra_leadership_sync.py
- gitnexus-opencode.js
- _build_report.py
- _parse_issues.py
- discoverRepos()
- crawl_spa.py
- web-crawl.ps1
- buildEnvelope()
- createMessagesTransformHandler()
- bootstrap-opencode.sh script
- graphify_pipeline.py
- gitnexusCmd()

## God Nodes (most connected - your core abstractions)
1. `compute_window()` - 5 edges
2. `build_prompt()` - 4 edges
3. `main()` - 4 edges
4. `esc()` - 4 edges
5. `normalize()` - 4 edges
6. `_run_report()` - 4 edges
7. `_inject_date_override()` - 4 edges
8. `isStale()` - 4 edges
9. `discoverRepos()` - 4 edges
10. `buildEnvelope()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `_log_summary_line()` --indirect_call--> `label()`  [INFERRED]
  cursor-skills/skills/scheduled-status-report/weekly_status_report.py → cursor-skills/skills/scheduled-status-report/_build_report.py

## Import Cycles
- None detected.

## Communities (21 total, 2 thin omitted)

### Community 0 - "weekly_status_report.py"
Cohesion: 0.14
Nodes (13): _build_logger(), _inject_date_override(), main(), date, Logger, Weekly LATC Status Reports --------------------------- Generates weekly status…, Run a single pillar report. Returns True on success, False on failure., Prepend a date-override instruction so the agent uses the backfill date. (+5 more)

### Community 1 - "latc_confluence_daily_digest.py"
Cohesion: 0.18
Nodes (12): _build_logger(), build_prompt(), compute_window(), main(), date, Logger, LATC Confluence Daily Digest ---------------------------- Scrapes LATC…, Return (window_start, window_end_inclusive, window_end_exclusive). Monday:… (+4 more)

### Community 2 - "infra_leadership_sync.py"
Cohesion: 0.18
Nodes (10): _build_logger(), _inject_date_override(), main(), date, Logger, Infrastructure Leadership Sync - weekly Confluence notes…, _run_sync(), Any (+2 more)

### Community 3 - "gitnexus-opencode.js"
Cohesion: 0.18
Nodes (4): createSystemTransformHandler(), extractGitDashCPath(), findGitRoot(), systemAddendumPresent()

### Community 4 - "_build_report.py"
Cohesion: 0.48
Nodes (6): chart_bar(), esc(), label(), pie(), Build Models weekly status Confluence storage XHTML., ticket_li()

### Community 5 - "_parse_issues.py"
Cohesion: 0.48
Nodes (6): load_issues(), main(), normalize(), parse_created(), parse_res(), Parse Models weekly-status Jira pages into structured stats.

### Community 6 - "discoverRepos()"
Cohesion: 0.33
Nodes (6): discoverRepos(), getHeadCommit(), hasIndex(), isGitRepo(), isStale(), readMeta()

### Community 7 - "crawl_spa.py"
Cohesion: 0.60
Nodes (4): clean_text(), main(), crawl_spa.py - Render a JS SPA with Playwright, crawl same-host routes BFS,…, same_host()

### Community 9 - "buildEnvelope()"
Cohesion: 0.40
Nodes (5): buildEnvelope(), createHintEnvelopeState(), rebuildHintCache(), escapeXml(), freshnessSummary()

### Community 10 - "createMessagesTransformHandler()"
Cohesion: 0.40
Nodes (5): createMessagesTransformHandler(), escapeRegex(), historyHasEnvelope(), scrubPromptGitnexusBlocks(), stripOptInMarker()

### Community 11 - "bootstrap-opencode.sh script"
Cohesion: 0.83
Nodes (3): note(), bootstrap-opencode.sh script, step()

### Community 13 - "gitnexusCmd()"
Cohesion: 0.67
Nodes (3): analyzeInBackground(), gitnexusCmd(), isGitNexusCliAvailable()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_log_summary_line()` connect `weekly_status_report.py` to `_build_report.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `label()` connect `_build_report.py` to `weekly_status_report.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `weekly_status_report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._