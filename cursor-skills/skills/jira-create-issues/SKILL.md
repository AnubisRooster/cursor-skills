---
name: jira-create-issues
description: Create Jira Epics/Features and child sprint issues via the mcp-atlassian server (self-hosted Jira Data Center), enforcing a mandatory field set (Summary, Description, Epic Link/Parent Link, Estimate, Components, Labels, Function area, Business Value, Acceptance Criteria, Definition of Ready, Definition of Done) and a hierarchical WBS numbering rule (Initiative X.0 -> Epic/Feature X.Y -> Story/Task/Test/Defect X.Y.Z) regardless of what Jira's screens require. Enforces the three-orthogonal-dimensions model (Pillars=Components, Teams=Labels, Programs=Initiatives), 8 pillar-based components, team/product/BU labels, cross-pillar work rules, and initiative gating. Always shows the proposed payload to the user for approval before creating. Use when the user asks to create, draft, file, scaffold, or open a Jira Epic, Feature, Story, Task, Test, Defect, or sub-task under an Epic/Feature/Initiative.
---

# Jira: Create Epics, Features, and Sprint Issues (mcp-atlassian)

This skill governs how the agent creates Jira issues through the `user-mcp-atlassian` MCP server against a **self-hosted Jira Data Center** instance. It enforces a stricter mandatory field set than Jira's screens require and the organisation's three-dimension governance model.

---

## Initiative → Epic/Feature → Sprint-Issue Hierarchy

This project uses a multi-level hierarchy:

1. **Initiative** — top-level parent. Carries the WBS root number with a **pillar prefix** (e.g. `0.0 OPS: Operational Tasks & General Work`, `1.0 DCM: Knowledge Graph Platform`).
2. **Epic / Feature** — children of the Initiative and peers at the same hierarchy level. They share the same `X.Y` WBS sequence.
3. **Story / Task / Test / Defect** — sprint-level delivery issues under an Epic or Feature. Inherit `X.Y.Z`.
4. **Sub-task** — granular work items under Story/Task/Test/Defect.

### Epic vs Feature decision rule

- Use **Feature** when the scoped deliverable should close within roughly one quarter (typically <= 2 months).
- Use **Epic** when work is broad, exploratory, or expected to run across multiple quarters.
- If unclear, default to **Feature** and note the assumption in the proposal for user confirmation.

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

Team inference rule notes:
- If work is for **Tianxi**, default to `team:ro-prc-p` unless the user explicitly specifies another Tianxi team.
- For **Reasoning & Orchestration** component work, pick an `team:ro-*` label (do not map to non-RO teams).

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

### For sprint-level issues (Story/Task/Test/Defect)

