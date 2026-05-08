---
name: jira-create-issues
description: Create Jira Epics and child Stories/Tasks via the mcp-atlassian server (self-hosted Jira Data Center), enforcing a mandatory field set (Summary, Description, Epic Link, Estimate, Components, Labels, Function area, Acceptance Criteria, Definition of Ready, Definition of Done) and a hierarchical WBS numbering rule (Initiative X.0 -> Epic X.Y -> Story X.Y.Z) regardless of what Jira's screens require. Enforces the three-orthogonal-dimensions model (Pillars=Components, Teams=Labels, Programs=Initiatives), 8 pillar-based components, team/product/BU labels, cross-pillar work rules, and initiative gating. Always shows the proposed payload to the user for approval before creating. Use when the user asks to create, draft, file, scaffold, or open a Jira Epic, Story, Task, or sub-tasks under an Epic or Initiative.
---

# Jira: Create Epics and Stories/Tasks (mcp-atlassian)

This skill governs how the agent creates Jira issues through the `user-mcp-atlassian` MCP server against a **self-hosted Jira Data Center** instance. It enforces a stricter mandatory field set than Jira's screens require and the organisation's three-dimension governance model.

---

## MCP migration workflow (Jira)

Use this workflow when migrating Jira planning/tracking from manual ticket authoring to MCP-driven issue creation:

1. **Baseline discovery**: read current Initiative/Epic/Story state with `jira_get_issue` and `jira_search`.
2. **Structure reconciliation**: map legacy work into Initiative -> Epic -> Story hierarchy and identify non-conforming items.
3. **WBS pre-allocation**: compute next slots from sibling scans before drafting payloads.
4. **Draft-first gate**: present all required fields (including components, labels, AC, DoR, DoD) and wait for approval.
5. **Validated creation**: use `jira_batch_create_issues` with `validate_only: true` for batches before live creation.
6. **Link completion**: ensure Parent Link / Epic Link and required GANTT links are applied.
7. **Verification report**: return created keys, numbering decisions, and any follow-up cleanup (for legacy non-WBS issues).

Rule: never migrate by raw REST or direct Jira UI-first edits when MCP tools are available.

---

## Initiative → Epic → Story Hierarchy

This project uses a three-level hierarchy:

1. **Initiative** — top-level parent. Carries the WBS root number with a **pillar prefix** (e.g. `0.0 OPS: Operational Tasks & General Work`, `1.0 DCM: Knowledge Graph Platform`).
2. **Epic** — child of the Initiative. Inherits the Initiative's WBS prefix (e.g. `0.1 TPM Tasks`, `1.1 Entity Extraction Pipeline`).
3. **Story / Task** — child of the Epic. Inherits the Epic's prefix (e.g. `0.1.1 Set up monitoring dashboard`).

### Initiative Pillar Prefixes

Initiatives are numbered and prefixed by pillar:

| Prefix   | Pillar                      | WBS Range | Example                                       |
| -------- | --------------------------- | --------- | --------------------------------------------- |
| `OPS-`   | Operations (Non-Tech)       | `0.x`     | `0.0 OPS: Operational Tasks and General Work` |
| `DCM-`   | Data, Context & Memory      | `1.x`     | `1.0 DCM: Knowledge Graph Platform`           |
| `RO-`    | Reasoning & Orchestration   | `2.x`     | `2.0 RO: Multi-Agent Routing`                 |
| `RT-`    | Runtime                     | `3.x`     | `3.0 RT: On-Device Inference`                 |
| `INFRA-` | Operations & Infrastructure | `4.x–5.x` | `4.0 INFRA: GPU Cluster Operations`           |
| `EVAL-`  | Evaluation                  | `6.x`     | `6.0 EVAL: Model Eval Framework`              |
| `MF-`    | Models                      | `7.x–8.x` | `7.0 MF: Model Factory Platform`              |
| `HIVE-`  | HiVE Platform               | `9.x`     | `9.0 HIVE: Platform Integration`              |
| `BU-`    | Cross-pillar BU delivery    | `10.x+`   | `10.0 BU: Qira Delivery`                      |

### Initiative Gating Rule

An Initiative requires **3+ Epics** and a **3+ month timeline**. Work that doesn't meet this threshold should be modelled as Epics under an existing Initiative, not as new Initiatives. Single-deliverable items (e.g. "Construct Cursor Rules", "Reaching out to stakeholder") must be **demoted to Epic**.

---

## Three Orthogonal Dimensions

The core principle: **pillars, teams, and products are three different things.** Use three separate Jira mechanisms — never overload one to encode the others:

| Dimension    | Jira mechanism       | Purpose                                                    | Multi-select?                                    |
| ------------ | -------------------- | ---------------------------------------------------------- | ------------------------------------------------ |
| **Pillar**   | Components (8 total) | *What technical capability area does this work belong to?* | Yes — cross-pillar work gets multiple components |
| **Team/Product** | Labels (prefixed)| *Who is doing this work? For what product?*                | Yes — naturally multi-select                     |
| **Program**  | Initiatives (gated)  | *What major program of work does this fall under?*         | No — single parent                               |

