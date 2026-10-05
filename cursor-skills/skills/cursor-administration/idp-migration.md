# Lenovo: move remaining teams into the Organization Default IdP

Operator runbook from *Cursor — Lenovo Default IdP Migration Guide*. Each step is **Where / Do / Expect**. Screens may differ slightly from Cursor test orgs.

A sentence tagged **(Confirm with support)** depends on a Cursor production setting or Lenovo's WorkOS setup. Get support's written answer (step 2.4) before relying on it.

## Starting state (confirm again before acting)

Recorded as of 25 Sep 2026:

- SSO live on Default IdP (Microsoft Entra, SAML)
- Org-level SCIM connected and syncing
- Root team = **Holding Team**; **Auto Add OFF**
- Password login still works because support keeps WorkOS **SSO for domain members** = **Not required**
- Remaining teams (Team A–E) move via Organization Groups, group-to-team mapping, then **Merge into default IDP**

Section 2 verifies this still holds.

## Warnings (read before any change)

**W1 — Merge is permanent.** Moves members' WorkOS memberships to Default and removes the team's IdP record in Cursor. Do not delete anything in WorkOS yourself.

**W2 — Entra assignment.** Assign every user and every admin of a team to **both** Cursor apps (SSO + provisioning) before that team's merge (3D) and before forced SSO. Nested groups unsupported → AADSTS50105. Direct assignment or a directly assigned group only.

**W3 — Role mappings.** If a mapping sets a role, every sync applies it. A team admin (Org Admins included) not in an Admin-mapped group gets the highest role of their groups (Unpaid Admin, else Member). Org Admins still have org admin access to the team. Even with **Use groups to set role** off, a team admin in **no** mapped group is **removed**. Cursor will not stop demoting/removing the last team admin.

**W4 — Last-team SCIM removal.** Removing someone from the Entra group mapped to a Synced team removes them from the team; last team → leave Organization, lose seat, signed out. Direct Org Admin keeps Organization access (Members may show **No team** / None). Entra delete/disable/unassign hits Cursor as deactivation: removed from directory's own team and Synced mapped teams; **Manual** teams keep them. Permanent Entra delete (30 days, or immediate from recycle bin) then removes even Manual teams and Org Admins — including the last Org Admin. After disable/unassign of an Org Admin, also **Remove from Organization** on Members. Recheck Members after the next Entra cycle and after permanent delete.

**W5 — Per-user spend limits.** Org API `destinationTeamId` or CSV move deletes old team membership and **drops** that team's per-user limit (Monthly Limit / On-Demand Limit). Organization Group spend limits are not carried/restored on group leave/rejoin. If SCIM removes then re-adds to the **same** team within 30 days, the per-user limit restores; invite/SSO/dashboard/API/CSV or >30 days does not. Record all per-user and group limits in 1.3.

**W6 — No skip-SSO.** Admins cannot toggle forced SSO. Cursor does not check that an Org Admin can still sign in before SSO on, domain verify, forced SSO, or merge. No admin password bypass once a domain is forced. Only support changes **SSO for domain members**. Do not delete the Default SSO connection from WorkOS Admin Portal (blocks remaining merges, E1). Keep policy **Not required** until all remaining teams are moved. If SSO breaks: support sets policy **Not required** **and** disables SSO on **every** WorkOS org Cursor's sign-in page checks for the domain (up to 5 minutes). Direct Org Admin does not help if SSO is down. Permanent Entra delete of the admin removes the role (W4).

## 1. Prerequisites

### 1.1 Confirm Org Admin

- **Where:** `cursor.com/o/<org-slug>/members`
- **Do:** Find your row.
- **Expect:** Role = **Org Admin**. Team Admin / Unpaid Admin cannot edit Default IdP, SCIM, Organization Groups, or merges.

### 1.2 Two direct Org Admins

- **Where:** Organization Members; Entra → Cursor SSO app → Users and groups.
- **Do:** Two Org Admins whose org role is set **directly** on Members; keep them **out** of role-mapped groups; assign both **directly** in the Entra SSO app. Both fully sign out, then SSO sign-in. Do this **before the first merge**. Pick admins already on a team under Default card **Used by:** (e.g. Holding Team) — a still-separate team IdP does not test Default.
- **Expect:** Direct org role survives group-mapping team removal (W4). Does **not** survive SSO outage (W6) or permanent Entra delete (W4). Agree with support how they restore password login (5.2). Nobody unassigns/disables/deletes these two in Entra during migration.

### 1.3 Baseline + change log

