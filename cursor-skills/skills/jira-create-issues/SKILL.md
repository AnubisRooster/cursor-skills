---
name: jira-create-issues
description: Create Jira Epics/Features and child sprint issues via the mcp-atlassian server (self-hosted Jira Data Center), enforcing a mandatory field set (Summary, Description, Epic Link/Parent Link, Estimate, Components, Labels, Function area, Business Value, Acceptance Criteria, Definition of Ready, Definition of Done) and a hierarchical WBS numbering rule (Initiative X.0 -> Epic/Feature X.Y -> Story/Task/Test/Defect X.Y.Z) regardless of what Jira's screens require. Business Value/AC/DoR/DoD live in dedicated custom fields ONLY for Story/Task/Test/Defect/Sub-task (never duplicated in the description); Epics/Initiatives keep the fuller narrative-style description with both custom field and matching heading. Enforces the three-orthogonal-dimensions model (Pillars=Components, Teams=Labels, Programs=Initiatives), 8 pillar-based components, team/product/BU labels, cross-pillar work rules, and initiative gating. Always shows the proposed payload to the user for approval before creating. Use when the user asks to create, draft, file, scaffold, or open a Jira Epic, Feature, Story, Task, Test, Defect, or sub-task under an Epic/Feature/Initiative.
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

