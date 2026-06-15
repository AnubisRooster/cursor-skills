---
name: jira-create-issues
description: Create Jira Epics and child Stories/Tasks via the mcp-atlassian server (self-hosted Jira Data Center), enforcing a mandatory field set (Summary, Description, Epic Link, Estimate, Components, Labels, Function area, Acceptance Criteria, Definition of Ready, Definition of Done) and a hierarchical WBS numbering rule (Initiative X.0 -> Epic X.Y -> Story X.Y.Z) regardless of what Jira's screens require. Enforces the three-orthogonal-dimensions model (Pillars=Components, Teams=Labels, Programs=Initiatives), 8 pillar-based components, team/product/BU labels, cross-pillar work rules, and initiative gating. Always shows the proposed payload to the user for approval before creating. Use when the user asks to create, draft, file, scaffold, or open a Jira Epic, Story, Task, or sub-tasks under an Epic or Initiative.
---

# Jira: Create Epics and Stories/Tasks (mcp-atlassian)

This skill governs how the agent creates Jira issues through the `user-mcp-atlassian` MCP server against a **self-hosted Jira Data Center** instance. It enforces a stricter mandatory field set than Jira's screens require and the organisation's three-dimension governance model.

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
| `team:infra-row`     | Thompson's ops team (ROW)             |
| `team:ro-prc-p`      | Qiu's R&O team (PRC Personal)         |
| `team:ro-prc-e`      | Cai's R&O team (PRC Enterprise)       |
| `team:ro-intent`     | Miao's intent routing team            |
| `team:ro-tools`      | Luo's tooling team                    |
| `team:eval`          | Tuli's evaluation team                |
| `team:models-prc`    | Zhang/Wang's model factory team (PRC) |
| `team:models-na`     | Marthi's models team (NA)             |
| `team:runtime-model` | Webb's model runtime team             |
| `team:runtime-agent` | Zhu's agent runtime team              |
| `team:dcm`           | Thompson/Li's data & context team     |
| `team:hive-core`     | HiVE platform core team               |

### Product / BU labels (`product:*`, `bu:*`)

| Label               | Product/Program             |
| ------------------- | --------------------------- |
| `product:qira`      | IDG AIES - Qira             |
| `product:tianxi`    | PRC Personal AI - Tianxi    |
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

**Every issue created by this skill MUST include ALL of the following fields, regardless of whether Jira marks them as required.** Never skip these. If the user hasn't provided content for one of them, generate sensible defaults or ask the user — do NOT create issues with blank mandatory fields.

### For Stories/Tasks

| Field | Type | Tool parameter / Custom field | Notes |
|---|---|---|---|
| Summary | string | `summary` (system) | Must start with WBS number |
| Description | markdown | `description` (system) | Must also contain `## Acceptance Criteria`, `## Definition of Ready`, `## Definition of Done` sections |
| Epic Link | issue key | `customfield_10006` via `additional_fields.epic_link` | Links story to epic |
| Estimate (Story Points) | number | `customfield_10816` via `additional_fields` | e.g. "3", "5", "8" |
| Component/s | comma-separated string | `components` (dedicated tool param) | One or more from 8-pillar list |
| Labels | array | `labels` in `additional_fields` | At least one `team:*` label required |
| Function area | string (pillar name) | `customfield_16400` via `additional_fields` | Auto-derived from Components |
| Acceptance Criteria | markdown | `customfield_10515` via `additional_fields` **AND** `## Acceptance Criteria` in description | **Always set both** |
| Definition of Ready | markdown | `customfield_16516` via `additional_fields` **AND** `## Definition of Ready` in description | **Always set both** |
| Definition of Done | markdown | `customfield_16544` via `additional_fields` **AND** `## Definition of Done` in description | **Always set both** |

### For Epics

Epics do NOT get an Epic Link field (they are the epic). Instead, Epics require:

