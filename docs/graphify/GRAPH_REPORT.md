# Graph Report - cursor-skills  (2026-10-07)

## Corpus Check
- 125 files · ~197,166 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 180 nodes · 297 edges · 18 communities (11 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- gitnexus-opencode.js
- graphify_pipeline.py
- infra_leadership_sync.py
- infra-leadership-sync/_win_bridge_patch.
- os
- latc_confluence_daily_digest.py
- read_docx.py
- _build_report.py
- extract_pdf.py
- web-crawl.ps1
- bootstrap-opencode.sh script
- run_digest_via_herdr.ps1

## God Nodes (most connected - your core abstractions)
1. `main()` - 8 edges
2. `main()` - 7 edges
3. `main()` - 7 edges
4. `main()` - 6 edges
5. `_run_digest()` - 6 edges
6. `main()` - 6 edges
7. `compute_window()` - 5 edges
8. `para_md()` - 5 edges
9. `main()` - 5 edges
10. `_read_discovery_win()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `_log_summary_line()` --indirect_call--> `label()`  [INFERRED]
  cursor-skills/skills/scheduled-status-report/weekly_status_report.py → cursor-skills/skills/scheduled-status-report/_build_report.py

## Import Cycles
- None detected.

## Communities (18 total, 7 thin omitted)

### Community 0 - "gitnexus-opencode.js"
Cohesion: 0.07
Nodes (23): analyzeInBackground(), buildEnvelope(), createHintEnvelopeState(), rebuildHintCache(), createMessagesTransformHandler(), createSystemTransformHandler(), discoverRepos(), escapeRegex() (+15 more)

### Community 1 - "graphify_pipeline.py"
Cohesion: 0.13
Nodes (5): load_issues(), main(), normalize(), parse_created(), parse_res()

### Community 2 - "infra_leadership_sync.py"
Cohesion: 0.17
Nodes (7): _inject_date_override(), main(), _run_sync(), _inject_date_override(), main(), _run_report(), _log_summary_line()

### Community 3 - "infra-leadership-sync/_win_bridge_patch."
Cohesion: 0.16
Nodes (3): _read_discovery_win(), _read_discovery_win(), _read_discovery_win()

### Community 4 - "os"
Cohesion: 0.18
Nodes (6): _build_logger(), _build_logger(), _build_logger(), clean_text(), main(), same_host()

### Community 5 - "latc_confluence_daily_digest.py"
Cohesion: 0.25
Nodes (7): _BudgetBlocked, build_prompt(), compute_window(), _is_budget_block(), main(), _model_label(), _run_digest()

### Community 6 - "read_docx.py"
Cohesion: 0.36
Nodes (7): cell_text(), main(), para_md(), read_meta(), style_of(), table_md(), text_of()

### Community 7 - "_build_report.py"
Cohesion: 0.33
Nodes (5): chart_bar(), esc(), label(), pie(), ticket_li()

### Community 8 - "extract_pdf.py"
Cohesion: 0.32
Nodes (3): extract(), main(), _reflow()

### Community 10 - "bootstrap-opencode.sh script"
Cohesion: 0.83
Nodes (3): note(), bootstrap-opencode.sh script, step()

### Community 11 - "run_digest_via_herdr.ps1"
Cohesion: 0.83
Nodes (3): Ensure-HerdrServer(), Invoke-DirectDigest(), Log()

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `os` to `graphify_pipeline.py`, `infra_leadership_sync.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `gitnexus-opencode.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07051282051282051 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `read_docx.py` to `infra_leadership_sync.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `graphify_pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12987012987012986 - nodes in this community are weakly interconnected._