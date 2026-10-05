# Cursor Admin Handbook (operator reference)

Condensed from the Cursor Admin Handbook. Confirm retention windows, API surfaces, and residency exclusions with the Cursor account team before locking them into policy.

## Part I — Orientation

Cursor is an AI code editor and agent platform. Developers use it locally; admins govern identity, access, data posture, model policy, and where agents run.

An **Organization** sits above one or more **Teams**. Objectives: stand up identity and membership; enforce data/model posture; decide where agents run. Tight policy blocks productivity; loose policy fails finance/security. Measure outcomes, not only activity.

### Deployment (tool-call placement)

Does **not** move the Cloud Agent loop or model inference out of Cursor's cloud.

| Pattern | Tool calls run | You operate |
|---|---|---|
| Editor agents | Workstation / automation host | Endpoint, credentials, software, network |
| Cursor-managed Cloud Agents (default for most teams) | Cursor isolated VM | Repo access, secrets, environment, network policy |
| My Machines | User-assigned laptop/VM | Machine, worker, checkout, credentials, cleanup |
| Self-Hosted Pool | Your worker fleet | Hosts, images, isolation, capacity, autoscaling, updates, monitoring, secrets, network, IR |

Consequences: Privacy Mode ≠ runtime placement. Cloud Agent network policy is layered (user / environment / Team). Ownership scales with placement: managed is least ops; Self-Hosted is a production fleet.

Trust: SOC 2 Type II; artifacts in the Cursor Trust Center; contractual processing in the DPA. Privacy Mode on (Enterprise default, lockable): neither Cursor nor providers train on Customer Data. Most Cursor-routed models are ZDR; exceptions are BYOK and admin-approved non-ZDR models. Feature retention (Cloud Agent history, snapshots) is separate from ZDR. US residency is per-Team and not universal.

## Part II — Organizations model

Overlapping layers, not a strict hierarchy. A user can belong to several Teams and Groups.

**Organization** — shared identity (org SSO/SCIM, membership, domain verification), Org Admins, Organization Groups, pooled commercial posture, org analytics/audit. Team-level SSO remains available when needed. The **default Team** is a login/routing home only — not a parent of other Teams; do not infer billing or IdP routing from it. Org membership lasts while the user is Org Admin **or** on at least one linked Team.

**Team** — primary operational unit. Owns membership/roles, policy defaults (privacy, usage, security, models, features), Directory Groups, Billing Groups, team audit/analytics. Teams are **flat**; policy does not cross Teams.

**Three "Groups":**

| Construct | Scope | What it does |
|---|---|---|
| Organization Groups | Org; users from one or more Teams | Model/provider access, agent auto-run, spend limits. Generally **widen** Team access. |
| Directory Groups | From IdP via SCIM; Team-scoped policy | To drive Team membership/roles: sync into an Organization Group, then map that group to the Team with a role. |
| Billing Groups | Attribution | Reporting/chargeback only. Do **not** restrict actions. One Billing Group per user; delete reassigns history to Unassigned. |

User settings apply only where allowed. Member-level spend overrides exist. Cloud Agent environment precedence (repo → personal saved env → Team saved env) is **not** the org policy hierarchy. Self-hosted pools/machines are execution targets, not policy layers.

### Inheritance (per-control; no global lock)

- **Floor:** Team baseline; Groups grant, they do not revoke Team-permitted access. Restrict a cohort with a tight Team baseline, then widen via Organization Groups.
- **Widen (loosest wins):** model access, provider access, agent auto-run allowances, spend limits.
- **Sticky / restrictive:**
  - Privacy Mode is Team-enforced; Groups cannot turn it off.
  - Allowed Team IDs (MDM) block unapproved Teams and personal accounts.
  - File-Deletion Protection and Browser Protection are **on** if Team **or** an applicable Group enables them.
  - MCP: admin patterns → `permissions.json` → editor allowlist. Admin MCP overrides managed permissions and editor allowlists.
- **Lock:** where exposed, admin forces a value; mechanism differs by control.

### Roles

**Org Admin** — org settings, membership, shared identity, Organization Groups, org reporting. Keep small, strongly authenticated, reviewed.

