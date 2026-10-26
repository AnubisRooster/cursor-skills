# Graph Report - cursor-skills  (2026-10-26)

## Corpus Check
- 164 files · ~228,834 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .mdc 3, .xml 2, .jsonl 1)

## Summary
- 213 nodes · 326 edges · 21 communities (13 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- latc_confluence_daily_digest.py
- gitnexus-opencode.js
- _parse_issues.py
- tools
- main()
- read_docx.py
- .gitlab-ci.yml
- extract_pdf.py
- crawl_spa.py
- interface
- interface
- web-crawl.ps1
- bootstrap-opencode.sh script
- run_digest_via_herdr.ps1

## God Nodes (most connected - your core abstractions)
1. `main()` - 8 edges
2. `main()` - 7 edges
3. `main()` - 7 edges
4. `tools` - 6 edges
5. `main()` - 6 edges
6. `_run_digest()` - 6 edges
7. `main()` - 6 edges
8. `compute_window()` - 5 edges
9. `para_md()` - 5 edges
10. `main()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `_log_summary_line()` --indirect_call--> `label()`  [INFERRED]
  cursor-skills/skills/scheduled-status-report/weekly_status_report.py → cursor-skills/skills/scheduled-status-report/_build_report.py

## Import Cycles
- None detected.

## Communities (21 total, 8 thin omitted)

### Community 0 - "latc_confluence_daily_digest.py"
Cohesion: 0.09
Nodes (11): _build_logger(), _inject_date_override(), main(), _run_sync(), _read_discovery_win(), _build_logger(), _read_discovery_win(), _build_logger() (+3 more)

### Community 1 - "gitnexus-opencode.js"
Cohesion: 0.07
Nodes (23): analyzeInBackground(), buildEnvelope(), createHintEnvelopeState(), rebuildHintCache(), createMessagesTransformHandler(), createSystemTransformHandler(), discoverRepos(), escapeRegex() (+15 more)

### Community 2 - "_parse_issues.py"
Cohesion: 0.14
Nodes (12): chart_bar(), esc(), label(), pie(), ticket_li(), load_issues(), main(), normalize() (+4 more)

### Community 3 - "tools"
Cohesion: 0.17
Nodes (11): dependencies, tools, interface, default_prompt, display_name, short_description, description, transport (+3 more)

### Community 4 - "main()"
Cohesion: 0.23
Nodes (7): _BudgetBlocked, build_prompt(), compute_window(), _is_budget_block(), main(), _model_label(), _run_digest()

### Community 5 - "read_docx.py"
Cohesion: 0.36
Nodes (7): cell_text(), main(), para_md(), read_meta(), style_of(), table_md(), text_of()

### Community 7 - ".gitlab-ci.yml"
Cohesion: 0.20
Nodes (9): include, template, sast, stage, secret_detection, stage, stages, variables (+1 more)

### Community 8 - "extract_pdf.py"
Cohesion: 0.32
Nodes (3): extract(), main(), _reflow()

### Community 9 - "crawl_spa.py"
Cohesion: 0.39
Nodes (3): clean_text(), main(), same_host()

### Community 10 - "interface"
Cohesion: 0.33
Nodes (5): interface, display_name, short_description, policy, allow_implicit_invocation

### Community 11 - "interface"
Cohesion: 0.40
Nodes (4): interface, default_prompt, display_name, short_description

### Community 13 - "bootstrap-opencode.sh script"
Cohesion: 0.83
Nodes (3): note(), bootstrap-opencode.sh script, step()

### Community 14 - "run_digest_via_herdr.ps1"
Cohesion: 0.83
Nodes (3): Ensure-HerdrServer(), Invoke-DirectDigest(), Log()

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_run_report()` connect `_parse_issues.py` to `latc_confluence_daily_digest.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Should `latc_confluence_daily_digest.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `crawl_spa.py` to `latc_confluence_daily_digest.py`, `_parse_issues.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Should `gitnexus-opencode.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07051282051282051 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `read_docx.py` to `latc_confluence_daily_digest.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Should `_parse_issues.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1422924901185771 - nodes in this community are weakly interconnected._