# Graph Report - cursor-skills  (2026-10-05)

## Corpus Check
- 117 files · ~182,572 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 161 nodes · 260 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- gitnexus-opencode.js
- infra_leadership_sync.py
- _parse_issues.py
- infra-leadership-sync/_win_bridge_patch.
- os
- latc_confluence_daily_digest.py
- web-crawl.ps1
- bootstrap-opencode.sh script
- run_digest_via_herdr.ps1

## God Nodes (most connected - your core abstractions)
1. `main()` - 8 edges
2. `main()` - 7 edges
3. `main()` - 6 edges
4. `_run_digest()` - 6 edges
5. `main()` - 6 edges
6. `compute_window()` - 5 edges
7. `main()` - 5 edges
8. `_read_discovery_win()` - 4 edges
9. `_build_logger()` - 4 edges
10. `_read_discovery_win()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `_log_summary_line()` --indirect_call--> `label()`  [INFERRED]
  cursor-skills/skills/scheduled-status-report/weekly_status_report.py → cursor-skills/skills/scheduled-status-report/_build_report.py

## Import Cycles
- None detected.

## Communities (16 total, 8 thin omitted)

### Community 0 - "gitnexus-opencode.js"
Cohesion: 0.07
Nodes (23): analyzeInBackground(), buildEnvelope(), createHintEnvelopeState(), rebuildHintCache(), createMessagesTransformHandler(), createSystemTransformHandler(), discoverRepos(), escapeRegex() (+15 more)

### Community 1 - "infra_leadership_sync.py"
Cohesion: 0.17
Nodes (7): _inject_date_override(), main(), _run_sync(), _inject_date_override(), main(), _run_report(), _log_summary_line()

### Community 2 - "_parse_issues.py"
Cohesion: 0.17
Nodes (10): chart_bar(), esc(), label(), pie(), ticket_li(), load_issues(), main(), normalize() (+2 more)

### Community 3 - "infra-leadership-sync/_win_bridge_patch."
Cohesion: 0.16
Nodes (3): _read_discovery_win(), _read_discovery_win(), _read_discovery_win()

### Community 4 - "os"
Cohesion: 0.18
Nodes (6): _build_logger(), _build_logger(), _build_logger(), clean_text(), main(), same_host()

### Community 5 - "latc_confluence_daily_digest.py"
Cohesion: 0.25
Nodes (7): _BudgetBlocked, build_prompt(), compute_window(), _is_budget_block(), main(), _model_label(), _run_digest()

### Community 8 - "bootstrap-opencode.sh script"
Cohesion: 0.83
Nodes (3): note(), bootstrap-opencode.sh script, step()

### Community 9 - "run_digest_via_herdr.ps1"
Cohesion: 0.83
Nodes (3): Ensure-HerdrServer(), Invoke-DirectDigest(), Log()

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `os` to `infra_leadership_sync.py`, `_parse_issues.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `gitnexus-opencode.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07051282051282051 - nodes in this community are weakly interconnected._