| Field | Type | Custom field | Notes |
|---|---|---|---|
| Epic Name | string | `customfield_10005` | Required by Jira for Epics — same as summary |
| Summary | string | `summary` (system) | Must start with WBS number |
| Description | markdown | `description` (system) | Also carries AC, DoR, and DoD |
| Component/s | comma-separated string | `components` | One or more from 8-pillar list |
| Labels | array | `labels` in `additional_fields` | At least one `team:*` label required |
| Function area | string | `customfield_16400` via `additional_fields` | Auto-derived from Components |
| Acceptance Criteria | markdown | `customfield_10515` via `additional_fields` **AND** `## Acceptance Criteria` in description | **Always set both** |
| Definition of Ready | markdown | `customfield_16516` via `additional_fields` **AND** `## Definition of Ready` in description | **Always set both** |
| Definition of Done | markdown | `customfield_16544` via `additional_fields` **AND** `## Definition of Done` in description | **Always set both** |

**Note:** Estimate is optional on Epics (story points usually live on child Stories).

### Field Guidelines

**Summary**: Every summary MUST begin with a **WBS (Work Breakdown Structure) number** that reflects the issue's position in the hierarchy.

**Description**: Markdown body explaining what the issue is about. Must always contain `## Acceptance Criteria`, `## Definition of Ready`, and `## Definition of Done` sections with real content.

**Acceptance Criteria** (`customfield_10515` in `additional_fields` AND `## Acceptance Criteria` section in description): **Always set both.** Write in "Given/When/Then" or checkbox format.

**Definition of Ready** (`customfield_16516` AND embedded in description under `## Definition of Ready`): **Always set both.** Generate sensible defaults if not provided.

**Definition of Done** (`customfield_16544` AND embedded in description under `## Definition of Done`): **Always set both.** Generate sensible defaults if not provided.

### Screen availability

**Rule:** AC (`customfield_10515`), DoR (`customfield_16516`), and DoD (`customfield_16544`) must **always** be set as custom fields via `additional_fields` AND embedded as sections in the `description` body. Setting only one or the other is not acceptable — both are always required on every issue type.

---

## How Epics link to Initiatives

Epics are linked to their parent Initiative via **two mechanisms** — both must be set:

1. **Parent Link custom field** (`customfield_12913`) — set on the Epic at create time.
2. **GANTT hierarchy link** — after creating the Epic, call `jira_create_issue_link` with `type_name: "multi-level hierarchy [GANTT]"`.

---

## WBS numbering

Every issue carries a Work Breakdown Structure prefix at the front of both the **Summary** and (for Epics) the **Epic Name**:

| Level | Issue type | Prefix shape | Example |
|---|---|---|---|
| 1 | Initiative | `X.0` | `0.0 OPS: Operational Tasks & General Work` |
| 2 | Epic | `X.Y` | `0.4 Data and Infra Ops Tasks` |
| 3 | Story / Task | `X.Y.Z` | `0.4.7 Provision dashboard refresh job on shared VM` |
| 4 | Subtask | `X.Y.Z.N` | `0.4.7.1 Add pre-drain health check script` |

**NEVER invent or guess WBS numbers.** Always scan existing children, find the highest Z, and use max+1.

---

## Function area mapping

`customfield_16400` ("Function area") must be included in every new issue. Always derive from Components:

| Pillar value | Maps from component |
|---|---|
| `Data, Context, & Memory` | `Data, Context & Memory` |
| `Reasoning & Orchestration` | `Reasoning & Orchestration` |
| `Runtime` | `Runtime` |
| `Operations` | `Operations & Infrastructure` or `Operations (Non-Tech)` |
| `Model Evaluation` | `Evaluation` |
| `Model Factory` | `Models` |
| `HiVE Platform` | `HiVE Platform` |

---

## Operating contract

1. **Never silently omit a mandatory field.**
2. **Always show the proposed payload before creating.** Ask "Create this now?" Wait for affirmative reply. No exceptions.
3. **Always inherit a WBS prefix from the parent.**
4. **Never assume the project key.**
5. **Never assume Epic Link.**
6. **Use the MCP server, not raw REST.**
7. **Never use components outside the 8-pillar list.**
8. **HARD STOP — DoR, DoD, and AC are always required, never optional.** Every Epic, Story, and Task MUST have all three set as custom fields (`customfield_10515`, `customfield_16516`, `customfield_16544`) via `additional_fields` AND embedded in the description body. Generate real, task-specific content if the user hasn't provided it. A blank or placeholder-only value is not acceptable. The pre-create proposal MUST show the filled content for all three fields.

