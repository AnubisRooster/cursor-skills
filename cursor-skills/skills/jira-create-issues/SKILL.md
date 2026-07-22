---
name: jira-create-issues
description: Create Jira Epics/Features and child sprint issues via the mcp-atlassian server (self-hosted Jira Data Center), enforcing a mandatory field set (Summary, Description, Epic Link/Parent Link, Estimate, Components, Labels, Function area, Business Value, Acceptance Criteria, Definition of Ready, Definition of Done) and a hierarchical WBS numbering rule (Initiative X.0 -> Epic/Feature X.Y -> Story/Task/Test/Defect X.Y.Z) regardless of what Jira's screens require. Business Value/AC/DoR/DoD live in dedicated custom fields ONLY for every issue type (Initiative, Epic, Feature, Story, Task, Test, Defect) and are never duplicated in the description; the sole exceptions are Business Value on Task and all four on Sub-task, which have no screen slot and fall back to description headings. Enforces the three-orthogonal-dimensions model (Pillars=Components, Teams=Labels, Programs=Initiatives), 8 pillar-based components, team/product/BU labels, cross-pillar work rules, and initiative gating. Always shows the proposed payload to the user for approval before creating. Use when the user asks to create, draft, file, scaffold, or open a Jira Epic, Feature, Story, Task, Test, Defect, or sub-task under an Epic/Feature/Initiative.
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

For the complete remainder of this skill (Mandatory fields, WBS numbering, Workflow, Tool call shape, Templates, Examples, Anti-patterns, Quick field reference, etc.), see the canonical copy on GitLab: `cursor-skills/skills/jira-create-issues/SKILL.md` in project `latc/users/mfink` — this GitHub mirror should be kept byte-for-byte in sync with that file. (Sync note: this mirror push hit tool-call length limits for pasting the full ~67KB file inline; the GitLab copy and the Confluence catalog attachment are complete and authoritative as of 2026-07-22.)