| Field | Type | Tool parameter / Custom field | Notes |
|---|---|---|---|
| Summary | string | `summary` (system) | Must start with WBS number |
| Description | markdown | `description` (system) | Must also contain `## Acceptance Criteria`, `## Definition of Ready`, `## Definition of Done` sections |
| Parent (Epic/Feature) | issue key | `customfield_10006` via `additional_fields.epic_link` | Links sprint issue to its Epic/Feature |
| Estimate (Story Points) | number | `customfield_10816` via `additional_fields` | e.g. "3", "5", "8" |
| Component/s | comma-separated string | `components` (dedicated tool param) | One or more from 8-pillar list |
| Labels | array | `labels` in `additional_fields` | At least one `team:*` label required |
| Function area | string (pillar name) | `customfield_16400` via `additional_fields` | Auto-derived from Components (see [Function area mapping](#function-area-mapping)) |
| Business Value | markdown | `customfield_11491` via `additional_fields` **AND** `## Business Value` in description | Not on the Task/Story screen (tested — rejected). **Always** embed in description; attempt the custom field and drop silently if rejected |
| Acceptance Criteria | markdown | `customfield_10515` via `additional_fields` **AND** `## Acceptance Criteria` in description | **Always set both** — the custom field for native Jira field display, the description section as fallback |
| Definition of Ready | markdown | `customfield_16516` via `additional_fields` **AND** `## Definition of Ready` in description | **Always set both** — custom field + description embed |
| Definition of Done | markdown | `customfield_16544` via `additional_fields` **AND** `## Definition of Done` in description | **Always set both** — custom field + description embed |

### For Epics

Epics do NOT get an Epic Link field (they are the epic). Instead, Epics require:

| Field | Type | Custom field | Notes |
|---|---|---|---|
| Epic Name | string | `customfield_10005` | Required by Jira for Epics — same as summary |
| Summary | string | `summary` (system) | Must start with WBS number |
| Description | markdown | `description` (system) | Also carries Business Value, AC, DoR, and DoD |
| Component/s | comma-separated string | `components` | One or more from 8-pillar list |
| Labels | array | `labels` in `additional_fields` | At least one `team:*` label required |
| Function area | string | `customfield_16400` via `additional_fields` | Auto-derived from Components |
| Business Value | markdown | **Description body only** (attempt `customfield_11491` too) | Untested on Epic screen — embed in description as the safe default |
| Acceptance Criteria | markdown | **Description body only** | Not on Epic screen — embed in description |
| Definition of Ready | markdown | **Description body only** | Not on any screen — always embed |
| Definition of Done | markdown | **Description body only** | Not on any screen — always embed |

**Note:** Estimate is optional on Epics (story points usually live on child Stories).

### For Features

Features are peers of Epics under an Initiative and follow the same approval/workflow expectations.

| Field | Type | Custom field | Notes |
|---|---|---|---|
| Summary | string | `summary` (system) | Must start with WBS number `X.Y` |
| Description | markdown | `description` (system) | Must contain Business Value, AC, DoR, DoD sections |
| Parent Link | issue key | `customfield_12913` via `additional_fields` | Required to link Feature to Initiative |
| Component/s | comma-separated string | `components` | One or more from 8-pillar list |
| Labels | array | `labels` in `additional_fields` | At least one `team:*` label required |
| Function area | string | `customfield_16400` via `additional_fields` | Auto-derived from Components |
| Business Value | markdown | Description body only (attempt `customfield_11491` too) | Embed under `## Business Value` |
| Acceptance Criteria | markdown | Description body only | Embed under `## Acceptance Criteria` |
| Definition of Ready | markdown | Description body only | Embed under `## Definition of Ready` |
| Definition of Done | markdown | Description body only | Embed under `## Definition of Done` |

### Screen availability — where fields are accepted by Jira

Not all mandatory fields are on all screen schemes. Based on testing:

| Field               | Epic screen | Story screen | Fallback                                    |
| ------------------- | ----------- | ------------ | ------------------------------------------- |
| Business Value      | ❌ (untested)| ❌ (tested — rejected on Task) | **Always** embed under `## Business Value` in Description; attempt `customfield_11491` and drop silently if rejected |
| Acceptance Criteria | ❌           | ✅            | Embed under `## Acceptance Criteria` in Description (Epics) |
| Definition of Ready | ❌           | ❌            | **Always** embed under `## Definition of Ready` in Description |
| Definition of Done  | ❌           | ❌            | **Always** embed under `## Definition of Done` in Description |

**Rule:** AC (`customfield_10515`), DoR (`customfield_16516`), DoD (`customfield_16544`), and Business Value (`customfield_11491`) must **always** be embedded as sections in the `description` body. Business Value has been confirmed **rejected on the Task screen** — attempt the custom field anyway and drop silently if rejected, keeping the description section regardless.

---

## How Epics link to Initiatives

1. **Parent Link** (`customfield_12913`) set at create time.
2. **GANTT hierarchy link** via `jira_create_issue_link` with `type_name: "multi-level hierarchy [GANTT]"`.

---

## WBS numbering

| Level | Issue type | Prefix shape | Example |
|---|---|---|---|
| 1 | Initiative | `X.0` | `0.0 OPS: Operational Tasks & General Work` |
| 2 | Epic / Feature | `X.Y` | `0.4 Data and Infra Ops Tasks` |
| 3 | Story / Task / Test / Defect | `X.Y.Z` | `0.4.7 Provision dashboard refresh job` |
| 4 | Subtask | `X.Y.Z.N` | `0.4.7.1 Add pre-drain health check` |

### WBS Number Derivation (CRITICAL)

**NEVER invent WBS numbers.** Always:
1. Fetch parent, extract WBS prefix.
2. Scan children: `project = <PROJ> AND "Parent Link" = <INIT> AND issuetype in (Epic, Feature)`
3. Find `max(Y) + 1`. Do NOT fill gaps.
4. Confirm with user before creating.

---

## Function area mapping

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

1. Never silently omit a mandatory field.
2. Always show the proposed payload before creating. Wait for explicit approval.
3. Always inherit a WBS prefix from the parent.
4. Never assume the project key.
5. Use the MCP server, not raw REST.
6. Never use components outside the 8-pillar list.
7. **DoR, DoD, AC, and Business Value are always required, never optional.**

---

## Tool call shape

Example payload for a Story:

```json
{
  "project_key": "LATC",
  "summary": "0.4.7 Provision dashboard refresh job on shared VM",
  "issue_type": "Story",
  "description": "## Context\n...\n\n## Business Value\n...\n\n## Definition of Ready\n- [ ] AC reviewed\n\n## Definition of Done\n- [ ] Code merged, CI green",
  "components": "Operations & Infrastructure",
  "additional_fields": "{\"epic_link\":\"LATC-1304\",\"customfield_10816\":\"3\",\"customfield_16400\":\"Operations\",\"customfield_10515\":\"- [ ] Given the VM is healthy, when the timer fires, then fresh data lands within 5 min.\",\"customfield_11491\":\"Removes recurring manual refresh toil and prevents stale data reaching stakeholder dashboards.\",\"labels\":[\"team:infra-row\"]}"
}
```

Notes:
- DoR and DoD go in `description` only.
- **Business Value** (`customfield_11491`) is rejected on the Task screen — attempt it via `additional_fields`, but always also embed `## Business Value` in `description`; if creation fails specifically on that field, retry without it.
- Sprints cannot be set at create time — use `jira_add_issues_to_sprint` after creating.

---

## Anti-patterns to avoid

- Don't create without DoR, DoD, AC, and Business Value.
- Don't pass Story Points as a number — use string `"3"`.
- Don't set Sprint at create time via `customfield_10004`.
- Don't set Epic Link on an Epic — use Parent Link + GANTT link.
- Don't skip the WBS scan.
- Don't omit Function area.
- Don't omit `team:*` labels.
- Don't omit Business Value — always embed `## Business Value` in the description even though the custom field is rejected on Task screens.
- Don't bypass confirmation before create operations.

---

## Resolution guidance (when transitioning to Done)

- Prefer `Done` or `Fixed` for successfully delivered work.
- Use `Won't Fix`, `Duplicate`, `Cannot Reproduce`, `Rejected` only when closing without delivery.
- On reopen transitions, clear Resolution back to unresolved.

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
| Business Value | `customfield_11491` (rejected on Task screen — description fallback always required) |
| Definition of Ready | `customfield_16516` |
| Definition of Done | `customfield_16544` |
| Parent Link (Portfolio) | `customfield_12913` |

---

## References

- Server: `user-mcp-atlassian`
- LATC Jira governance: [Jira Usage at LATC](https://km.xpaas.lenovo.com/pages/viewpage.action?pageId=551394388)