**Team:** Admin (paid, product access); Unpaid Admin (same admin, no product; Team still needs ≥1 paid user); Member (paid product, no team admin/billing). Roles are Team-scoped.

Directory-driven: map Organization Group → Team as Member, Admin, or no managed role. **IdP role attributes are not imported.**

Delegation is role-based, not granular. Do not assume billing, group management, or org membership can be granted apart from Org Admin / Team Admin / Unpaid Admin.

Service accounts: one per automation boundary; least repo access and scope; rotate; revoke; review usage. **No seat**, but they **draw Team usage**. Some Cloud Agent / self-hosted worker ops need **agent-scoped service-account keys**. Org keys use route-specific scopes. Personal/user/Team/Org API keys are **not** accepted for pool workers.

## Part III — Identity

Three stages: **SSO (auth)** → **Provisioning (membership)** → **Offboarding**. SSO is how; SCIM/invites/mappings are who and where.

SAML 2.0 on Teams and Enterprise. Prefer one org shared IdP; consolidate team-level providers into it. Verify each SSO domain (DNS TXT). JIT enrolls on first SSO sign-in only — no Directory Groups, no deprovision; those need SCIM. SCIM requires active SSO. Pilot, then enforce.

**Generic handbook break-glass:** Org Admin outside the SSO-enforced domain before forcing SSO. **Lenovo: this does not exist as a dashboard control — see SKILL.md hard rules and idp-migration.md W6.**

SCIM 2.0 (Enterprise + SSO): assign provisions; unassign/deactivate removes. User provisioning and group sync are often **separate IdP settings** — enable group sync explicitly. Map Directory Group → Organization Group → Teams. One Organization Group can map to multiple Teams.

Non-SCIM joins: email invite, invite link, domain matching. Restricting invites to approved domains currently requires domain matching first. These need a verified domain and are **unavailable under SCIM**. Revoke unused invite links.

Offboarding: IdP unassign/deactivate for SCIM users; else Team admin removes from Members. Remove from **every** Team. Org membership ends with no linked Team and no Org role. Removal **permanently deletes** that member's Memories and Cloud Agent data for the Team — preserve work first.

Removal does **not** auto-revoke personal keys, reassign service accounts, review SCM/integration ownership, or delete published chat/canvas/share links.

Before removing a Team Admin: another Admin or Unpaid Admin remains, and ≥1 paid user remains.

Deletion surfaces: user-initiated account delete (indexed data within 30 days; Team removal does not do this); Cloud Agent transcripts not deleted on removal by default (Delete Agent API or Team retention); snapshots expire after 90 days inactivity, no on-demand delete; DSAR/contract-end via Privacy Policy, DPA, account team.

## Part IV — Data & AI

Set privacy **before** models/agents. Record mode and enforcement per Team.

| Mode | Effect |
|---|---|
| Privacy Mode (Enterprise default) | No training; ZDR on supported Cursor-routed models; narrow purpose-scoped storage allowed (e.g. Cloud Agent repo/env state) |
| Privacy Mode (Legacy) | Blocks cloud-side code storage; disables Cloud Agents, Team Rules, shared canvases. Deprecated for new customers |

Enforce Privacy Mode so members cannot disable it.

Retention ≠ Privacy Mode / ZDR. Cloud Agent history retained indefinitely by default; Team-wide window available. Snapshots: 90-day inactivity. Delete Agent API for one transcript. Mechanisms do **not** combine into universal no-retention.

Context:

- `.cursorignore` — blocks Cursor-native Agent reads, Tab, Inline Edit, context, `@` mentions. Terminal and MCP may still read those files.
- Hierarchical Cursor Ignore — parent `.cursorignore` applies to descendant workspaces. Also: per-user global ignore; Enterprise Team-wide ignore.
- `.cursorindexingignore` — exclude from index/search but still allow AI features. Semantic search + local Instant Grep.
- `.cursor` Directory Protection — agent changes to protected project config need approval; users can still edit manually.
- Sensitive reads: ignore + `beforeReadFile` hooks with `failClosed: true`.
- Filesystem permissions, sandbox, approvals for hard isolation. Allowed Team IDs do not protect files.
- CMEK: embeddings and Cloud Agent data.