- **Where:** Members → Export CSV; each team Members & Groups → Members (download; Monthly / On-Demand Limit); each Organization Group → Members (Spending limit); Settings → Identity providers; each team's Manage membership sources.
- **Do:** Export org members (includes Role). Export Team A–E rosters. Record every per-user and group spend limit. Screenshot each IdP card and each Manage SCIM dialog. Start the change log (below). Audit Log does **not** record mapping changes or merges; it does show members sync adds/removes (actor = SCIM).
- **Expect:** Files to restore from. CSV restore brings everyone back as **Member** — you need recorded roles.

## 2. Starting-state checks (look only, except 2.3 auto-enrollment)

### 2.1 Default SSO active; domains complete

- **Where:** Settings → Identity providers. **Default card** = card with Default badge. Rows: SSO-Provider Connection Settings; Domain Verification Settings (`Configure` → WorkOS).
- **Do:** Default SSO status Active; **Manage** shows the connection active. Before each merge, note domains on the **team's** SSO connection; those domains must also be on Default's SSO connection and verified in WorkOS + Entra. Check every domain users actually sign in with.
- **Expect:** One Default badge; each card lists teams under **Used by:**. Card **Active** + button **Manage**. Active only means an SSO connection exists — still verify under Manage. Domain listed on the **card** is not enough. **Setup required** / **Disabled** / **Configure** → stop (merge refused, E1).

### 2.2 Org SCIM connected

- **Where:** Default card → SCIM Directory.
- **Do:** Read status. In Entra provisioning app: Mappings → Microsoft Entra ID groups **enabled** (E11).
- **Expect:** Manage Mappings, Sync Directory, Configure in WorkOS, Directory ID, "Organization-scoped directory", Last synced, Disconnect. **Do not Disconnect.** Do not Delete directory in WorkOS. If no Directory ID / offers Connect directory while users sync: **do not** Sync/Connect/create a new endpoint — screenshot to support. Expired SCIM token shows **no** Cursor warning. Last synced = last finished **group-mapping** sync, not each Entra cycle. Check daily; if stuck or "Not synced yet" after mappings, screenshot (E12).

### 2.3 Root Auto Add OFF; turn SSO auto-enrollment OFF

- **Where:** Default card → Auto Add Users to Root Team (newer: "Auto add users to root team"; older: "Sync directory users to root team"). SSO auto-enrollment is just below.
- **Do:** Confirm Auto Add **off**; leave it off. Record SSO auto-enrollment state, then **turn it off** (this is the one section-2 change) and log it. Support advises both off so new users join only the mapped team (E10). After any SCIM change, re-check Auto Add (reconnect turns it **on**).
- **Expect:** Mappings decide team, not Auto Add. Turning Auto Add off does not by itself stop Holding Team adds (SSO auto-enrollment, mappings owned by holding team, domain join, invites, admin moves). If **both** toggles are off, a person with no team seat and no pending invite cannot SSO in ("You are not a member of this team…"). Existing members, pending invites, and direct Org Admins still can. From then on, provision new users from Entra into a Synced team **before** first sign-in. If unexpected people keep appearing on Holding Team, **stop** and tell support.

### 2.4 Written confirmations from support (Zane or TSE)

No dashboard setting. Get written answers:

1. **SSO for domain members** = **Not required** on Default WorkOS org **and** each remaining team's WorkOS org (ask by name). WorkOS turns password off when SSO is first set up unless support changed it. Not visible in Cursor or WorkOS Admin Portal.
2. List of WorkOS orgs Cursor's sign-in page checks for the email domain, and that Cursor has **no** hand-set sign-in rule for the domain. Commitment: if SSO breaks, they set policy Not required **and** disable SSO on every org on that list (W6, 5.2).
3. Only if SSO auto-enrollment toggle is missing: support surfaces it so you can turn it off (2.3). If the toggle shows, skip.
4. Group sync is on for Organization Groups (Cursor-wide, not in dashboard). If off, Synced groups do not pick up Entra members (3B.4 mismatch, 3C mapping stale, Last synced "Not synced yet").

Expect: all answered; password sign-in still works for Lenovo users.

### 2.5 Merge control + invite links

- **Where:** Settings → any **non-Default** card ⋯ menu (`Merge into default IDP` or `Merge into default`). Each remaining team + Holding Team → Team Invite Links.
- **Do:** Confirm merge item exists. Record **Allow members to invite teammates**.
- **Expect:** Merge listed ⇒ Cursor has merging on (global flag). If missing and no merge running, ask support when it will be (E16). If the invite switch exists, restrict to admins (E14); if not, members can create links — note unknown links in baseline.

## 3. Move each remaining team (one at a time; smallest first = pilot)

