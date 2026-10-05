---
name: cursor-administration
description: >-
  Administer Cursor Enterprise Organizations: identity (SSO, SAML, SCIM, Microsoft Entra, WorkOS),
  Organization vs Team roles, Organization Groups and group-to-team mapping, Privacy Mode and ZDR,
  model access, MCP and agent run policy, Cloud Agents, spend limits, audit, and Lenovo Default IdP
  migration (Merge into default IDP). Use when the user asks about Cursor org admin, the admin
  dashboard, SSO enforcement, SCIM sync, team membership, seats, spend, MDM, Cloud Agents, or
  moving Lenovo teams onto the Organization Default identity provider.
---

# Cursor Administration

Governance and operations skill for Cursor Enterprise. Source documents:

- Cursor Admin Handbook (enterprise controls, where they live, how they merge)
- Lenovo Default IdP Migration Guide (moving remaining teams onto the Organization Default IdP)

This skill covers **admin controls**, not end-user prompting or editor mechanics.

## How to answer

1. Classify the request (see routing below).
2. Read the matching reference **before** giving steps:
   - Controls, inheritance, privacy, models, agents, spend, rollout → [handbook.md](handbook.md)
   - Lenovo team merge / Default IdP / Entra assignment / forced SSO → [idp-migration.md](idp-migration.md)
   - Merge-dialog text, AADSTS50105, SCIM drift → [errors.md](errors.md)
3. Give **Where / Do / Expect** for dashboard actions (page → section → button or field).
4. Flag irreversible or lockout-risk steps **before** the click.
5. If a fact is marked **(Confirm with support)** in the Lenovo guide, do not treat it as dashboard-truth. Require Cursor support's written answer first.
6. Prefer the **identity provider as lifecycle source of truth**. Do not recommend unassigning, disabling, or deleting users in Entra as a Cursor-side cleanup during migration.

## Request routing

| User is asking about | Read |
|---|---|
| What a control does, where it lives, merge/lock behavior | [handbook.md](handbook.md) |
| Org vs Team vs Group vs User; Admin / Unpaid Admin / Member | [handbook.md](handbook.md) |
| Privacy Mode, ZDR, residency, CMEK, `.cursorignore` | [handbook.md](handbook.md) |
| Model access, BYOK, Bedrock/Azure, Auto | [handbook.md](handbook.md) |
| Run modes, sandbox, MCP, extensions, hooks, Bugbot | [handbook.md](handbook.md) |
| Cloud Agents, environments, Self-Hosted Pool | [handbook.md](handbook.md) |
| Seats, pooled usage, spend limits, Billing Groups, analytics, audit API | [handbook.md](handbook.md) |
| Rollout order, change management, generic troubleshooting | [handbook.md](handbook.md) |
| Merge into default IDP, remaining teams, Holding Team, Auto Add | [idp-migration.md](idp-migration.md) |
| Entra SSO app vs provisioning app, AADSTS50105 | [idp-migration.md](idp-migration.md) and [errors.md](errors.md) |
| Forced SSO / "SSO for domain members" / password login | [idp-migration.md](idp-migration.md) |
| Restore after a bad mapping or a failed merge | [idp-migration.md](idp-migration.md) |

Lenovo identity facts **override** generic handbook identity advice when they conflict (see hard rules).

## Operating principles (always)

- **IdP is lifecycle source of truth** for SCIM users and Directory Groups. Cursor owns Organization Groups, Team mappings, mapped roles, and Cursor policy.
- **Govern groups, not individuals.** Attach policy to cohorts.
- **Set data posture before features.** Privacy Mode, model access, residency, and runtime placement are separate decisions.
- **Know default vs lock vs merge.** A default is not a lock. Organization Groups generally **widen** access; some Team/device controls **lock**. MCP does **not** follow Group widening.
- **Pilot, then lock.** Announce impact before enforcement.
- **Observe usage before spend caps.**
- **Teams are flat.** Policy on one Team does not apply to sibling Teams. Set privacy, residency, and spend on **every** Team.
- **Validate effective result** on a real non-admin user, not only the admin UI.

## Hard rules (Lenovo)

These come from the Lenovo Default IdP Migration Guide. Apply them for Lenovo org-admin work even if the generic handbook suggests a simpler path.