ZDR exceptions: BYOK follows the customer's provider agreement; non-ZDR models blocked until admin approves retention (then still limit via model access). Confirm current non-ZDR list.

US residency (Team-level): in-scope inference/processing/storage on US infra. Documented exclusions include WorkOS SSO (any region), codebase indexing if the repo is stored outside the US, BYOK unsupported under US residency; custom models, MCP, external integrations, Bugbot, shared links, Slack/web-triggered commands have regional limits.

### Models

Access = **union** of Team + Organization Group + Directory Group. Restrict with a tight Team baseline.

Team Settings: Model Access Control — picker list; block provider or model; new models opt-in. Blocking the picker does **not** stop BYOK to a comparable model. Dashboard list is source of truth.

Auto and standard names use Cursor providers under ZDR, limited by model-access policy.

BYOK off keeps usage on Cursor models, ZDR, and the pool. BYOK on: retention per customer-provider agreement; inference bills to customer; Cursor Token Rate may still apply; recorded as user-API-key usage.

Bedrock: prefer IAM role; after Team validates role, per-user Bedrock toggle is off until enabled in Cursor Settings → Models; **only explicit Bedrock model IDs** route to the customer account; Auto/standard names stay on Cursor providers.

### Agents & execution

Local agents run as the user on the workstation — not an extra ACL. Pair with approvals, sandbox, hooks, OS/infra. Classifiers/allowlists reduce prompts; they are **not** security boundaries.

Org-level Run Mode (Enterprise):

- **Auto-review** (recommended): allowlisted immediately; supported shell sandboxed; rest through LLM classifier.
- **Allowlist:** listed without approval; others need review.
- **Run Everything:** no command-approval prompts. Do not treat allowlist as a security boundary.

Per-user command allowlist: `permissions.json` (MDM). Steers auto-run; does not harden the machine.

Sandbox: `sandbox.json` domains and extra r/w paths. Network modes: allowlist-only; allowlist + Cursor package-manager defaults (default); allow-all. Deny > allow. RFC1918, IPv6 private, and `169.254.169.254` blocked by default. Admin + hardcoded rules cannot be weakened by repo `sandbox.json`. Admin network allowlist **replaces** per-repo union. Allowlist `*.cursor.sh` and exclude from SSL inspection.

Protections (keep behind approval): File-Deletion (incl. `rm`); Browser (plus domain allowlist); External-File; `.cursor` directory protection (not an ACL).

MCP: **no** Organization Group widening. Admin patterns, per-server tools, per-server network, whether users may add outside patterns. Active server allowlist blocks non-matching servers.

Extensions: dashboard Allowed Extensions; MDM `AllowedExtensions` overrides. Once the list has an entry, unlisted extensions are blocked unless `"*": true`. Workspace trust off by default; restricted mode breaks AI; not a substitute for repo/execution controls.

Hooks: lifecycle logic (block patterns, scan, reject, record activity audit logs miss). MDM and server-side. Pair with OS/infra for a hard boundary.

Bugbot: automated PR review; not a replacement for human review.

Who can run: restrict CLI agent access and Cloud Agent creators **before** finer guardrails.

### Cloud Agents

Need current Privacy Mode (not Legacy). Set repo access before in-repo permissions. **Protected Git Scopes** bind a Git org/group/namespace to the Cursor Organization for Cloud Agents, Automations, Bugbot. PrivateLink or Cloudflare Tunnel for private GHES/GitLab. Git egress proxy when corporate IP allowlisting is required.

Network egress defaults **allow-all**. Modes: allow-all / default-plus-allowlist / allowlist-only at user, saved-environment, and Team. Team allowlist shared with sandbox defaults; lock per Team.

Environment precedence: repository → personal saved → Team saved. Team env/secrets are admin-sensitive. Snapshots encrypted; 90-day inactivity expiry.

Shared links outlive the creator. Scope automations narrowly; verify runtime, identity, env, network before use.

Restrict who may create Cloud Agents, then configure repo/network/env/retention for that population.

### Self-Hosted Pool