> **Correction (2026-07-16/17):** Business Value/AC/DoR/DoD used to be required in *both* the custom field and the description body for every issue type. That was wrong for sprint-level issues — for **Story/Task/Test/Defect/Sub-task**, these four now live **only** in their dedicated custom fields; do not add matching headings to the description (it's redundant duplication, not a compliance requirement). Epics/Initiatives are unchanged — they keep the fuller narrative description with both the custom field and the heading. This was also applied retroactively to 112 pre-existing sprint-level Infra issues on 2026-07-17.

### For sprint-level issues (Story/Task/Test/Defect/Sub-task)

| Field | Type | Tool parameter / Custom field | Notes |
|---|---|---|---|
| Summary | string | `summary` (system) | Must start with WBS number |
| Description | markdown | `description` (system) | **Dedicated-field-only policy**: no `## Business Value`, `## Acceptance Criteria`, `## Definition of Ready`, or `## Definition of Done` headings. Also no separate `## Context` / `## Goal` / `## Approach` — lead with a condensed 1–3 sentence summary (no heading) of what the work is and what it enables, then keep any remaining sections with no dedicated field (`## Out of scope`, `## Links`, `## Outcomes (value unlocked)`) |
| Parent (Epic/Feature) | issue key | `customfield_10006` via `additional_fields.epic_link` | Links sprint issue to its Epic/Feature |
| Estimate (Story Points) | number | `customfield_10816` via `additional_fields` | e.g. "3", "5", "8" |
| Component/s | comma-separated string | `components` (dedicated tool param) | One or more from 8-pillar list |
| Labels | array | `labels` in `additional_fields` | At least one `team:*` label required |
| Function area | string (pillar name) | `customfield_16400` via `additional_fields` | Auto-derived from Components (see [Function area mapping](#function-area-mapping)) |
| Business Value | markdown | `customfield_11491` via `additional_fields` **only** | Rejected on the Story/Task **create** screen but confirmed accepted on the **edit** screen (tested 2026-07-16 on `LATC-5804`). Attempt it at create; if rejected, immediately follow up with a `jira_update_issue` call to set it. Never add it to the description |
| Acceptance Criteria | markdown | `customfield_10515` via `additional_fields` **only** | Confirmed accepted at create on Story/Task screens. Not in the description |
| Definition of Ready | markdown | `customfield_16516` via `additional_fields` **only** | Confirmed accepted at create on Story/Task screens. Not in the description |
| Definition of Done | markdown | `customfield_16544` via `additional_fields` **only** | Confirmed accepted at create on Story/Task screens. Not in the description |

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
| Acceptance Criteria | markdown | **Description body only** | Not confirmed on Epic screen — embed in description |
| Definition of Ready | markdown | **Description body only** (attempt `customfield_16516` too) | Confirmed accepted on Task screens; untested on Epic screens — embed in description as the safe default, attempt the custom field too |
| Definition of Done | markdown | **Description body only** (attempt `customfield_16544` too) | Confirmed accepted on Task screens; untested on Epic screens — embed in description as the safe default, attempt the custom field too |

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

### Field Guidelines

**Summary**: Every summary MUST begin with a **WBS (Work Breakdown Structure) number** that reflects the issue's position in the hierarchy. The WBS number is followed by a space and the title text. Stories should use the format "[WBS] [verb] [object] [context]".

**Description**: For **Epics/Initiatives**, a markdown body explaining what the issue is about, why it matters, and relevant context, with DoR/DoD/AC/Business Value always embedded under their `##` headings alongside the custom fields. For **Story/Task/Test/Defect/Sub-task**, keep it short: a condensed 1–3 sentence summary (no heading) instead of separate Context/Goal/Approach sections, plus any remaining sections that genuinely have no dedicated field (`## Out of scope`, `## Links`, `## Outcomes (value unlocked)`). Business Value/AC/DoR/DoD go in their custom fields only — never in the description — for these issue types.

**Epic Link** (`epicKey` or `customfield_10006`): Only on stories/tasks — set to the epic key. Not used on the epic itself.

**Estimate** (`customfield_10816`): Story points. **Always pass this as a string** (e.g. `"0.5"`, `"1"`, `"3"`, `"5"`, `"8"`, `"13"`) — this Jira DC rejects a numeric value at create/update time with `Operation value must be a string`. If the user doesn't provide estimates, ask or make reasonable suggestions based on apparent complexity.

**Component/s**: The Jira component(s) this issue belongs to — must be from the 8-pillar list. Use `jira_get_project_components` to verify valid component names if needed.

**Labels**: Must include at least one `team:*` label. Add `product:*` / `bu:*` labels for BU-specific work. See [Labels — Teams and Products](#labels--teams-and-products).

**Function area** (`customfield_16400`): Auto-derived from Components — see [Function area mapping](#function-area-mapping). Always include this field.

**Business Value** (`customfield_11491` in `additional_fields`): 1–3 sentences on why this work matters — what risk it reduces, what outcome/metric it improves, or who benefits. Generate sensible, issue-specific content if the user hasn't supplied it; never leave it blank. For **Epics/Initiatives**, also embed `## Business Value` in the description. For **Story/Task/Test/Defect/Sub-task**, the custom field is the only home for it — do not add it to the description. `customfield_11491` has been confirmed **rejected on the Story/Task create screen** but **accepted on the edit screen** (tested 2026-07-16) — attempt it at create time via `additional_fields`, and if Jira rejects it, immediately follow up with a `jira_update_issue` call setting just that field rather than dropping it. Example:
```
Reduces manual reconciliation effort by ~2 hours/week for the TPM team and removes a recurring source of stale dashboard data reported by stakeholders.
```

**Acceptance Criteria** (`customfield_10515` in `additional_fields`): A bullet list of testable conditions that must be true for the issue to be considered accepted. Write these in "Given/When/Then" or simple checkbox format. For Epics/Initiatives, also embed `## Acceptance Criteria` in the description; for Story/Task/Test/Defect/Sub-task, the custom field only. Example:
```
- [ ] User can authenticate via OAuth2
- [ ] Existing sessions are migrated without data loss
- [ ] Error responses follow the standard API format
```

**Definition of Ready** (`customfield_16516`): Conditions that must be met before work can begin. For Epics/Initiatives, also embed under `## Definition of Ready` in the description; for Story/Task/Test/Defect/Sub-task, the custom field only. Generate sensible defaults if not provided:
```
- [ ] Requirements are clearly defined
- [ ] Acceptance criteria are documented
- [ ] Dependencies are identified
- [ ] Design/technical approach is agreed upon
```

**Definition of Done** (`customfield_16544`): Conditions that must be met for the work to be considered complete. For Epics/Initiatives, also embed under `## Definition of Done` in the description; for Story/Task/Test/Defect/Sub-task, the custom field only. Generate sensible defaults if not provided:
```
- [ ] Code is written and peer-reviewed
- [ ] Unit tests are passing
- [ ] Documentation is updated
- [ ] QA testing is complete
- [ ] Deployed to staging and verified
```

### Screen availability — where fields are accepted by Jira

Not all mandatory fields are on all screen schemes. Based on testing:

| Field               | Epic screen | Story/Task create screen | Story/Task edit screen | Fallback |
| ------------------- | ----------- | ------------------------ | ----------------------- | -------- |
| Summary             | ✅           | ✅                         | ✅                       | —        |
| Description         | ✅           | ✅                         | ✅                       | —        |
| Estimate            | ✅           | ✅                         | ✅                       | —        |
| Component/s         | ✅           | ✅                         | ✅                       | —        |
| Labels              | ✅           | ✅                         | ✅                       | —        |
| Epic Name           | ✅           | N/A                       | N/A                     | —        |
| Epic Link           | N/A         | ✅                         | ✅                       | —        |
| Business Value      | ❌ (untested)| ❌ (tested — rejected)     | ✅ (tested 2026-07-16 on `LATC-5804`) | Attempt `customfield_11491` at create; if rejected, immediately set it via `jira_update_issue` right after creation. Epics: also embed `## Business Value` in Description |
| Acceptance Criteria | ❌           | ✅ (tested)                | ✅                       | Set `customfield_10515` on Story/Task at create. Epics: embed under `## Acceptance Criteria` in Description instead (no confirmed custom field there) |
| Definition of Ready | ❌ (untested)| ✅ (tested — accepted on Task, confirmed 2026-07-09) | ✅ | Set `customfield_16516` on Story/Task at create. Epics: embed under `## Definition of Ready` in Description |
| Definition of Done  | ❌ (untested)| ✅ (tested — accepted on Task, confirmed 2026-07-09) | ✅ | Set `customfield_16544` on Story/Task at create. Epics: embed under `## Definition of Done` in Description |

**Rule (corrected 2026-07-16/17):** For **Story/Task/Test/Defect/Sub-task**, AC (`customfield_10515`), DoR (`customfield_16516`), DoD (`customfield_16544`), and Business Value (`customfield_11491`) live **only** in their native custom fields — do not embed matching `##` headings in the description for these issue types. Business Value is rejected on the create screen but accepted on edit, so: attempt it at create, and if rejected, immediately follow up with `jira_update_issue` to set it — never fall back to the description. For **Epics/Initiatives**, none of the four are confirmed available as custom fields (untested/rejected) except where explicitly noted — embed all four in the description body there, exactly as before.

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
| 1 | Initiative | `X.0` | `0.0 OPS: Operational Tasks & General Work` |
| 2 | Epic / Feature | `X.Y` | `0.4 Data and Infra Ops Tasks` |
| 3 | Story / Task / Test / Defect | `X.Y.Z` | `0.4.7 Provision dashboard refresh job on shared VM` |
| 4 | Subtask | `X.Y.Z.N` | `0.4.7.1 Add pre-drain health check script` |

### Format rules

- Single space between the WBS number and the title text.
- Zero-padding is **not** used (`0.10`, never `0.010`).
- Initiatives are not created by this skill; their prefix is read, not assigned. If an Initiative has no prefix, stop and ask the user to add one.
- The same WBS string goes into both `summary` and (for Epics) `customfield_10005` (Epic Name).

### WBS Number Derivation (CRITICAL — Always Required)

**NEVER invent or guess WBS numbers.** Before assigning a WBS number to any new issue, you MUST:

1. **Fetch the parent** using `jira_get_issue` to get its summary and extract the WBS prefix.
   - For an Epic under an Initiative: extract the root number (e.g., `0` from `"0.0 OPS: Operational Tasks"`)
   - For a Story under an Epic: extract the Epic's full prefix (e.g., `0.4` from `"0.4 Data and Infra Ops Tasks"`)

2. **Scan existing children** to find all existing WBS numbers at that level:
   - For Epics: run `project = <PROJ> AND "Parent Link" = <INIT> AND issuetype = Epic`
   - For Stories/Tasks: run `project = <PROJ> AND "Epic Link" = <EPIC> AND issuetype in (Story, Task)`

3. **Parse WBS prefixes** from each child's summary and collect the numbers at the relevant level.

4. **Determine the next available number** — find the highest existing number and increment by 1. 
   - For example, if children are `0.1`, `0.2`, `0.4`, the next available is `0.5`
   - **DO NOT fill gaps** (like `0.3` in this example) — gaps may be intentional

5. **For batch creates**, allocate consecutive numbers starting at the next free slot: `0.5`, `0.6`, `0.7`, etc.

6. **Report to the user** before creating: "Initiative `<INIT>` is `X.0`. Existing Epics: `<list>`. Next Epic will be `X.<nextY>`. Confirm?"

7. **Flag non-conforming siblings** (e.g., issues without WBS prefixes) for the user to review later.

### Computing the next number

**Creating an Epic or Feature under Initiative `<INIT>`:**

1. Run `jira_get_issue` on `<INIT>` and extract the leading `X.0` from `summary`. Call this `X`.
2. List children at level `X.Y` (both Epics and Features):
   ```
   project = <PROJ> AND "Parent Link" = <INIT> AND issuetype in (Epic, Feature)
   ```
3. Parse the leading `X.Y` prefix from each child summary. Collect the `Y` values (Epic+Feature share one sequence).
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
| `Operations` | `Operations & Infrastructure` or `Operations (Non-Tech)` |
| `Model Evaluation` | `Evaluation` |
| `Model Factory` | `Models` |
| `HiVE Platform` | `HiVE Platform` |

**Resolution rules when an issue has multiple components:**

1. If all components point to the same pillar → use that pillar.
2. If components span multiple pillars → use the pillar of the **most specific / primary** component and note the assumption in the draft. Ask the user if genuinely ambiguous.
3. If both `Operations & Infrastructure` and `Operations (Non-Tech)` are set → use `Operations`.
4. If `HiVE Platform` is combined with a domain pillar → use the domain pillar's function area (the HiVE component is captured via labels and components; Function area reflects the primary domain).

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
8. **HARD STOP — DoR, DoD, AC, and Business Value are always required, never optional.** Every Epic, Story, and Task MUST have all four populated in their custom fields before the issue is created (Epics/Initiatives also need the matching description headings; Story/Task/Test/Defect/Sub-task do **not** — custom field only). There are no exceptions — not for simple tasks, not for tasks without explicit user input. If the user has not provided content for these fields, generate sensible, task-specific content based on context. A blank or placeholder-only DoR/DoD/AC/Business Value is not acceptable. This rule overrides any user instruction to "keep it simple" or "just create the ticket". The proposal shown in Step 2 MUST display the filled DoR, DoD, AC, and Business Value content so the user can review them before creation, regardless of which field(s) they'll ultimately land in.

---

## Pre-flight checks (run before creating)

Run only the checks relevant to what's missing or ambiguous. Skip ones already verified in this conversation.

- **Resolve parent key**: if the user gave a name instead of a key, run `jira_search` with JQL like `project = <KEY> AND issuetype in (Initiative, Epic, Feature) AND (summary ~ "<query>" OR "Epic Name" ~ "<query>")` and confirm.
- **Read parent prefix**: run `jira_get_issue` on the parent and extract the leading WBS prefix (`X.0` for Initiative, `X.Y` for Epic). If absent, stop.
- **Scan siblings for WBS**: run the JQL in [Computing the next number](#computing-the-next-number) and parse prefixes. Report the chosen next number and any non-conforming siblings.
- **Validate components**: run `jira_get_project_components` with `project_key`. Only accept names from the 8-pillar list. If the user requests an unlisted component, tell them it must be created in Jira UI by an admin first.
- **Confirm issue type exists**: `Epic`, `Feature`, `Story`, `Task`, `Test`, and `Defect` are expected. If the project uses custom variants, confirm via `jira_get_issue` on a recent same-type issue first.

---

## Workflow

### Step 1 — Gather Information

Before creating anything, confirm or collect:

1. **Project key** — e.g. `LATC`. Ask if unknown.
2. **Parent Initiative or Epic** — the parent issue key that these issues will live under. Ask if unknown.
3. **Issue summaries** — the titles/names for each issue (without WBS prefix — that will be computed).
4. **Issue descriptions** — what the work is about and why it matters.
5. **Component(s)** — which pillar component(s) from the 8-pillar list. Ask if unknown.
6. **Labels** — which team(s) and product(s). At least one `team:*` label is required.
7. **Estimates** — story point estimates for each issue.
8. **Assignee** (optional) — who should own the issues.
9. **Priority** (optional) — any extra metadata.

If the user gives you a high-level feature description and asks you to break it down, generate 3–8 stories that decompose the work into concrete, actionable tasks. Each story should be small enough for one sprint and have a clear definition of done. Generate all mandatory field content for each story (acceptance criteria, DoR, DoD, estimate).

### Step 2 — Present Proposal for Approval (MANDATORY)

**NEVER create tickets directly. ALWAYS present a proposal first and wait for the user to approve it before creating anything in Jira.**

After gathering information and computing WBS numbers, present the full plan as a formatted table showing all issues you intend to create. Include:

- WBS number (computed from parent scan)
- Issue type (Epic / Story / Task / Subtask)
- Summary title (with WBS prefix)
- Estimate (story points)
- Component(s)
- Label(s)

Example proposal format:

| WBS   | Type    | Summary                                    | Est | Component(s)                | Labels                        |
|-------|---------|--------------------------------------------|-----|---------------------------|----------------------------|
| 0.5   | Epic    | 0.5 Data Ingestion & Entity Extraction     | 34  | Data, Context & Memory    | team:dcm                   |
| 0.5.1 | Story   | 0.5.1 Design document ingestion architecture | 5   | Data, Context & Memory    | team:dcm                   |
| 0.5.2 | Story   | 0.5.2 Implement preprocessing and chunking | 8   | Data, Context & Memory    | team:dcm                   |
| 0.5.3 | Story   | 0.5.3 Develop entity extraction prompts    | 8   | Data, Context & Memory    | team:dcm                   |
| 0.6   | Epic    | 0.6 Knowledge Graph Infrastructure         | 26  | Data, Context & Memory    | team:dcm                   |
| 0.6.1 | Story   | 0.6.1 Evaluate and deploy graph database   | 5   | Data, Context & Memory    | team:dcm                   |

After presenting the proposal, explicitly ask the user:

**"Does this look good? I'll create these tickets once you approve, or let me know what you'd like to change."**

Wait for explicit approval. The user may:
- Approve as-is → proceed to creation
- Request additions, removals, or modifications → update the proposal and present it again
- Change estimates, components, or story wording → update and re-present

**Only proceed to ticket creation after the user confirms the proposal.**

### Step 3 — Compute WBS Numbers

Before creating, compute WBS numbers by scanning existing children (see [WBS Number Derivation](#wbs-number-derivation-critical--always-required)):

1. Fetch the parent issue and extract its WBS prefix
2. Scan existing children with appropriate JQL
3. Parse WBS numbers from summaries
4. Determine next available number(s)
5. Show the scan results to the user and confirm the chosen numbers

### Step 4 — Create Issues

For each issue in the approved proposal:

**For an Epic:**

Use `jira_create_issue` with:
- `issue_type: "Epic"`
- `summary` with WBS prefix
- `customfield_10005` (Epic Name) set to same value as summary
- `customfield_12913` (Parent Link) set to Initiative key in `additional_fields`
- All mandatory fields (components, labels, description with Business Value/AC/DoR/DoD embedded)

After creation, call `jira_create_issue_link` to establish the GANTT hierarchy:
```
type_name: "multi-level hierarchy [GANTT]"
inward_issue_key:  "<EPIC-KEY>"        # the new epic (child)
outward_issue_key: "<INITIATIVE-KEY>"  # the parent initiative
```

**For a sprint-level issue (Story/Task/Test/Defect/Sub-task):**

Use `jira_create_issue` with:
- `issue_type`: one of `"Story"`, `"Task"`, `"Test"`, `"Defect"`
- `summary` with WBS prefix
- `epic_link` in `additional_fields` set to the Epic key
- All mandatory fields (estimate, components, labels, Business Value, AC, DoR, DoD)
- AC (`customfield_10515`), DoR (`customfield_16516`), and DoD (`customfield_16544`) set via `additional_fields` **only** — all three confirmed accepted on Story/Task screens; do **not** add matching headings to the description. Business Value (`customfield_11491`) also attempted via `additional_fields`; confirmed rejected on the *create* screen but accepted on *edit* — if the create call rejects it, immediately call `jira_update_issue` right after to set it. Never fall back to putting it in the description.
- Description is short: a 1–3 sentence summary (no heading) of what the work is/enables, plus any of `## Out of scope`, `## Links`, `## Outcomes (value unlocked)` that apply. No `## Context`, `## Goal`, `## Approach`, `## Business Value`, `## Acceptance Criteria`, `## Definition of Ready`, or `## Definition of Done` headings.

**For batch creates:**

Use `jira_batch_create_issues`:
1. Call with `validate_only: true` first to catch errors
2. Fix any reported errors
3. Call with `validate_only: false` to create
4. Report the resulting keys with their WBS numbers

### Step 5 — Report Results

After all issues are created, present a summary table:

| WBS   | Key        | Type  | Summary                                  | Estimate | Components | Status  |
|-------|------------|-------|-------------------------------------------|----------|------------|---------|
| 0.5   | LATC-1400  | Epic  | 0.5 Data Ingestion & Entity Extraction  | 34       | Data, Context & Memory | To Do   |
| 0.5.1 | LATC-1401  | Story | 0.5.1 Design document ingestion architecture | 5    | Data, Context & Memory | To Do   |
| 0.5.2 | LATC-1402  | Story | 0.5.2 Implement preprocessing and chunking  | 8     | Data, Context & Memory | To Do   |

Also note that all issues include Business Value, Acceptance Criteria, Definition of Ready, and Definition of Done.

---

## Tool call shape

Use `jira_create_issue` with `additional_fields` carrying the custom fields. **`additional_fields` is a JSON-encoded string**, not a JSON object.

Example payload for a Story:

```json
{
  "project_key": "LATC",
  "summary": "0.4.7 Provision dashboard refresh job on shared VM",
  "issue_type": "Story",
  "description": "Automates the currently-manual JIRAFlow dashboard refresh so stakeholders always see current data without operator intervention.\n\n## Out of scope\n- Power BI report layout changes\n\n## Links\n- TBD: link to runbook",
  "components": "Operations & Infrastructure",
  "additional_fields": "{\"epic_link\":\"LATC-1304\",\"customfield_10816\":\"3\",\"customfield_16400\":\"Operations\",\"customfield_10515\":\"- [ ] Given the VM is healthy, when the timer fires, then fresh data lands within 5 min.\",\"customfield_16516\":\"- Requirements are clearly defined\\n- Dependencies are identified\",\"customfield_16544\":\"- Code merged and CI green\\n- AC verified by reviewer\",\"customfield_11491\":\"Removes recurring manual refresh toil and prevents stale data reaching stakeholder dashboards.\",\"labels\":[\"team:infra-row\"],\"priority\":{\"name\":\"Medium\"}}"
}
```

Notes on this example: `customfield_10515` (AC), `customfield_16516` (DoR), `customfield_16544` (DoD), and `customfield_11491` (Business Value) are all set via `additional_fields` **only** — none of them are duplicated in the description, per the 2026-07-16/17 correction. If `customfield_11491` is rejected at create (expected on the Task create screen), follow up immediately with a `jira_update_issue` call to set it rather than dropping it or adding it to the description.

Example payload for an Epic (under Initiative `LATC-7`):

```json
{
  "project_key": "LATC",
  "summary": "0.5 Self-service Jira Reports for Managers",
  "issue_type": "Epic",
  "description": "## Problem / Opportunity\n...\n\n## Outcomes\n...\n\n## Scope\n...\n\n## Out of scope\n...\n\n## Stakeholders\n...\n\n## Business Value\n...\n\n## Acceptance Criteria\n- [ ] Managers can generate reports without admin help.\n\n## Definition of Ready\n- [ ] AC reviewed\n- [ ] Dependencies confirmed\n\n## Definition of Done\n- [ ] All child Stories closed\n- [ ] AC verified\n- [ ] Stakeholders notified",
  "components": "Operations (Non-Tech)",
  "additional_fields": "{\"customfield_10005\":\"0.5 Self-service Jira Reports for Managers\",\"customfield_12913\":\"LATC-7\",\"customfield_16400\":\"Operations\",\"labels\":[\"team:infra-row\"]}"
}
```

Notes:
- `summary` carries the WBS prefix. Never call create with a bare title.
- `epic_link` is the MCP-friendly alias for `customfield_10006`. Either works on Stories.
- Epics use `customfield_10005` (Epic Name) and `customfield_12913` (Parent Link); they do **not** get an `epic_link`.
- **DoR and DoD** (`customfield_16516`, `customfield_16544`) are confirmed **accepted** via `additional_fields` on Story/Task screens (tested 2026-07-09 on `LATC-5309`) — set the custom field only, no description heading. On Epic screens this is unconfirmed; embed in `description` only there unless tested.
- **AC** (`customfield_10515`) is accepted on Story/Task screens; pass it in `additional_fields` there, custom-field only. For Epics, embed it in `description` only.
- **Business Value** (`customfield_11491`) is **rejected on the Task create screen** (`Field 'customfield_11491' cannot be set...`) but **confirmed accepted on the edit screen** (tested 2026-07-16 on `LATC-5804`) — attempt it in `additional_fields` at create; if creation fails specifically on that field, retry create without it, then immediately call `jira_update_issue` to set it. For Story/Task/Test/Defect/Sub-task, never fall back to the description. For Epics, always embed `## Business Value` in `description` (custom field unconfirmed there).
- After creating an Epic, always also call `jira_create_issue_link` with `type_name: "multi-level hierarchy [GANTT]"`.
- **Sprints cannot be set at create time** through this MCP — passing `customfield_10004` to `jira_create_issue` raises `Operation value must be a string`. Create the issue(s) first, then add them with `jira_add_issues_to_sprint` (`sprint_id` + comma-separated `issue_keys`). Resolve the active sprint id via `jira_get_sprints_from_board` (state `active`) if needed.
- `labels` must be an array of strings using the `team:*`, `product:*`, or `bu:*` prefix conventions.

---

## Proposal table format (Step 2 of every workflow)

Before creating anything, present this table and wait for explicit approval:

| WBS   | Type  | Summary                                      | Est | Component(s)                | Labels                        |
| ----- | ----- | -------------------------------------------- | --- | --------------------------- | ----------------------------- |
| 4.1   | Epic  | 4.1 Kubernetes Cluster Upgrade               | —   | Operations & Infrastructure | team:infra-row                |
| 4.1.1 | Story | 4.1.1 Design rolling upgrade strategy        | 5   | Operations & Infrastructure | team:infra-row                |
| 4.1.2 | Story | 4.1.2 Implement node draining and migration  | 8   | Operations & Infrastructure | team:infra-row                |
| 4.1.3 | Story | 4.1.3 Update monitoring dashboards           | 5   | Operations & Infrastructure, Evaluation | team:infra-row, team:eval |

Ask explicitly: **"Does this look good? I'll create these tickets once you approve, or let me know what you'd like to change."**

---

## Templates

### Description (Story/Task/Test/Defect/Sub-task)

**Corrected 2026-07-16/17:** Business Value, AC, DoR, and DoD live **only** in their custom fields for sprint-level issues — no matching headings in the description. Context/Goal/Approach are also dropped as separate headings; replace them with one condensed 1–3 sentence summary up top (no heading needed).

```markdown
[1–3 sentences: what this work is and what it enables. Replaces separate Context/Goal/Approach sections.]

## Out of scope
- [Anything explicitly not being done in this issue.]

## Links
- [Confluence / dashboard / parent doc URLs]

## Outcomes (value unlocked)
- [What becomes possible / de-risked once this ships — only include if it adds information beyond the opening summary.]
```

Set `customfield_10515` (AC), `customfield_16516` (DoR), `customfield_16544` (DoD), and `customfield_11491` (Business Value) via `additional_fields` — see [Mandatory fields](#mandatory-fields-always) for content guidance on each.

### Description (Epic)

Business Value, AC, DoR, and DoD are **not confirmed** on the Epic screen (only tested on Task screens so far) — all four must always be embedded in the description regardless of whether the custom-field attempt succeeds.

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

## Business Value
[1–3 sentences: what risk this reduces, what outcome/metric it improves, or who benefits.]

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
- Component: `Operations & Infrastructure`. Label: `team:infra-row`. Function area: `Operations`.

```json
{
  "project_key": "LATC",
  "summary": "0.4.7 Automate JIRAFlow dashboard refresh on shared Linux VM",
  "issue_type": "Story",
  "description": "Replaces the currently-manual JIRAFlow dashboard refresh with a systemd timer on the shared VM that refreshes the dataset hourly and alerts on failure, reducing operator toil and keeping stakeholder data current.\n\n## Out of scope\n- Power BI report layout changes\n\n## Links\n- TBD: link to runbook",
  "components": "Operations & Infrastructure",
  "additional_fields": "{\"epic_link\":\"LATC-1304\",\"customfield_10816\":\"3\",\"customfield_16400\":\"Operations\",\"customfield_10515\":\"- [ ] Given the VM is healthy, when the timer fires, then a fresh dataset lands in the target store within 5 minutes.\\n- [ ] A failure surfaces an alert in the operational dashboard within 10 minutes.\",\"customfield_16516\":\"- [ ] AC reviewed by assignee\\n- [ ] VM access and credentials confirmed\\n- [ ] Effort estimated; risks captured\",\"customfield_16544\":\"- [ ] Timer deployed and green for 24 h\\n- [ ] Runbook updated\\n- [ ] AC verified by reviewer\\n- [ ] Stakeholders notified\",\"customfield_11491\":\"Removes manual refresh toil and prevents stale data reaching stakeholder dashboards.\",\"labels\":[\"team:infra-row\"],\"priority\":{\"name\":\"Medium\"}}"
}
```

### Example 2: New Epic + Stories (cross-pillar BU work)

User: "Create an epic for Qira model routing work — it spans Reasoning & Orchestration and Runtime pillars."

- Components: `Reasoning & Orchestration, Runtime` (both pillars).
- Labels: `product:qira, team:ro-prc-p` (or whichever team is delivering).
- Initiative: under the `BU-` prefixed Initiative for Qira (e.g. `10.0 BU: Qira Delivery`).
- Function area: `Reasoning & Orchestration` (primary pillar; note the Runtime component in the draft).
- Present proposal and wait for approval before creating.

### Example 3: Complete Interaction Flow

User: "Create an epic in LATC under initiative LATC-7 for migrating our auth service to OAuth2, with stories for the main tasks. Use the Operations (Non-Tech) component and team:infra-row label."

**Agent's approach:**

1. Confirm project key `LATC`, component `Operations (Non-Tech)`, label `team:infra-row`
2. **Fetch LATC-7** to get the WBS root (`0.0 OPS: Operational Tasks & General Work` → root `0`) and existing children
3. Find existing child Epics: `0.1`, `0.2`, `0.3`, `0.4` → next available is `0.5`
4. Generate stories from the feature description with all mandatory fields
5. **Present proposal table to the user with WBS numbering:**

   | WBS   | Type  | Summary                                          | Est | Component           | Labels        |
   |-------|-------|--------------------------------------------------|-----|---------------------|---------------|
   | 0.5   | Epic  | 0.5 Migrate Auth Service to OAuth2               | 34  | Operations (Non-Tech) | team:infra-row |
   | 0.5.1 | Story | 0.5.1 Research OAuth2 providers and select one   | 3   | Operations (Non-Tech) | team:infra-row |
   | 0.5.2 | Story | 0.5.2 Implement authorization code flow          | 8   | Operations (Non-Tech) | team:infra-row |
   | 0.5.3 | Story | 0.5.3 Migrate existing user sessions             | 8   | Operations (Non-Tech) | team:infra-row |
   | 0.5.4 | Story | 0.5.4 Update API gateway configuration           | 5   | Operations (Non-Tech) | team:infra-row |
   | 0.5.5 | Story | 0.5.5 Write integration tests for OAuth2 flows   | 5   | Operations (Non-Tech) | team:infra-row |
   | 0.5.6 | Story | 0.5.6 Update documentation and runbooks          | 5   | Operations (Non-Tech) | team:infra-row |

6. **Ask:** "Does this look good? I'll create these tickets once you approve, or let me know what you'd like to change."
7. **After approval**:
   - Create the Epic with WBS `0.5`, set Epic Name and Parent Link fields
   - Link Epic to Initiative LATC-7 via "multi-level hierarchy [GANTT]"
   - Create stories sequentially with all mandatory fields (Business Value, AC, DoR, DoD set via their custom fields only — not embedded in descriptions)
8. Present summary table with Jira keys mapped to WBS numbers

---

## Optional Enhancements

After the core Epic + Stories are created, offer the user these options:

- **Set priority** — pass `{"priority": {"name": "High"}}` in `additional_fields`
- **Add to a sprint** — create the issue(s) first, then call `jira_add_issues_to_sprint` (`sprint_id`, comma-separated `issue_keys`). Do **not** set `customfield_10004` in `additional_fields` at create time — this MCP rejects it with `Operation value must be a string`.
- **Link to existing issues** — use `jira_create_issue_link`
- **Add watchers** — use `jira_add_watcher`
- **Add additional labels** — pass `{"labels": ["label1", "label2"]}` in `additional_fields`

---

## Anti-patterns to avoid

- **Don't create an issue without DoR, DoD, AC, and Business Value.** These four fields are mandatory on every issue, always. If you catch yourself about to call `jira_create_issue` without all four populated with real, task-specific content — stop, fill them, then create. For Story/Task/Test/Defect/Sub-task, they belong in the custom fields **only** — don't also write them into the description. For Epic/Initiative, they go in both the custom field (where available) and the description.
- **Don't add `## Business Value`, `## Acceptance Criteria`, `## Definition of Ready`, or `## Definition of Done` headings to a Story/Task/Test/Defect/Sub-task description.** That duplicates the dedicated custom fields — corrected 2026-07-16/17 after finding this pattern across 12 new + 112 pre-existing Infra tickets.
- **Don't add separate `## Context` / `## Goal` / `## Approach` headings to a Story/Task/Test/Defect/Sub-task description.** Use one condensed 1–3 sentence summary at the top instead (no heading).
- **Don't pass JSON objects to `additional_fields`.** It must be a JSON **string**.
- **Don't pass Story Points as a number.** `customfield_10816` must be a **string** (`"0.5"`, `"3"`); a numeric value is rejected with `Operation value must be a string`.
- **Don't set the Sprint at create time.** `customfield_10004` cannot be set via `jira_create_issue` on this DC (same `Operation value must be a string` error). Add issues to the sprint afterward with `jira_add_issues_to_sprint`.
- **Don't set Epic Link on an Epic.** Use Epic Name (`customfield_10005`) on Epics; Epic Link on children. For Epics, also set Parent Link (`customfield_12913`) and create the GANTT hierarchy link.
- **Don't skip the WBS scan.** Never invent the next number — always re-run the JQL scan right before showing the draft.
- **Don't reuse a number.** If the parent has gaps (e.g. `0.4.1`, `0.4.3`, `0.4.5`), still use `max+1` (`0.4.6`). Filling gaps causes confusion in roadmaps.
- **Don't back-fill or rename existing siblings** without an explicit user request.
- **Don't omit Function area.** Always derive and include `customfield_16400`. If rejected by the screen, note the omission.
- **Don't set AC, DoR, or DoD in only one place — but "one place" means different things by issue type.** For Story/Task/Test/Defect/Sub-task, the one required place is the custom field (`customfield_10515` / `customfield_16516` / `customfield_16544`) — do not also add description headings. For Epic/Initiative, both the custom field (where available) and the description heading are required.
- **Don't omit Business Value.** Every issue needs it populated with real content (1–3 sentences: risk reduced, outcome/metric improved, or who benefits). For Epics, it's a `## Business Value` description section (custom field unconfirmed there). For Story/Task/Test/Defect/Sub-task, it's `customfield_11491` only — attempt it at create, and if rejected (expected on the create screen), immediately set it via `jira_update_issue` rather than falling back to the description.
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
| Business Value | `customfield_11491` (rejected on Task *create* screen, confirmed accepted on *edit* screen 2026-07-16 — attempt at create, else set via update immediately after; custom-field only for Story/Task/Test/Defect/Sub-task, no description fallback) |
| Definition of Ready | `customfield_16516` (confirmed accepted on Task screen 2026-07-09 — custom field only for sprint-level issues, no description heading) |
| Definition of Done | `customfield_16544` (confirmed accepted on Task screen 2026-07-09 — custom field only for sprint-level issues, no description heading) |
| Original story points (Portfolio) | `customfield_12916` |
| Target start / end (Portfolio) | `customfield_12914` / `customfield_12915` |
| Parent Link (Portfolio) | `customfield_12913` |

## Resolution guidance (when transitioning to Done)

- For successfully delivered work, prefer `Done` or `Fixed` (team convention may pick one default).
- Use non-delivery resolutions (for example `Won't Fix`, `Duplicate`, `Cannot Reproduce`, `Rejected`) only when the issue is intentionally closed without delivery.
- On reopen transitions, clear Resolution back to unresolved.

**Field-type quirks (this DC):** pass Story Points (`customfield_10816`) as a **string** (e.g. `"0.5"`); the Sprint field (`customfield_10004`) **cannot** be set at create time — use `jira_add_issues_to_sprint` after creating. Both quirks surface as the error `Operation value must be a string`.

If a future project surfaces different IDs for AC/DoR/DoD/Business Value, confirm with `jira_search_fields` before creating.

---

## References

- MCP tools used: `jira_create_issue`, `jira_batch_create_issues`, `jira_create_issue_link`, `jira_link_to_epic`, `jira_get_project_components`, `jira_search`, `jira_search_fields`, `jira_get_issue`, `jira_get_sprints_from_board`.
- Server: `user-mcp-atlassian` (sooperset / SharkyND mcp-atlassian, stdio over `uvx`).