1. **Merge is permanent.** `Merge into default IDP` / `Merge into default` cannot be undone from the dashboard. Do not delete anything in WorkOS yourself.
2. **No SSO skip.** There is no emergency password bypass once a domain is forced to SSO. Org Admins cannot turn forced SSO on or off. Only Cursor support can change the WorkOS policy **SSO for domain members**. Do **not** tell the user they can rely on a Cursor-side SSO bypass unless support has confirmed it for this org.
3. **Do not delete the Default SSO connection.** Manage on the Default card's SSO-Provider Connection Settings opens the WorkOS Admin Portal. Deleting the connection cannot be undone, does not help lockouts, and can block remaining merges (E1).
4. **Two Entra apps.** Lenovo has a separate Entra **SSO** app and **provisioning** app for the Default. Assign users and admins in **both**. Nested groups are not supported (AADSTS50105).
5. **Never unassign / disable / delete in Entra** as a Cursor cleanup. That deprovisions. Never change provisioning-app scoping filters during migration.
6. **Don't click Disconnect** on org SCIM. Don't create a second SCIM endpoint if users are already syncing. Don't use WorkOS Danger zone → Delete directory.
7. **Keep Auto Add Users to Root Team OFF.** A SCIM reconnect turns it back on — re-check after any SCIM change. Prefer SSO auto-enrollment **off** so new users join only the mapped team.
8. **Enable sync removes anyone not in the mapped group.** Never pilot by mapping a small group onto a populated team. Get written sign-off on the removal list first.
9. **Role mappings can demote or remove the last team admin.** Leave **Use groups to set role** off unless every admin is in an Admin-mapped group. Org Admins keep org access; they can still lose the team seat.
10. **Two direct Org Admins** whose Org Admin role is set on Organization Members, **not** via a role-mapped group, assigned directly in the Entra SSO app, already on a team listed under the Default card's `Used by:`.
11. **Password login stays until all remaining teams are merged and the forced-SSO checklist is complete.** Ask support to keep **SSO for domain members** at **Not required** until then.
12. **Audit Log does not record mappings or merges.** Keep the change log (template in [idp-migration.md](idp-migration.md)).
13. **Support contacts for Lenovo migration:** Zane Chua (Cursor SA), Tham Weng Yew (TSE), Cursor engineering via support. Security incidents: `security@cursor.com` (no secrets in tickets).

## Dashboard map

Org URLs use `cursor.com/o/<org-slug>/…`.

| Surface | Path |
|---|---|
| Members (Org Admin role, Export CSV) | Organization → Members |
| Groups | Organization → Groups |
| Identity providers (Default card, merge) | Organization → Settings → Identity providers |
| Manage membership sources | Overview → Teams → ⋯ on the team → Manage SCIM |
| Audit Log | `cursor.com/o/<org-slug>/audit-logs` (if enabled) |
| Team Members & spend | Team → Members & Groups → Members (Monthly Limit / On-Demand Limit) |
| Team invite links | Team settings → Team Invite Links |

Only **Org Admins** can edit the Default IdP, SCIM, Organization Groups, and merges. Team Admin / Unpaid Admin is not enough.

## Change-control checklist

Copy and track:

```
- [ ] Named the control, Team/Group/user scope, and merge rule
- [ ] Listed blast radius (Teams, Groups, users, runtimes, integrations)
- [ ] Saved baseline (CSV, spend limits, IdP screenshots) if identity or roster will change
- [ ] Pilot cohort first; reversible default before lock
- [ ] Confirmed effective result on a non-admin user
- [ ] Announced purpose, timing, impact
- [ ] Rollback path exists, or the change is intentionally irreversible and called out
```

For identity merges, also complete the pre-merge gate in [idp-migration.md](idp-migration.md).

## Conflict: handbook vs Lenovo IdP guide

| Topic | Generic handbook | Lenovo |
|---|---|---|
| Break-glass admin | Provision an Org Admin **outside** the SSO-enforced domain before forcing SSO | There is **no** skip-SSO login. Direct Org Admin does not help if SSO breaks. Recovery is support: set policy to Not required **and** disable SSO on every WorkOS org on the domain list (up to 5 minutes). |
| Consolidate team IdPs | Dashboard merge is the recommended approach | Same action, but **permanent**, with Entra dual-app assignment, SCIM mapping, and support-written gates first |

When advising Lenovo, use the Lenovo column.

## What this skill does not do

- Click the Cursor dashboard (no admin API in this workspace unless the user supplies a key and asks).
- Change Entra or WorkOS.
- Invent current product labels, residency exclusions, or contract terms. Confirm with the Cursor account team / Trust Center / DPA when the user is locking policy.

## Additional resources

- [handbook.md](handbook.md) — Organizations model through rollout
- [idp-migration.md](idp-migration.md) — Lenovo Default IdP runbook
- [errors.md](errors.md) — E1–E17 and symptom table