Moves **tool execution** (shell, edits, browser, local MCP, internal services) onto your workers. Loop, planning, inference, UX stay in Cursor cloud. File chunks and artifacts still go to Cursor. **Not air-gapped.**

Worker: long-lived outbound HTTPS; no inbound ports. `agent worker start`; one session at a time; `--idle-release-timeout`; `HTTPS_PROXY` if needed.

Need: Enterprise + Self-Hosted enabled; **service-account API key** (not personal/user/Team/Org keys); cloned repo with least Git creds; egress to published Cursor hosts (e.g. `api2.cursor.sh`, `api2direct.cursor.sh`), artifact upload, Git, package registries.

Fleet: Helm chart / Kubernetes `WorkerDeployment`; or Cloud Run + fleet-summary API. Sessions only hit workers in the **named pool**. Triggers: Slack `self_hosted=true` or `pool=<name>`; GitHub `@cursoragent self_hosted=true` or `pool=<name>`; Linear `pool=<name>` or labels. Team toggles: Allow Self-Hosted Agents / Require Self-Hosted Agents. Public GitHub: only OWNER/COLLABORATOR can route to self-hosted.

Do **not** assume managed Cloud Agent network policy/lock applies to worker-host traffic. If you cannot run the fleet as production infra, use Cursor-managed Cloud Agents.

## Part V — Integrations & collaboration

Controls on one surface do not govern another.

- Protected Git Scopes before Cloud Agents / Automations / Bugbot.
- Private GHES/GitLab: PrivateLink or Cloudflare Tunnel; Git egress proxy (GitHub, GitLab, Azure DevOps, Bitbucket).
- Repository blocklists and mappings are **Team-scoped**.
- Slack/Linear/Jira: govern who can trigger and where it executes. Slack Allow/Require Self-Hosted is audited. Treat chat/ticket triggers as security-sensitive.
- Shared chats/canvases: published links are **not** revoked by member removal.
- Team Rules: enforceable or optional. Enforceable blocks user override but does not make the model deterministic — pair with hooks/approvals/infra.
- Rules, commands, hooks have their own audit event types.

## Part VI — Cost, visibility, accountability

Confirm current prices, seat definitions, and allowances with the account team.

Plans: individual (Pro, Pro+, Ultra), Teams, Enterprise. Enterprise adds SCIM, audit logs, model-access restrictions, repo blocklists, auto-run, browser/network controls, service accounts, Billing Groups, pooled usage, org admin. Do not design around Enterprise controls without entitlement.

Seats: Member and Admin consume; Unpaid Admin does not (identity/security/finance can admin without a seat); service accounts consume **usage not seats**. Each Team needs ≥1 paid user.

Per-seat vs pooled (Enterprise): pooled is one committed amount across the term (not monthly reset). Org-pooled: linked Teams share the committed pool; each Team keeps its own spend settings. On-demand continues usage at applicable rates; on pooled accounts, member limits apply to **total** usage, not only on-demand. Track BYOK separately.

**Required commercial record before spend controls:** plan/entitlements; per-seat vs pooled (Team or Org); on-demand on/off; seat mix including Unpaid Admins and service accounts; BYOK yes/no.

Spend layers (distinct places, specific resolution):

1. Team spend limit
2. Team default per-user limit
3. Member override (beats Team and Group)
4. Group overrides (Directory + Organization Groups): highest applicable; vs Team baseline, highest still wins

Start restrictive Team default; raise via Groups/individuals. Spend alerts email only — they do **not** block. Dynamic spend limits scale with seat count. Limits do not cross sibling Teams.

Admin API examples: `POST /teams/user-spend-limit`, `GET /teams/spend`, filtered-usage-events. Enable administrator-only usage-pricing when exposed so members cannot change Team spend policy.

Analytics (Team + Org): adoption, model usage, AI code metrics, agent activity. Enterprise: Conversation Insights (aggregate-only; SCIM-group filter dashboard-only), AI Code Tracking API, Cursor Blame, Analytics API. Treat as **activity not productivity**. Restrict analytics dashboard to admins if required.

