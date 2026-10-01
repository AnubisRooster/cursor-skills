# Graph Report - cursor-skills  (2026-10-01)

## Corpus Check
- 116 files · ~181,454 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 155 nodes · 223 edges · 22 communities (12 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- infra_leadership_sync.py
- infra-leadership-sync/_win_bridge_patch.
- gitnexus-opencode.js
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

## Communities (22 total, 10 thin omitted)

### Community 0 - "infra_leadership_sync.py"
Cohesion: 0.12
Nodes (8): _build_logger(), _inject_date_override(), main(), _run_sync(), _build_logger(), _inject_date_override(), main(), _run_report()

### Community 1 - "infra-leadership-sync/_win_bridge_patch."
Cohesion: 0.14
Nodes (3): _read_discovery_win(), _read_discovery_win(), _read_discovery_win()

### Community 4 - "_build_report.py"
Cohesion: 0.29
Nodes (6): chart_bar(), esc(), label(), pie(), ticket_li(), _log_summary_line()

### Community 5 - "latc_confluence_daily_digest.py"
Cohesion: 0.31
Nodes (5): _build_logger(), build_prompt(), compute_window(), main(), _run_digest()

### Community 6 - "crawl_spa.py"
Cohesion: 0.28
Nodes (3): clean_text(), main(), same_host()

### Community 7 - "_parse_issues.py"
Cohesion: 0.39
Nodes (5): load_issues(), main(), normalize(), parse_created(), parse_res()

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
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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