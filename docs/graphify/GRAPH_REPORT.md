# Graph Report - cursor-skills  (2026-10-05)

## Corpus Check
- 122 files · ~192,730 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 169 nodes · 273 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- gitnexus-opencode.js
- weekly_status_report.py
- infra_leadership_sync.py
- _parse_issues.py
- latc_confluence_daily_digest.py
- argparse
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

### Community 1 - "weekly_status_report.py"
Cohesion: 0.11
Nodes (6): _read_discovery_win(), _read_discovery_win(), _inject_date_override(), main(), _run_report(), _read_discovery_win()

### Community 2 - "infra_leadership_sync.py"
Cohesion: 0.13
Nodes (9): _build_logger(), _inject_date_override(), main(), _run_sync(), _build_logger(), _build_logger(), clean_text(), main() (+1 more)

### Community 3 - "_parse_issues.py"
Cohesion: 0.15
Nodes (11): chart_bar(), esc(), label(), pie(), ticket_li(), load_issues(), main(), normalize() (+3 more)

### Community 4 - "latc_confluence_daily_digest.py"
Cohesion: 0.25
Nodes (7): _BudgetBlocked, build_prompt(), compute_window(), _is_budget_block(), main(), _model_label(), _run_digest()

### Community 6 - "argparse"
Cohesion: 0.31
Nodes (3): extract(), main(), _reflow()

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

- **Why does `_run_report()` connect `weekly_status_report.py` to `_parse_issues.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `gitnexus-opencode.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07051282051282051 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `infra_leadership_sync.py` to `_parse_issues.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `weekly_status_report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11375661375661375 - nodes in this community are weakly interconnected._
- **Should `infra_leadership_sync.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13405797101449277 - nodes in this community are weakly interconnected._