---

## Components — Pillars Only (8 Total)

Components map directly to the governance model pillars. **Every issue MUST have at least one component.** Cross-pillar work gets multiple components.

| Component                     | Pillar Lead (Architect) | TPM           | Scope                                                                |
| ----------------------------- | ----------------------- | ------------- | -------------------------------------------------------------------- |
| **Data, Context & Memory**    | Lijun Gu                | James Meng    | RAG, data engineering, knowledge graphs, entity extraction, memory   |
| **Reasoning & Orchestration** | Sathish Raju            | Xin Ding      | Agent orchestration, intent routing, model routing, tool use, MCP    |
| **Runtime**                   | Pankaj Telang           | Amit Rahalkar | Model runtime (inference), agent runtime, on-device execution        |
| **Operations & Infrastructure** | Tom Sheffler          | Mike Fink     | GPU clusters, CI/CD, deployment, monitoring, Kubernetes, cloud infra |
| **Evaluation**                | Pradyumna Singh         | YanXia Chen   | Model eval frameworks, benchmarking, safety testing, auto pipelines  |
| **Models**                    | Suneel Marthi           | Allie Manasco | Model training, fine-tuning, quantization, model factory             |
| **HiVE Platform**             | Rafael Radkowski        | Amit Rahalkar | Cross-pillar platform integration, SDK, shared services              |
| **Operations (Non-Tech)**     | —                       | Mike Fink     | Hiring, governance, tooling, compliance, process improvements        |

### Choosing the right component(s)

- If the work belongs to **one pillar**, set that single component.
- If the work is **cross-pillar** (e.g. a model routing epic touching Reasoning & Orchestration + Runtime), set **both** components.
- If the work is **HiVE platform integration** contributed by a specific pillar, set **both** the pillar component and `HiVE Platform`.
- If unsure, ask the user. Use `jira_get_project_components` to verify component names.

---

## Labels — Teams and Products

Labels encode **who** is doing the work and **what product** it serves. **Every issue MUST have at least one `team:*` label.** Product/BU labels are required for issues serving specific BU projects.

### Team labels (`team:*`)

| Label                | Team                                  |
| -------------------- | ------------------------------------- |
| `team:infra-prc`     | Wang's infrastructure team (PRC)      |
| `team:infra-row`      | Thompson's ops team (ROW)             |
| `team:ro-prc-p`      | Qiu's R&O team (PRC Personal)         |
| `team:ro-prc-e`      | Cai's R&O team (PRC Enterprise)       |
| `team:ro-intent`     | Miao's intent routing team            |
| `team:ro-tools`      | Luo's tooling team                    |
| `team:eval`          | Tuli's evaluation team                |
| `team:models-prc`    | Zhang/Wang's model factory team (PRC) |
| `team:models-row`     | Marthi's models team (ROW)            |
| `team:runtime-model` | Webb's model runtime team             |
| `team:runtime-agent` | Zhu's agent runtime team              |
| `team:dcm`           | Thompson/Li's data & context team     |
| `team:hive-core`     | HiVE platform core team               |

Region convention: use `PRC` and `ROW` labels (not `NA`).

### Product / BU labels (`product:*`, `bu:*`)

| Label               | Product/Program             |
| ------------------- | --------------------------- |
| `product:qira`      | IDG AIES - Qira             |
| `product:tianxi`    | PRC Personal AI - Tianxi    |
| `product:prc-e`     | PRC Enterprise              |
| `product:hive`      | HiVE Platform               |
| `product:atp`       | ATP + External Partnerships |
| `bu:idg-gic`        | IDG GIC (CSW)               |
| `bu:idg-cpc`        | IDG CPC&SMB (Commercial)    |
| `bu:idg-ret`        | IDG RET (Consumer Retail)   |
| `bu:idg-phone`      | IDG Phone & TAB             |
| `bu:prc-enterprise` | PRC Enterprise AI           |
| `bu:ssg-aics`       | SSG AICS                    |
| `bu:dtit`           | DTIT                        |
| `bu:ssg-row`        | SSG ROW                     |
| `bu:isg-row`        | ISG ROW                     |
| `bu:isg-prc`        | ISG PRC                     |

### Special labels

| Label          | Purpose                                       |
| -------------- | --------------------------------------------- |
| `cross-pillar` | Issue involves temporary cross-pillar support |

---

## Cross-Pillar Work Rules

### Structural long-term exceptions (Qira, Tianxi, Enterprise AI)

BU projects that span multiple pillars by design:
- Get a `BU-` prefixed Initiative.
- Get `product:*` / `bu:*` labels on every issue.
- Get **multiple pillar components** on each issue.

### Temporary exceptions (time-bound cross-pillar support)

