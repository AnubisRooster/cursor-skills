# Graph Report - cursor-skills  (2026-09-24)

## Corpus Check
- 111 files · ~177,076 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 155 nodes · 223 edges · 22 communities (14 shown, 8 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- infra_leadership_sync.py
- infra-leadership-sync/_win_bridge_patch.
- gitnexus-opencode.js
- graphify_pipeline.py
- _build_report.py
- latc_confluence_daily_digest.py
- crawl_spa.py
- _parse_issues.py
- discoverRepos()
- web-crawl.ps1
- buildEnvelope()
- createMessagesTransformHandler()
- bootstrap-opencode.sh script
- run_digest_via_herdr.ps1
- gitnexusCmd()
- createSystemTransformHandler()

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

## Communities (22 total, 8 thin omitted)

### Community 0 - "infra_leadership_sync.py"
Cohesion: 0.12
Nodes (20): argparse, _build_logger(), _inject_date_override(), main(), date, Logger, Infrastructure Leadership Sync - weekly Confluence notes…, _run_sync() (+12 more)

### Community 1 - "infra-leadership-sync/_win_bridge_patch."
Cohesion: 0.14
Nodes (15): cursor_sdk, cursor_sdk_errors, Any, Windows compatibility shim for cursor-sdk 0.1.6. The SDK's bridge discovery…, _read_discovery_win(), Any, Windows compatibility shim for cursor-sdk 0.1.6. The SDK's bridge discovery…, _read_discovery_win() (+7 more)

### Community 2 - "gitnexus-opencode.js"
Cohesion: 0.11
Nodes (10): ref_child_process, ref_fs, ref_node_child_process, ref_node_fs, ref_node_path, ref_opencode_ai_plugin, ref_os, ref_path (+2 more)

### Community 3 - "graphify_pipeline.py"
Cohesion: 0.15
Nodes (11): graphify_analyze, graphify_build, graphify_cluster, graphify_detect, graphify_export, graphify_extract, graphify_llm, graphify_report (+3 more)

### Community 4 - "_build_report.py"
Cohesion: 0.29
Nodes (9): collections, chart_bar(), esc(), label(), pie(), Build Models weekly status Confluence storage XHTML., ticket_li(), _log_summary_line() (+1 more)

### Community 5 - "latc_confluence_daily_digest.py"
Cohesion: 0.31
Nodes (9): _build_logger(), build_prompt(), compute_window(), main(), date, Logger, LATC Confluence Daily Digest ---------------------------- Scrapes LATC…, Return (window_start, window_end_inclusive, window_end_exclusive). Monday:… (+1 more)

### Community 6 - "crawl_spa.py"
Cohesion: 0.28
Nodes (8): clean_text(), main(), crawl_spa.py - Render a JS SPA with Playwright, crawl same-host routes BFS,…, same_host(), playwright_sync_api, re, time, urllib_parse

### Community 7 - "_parse_issues.py"
Cohesion: 0.39
Nodes (7): load_issues(), main(), normalize(), parse_created(), parse_res(), Parse Models weekly-status Jira pages into structured stats., statistics

### Community 8 - "discoverRepos()"
Cohesion: 0.33
Nodes (6): discoverRepos(), getHeadCommit(), hasIndex(), isGitRepo(), isStale(), readMeta()

### Community 10 - "buildEnvelope()"
Cohesion: 0.40
Nodes (5): buildEnvelope(), createHintEnvelopeState(), rebuildHintCache(), escapeXml(), freshnessSummary()

### Community 11 - "createMessagesTransformHandler()"
Cohesion: 0.40
Nodes (5): createMessagesTransformHandler(), escapeRegex(), historyHasEnvelope(), scrubPromptGitnexusBlocks(), stripOptInMarker()

### Community 12 - "bootstrap-opencode.sh script"
Cohesion: 0.83
Nodes (3): note(), bootstrap-opencode.sh script, step()

### Community 13 - "run_digest_via_herdr.ps1"
Cohesion: 0.83
Nodes (3): Ensure-HerdrServer(), Invoke-DirectDigest(), Log()

### Community 14 - "gitnexusCmd()"
Cohesion: 0.67
Nodes (3): analyzeInBackground(), gitnexusCmd(), isGitNexusCliAvailable()

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_run_report()` connect `infra_leadership_sync.py` to `_build_report.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `infra_leadership_sync.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12121212121212122 - nodes in this community are weakly interconnected._
- **Should `infra-leadership-sync/_win_bridge_patch.` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `gitnexus-opencode.js` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._