Team A–E still have their own IdP card. **Merge into default IDP** is the only move. Per team: prepare (3A) → Organization Group (3B) → map (3C) → merge (3D).

Never pilot by mapping a small group onto a team that already has members — **Enable sync** removes everyone not in the group.

### 3A Prepare

**3A.1 Pilot.** Smallest remaining team first. Assign 3–5 of its users in Default Entra **SSO** app. Pre-merge sign-in still uses the team's own IdP — not a Default test. Immediately after 3D, those users full sign-out + SSO. Expect: right team, no wrong org picker, right spend limit. Keep password login (2.4) until pilot is clean for **one full day** before the next team.

**3A.2 Entra both apps.** Assign Team A's Entra group **and every Team A admin** in SSO app and provisioning app. Never unassign groups or change scoping filters.

**3A.3 Roster vs Entra.** Export Team Members vs Entra group. Cursor matches SCIM by **email**. Anyone on the team not in the group will be removed at 3C.3 (and leave the Organization if last team). Written sign-off from Lenovo team owner on removals, or empty list.

**3A.4 Disconnect team SCIM + domain join *before* any mapping.** If the team is already under Default **Used by:**, skip 3D. Else ask support to **deactivate the team's own SCIM** (they delete that team's WorkOS directory). WorkOS sends one directory-deleted event (not per-user deletes); Cursor drops that directory's groups/mappings but **keeps members**. Turn off domain join / auto-join (Edit). If the card shows SSO Active, that row may be hidden — ask support to confirm auto-join off. If team-owned SCIM or auto-join still active, merge refused (E2, E3). Do this **before** another membership source exists (3C), or Cursor would recheck the roster and drop anyone missing.

### 3B Organization Group

**3B.1** Groups → Add → **exact Entra group name**, Type = **Manual**, Create. (Empty Manual first; name alone does not prevent duplicates.)

**3B.2** Assign group in provisioning app; Provision on demand (up to 5 members). Entra cycles typically 20–40 minutes.

**3B.3** Group → Settings → SCIM directory group → Connect. If two rows, pick the **upper org-scoped** row; ask support to remove stale lower copy.

**3B.4** Members tab count vs Entra. Do not continue with unexplained gaps (no Cursor account yet, email mismatch).

### 3C Map group to team

**3C.1** Overview → Teams → ⋯ → Manage SCIM → Membership Type = **Synced** → + Add source → that Organization Group. One group to one team. Only Organization Groups can be sources.

**3C.2 Roles (read W3).** Leave **Use groups to set role** **off** unless every admin is in an Admin-mapped group. Off: members added as Member; dashboard can still change roles; **admins not in the group are still removed**. Off also requires picking **Team admin** before save — that person becomes admin, previous admin becomes Member. Pick someone **in the group**. On: at least one group must be Admin or save is refused; roles greyed out in dashboard.

**3C.3 Enable sync.** Recheck signed-off removal list. Removals start **15 minutes** after the newest mapping. Switching back to Manual (5.1) stops further removals but does **not** add people back. Direct Org Admin who loses their only team keeps Organization access.

### 3D Merge (permanent)

**3D.1 Pre-merge gate (every merge):**

- [ ] Team card: no active SCIM; auto-join off (3A.4)
- [ ] Both direct Org Admins signed out + fresh SSO since last merge; still Org Admin
- [ ] Support written answers (2.4) and 2.5 checks done
- [ ] Every domain on team's SSO connection is on Default SSO (2.1)
- [ ] If engineering flagged this card as leftover team IdP, they signed off

**3D.2** Team card → Merge into default IDP / Merge into default → fix red blockers (Configure SSO, Verify domains, Manage SCIM, Manage directory) → reopen. Expect no blockers; notes that it can't be undone and may take a few minutes. Menu only on non-default card, only when no merge running, only if merging is enabled. Blocker texts: [errors.md](errors.md) E1–E5, E15. E16/E17 appear **after** Start merge.

**3D.3** Tick "I understand this can't be undone…" → **Start merge**. PERMANENT. Card shows Merging… and settings lock. Does **not** sign people out. Next sign-in uses Default. Staying signed in is **not** an SSO test.

**3D.4** Refresh Identity providers. Success: team's own card gone; team under Default **Used by:**. Failed merge shows **no error** — Merging… vanishes and old card remains; ask support for last error before retry. Stuck Merging… well past "a few minutes": **do not retry** (E6). Send org, source/destination team IDs, IdP, start time, screenshot.

## 3E Forced SSO (only after all remaining teams)