- Issues go in the **lending pillar's** Initiative.
- Add label `cross-pillar` + the supporting pillar's component.
- Include an **explicit end date** in the epic description.

### HiVE platform contributions (all pillars contribute)

- Component: the pillar that owns the capability + `HiVE Platform`.
- Label: `product:hive`.
- Initiative: under the **pillar's** Initiative (not `HIVE-9.0`) unless it is HiVE core team work.

---

## Mandatory fields (always)

Every Story/Task created under an Epic MUST have all of these populated. Never skip them; draft sensible placeholders from context and present them to the user if values are missing.

| Field | Type | Tool parameter / Custom field |
|---|---|---|
| Summary | string | `summary` (system) |
| Description | markdown | `description` (system) — also carries DoR and DoD (see below) |
| Epic Link | issue key | `customfield_10006` via `additional_fields.epic_link` |
| Estimate (Story Points) | number | `customfield_10816` via `additional_fields` |
| Component/s | comma-separated string | `components` (dedicated tool param) |
| Labels | array | `labels` in `additional_fields` — at least one `team:*` label |
| Function area | string (pillar name) | `customfield_16400` via `additional_fields` — auto-derived from Components (see [Function area mapping](#function-area-mapping)) |
| Acceptance Criteria | markdown | `customfield_10515` via `additional_fields` (Story screen only — see below) |
| Definition of Ready | markdown | **Description body only** — not on any screen |
| Definition of Done | markdown | **Description body only** — not on any screen |

For an **Epic** itself, Epic Link is **not** applicable. Instead, an Epic requires:

| Field | Type | Custom field |
|---|---|---|
| Epic Name | string | `customfield_10005` (required by Jira for Epics) |

The other mandatory fields (Description, Components, Labels, AC, DoR, DoD) still apply to Epics. Estimate is optional on Epics (points usually live on children).

### Screen availability — where fields are accepted by Jira

| Field               | Epic screen | Story screen | Fallback                                    |
| ------------------- | ----------- | ------------ | ------------------------------------------- |
| Summary             | ✅           | ✅            | —                                           |
| Description         | ✅           | ✅            | —                                           |
| Estimate            | ✅           | ✅            | —                                           |
| Component/s         | ✅           | ✅            | —                                           |
| Labels              | ✅           | ✅            | —                                           |
| Epic Name           | ✅           | N/A          | —                                           |
| Epic Link           | N/A         | ✅            | —                                           |
| Acceptance Criteria | ❌           | ✅            | Embed under `## Acceptance Criteria` in Description (Epics) |
| Definition of Ready | ❌           | ❌            | **Always** embed under `## Definition of Ready` in Description |
| Definition of Done  | ❌           | ❌            | **Always** embed under `## Definition of Done` in Description |

**Rule:** DoR and DoD are **never** sent via `additional_fields` — they do not appear on any Jira screen and will be silently rejected. Always embed them in the `description` body. AC may be sent via `customfield_10515` on Stories, but must also appear in the Description body for Epics.

---

## How Epics link to Initiatives

Epics are linked to their parent Initiative via **two mechanisms** — both must be set:

1. **Parent Link custom field** (`customfield_12913`) — set on the Epic at create time so portfolio scans work.
2. **GANTT hierarchy link** — after creating the Epic, call `jira_create_issue_link`:

```
type_name: "multi-level hierarchy [GANTT]"
inward_issue_key:  "<EPIC-KEY>"        # the child
outward_issue_key: "<INITIATIVE-KEY>"  # the parent
```

This makes the Initiative "is parent task of" the Epic.

---

## WBS numbering

Every issue carries a Work Breakdown Structure prefix at the front of both the **Summary** and (for Epics) the **Epic Name**:

| Level | Issue type | Prefix shape | Example |
|---|---|---|---|
| 1 | Initiative | `X.0` | `0.0 Operational Tasks & General Work` |
| 2 | Epic | `X.Y` | `0.4 Data and Infra Ops Tasks` |
| 3 | Story / Task | `X.Y.Z` | `0.4.7 Provision dashboard refresh job on shared VM` |
| 4 | Subtask | `X.Y.Z.N` | `0.4.7.1 Add pre-drain health check script` |

Format rules:
- Single space between the WBS number and the title text.
- Zero-padding is **not** used (`0.10`, never `0.010`).
- Initiatives are not created by this skill; their prefix is read, not assigned. If an Initiative has no prefix, stop and ask the user to add one.
- The same WBS string goes into both `summary` and (for Epics) `customfield_10005` (Epic Name).

### Computing the next number

Before creating an Epic or a Story/Task, scan existing siblings and pick the **lowest unused integer** for the new level. Always show the user the scan result and the chosen number before creating.

**Creating an Epic under Initiative `<INIT>`:**

1. Run `jira_get_issue` on `<INIT>` and extract the leading `X.0` from `summary`. Call this `X`.
2. List children Epics:
   ```
   project = <PROJ> AND "Parent Link" = <INIT> AND issuetype = Epic
   ```
3. Parse the leading `X.Y` prefix from each child summary. Collect the `Y` values.
4. **Next `Y` = max(Y) + 1**, floor of `1` if set is empty.
5. Show the user: "Initiative `<INIT>` is `X.0`. Existing Epics: `<list>`. Next Epic will be `X.<nextY>`. Confirm?"
6. Flag any siblings that don't match the `X.Y` pattern (e.g. `LATC-1980`) for the user to decide whether to renumber later.

**Creating a Story/Task under Epic `<EPIC>`:**

1. Run `jira_get_issue` on `<EPIC>` and extract the leading `X.Y` from `summary`.
2. List children:
   ```
   project = <PROJ> AND "Epic Link" = <EPIC> AND issuetype in (Story, Task)
   ```
3. Parse the leading `X.Y.Z` prefix from each child summary. Collect the `Z` values.
4. **Next `Z` = max(Z) + 1**, floor of `1` if set is empty.
5. Show the user the list and chosen number before creating.
6. If the Epic has un-numbered legacy children, **do not back-fill them**. Start `X.Y.1` for the new one and warn the user.

**Batch creates:**

Allocate consecutive numbers starting at the next free slot. Example: if the highest existing Epic under `LATC-7` is `0.4`, a batch of 3 new Epics gets `0.5`, `0.6`, `0.7`. Show the full numbered list before creating.

### Worked example: LATC-7 (`0.0 Operational Tasks & General Work`)

| Key | Summary | Conforms? |
|---|---|---|
| `LATC-8` | `0.1 TPM Tasks` | yes |
| `LATC-63` | `0.2 Research and Development` | yes |
| `LATC-1235` | `0.3 Operational Dashboards & Data Pipelines` | yes |
| `LATC-1304` | `0.4 Data and Infra Ops Tasks` | yes |
| `LATC-1980` | `Define the Settings GitLab repositories within LATC should have.` | **no** |

Highest conforming `Y` = `4`. Next Epic under `LATC-7` would be `0.5 <title>`. Surface `LATC-1980` to the user as a follow-up to renumber.

---

## Function area mapping

`customfield_16400` ("Function area") must be included in every new issue where the Jira screen supports it. **Always derive it automatically from the Components field** — do not ask the user.

| Pillar value | Maps from component |
|---|---|
| `Data, Context, & Memory` | `Data, Context & Memory` |
| `Reasoning & Orchestration` | `Reasoning & Orchestration` |
| `Runtime` | `Runtime` |
| `Infrastructure` | `Operations & Infrastructure` |
| `Operations` | `Operations (Non-Tech)` |
| `Model Evaluation` | `Evaluation` |
| `Model Factory` | `Models` |
| `HiVE Platform` | `HiVE Platform` |

**Resolution rules when an issue has multiple components:**

1. If all components point to the same pillar → use that pillar.
2. If components span multiple pillars → set Function area from the **first listed component** and add label `cross-pillar`.
3. If both `Operations & Infrastructure` and `Operations (Non-Tech)` are set → follow the first listed component rule and still add `cross-pillar`.
4. If `HiVE Platform` is combined with a domain pillar → follow the first listed component rule and still add `cross-pillar` when multiple components are present.

**Always show the resolved pillar** in the pre-create draft so the user can override before confirmation.

**If the field is rejected at create time** (`"Field 'customfield_16400' cannot be set. It is not on the appropriate screen"`): omit it, note the omission in the creation report, and advise the user that a Jira admin needs to add the field to that issue type's screen.

The value is a **free-text string** — use the exact pillar names from the table above, including punctuation (`Data, Context, & Memory`).

---

## Operating contract

1. **Never silently omit a mandatory field.** If a value is missing, draft a placeholder from conversation context and present the full draft to the user for confirmation before calling `jira_create_issue`. Mark uncertain content as `TBD: <what's needed>`.
2. **Always show the proposed payload before creating.** Single create AND batch create. Show every mandatory field filled, then explicitly ask "Create this now?" Wait for an affirmative reply. No exceptions.
3. **Always inherit a WBS prefix from the parent.** Every Epic and Story summary MUST start with the WBS number computed from its parent's prefix and the next free sibling slot. If the parent has no WBS prefix, stop and tell the user — do not invent one.
4. **Never assume the project key.** Ask if not stated. The MCP tool's regex enforces `^[A-Z][A-Z0-9_]+$`.
5. **Never assume Epic Link.** If the user says "create stories under Epic X" without a key, search first and ask which one.
6. **Use the MCP server, not raw REST.** All operations go through `user-mcp-atlassian` tools.
7. **Never use components outside the 8-pillar list.** Old sub-component names (e.g. "RAG", "Agentic Framework", "AI Agent Runtime") are retired. If the user uses old names, map them to the correct pillar component and confirm with the user.

---

## Pre-flight checks (run before creating)

Run only the checks relevant to what's missing or ambiguous. Skip ones already verified in this conversation.

- **Resolve parent key**: if the user gave a name instead of a key, run `jira_search` with JQL like `project = <KEY> AND issuetype = <Epic|Initiative> AND (summary ~ "<query>" OR "Epic Name" ~ "<query>")` and confirm.
- **Read parent prefix**: run `jira_get_issue` on the parent and extract the leading WBS prefix (`X.0` for Initiative, `X.Y` for Epic). If absent, stop.
- **Scan siblings for WBS**: run the JQL in [Computing the next number](#computing-the-next-number) and parse prefixes. Report the chosen next number and any non-conforming siblings.
- **Validate components**: run `jira_get_project_components` with `project_key`. Only accept names from the 8-pillar list. If the user requests an unlisted component, tell them it must be created in Jira UI by an admin first.
- **Confirm issue type exists**: `Epic`, `Story`, and `Task` are standard. If the project uses something custom (e.g. `Spike`), confirm via a `jira_get_issue` on a recent same-type issue first.

---

## Workflow

### A. Creating a single Story/Task under an existing Epic

1. **Gather inputs.** Required:
   - `project_key` (e.g. `LATC`)
   - `epic_key` (e.g. `LATC-1304`)
   - `summary` (title text only; WBS prefix is computed)
   - `components` (one or more from the 8-pillar list)
   - `labels` (at least one `team:*` label)
   - Optional but encouraged: `assignee`, `priority`, `sprint`

2. **Compute WBS.** Read `<epic_key>` prefix `X.Y`; scan child Stories/Tasks; pick next `Z`. Final summary = `"X.Y.Z <title>"`.

3. **Draft all mandatory fields.** Use the templates in [Templates](#templates). Mark uncertain content as `TBD:`.

4. **Pre-flight** as needed (Epic key valid? Components valid? Labels valid? WBS scan complete?).

5. **Show the full draft** to the user:

   ```
   Project: LATC
   Issue type: Story
   Epic Link: LATC-1304 (0.4 Data and Infra Ops Tasks)
   WBS: 0.4.7  (existing children: 0.4.1..0.4.6; 0 un-numbered legacy)
   Summary: 0.4.7 Provision dashboard refresh job on shared VM
   Components: Operations & Infrastructure
   Labels: team:infra-row
   Function area: Infrastructure  ← derived from Components
   Story Points: 3
   Description: ...
   Acceptance Criteria: ... [via customfield_10515]
   Definition of Ready: ... [embedded in Description — not on Jira screen]
   Definition of Done: ...  [embedded in Description — not on Jira screen]
   ```

6. **Confirm** ("Create this Story now? Reply with edits or 'go'.").

7. **Create** via `jira_create_issue` (see [Tool call shape](#tool-call-shape)).

8. **Report result.** Show the created issue key and a one-line summary; offer to add a worklog, comments, or transitions.

### B. Creating a new Epic under an Initiative

1. Gather: `project_key`, `initiative_key` (e.g. `LATC-7`), `summary` (title text only), `components`, `labels`.
2. **Compute WBS.** Read `<initiative_key>` prefix `X.0`; scan child Epics; pick next `Y`. Final summary and Epic Name = `"X.Y <title>"`.
3. Set `customfield_10005` (Epic Name) to the same `"X.Y <title>"` string.
4. Set `customfield_12913` (Parent Link) to `<initiative_key>` in `additional_fields`.
5. Draft Description, AC, DoR, DoD (Estimate optional on Epics).
6. **Show the draft**, confirm, then create with `issue_type: "Epic"`.
7. **After creation**, call `jira_create_issue_link` to add the GANTT hierarchy link:
   ```
   type_name: "multi-level hierarchy [GANTT]"
   inward_issue_key:  "<NEW-EPIC-KEY>"
   outward_issue_key: "<INITIATIVE-KEY>"
   ```

### C. Scaffolding multiple Stories under one Epic

1. Gather the Epic key and a list of work items (titles or short descriptions).
2. **Compute consecutive WBS.** Scan child Stories/Tasks; allocate `X.Y.<nextZ>`, `X.Y.<nextZ+1>`, ... in input order.
3. For each item, draft all mandatory fields (Epic Link and Labels are the same for all).
4. **Validate first**: call `jira_batch_create_issues` with `validate_only: true` and the full payload. Fix any reported errors.
5. Show a compact numbered table of all drafts (one row per issue, including WBS, component, labels, and estimate) and ask for batch confirmation.
6. Create with `jira_batch_create_issues` (`validate_only: false`).
7. Report the resulting keys with their WBS numbers.

### D. Creating an Epic and its Stories together

Two-pass: run workflow B for the Epic, capture its key and `X.Y` prefix, then run workflow C against that Epic. Do not pre-allocate Story numbers until the Epic exists, because batch validation can fail and you don't want orphan numbers.

---

## Tool call shape

Use `jira_create_issue` with `additional_fields` carrying the custom fields. **`additional_fields` is a JSON-encoded string**, not a JSON object.

Example payload for a Story:

```json
{
  "project_key": "LATC",
  "summary": "0.4.7 Provision dashboard refresh job on shared VM",
  "issue_type": "Story",
  "description": "## Context\n...\n\n## Goal\n...\n\n## Approach\n...\n\n## Out of scope\n...\n\n## Links\n...\n\n## Definition of Ready\n- [ ] AC reviewed by assignee\n- [ ] Dependencies confirmed\n- [ ] Effort estimated\n\n## Definition of Done\n- [ ] Code merged, CI green\n- [ ] Tests passing\n- [ ] AC verified by reviewer\n- [ ] Stakeholders notified",
  "components": "Operations & Infrastructure",
  "additional_fields": "{\"epic_link\":\"LATC-1304\",\"customfield_10816\":3,\"customfield_16400\":\"Infrastructure\",\"customfield_10515\":\"- [ ] Given the VM is healthy, when the timer fires, then fresh data lands within 5 min.\",\"labels\":[\"team:infra-row\"],\"priority\":{\"name\":\"Medium\"}}"
}
```

Example payload for an Epic (under Initiative `LATC-7`):

```json
{
  "project_key": "LATC",
  "summary": "0.5 Self-service Jira Reports for Managers",
  "issue_type": "Epic",
  "description": "## Problem / Opportunity\n...\n\n## Outcomes\n...\n\n## Scope\n...\n\n## Out of scope\n...\n\n## Stakeholders\n...\n\n## Acceptance Criteria\n- [ ] Managers can generate reports without admin help.\n\n## Definition of Ready\n- [ ] AC reviewed\n- [ ] Dependencies confirmed\n\n## Definition of Done\n- [ ] All child Stories closed\n- [ ] AC verified\n- [ ] Stakeholders notified",
  "components": "Operations (Non-Tech)",
  "additional_fields": "{\"customfield_10005\":\"0.5 Self-service Jira Reports for Managers\",\"customfield_12913\":\"LATC-7\",\"customfield_16400\":\"Operations\",\"labels\":[\"team:infra-row\"]}"
}
```

Notes:
- `summary` carries the WBS prefix. Never call create with a bare title.
- `epic_link` is the MCP-friendly alias for `customfield_10006`. Either works on Stories.
- Epics use `customfield_10005` (Epic Name) and `customfield_12913` (Parent Link); they do **not** get an `epic_link`.
- **DoR and DoD go in `description` only** — never in `additional_fields`. They are not on any Jira screen and will be silently dropped if sent as custom fields.
- **AC** (`customfield_10515`) is accepted on Story screens; pass it in `additional_fields` for Stories. For Epics, embed it in `description` only.
- After creating an Epic, always also call `jira_create_issue_link` with `type_name: "multi-level hierarchy [GANTT]"`.
- For sprints, set `"customfield_10004": <sprintId>` (numeric ID). Resolve via `jira_get_sprints_from_board` if needed.
- `labels` must be an array of strings using the `team:*`, `product:*`, or `bu:*` prefix conventions.

---

## Proposal table format (Step 2 of every workflow)

Before creating anything, present this table and wait for explicit approval:

| WBS   | Type  | Summary                               | Est | Component(s)                | Labels                        |
| ----- | ----- | ------------------------------------- | --- | --------------------------- | ----------------------------- |
| 4.1   | Epic  | Kubernetes Cluster Upgrade            | —   | Operations & Infrastructure | team:infra-row                 |
| 4.1.1 | Story | Design rolling upgrade strategy       | 5   | Operations & Infrastructure | team:infra-row                 |
| 4.1.2 | Story | Implement node draining and migration | 8   | Operations & Infrastructure | team:infra-row                 |
| 4.1.3 | Story | Update monitoring dashboards          | 5   | Operations & Infrastructure, Evaluation | team:infra-row, team:eval |

Ask explicitly: **"Does this look good? I'll create these tickets once you approve, or let me know what you'd like to change."**

---

## Templates

### Description (Story/Task)

DoR and DoD **must** be embedded in every Story description — they are not on any Jira screen.

```markdown
## Context
[1–3 sentences: why this work matters and what triggered it.]

## Goal
[The outcome a reviewer can verify, in one sentence.]

## Approach
- [Bullet steps or design notes; keep at the level a peer can pick up.]

## Out of scope
- [Anything explicitly not being done in this issue.]

## Links
- [Confluence / dashboard / parent doc URLs]

## Definition of Ready
- [ ] Acceptance criteria are written and reviewed by the assignee.
- [ ] Dependencies (services, data, access, approvals) are identified and unblocked.
- [ ] Effort is estimated; risks/unknowns are called out in Description.
- [ ] Test approach is agreed (unit / integration / manual / N-A).
- [ ] Designs / specs linked from Description if applicable.

## Definition of Done
- [ ] Code merged to the target branch and CI is green.
- [ ] Tests added/updated; coverage and pass status verified.
- [ ] Docs / runbooks / dashboards updated where touched.
- [ ] Acceptance criteria all checked off and verified by the reviewer.
- [ ] Deployed to the intended environment(s); rollback path noted if risky.
- [ ] Stakeholders notified; ticket transitioned to Done.
```

### Description (Epic)

AC, DoR, and DoD are **not** on the Epic screen — all three must be embedded in the description.

```markdown
## Problem / Opportunity
[Why this Epic exists, who benefits, what changes when it's done.]

## Outcomes
- [Measurable outcome 1]
- [Measurable outcome 2]

## Scope
- [In scope bullets]

## Out of scope
- [Out of scope bullets]

## Stakeholders
- Sponsor: [name]
- Tech lead: [name]

## Acceptance Criteria
- [ ] [Measurable condition that signals the Epic is complete.]
- [ ] [Measurable condition 2]

## Definition of Ready
- [ ] Acceptance criteria are written and reviewed by the assignee.
- [ ] Dependencies (services, data, access, approvals) are identified and unblocked.
- [ ] Effort is estimated; risks/unknowns are called out in Description.
- [ ] Designs / specs linked from Description if applicable.

## Definition of Done
- [ ] All child Stories are closed.
- [ ] Acceptance criteria above are verified.
- [ ] Docs / runbooks updated where touched.
- [ ] Stakeholders notified; Epic transitioned to Done.
```

### Acceptance Criteria (for `customfield_10515` on Stories)

Prefer Given/When/Then for behaviour; bullet checklist for deliverables. Mix is fine.

```markdown
- [ ] **Given** [precondition] **when** [action] **then** [observable result].
- [ ] [Deliverable: a thing that exists / is merged / is published].
- [ ] [Telemetry / metric / log line that confirms behaviour in production].
```

---

## Estimation guidance

Default to **Story Points** (Fibonacci-ish: 1, 2, 3, 5, 8, 13).

| Points | Rough meaning |
|---|---|
| 1 | Trivial; under half a day; no unknowns. |
| 2 | A focused day or less; well-understood. |
| 3 | A couple of days; minor unknowns. |
| 5 | Most of a sprint slice; some integration risk. |
| 8 | Full sprint slice; non-trivial unknowns. |
| 13 | Probably needs splitting; flag this in Description. |

If the user supplies hours/days, convert to a point estimate using the table and note the assumption in Description.

---

## Examples

### Example 1: Single Story under LATC-1304

User: "Create a story under LATC-1304 to set up automated dashboard refresh on the shared VM."

WBS work:
- `LATC-1304` summary is `0.4 Data and Infra Ops Tasks` → parent prefix `0.4`.
- Scan: `project = LATC AND "Epic Link" = LATC-1304 AND issuetype in (Story, Task)`. Suppose existing children `0.4.1..0.4.6`.
- Next slot: `0.4.7`.
- Component: `Operations & Infrastructure`. Label: `team:infra-row`. Function area: `Infrastructure`.

```json
{
  "project_key": "LATC",
  "summary": "0.4.7 Automate JIRAFlow dashboard refresh on shared Linux VM",
  "issue_type": "Story",
  "description": "## Context\nThe JIRAFlow dashboard currently refreshes manually. A scheduled job would reduce operator toil and ensure stakeholders always see current data.\n\n## Goal\nA systemd timer on the shared VM refreshes the JIRAFlow dataset hourly with monitoring alerts on failure.\n\n## Approach\n- Provision systemd timer for the refresh script\n- Push status to operational dashboard\n\n## Out of scope\n- Power BI report layout changes\n\n## Links\n- TBD: link to runbook\n\n## Definition of Ready\n- [ ] AC reviewed by assignee\n- [ ] VM access and credentials confirmed\n- [ ] Effort estimated; risks captured\n\n## Definition of Done\n- [ ] Timer deployed and green for 24 h\n- [ ] Runbook updated\n- [ ] AC verified by reviewer\n- [ ] Stakeholders notified",
  "components": "Operations & Infrastructure",
  "additional_fields": "{\"epic_link\":\"LATC-1304\",\"customfield_10816\":3,\"customfield_16400\":\"Infrastructure\",\"customfield_10515\":\"- [ ] Given the VM is healthy, when the timer fires, then a fresh dataset lands in the target store within 5 minutes.\\n- [ ] A failure surfaces an alert in the operational dashboard within 10 minutes.\",\"labels\":[\"team:infra-row\"],\"priority\":{\"name\":\"Medium\"}}"
}
```

### Example 2: New Epic + Stories (cross-pillar BU work)

User: "Create an epic for Qira model routing work — it spans Reasoning & Orchestration and Runtime pillars."

- Components: `Reasoning & Orchestration, Runtime` (both pillars).
- Labels: `product:qira, team:ro-prc-p` (or whichever team is delivering).
- Initiative: under the `BU-` prefixed Initiative for Qira (e.g. `10.0 BU: Qira Delivery`).
- Function area: `Reasoning & Orchestration` (primary pillar; note the Runtime component in the draft).
- Present proposal and wait for approval before creating.

### Example 3: New Epic under LATC-7 + first Story

User: "New Epic in LATC for 'Self-service Jira reports for managers' under Operational Tasks (LATC-7). Add a first Story for 'Pick reporting library and POC'."

WBS for the Epic:
- `LATC-7` is `0.0 Operational Tasks & General Work` → root `0`.
- Scan child Epics; highest conforming `Y` is `4` (`LATC-1304`). `LATC-1980` is non-conforming and flagged.
- Next slot: `0.5`. Epic summary = Epic Name = `0.5 Self-service Jira reports for managers`.
- Set `customfield_12913 = "LATC-7"` (Parent Link) + create GANTT link after creation.

After Epic is created (`LATC-9999`):
- Scan stories under `LATC-9999` → none → next is `0.5.1`.
- Story summary = `0.5.1 Pick reporting library and POC`, `epic_link = "LATC-9999"`, 5 points.

---

## Anti-patterns to avoid

- **Don't pass JSON objects to `additional_fields`.** It must be a JSON **string**.
- **Don't set Epic Link on an Epic.** Use Epic Name (`customfield_10005`) on Epics; Epic Link on children. For Epics, also set Parent Link (`customfield_12913`) and create the GANTT hierarchy link.
- **Don't skip the WBS scan.** Never invent the next number — always re-run the JQL scan right before showing the draft.
- **Don't reuse a number.** If the parent has gaps (e.g. `0.4.1`, `0.4.3`, `0.4.5`), still use `max+1` (`0.4.6`). Filling gaps causes confusion in roadmaps.
- **Don't back-fill or rename existing siblings** without an explicit user request.
- **Don't omit Function area.** Always derive and include `customfield_16400`. If rejected by the screen, note the omission.
- **Don't pass DoR or DoD via `additional_fields`.** `customfield_16516` and `customfield_16544` are not on any screen and will be silently ignored. Always embed DoR and DoD in the Description body under `## Definition of Ready` and `## Definition of Done` headings.
- **Don't pass AC via `additional_fields` on Epics.** `customfield_10515` is not on the Epic screen. Embed AC in the Epic description body under `## Acceptance Criteria`.
- **Don't use old sub-component names** (`RAG`, `Agentic Framework`, `AI Agent Runtime`, etc.). Map them to the correct pillar component and confirm.
- **Don't omit Labels.** At least one `team:*` label is mandatory on every issue.
- **Don't encode team or product in Components.** Labels are the mechanism for team/product; Components are for pillars only.
- **Don't bypass the Initiative Gating Rule.** If a proposed Initiative has fewer than 3 Epics or a timeline under 3 months, recommend modelling it as an Epic under an existing Initiative.
- **Don't fabricate component names.** If the requested component doesn't exist in `jira_get_project_components`, stop and tell the user.
- **Don't bypass confirmation** for create/batch-create operations. Always show the full proposed payload(s) and wait for an explicit go-ahead.

---

## Error handling

- **400 with field errors**: re-read the response, fix the offending field (most often a value-list option that doesn't exist in this project), and re-confirm.
- **403 / 401**: credentials are wrong or the project requires extra permissions; tell the user — do not retry.
- **Schema-name mismatches** (e.g. "Epic Name" vs `customfield_10005`): always set custom fields by `customfield_NNNNN` ID rather than display name.
- **Component not found**: do not create the issue without it; ask the user to pick from the valid 8-pillar list.
- **GANTT link fails**: log the error, inform the user, and advise them to create the link manually in Jira. Do not block story creation.

---

## Quick field reference (Lenovo Jira DC)

| Field | Custom field ID |
|---|---|
| Story Points / Estimate | `customfield_10816` |
| Sprint | `customfield_10004` |
| Epic Name | `customfield_10005` |
| Epic Link | `customfield_10006` |
| Acceptance Criteria | `customfield_10515` |
| Function area | `customfield_16400` |
| Definition of Ready | `customfield_16516` |
| Definition of Done | `customfield_16544` |
| Original story points (Portfolio) | `customfield_12916` |
| Target start / end (Portfolio) | `customfield_12914` / `customfield_12915` |
| Parent Link (Portfolio) | `customfield_12913` |

If a future project surfaces different IDs for AC/DoR/DoD, confirm with `jira_search_fields` before creating.

---

## References

- MCP tools used: `jira_create_issue`, `jira_batch_create_issues`, `jira_create_issue_link`, `jira_link_to_epic`, `jira_get_project_components`, `jira_search`, `jira_search_fields`, `jira_get_issue`, `jira_get_sprints_from_board`.
- Server: `user-mcp-atlassian` (sooperset / SharkyND mcp-atlassian, stdio over `uvx`).