Audit Logs (Enterprise, admin dashboard): security and admin actions, **not** development activity (use hooks for file access/prompts/tool calls). Event types include auth, user management (SSO/invite/signup/auto-enroll/removals/roles/spend-limit), API keys, Team settings (Privacy Mode, spend, usage pricing, name, Slack, repo mappings), Directory Groups, MCP, Team Rules/hooks/commands, Bugbot. Verify a required control has an event before compliance use. Admin API audit requests max **30-day** range. Public docs do not specify underlying retention. Streaming to SIEM/webhook/S3 is **arranged with Cursor**, not self-serve.

## Part VII — Rollout

Dependency order (do not skip):

1. **Identity** — SSO, verify domains, test with >1 admin, break-glass (generic) / Lenovo support restore plan, SCIM user **and** group sync separately. Initial SCIM sync does not remove pre-existing members; user may not appear in Members until first sign-in. Map Directory Group → Organization Group → Team + role. Manual edits to synced rosters are drift.
2. **Privacy** — enforce Privacy Mode per Team; record retention; residency per Team with exclusions. Values do not propagate across Teams.
3. **Models** — restrictive Team baseline; widen via Groups; decide BYOK.
4. **Agents/integrations** — auto-run, protections, sandbox/network, MCP, extensions, Protected Git Scopes, repo blocklists, Cloud Agent repo/network/runtime/env. MCP is its own surface. Choose runtime before relying on a network lock.
5. **Spend** — after representative usage, not during onboarding noise. Billing Groups = attribution only.
6. **Analytics/audit/export** — confirm entitlement, format, retention, Org vs Team scope.

Pilot on real repos, OSes, networks, IdP mappings, models, integrations, admin roles. Define "working" (sign-in/provision/offboard, effective policy, data/model posture, repo/network, support volume, spend, audit, rollback) before expand. Reversible defaults before locks, hard limits, or retention changes.

Before changing a control: read merge/lock; list every level that sets it; blast radius; pilot; confirm on a non-admin; announce; keep rollback unless intentionally irreversible.

### Generic symptom table

| Symptom | Check |
|---|---|
| Sign-in fails | Domain verification, SSO enforcement, IdP assignment, SAML |
| Wrong/missing Team | SCIM status, invites, JIT, membership, Org Group → Team mappings |
| Missing capability | Team baseline never allowed it — Groups cannot widen from nothing |
| IdP vs Cursor drift | SCIM-managed? User **and** group sync? Directory → Org Group → Team → role? Bulk lag? First sign-in? Pre-SCIM leftovers? |
| "Bug" that is merge behavior | Union (models), highest (spend), field-by-field (protections), locks, MCP precedence |
| Integration/network | Auth, repo policy, MCP, marketplace, Cloud Agent access, egress; note runtime + destination + governing policy |
| Billing dispute | Scope, dates, Team, account; spend allowance vs Billing Group attribution |

Escalate with: users/Teams/Groups/repos; timestamps + TZ; expected vs actual; settings + scopes; recent admin changes; repro; errors/request IDs; business impact. Product/ops → official support. Contract/residency/account structure → account contact. Compromise → documented security process including `security@cursor.com`. Never put secrets, tokens, private source, or extra PII in tickets.

Incidents: fold Cursor into existing IR. SSO outage: locate IdP vs SAML vs Cursor membership; surviving admin session; IdP recovery; Cursor if all admins locked out; do not weaken auth except approved time-bound plan; after recovery verify sign-in, review incident changes, preserve logs. Admin loss: Org Admin ≠ Team Admin; keep >1 admin per critical scope. No dedicated read-only security role — use existing Team Admin/Unpaid Admin, audit export, least-scope API key, or SIEM; time-box it. Compromise: contain/revoke first; roster reconcile after.

ROI: cost = seats + usage (incl. service accounts) per **active developer**, not list price per purchased seat. Do not convert acceptances/AI lines into "hours saved" with a fixed multiplier. Track throughput, cycle time, rework/CFR, review load, time to first contribution, sentiment/retention; baseline before rollout; compare pilot vs matched non-pilot. Weekly adoption during rollout; monthly cost vs budget; quarterly outcomes.