- [ ] Every user on every verified domain, every team (incl. Holding Team and teams outside this guide), assigned **directly** in Entra SSO app; no AADSTS50105 in Entra sign-in logs for Cursor SSO
- [ ] Both direct Org Admins fresh SSO after last merge; still Org Admin
- [ ] Support confirmed which WorkOS orgs get Required, and which other orgs the sign-in page checks (2.4)
- [ ] Named Lenovo migration owners (agreed with Zane) written go-ahead; rollback people (section 5) available while support changes the policy

Only then support sets **SSO for domain members** = **Required**.

## 4. Verify after each team's merge

**4.1** Team Members vs Entra vs baseline. Members tab can show someone after a source adds them, even before sign-in. No source → not on the tab. Org Admin rows on a team cannot be edited/removed there; Org Admins keep admin access to every team.

**4.2** Test user: add to Entra group → Provision on demand or wait 20–40 min → Entra Provisioning logs (P1/P2) → appears in Organization Group and on Team. Remove from Entra group → removed from Team.

## 5. Rollback

Merge cannot be undone from the dashboard. "Rollback" = stop before merge, or restore via support from 1.3 checkpoints.

**5.1 Before merge — mapping:** Manage SCIM → Membership Type **Manual** → Save. "Saving will stop future group sync. Current team members and roles will remain." Already-removed people are **not** restored. After Manual, Entra add does not put them back. Re-add via dashboard, Org API (≤500/request), or Import CSV on Organization Members (≤10,000) — **only if still in the Organization**. Org-removed people need support. Do not start 3D on other teams; freeze mappings while diagnosing.

**5.2 SSO broken:** Support sets **SSO for domain members** = Not required **and** disables SSO on every WorkOS org linked to the email domain (Default, unmerged team orgs, others from 2.4). Already-signed-in users stay in. Up to 5 minutes. Not enough if Cursor has a hand-set domain sign-in rule (2.4).

**5.3 After merge:** Support cannot undo. Moving a team back out of Default is an engineering request and might be impossible. Synced teams: restore membership via Entra group. API/CSV only on **Manual** teams and only for people still in the Organization. CSV move = exactly one team, **Member** role. Re-enter group spend limits from 1.3. Per-user team limit auto-restores only if SCIM re-adds to the **same** team within 30 days (W5).

Contacts: Zane Chua (Cursor SA), Tham Weng Yew (TSE), engineering via support.

## Appendix 1 — Optional (not required for this migration)

**O.1** Overview → + Add team visible only if contract allows team creation; disabled at cap. Linking existing teams is Cursor provisioning. All five Lenovo in-scope teams are already linked.

**O.2** New team: Identity provider = **Organization IDP** (not New team IDP), Membership Type Synced, group's source. Appears under Default **Used by:**.

**O.3** `GET /organizations/members` with Org API key `members:read` / Members (read-only); `pageSize` ≤ 200. Compare teams to baseline + change log.

## Appendix 2 — SCIM group-to-team chain

```
Entra group --SCIM--> directory group (read-only in Cursor)
  --> Organization Group (Synced)   [Groups > Add, then Settings > Connect]
  --> Team membership source ± role [Overview > Teams > ⋯ > Manage SCIM]
```

- Entra decides group membership. Teams, mappings, roles are Cursor. Entra role attributes do not sync.
- Connecting directory group → Organization Group alone puts **no one** on a team. Need a membership source (or Auto Add to root).
- Several sources: roster is **union**. Highest mapped role wins (Admin > Unpaid Admin > Member). Role mapping can raise or lower.
- One mapping ⇒ sync owns the whole roster; manual edits disabled. Removing a source while still Synced recalculates; people in no remaining source drop at next sync. Newest mapping: removals wait until it is **15 minutes** old; removing a source does not restart that wait. Cannot save Synced with zero sources — switch to Manual (keeps current members).
- Auto Add off: SCIM user with no mapping has a Cursor identity but no team; not on Organization Members until mapping, invite, or sign-in.
- One IdP connection = one SCIM directory.
- Org API `POST /organizations/team-memberships/sync`, CSV, UI: for SCIM teams change **Entra**. Once a team has a membership source, API/CSV fail: *"This team's membership is managed by your SCIM directory. Add or remove members through your identity provider."*

## Change log template

| Date/time (SGT) | Team | Change | Done by | Before (file/screenshot) | Check after | Result / notes |
|---|---|---|---|---|---|---|
| | | | | | | |

## Support background questions

- Is the team's old WorkOS organization deleted after merge? Cursor-side retire setting is **off by default**. Do not delete in WorkOS (W1).
- Is Organization Audit Log on? `cursor.com/o/<org-slug>/audit-logs`. Does not record mappings, merges, or WorkOS SSO/domain/token events.
