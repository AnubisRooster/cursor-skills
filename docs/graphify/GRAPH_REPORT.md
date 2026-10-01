# Graph Report - cursor-skills  (2026-10-01)

## Corpus Check
- 116 files · ~181,837 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 161 nodes · 234 edges · 16 communities (9 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- gitnexus-opencode.js
- infra_leadership_sync.py
- graphify_pipeline.py
- infra-leadership-sync/_win_bridge_patch.
- latc_confluence_daily_digest.py
- _build_report.py
- crawl_spa.py
- web-crawl.ps1
- bootstrap-opencode.sh script
- run_digest_via_herdr.ps1

## God Nodes (most connected - your core abstractions)
1. `_run_digest()` - 6 edges
2. `compute_window()` - 5 edges
3. `main()` - 5 edges
4. `build_prompt()` - 4 edges
5. `_model_label()` - 4 edges
6. `_BudgetBlocked` - 4 edges
7. `esc()` - 4 edges
8. `normalize()` - 4 edges
9. `_run_report()` - 4 edges
10. `_inject_date_override()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `_log_summary_line()` --indirect_call--> `label()`  [INFERRED]
  cursor-skills/skills/scheduled-status-report/weekly_status_report.py → cursor-skills/skills/scheduled-status-report/_build_report.py

## Import Cycles
- None detected.

## Communities (16 total, 7 thin omitted)

### Community 0 - "gitnexus-opencode.js"
Cohesion: 0.07
Nodes (23): analyzeInBackground(), buildEnvelope(), createHintEnvelopeState(), rebuildHintCache(), createMessagesTransformHandler(), createSystemTransformHandler(), discoverRepos(), escapeRegex() (+15 more)

### Community 1 - "infra_leadership_sync.py"
Cohesion: 0.12
Nodes (8): _build_logger(), _inject_date_override(), main(), _run_sync(), _build_logger(), _inject_date_override(), main(), _run_report()

### Community 2 - "graphify_pipeline.py"
Cohesion: 0.12
Nodes (5): load_issues(), main(), normalize(), parse_created(), parse_res()

### Community 3 - "infra-leadership-sync/_win_bridge_patch."
Cohesion: 0.14
Nodes (3): _read_discovery_win(), _read_discovery_win(), _read_discovery_win()

### Community 4 - "latc_confluence_daily_digest.py"
Cohesion: 0.21
Nodes (8): _BudgetBlocked, _build_logger(), build_prompt(), compute_window(), _is_budget_block(), main(), _model_label(), _run_digest()

### Community 5 - "_build_report.py"
Cohesion: 0.29
Nodes (6): chart_bar(), esc(), label(), pie(), ticket_li(), _log_summary_line()

### Community 6 - "crawl_spa.py"
Cohesion: 0.28
Nodes (3): clean_text(), main(), same_host()

### Community 8 - "bootstrap-opencode.sh script"
Cohesion: 0.83
Nodes (3): note(), bootstrap-opencode.sh script, step()

### Community 9 - "run_digest_via_herdr.ps1"
Cohesion: 0.83
Nodes (3): Ensure-HerdrServer(), Invoke-DirectDigest(), Log()

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_run_report()` connect `infra_leadership_sync.py` to `_build_report.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `gitnexus-opencode.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07051282051282051 - nodes in this community are weakly interconnected._
- **Should `infra_leadership_sync.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12121212121212122 - nodes in this community are weakly interconnected._
- **Should `graphify_pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11688311688311688 - nodes in this community are weakly interconnected._
- **Should `infra-leadership-sync/_win_bridge_patch.` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._