---

## Workflow

### Step 1 — Gather Information

Confirm: project key, parent Epic/Initiative, summaries, descriptions, components, labels, estimates, assignee, priority.

### Step 2 — Present Proposal for Approval (MANDATORY)

**NEVER create tickets directly.** Present a formatted table with WBS number, issue type, summary, estimate, components, labels, and the AC/DoR/DoD content. Ask explicitly: **"Does this look good?"** Wait for approval.

### Step 3 — Compute WBS Numbers

Scan existing children, parse WBS prefixes, determine next slot, confirm with user.

### Step 4 — Create Issues

For each issue, include `customfield_10515` (AC), `customfield_16516` (DoR), `customfield_16544` (DoD) in `additional_fields`, and embed the same content in the description.

For Epics: also set `customfield_10005` (Epic Name) and `customfield_12913` (Parent Link), then call `jira_create_issue_link` with `type_name: "multi-level hierarchy [GANTT]"`.

### Step 5 — Report Results

Present a summary table with all created issue keys, WBS numbers, types, and statuses.

---

## Tool call shape

Example payload for a Story/Task (showing all three AC/DoR/DoD fields):

```json
{
  "project_key": "LATC",
  "summary": "0.4.7 Provision dashboard refresh job on shared VM",
  "issue_type": "Task",
  "description": "## Context\n...\n\n## Acceptance Criteria\n- [ ] Timer fires and data lands within 5 min.\n\n## Definition of Ready\n- [ ] AC reviewed\n- [ ] Dependencies confirmed\n\n## Definition of Done\n- [ ] Timer deployed 24h\n- [ ] Runbook updated",
  "components": "Operations & Infrastructure",
  "additional_fields": "{\"epic_link\":\"LATC-1304\",\"customfield_10816\":\"3\",\"customfield_16400\":\"Operations\",\"customfield_10515\":\"- [ ] Timer fires and data lands within 5 min.\",\"customfield_16516\":\"- [ ] AC reviewed\\n- [ ] Dependencies confirmed\",\"customfield_16544\":\"- [ ] Timer deployed 24h\\n- [ ] Runbook updated\",\"labels\":[\"team:infra-row\"],\"priority\":{\"name\":\"Medium\"}}"
}
```

Notes:
- `customfield_10515` (AC), `customfield_16516` (DoR), `customfield_16544` (DoD) must always be in `additional_fields` AND in the description.
- Sprints cannot be set at create time — use `jira_add_issues_to_sprint` after creation.
- Story Points (`customfield_10816`) must be a **string**, not a number.

---

## Anti-patterns to avoid

- **Don't create an issue without DoR, DoD, and AC.** Always fill all three before calling `jira_create_issue`.
- **Don't set AC, DoR, or DoD in only one place.** Both the custom field and the description section are required.
- **Don't pass JSON objects to `additional_fields`.** It must be a JSON **string**.
- **Don't pass Story Points as a number.** Must be a string.
- **Don't set the Sprint at create time.** Use `jira_add_issues_to_sprint` after creation.
- **Don't set Epic Link on an Epic.** Use `customfield_10005` and `customfield_12913`.
- **Don't skip the WBS scan.** Never invent the next number.
- **Don't omit Function area.** Always derive and include `customfield_16400`.
- **Don't bypass confirmation** for create/batch-create operations.

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
| Parent Link (Portfolio) | `customfield_12913` |

---

## References

- MCP tools: `jira_create_issue`, `jira_batch_create_issues`, `jira_create_issue_link`, `jira_get_project_components`, `jira_search`, `jira_get_issue`, `jira_get_sprints_from_board`, `jira_add_issues_to_sprint`.
- Server: `user-mcp-atlassian`.
- Companion rule: `~/.cursor/rules/jira-mandatory-fields.mdc` (alwaysApply: true).
