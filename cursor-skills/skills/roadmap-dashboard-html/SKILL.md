---
name: roadmap-dashboard-html
description: >
  Generate a single self-contained, interactive HTML dashboard from a roadmap
  workbook (XLSX) for portfolio/program planning. Use this skill whenever the
  user wants an HTML roadmap, an interactive Gantt, a cross-team/pillar
  dependency map or DAG, a schedule-risk view, a resourcing/capacity view, or an
  executive summary built from a planning spreadsheet — especially when they say
  "make an interactive HTML", "build a dashboard from this roadmap", "visualize
  dependencies", "Gantt with dependencies", "schedule risks", or "executive
  report". Output is one offline .html file (no server, no build) with inline
  editing, browser-local persistence, and CSV export. Complements
  confluence-publish-html (to publish the result) and repo-mental-map-tpm.
---

# roadmap-dashboard-html

Builds a **single, offline, self-contained HTML dashboard** from a roadmap
workbook. Everything (data, CSS, JS) is inlined into one `.html` file that opens
directly in any modern browser — no server, no build step, no external requests.

## When to use

- Turning a planning XLSX into an interactive, shareable artifact.
- Showing **cross-team / cross-pillar dependencies** as a DAG plus an item-level
  Gantt with dependency arrows.
- Surfacing **schedule risks** (date inversions, late prerequisites, tight
  overlaps) and **staffing gaps** on the critical path.
- Giving leadership an **editable executive summary** + resourcing view.

## Input contract

| Input | Required | Notes |
|---|---|---|
| Roadmap workbook (`.xlsx`) | **Yes** | Sheets for pillar/team roadmaps, item-level dependencies, and (optional) business value. Parsed by unzipping the xlsx and reading `xl/sharedStrings.xml` + `xl/worksheets/*.xml`. |
| Resource registry | No | People by team/pillar/project (e.g., a Confluence page read via `confluence-dc-mcp`). Drives the Resources + capacity views. |
| Hiring plan (`.xlsx`) | No | Open roles → rendered as "gaps" per pillar/project. |
| Date window / phases | No | Defaults inferred from item dates; override with explicit quarters/months. |

## Output contract

- `*<name>*.html` — the standalone dashboard with these tabs:
  Executive Summary (editable) · Pillar Dependency DAG (clickable nodes) ·
  Teams & Capacity · Roadmap/Gantt (inline-editable, dependency arrows) ·
  Resources · Blockers · Critical Delivery Chains · Item-Level Dependencies ·
  Schedule Risks (auto-detected + manually annotatable).
- Optional `*<name>*.fragment.html` — a Confluence HTML-macro fragment (see
  `confluence-publish-html`).
- All edits persist client-side via `localStorage`; every tab exports to CSV
  (UTF-8 BOM).

## Build approach (deterministic, no heavy deps)

1. **Parse** the xlsx as a zip; map shared strings; read each sheet into row
   objects. Do **not** require pandas/openpyxl unless already available.
2. **Model** the data: items, dependencies, teams, resources, blockers, chains.
3. **Detect schedule risks**: for each dependency, compare provider end vs
   consumer start → classify `inversion` (consumer starts before provider ends),
   `finish` (late prerequisite), `overlap` (tight), or `ok`.
4. **Render** one HTML file: inline `<style>` + `<script>`; SVG for the DAG and
   Gantt dependency arrows; vanilla JS for editing/persistence/CSV. No CDN links.
5. **Verify**: open-check the file size and that it has no external `http(s)://`
   asset references.

## Guardrails

- **Read-only on sources.** Never modify the input workbook or registry.
- **PII awareness.** Resource/hiring data embeds names/emails — warn the user and
  keep any repo/Confluence destination **private**. Offer a sanitized build.
- **Offline-only output.** The generated HTML must make no network calls.
- **No secrets** in the file. Tokens/credentials never get embedded.

## Starter instruction

```
Use roadmap-dashboard-html on <PATH_TO_ROADMAP.xlsx> (optionally with
<RESOURCE_REGISTRY> and <HIRING_PLAN.xlsx>). Produce a single offline
dashboard.html with dependency DAG, editable Gantt, resourcing, and a
Schedule Risks tab. Keep it self-contained and warn me about any embedded PII.
```
