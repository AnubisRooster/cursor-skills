# Graph Report - cursor-skills  (2026-09-06)

## Corpus Check
- 105 files · ~149,797 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 112 nodes · 130 edges · 24 communities (15 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- gitnexus-opencode.js
- latc_confluence_daily_digest.py
- weekly_status_report.py
- infra_leadership_sync.py
- _build_report.py
- _parse_issues.py
- discoverRepos()
- crawl_spa.py
- web-crawl.ps1
- buildEnvelope()
- createMessagesTransformHandler()
- bootstrap-opencode.sh script
- infra-leadership-sync/_win_bridge_patch.
- latc-confluence-daily-digest/_win_bridge
- scheduled-status-report/_win_bridge_patc
- graphify_pipeline.py
- gitnexusCmd()

## God Nodes (most connected - your core abstractions)
1. `compute_window()` - 5 edges
2. `build_prompt()` - 4 edges
3. `main()` - 4 edges
4. `esc()` - 4 edges
5. `normalize()` - 4 edges
6. `_inject_date_override()` - 4 edges
7. `isStale()` - 4 edges
8. `discoverRepos()` - 4 edges
9. `buildEnvelope()` - 4 edges
10. `createMessagesTransformHandler()` - 4 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (24 total, 2 thin omitted)

### Community 0 - "gitnexus-opencode.js"
Cohesion: 0.18
Nodes (4): createSystemTransformHandler(), extractGitDashCPath(), findGitRoot(), systemAddendumPresent()

### Community 1 - "latc_confluence_daily_digest.py"
Cohesion: 0.31
Nodes (9): _build_logger(), build_prompt(), compute_window(), main(), date, Logger, LATC Confluence Daily Digest ---------------------------- Scrapes LATC…, Return (window_start, window_end_inclusive, window_end_exclusive). Monday:… (+1 more)

### Community 2 - "weekly_status_report.py"
Cohesion: 0.24
Nodes (9): _build_logger(), _inject_date_override(), main(), date, Logger, Weekly LATC Status Reports --------------------------- Generates weekly status…, Run a single pillar report. Returns True on success, False on failure., Prepend a date-override instruction so the agent uses the backfill date. (+1 more)

### Community 3 - "infra_leadership_sync.py"
Cohesion: 0.32
Nodes (7): _build_logger(), _inject_date_override(), main(), date, Logger, Infrastructure Leadership Sync - weekly Confluence notes…, _run_sync()

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

### Community 12 - "infra-leadership-sync/_win_bridge_patch."
Cohesion: 0.50
Nodes (3): Any, Windows compatibility shim for cursor-sdk 0.1.6. The SDK's bridge discovery…, _read_discovery_win()

### Community 13 - "latc-confluence-daily-digest/_win_bridge"
Cohesion: 0.50
Nodes (3): Any, Windows compatibility shim for cursor-sdk 0.1.6. The SDK's bridge discovery…, _read_discovery_win()

### Community 14 - "scheduled-status-report/_win_bridge_patc"
Cohesion: 0.50
Nodes (3): Any, Windows compatibility shim for cursor-sdk 0.1.6. The SDK's bridge discovery…, _read_discovery_win()

### Community 16 - "gitnexusCmd()"
Cohesion: 0.67
Nodes (3): analyzeInBackground(), gitnexusCmd(), isGitNexusCliAvailable()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `buildEnvelope()` connect `buildEnvelope()` to `gitnexus-opencode.js`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **Why does `createHintEnvelopeState()` connect `buildEnvelope()` to `gitnexus-opencode.js`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._