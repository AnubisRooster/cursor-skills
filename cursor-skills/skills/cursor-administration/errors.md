# Cursor admin errors and symptoms

Quoted merge-dialog texts (E1–E6, E15–E17) are exact product messages from the Lenovo Default IdP Migration Guide. Merge blockers (E1–E5, E15) show in red in **Before you start**. E16/E17 appear after **Start merge**.

## Merge and identity (Lenovo)

| ID | Symptom | Likely cause | Fix |
|---|---|---|---|
| E1 | "Organization-level identity provider has no active SSO connection; configure SSO before merging" or "Organization-level identity provider's SSO connection is missing verified domains required by the source: {domains}" | Default SSO inactive, or a domain on Team A's SSO connection is missing from Default's SSO connection. Skipped if Team A's IdP has no active SSO. | Make Default SSO active; add each team SSO domain to Default (idp-migration 2.1). Reopen dialog. |
| E2 | "Source identity provider has an active SCIM connection; remove or deactivate it in WorkOS or the identity provider before merging" | Team SCIM still active on the source card | Support deactivates the team's own SCIM (3A.4). Remove link on a team group does **not** clear it. Do not unassign/disable/delete in Entra (W4). |
| E3 | "One or more teams on this identity provider use domain join (auto-join); merging domain-join teams is not supported yet…" | Domain join / auto-join on for a source team | Turn off domain join for that team (3A.4). |
| E4 | "Organization-level identity provider has an active WorkOS SCIM directory without an active Cursor routing record; disconnect or reconnect SCIM before merging" | Default WorkOS SCIM directory has no matching active routing record in Cursor | **Stop.** Screenshot to support/engineering. **Do not** disconnect or rebuild org SCIM despite the message. Reconnect also turns Auto Add back on (2.3). |
| E5 | "Organization-level identity provider requires a user directory; disable the user-directory requirement (or provision the source's users into the directory) before merging" | Default requires a user directory | Ask support. Unless they say otherwise, provision Team A's users into the directory before merge. |
| E6 | Card stuck on Merging… ("A merge into the default identity provider is in progress. These settings are locked until it completes.") | Background job pending or retrying | **Do not retry.** Send org, team IDs, IdP, start time, screenshot. No dashboard timeout. Retrying merge keeps the badge until finish or fail. Failed merge: badge gone, old card remains (3D.4). |
| E7 | WorkOS: domain already claimed | Domain verified on another IdP or WorkOS org | Do **not** remove the domain yourself. Support removes it there and verifies on Default **together with** the merge — removing it can kill sign-in for that IdP's users until merge. |
| E8 | AADSTS50105 ("The signed in user isn't assigned to a role for the signed in app") | User not **directly** assigned to Entra SSO app | Assign directly (not nested group). User signs in again. Delay is Entra; Cursor adds no wait. |
| E9 | User not on Team A after SCIM | No membership source; email mismatch; not assigned to provisioning app | Group as source (3C). Match Cursor email to Entra. Assign user to provisioning app itself. |
| E10 | New users land on root / Holding Team | Auto Add on (reconnect turns it on); SSO auto-enrollment on for someone with no team seat; holding-team mappings/groups; domain join; invites; admin moves; stale team-level directory | Auto Add **and** SSO auto-enrollment off on Default card. Re-check Auto Add after any SCIM change. Put target team Synced with their Entra group, provision from Entra. Remove holding-team mappings. Support soft-deletes duplicate directory. If still happening, tell support. |
| E11 | Groups don't appear | Groups mapping off in Entra provisioning, or group not assigned | Enable Microsoft Entra ID groups mapping; assign group; Provision on demand. |
| E12 | Entra Test Connection fails / SCIM token rejected, or Last synced stuck / "Not synced yet" after mappings | Wrong tenant URL (team vs org); expired/revoked token (no Cursor warning); Cursor not finishing group-mapping sync | Stuck Last synced only: screenshot to support (2.2). Use **org Default** SCIM endpoint. Rotate token in WorkOS Admin Portal from Default SCIM **Configure in WorkOS**: generate second token, update Entra, confirm Last used, then revoke old. |
| E13 | Admin lost role, or roles greyed ("Role managed at the organization level") | Use groups to set role on and admin not in Admin-mapped group; admin in no mapped group (removed); role-setting mapping demoted them (Org Admins included) | Add admin to Admin-mapped group, or turn Use groups to set role off. Dashboard cannot edit mapped roles. |
| E14 | People join by invite link, bypassing SCIM | Members can create invite links | Team settings → Team Invite Links → off **Allow members to invite teammates** if present (2.5). Else revoke links you did not create. |
| E15 | Other red merge-dialog errors: IdP unavailable/deleted; source not found; source shared with another organization; org has no org-level IdP; cannot merge org-level IdP into itself | Stale page; already merged; team IdP shared outside org; no Default; merge started from Default card | Refresh and reopen. If card gone, check Default **Used by:**. For "into itself", use the team's **non-default** card. Other messages: stop, screenshot, support/engineering. |
| E16 | "Organization identity provider merge is not enabled" (after Start merge) | Cursor has not turned merging on | Ask support when it will be on (2.5). |
| E17 | "A merge for this identity provider is already in progress" (after Start merge) | Merge already queued/running | Do not retry. Wait. If Merging… persists past a few minutes, E6. |

## Generic handbook troubleshooting

Capture first: time + time zone, affected users/cohorts, Team and Group membership, expected vs actual, recent admin changes.

| Symptom | Check |
|---|---|
| Sign-in fails | Domain verification, SSO enforcement, IdP assignment, SAML |
| Signed in but wrong/missing Team | SCIM, invitations, JIT, Team membership, Organization Group → Team mappings |
| Right Team, missing capability | Team baseline never allowed it — Groups cannot widen from nothing |
| IdP vs Cursor drift | SCIM-managed? User **and** group sync on? Directory Group → Organization Group → Team → role? Bulk lag? First sign-in before Members visibility? Pre-SCIM leftovers? |
| Apparent "bug" that is merge behavior | Models = union; spend = highest applicable; protections field-by-field; locks override users; MCP has its own precedence |
| Integration or network | Authorization, repo policy, MCP, marketplace, Cloud Agent access, egress. Note runtime, destination, governing policy |
| Usage/billing dispute | Scope, date range, Team, account. Spend **allowance** vs Billing Group **attribution** |

Escalation packet: affected users/Teams/Groups/repos; timestamps + TZ; expected vs actual; settings + scopes; recent admin changes; repro steps; errors / request IDs / log excerpts; business impact.

- Product/operations → official Cursor support
- Contract, residency, account structure → account contact
- Suspected compromise / exposed credentials → security process including `security@cursor.com`
- Never include secrets, tokens, private source, or unnecessary personal data
