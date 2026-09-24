---
name: glean-setup
description: Complete guide for setting up Glean workspace, SSO (Azure AD, Okta, Google), people data sync, connectors (SharePoint, Teams, OneDrive, Outlook), RBAC, and security. Use when setting up, configuring, or troubleshooting Glean for your organization.
disable-model-invocation: true
---

# Glean Setup

Complete setup guide for Glean workspace administration covering SSO, people data, connectors, RBAC, and security.

## Setup Overview

Glean deployment follows 4 stages:

1. **Pre-deployment** — Identify connectors, approvals, SSO, people data, timeline
2. **Stage 1: Create workspace** — Admin console, SSO, connectors, people data sync
3. **Stage 2: Prepare workspace** — Review crawled content, validate people data
4. **Stage 3: Go Live** — Branding, rollout
5. **Stage 4: Get the most out of Glean** — More connectors, agents, content population

**Timeline:** 1-3 weeks standard; 3-4+ weeks for large orgs.

## Deployment Models

- **Glean Hosted** (SaaS): Glean manages everything. Choose for simpler setup, auto-scaling, simpler pricing.
- **Customer Hosted** (GCP/AWS): Glean managed in your cloud. Choose for data residency, raw log access, cloud spend optimization. NOT traditional self-hosted — Glean still operates it as SaaS.

## Key Concept: No User List Required for SSO Setup

**You do NOT need a list of users to set up Azure/Entra ID access for Glean.** SSO uses app registration, not individual user provisioning.

**What you need instead:**
1. Azure permissions: Global Admin, Application Admin, or Cloud Application Admin
2. Email **domains** (e.g., `company.com`) — not individual emails
3. App registrations created in Azure AD

Users get access automatically if their email domain matches an approved domain. Optional: restrict via "Glean Users" security group.

## Stage 1: Admin Console Access

Navigate to [app.glean.com/admin](https://app.glean.com/admin). Before SSO activation, sign in via magic link (single-use, 15-min expiry).

### Get Tenant Backend Domain
Find your tenant ID from:
- **Admin Console → Platform → Connectors → Add App** (webhook section)
- URL pattern: `tenant_id-be.glean.com`

### Administrator Roles

1. **Setup Admin** — SSO setup, connectors, crawls, Indexing API tokens only
2. **Admin** — Full workspace settings, RBAC, feature config, API tokens (except global)
3. **Super Admin** — All Admin + sensitive content search, DLP, AI security. Requires written CISO/VP authorization via Glean support. Disabled by default.

### Add Administrators
During first sign-in, optionally add additional admins. Roles are hierarchical — Admins cannot downgrade/remove Super Admin.

## SSO Configuration

SSO is mandatory. Glean supports OIDC (preferred) and SAML 2.0.

### Email Domain Registration
**Critical:** Glean restricts authentication to pre-approved email domains. Notify Glean support of all domains your users will authenticate from. SSO fails if domain isn't registered.

### Microsoft Entra ID (Azure AD) — OIDC

**Prerequisites:** Global Admin, Application Admin, or Cloud Application Admin + Admin/Setup Admin in Glean + tenant backend domain.

#### Azure Steps:

1. **Create app registration** (`Glean SSO`):
   - Name: `Glean SSO`
   - Supported account types: Single tenant only
   - Redirect URIs: `https://<tenant_id-be.glean.com>/authorization-code/callback?isExtension=1` and `https://<tenant_id-be.glean.com>/authorization-code/callback`

2. **Configure delegated permissions**: `openid`, `email`, `offline_access`, `profile`

3. **Grant admin consent** (via Enterprise Applications)

4. **Create client secret** (24-month expiry; value shown only once)

5. **Get IDs**: Application (client) ID + Directory (tenant) ID

6. **(Optional) User restriction** — Create "Glean Users" security group, then assign under Enterprise App → Users and groups → Assignment required = Yes. **Glean recommends NOT restricting by default.**

#### Glean Admin Console Steps:
1. **Users & permissions → Single sign-on (SSO)** → Select Azure SSO
2. Paste: Client Secret, Client Secret Expiration Date, Application ID, Directory ID
3. Click Save
4. Activate: Click "Switch to Azure SSO" (after workspace provisioning)

#### CWS Mode Notes:
- Before workspace provisioning, admins use magic links (SSO can be configured but NOT activated)
- Add `https://apps-be.glean.com/central_sso/authorization-code/callback` for verification
- After provisioning, replace with tenant-specific callback URIs

### Troubleshooting (Entra ID)
| Error | Fix |
|---|---|
| SSO code exchange failed (Code 13) | Verify Directory ID, Application ID, Client Secret |
| Cannot authenticate (Code 14) | Ensure Email, First Name, Last Name, Department, Title populated in Entra ID |
| "You can't get there from here" | Amend Conditional Access policy to include Glean SSO app |
| "Need admin approval" | Grant admin consent for all permissions |
| Stuck at login after SSO success | Notify Glean support of ALL email domains used |
| Internal server error after SSO | IP restrictions — allowlist Glean static IPs (see Network Security below) |

### Google Workspace — OIDC
1. OAuth consent screen: Internal app, authorized domain `glean.com`
2. Create OAuth client ID: Web app, origins `https://app.glean.com`, redirect URIs for both callbacks
3. In Glean: Select GSuite, paste Client ID + Secret
4. Activate SSO

### Okta — OIDC (API Token Method)
1. Create temporary API token: Security → API → Tokens → Create token
2. In Glean: Enter Okta domain + API token → Create Connector App
3. **Revoke API token after setup**
4. Activate SSO

### Okta — SAML
1. SAML app fields: SSO URL `https://<tenant_id-be.glean.com>/authorization-code/callback`
2. Audience URI: `https://<tenant_id-be.glean.com>`
3. Name ID format: `emailAddress`
4. Name attribute: `${user.firstName} ${user.lastName}`
5. Optional SCIM provisioning: Admin Console → Platform → Connectors → Oktra SCIM (bearer token + base URL in Okta)

## People Data Sync

**SSO ≠ People Data.** SSO authenticates users but does NOT populate user profiles, org chart, or directory. People data must be synced separately from a directory source or CSV.

### Supported People Connectors
| Connector | Required | Notes |
|---|---|---|
| Okta | Super Admin access | Custom attribute mapping |
| Entra ID | Global/App/Cloud App Admin | Fixed mapping; contact support for non-default |
| Google Drive | Google Workspace admin | Same connector for docs + people |
| Workday | As configured | Same connector for docs + people |
| CSV | Manual upload | Required fields only; not for ongoing use |

### Required User Fields
- **Required:** First name, Last name, Email, Department
- **Recommended:** Title, Manager email (required for org chart), City, Country, Start date

### Sync from Entra ID (Azure AD) — People Data
This is a **separate** app registration from SSO.

1. Create app: Name=`Glean People`, Single tenant, no redirect URI
2. **Application permissions** (NOT delegated): `User.Read.All`, `GroupMember.Read.All`
3. Grant admin consent
4. Create client secret (copy value — shown once)
5. Get Application ID + Directory ID
6. In Glean: **Users & permissions → People data → Select Azure** → paste Client Secret, Application ID, Directory ID
7. Optional: Add additional user fields (23 available including upn, manager, officeLocation, etc.)
8. Enable crawl and Save

**Initial sync:** 2-4 hours. Updates: ~1 hour.

### CSV Upload
- **Required:** `first_name`, `last_name`, `email`, `department`
- **Recommended:** `title`, `manager_email`, `city`, `state`, `country`, `start_date`
- Re-upload needed for every change

### User Aliases & Identity Stitching
Glean stitches accounts using aliases from IdP attributes. For Entra ID:
- `userPrincipalName` → Primary email (default)
- `mail` → Alias (can promote to primary via support flag)
- `proxyAddresses` → Aliases (admin-controlled, default)
- `otherMails` → Aliases (opt-in, user-editable — security risk)

Avoid user-editable attributes (`otherMails`, `secondEmail`) for aliasing due to spoofing risk.

## Connectors

### Microsoft 365 Suite Architecture
- SharePoint, OneDrive, Outlook are child connectors of a parent Microsoft 365 connector
- ONE app registration in Entra ID serves the whole suite
- **Certificate authentication required** (client secrets NOT supported; Azure ACS retired April 2026)

### Microsoft 365 Setup
**App permissions (Application type):**
- Microsoft Graph: `User.Read.All`, `GroupMember.Read.All`, `Member.Read.Hidden`, `Reports.Read.All`
- SharePoint: `Sites.FullControl.All` (Graph + SharePoint REST)
- OneDrive: `Files.ReadWrite.All`
- Purview sensitivity labels (optional)

**Generate certificate (OpenSSL):**
```bash
openssl genrsa -out tempprivatekey.key 2048
openssl pkcs8 -topk8 -inform PEM -outform PEM -in tempprivatekey.key -out privatekey.key -nocrypt
openssl req -new -key privatekey.key -out request.csr
openssl x509 -req -days 365 -in request.csr -signkey privatekey.key -out certificate.crt
```

Certificate format: PEM with `BEGIN CERTIFICATE`/`END CERTIFICATE` and `BEGIN PRIVATE KEY`/`END PRIVATE KEY`.

**For tenants >1,000 users:** Add 1-10 additional app registrations with same permissions for faster crawls.

### SharePoint Connector
**3 capabilities:** Indexed connector, real-time search, read/write tools.

**Required Graph API permissions:**
- `User.Read.All` — Identity mapping
- `GroupMember.Read.All` — Group membership for permissions
- `Member.Read.Hidden` — Hidden group membership
- `Sites.FullControl.All` — Required by Microsoft for permission change events (Glean has NO write capability)
- `Files.ReadWrite.All` — Webhook reauthorization only
- `Reports.Read.All` — Crawl monitoring

**Constraining access:**
1. Glean-side crawl restrictions (Site URLs, Entra ID Group Object IDs, usernames)
2. Microsoft IP restrictions via Conditional Access (requires Entra Workload ID license)
3. Microsoft Purview audit monitoring
4. **Do NOT use Sites.Selected** — degrades quality, 24h sync limit, stale permissions

**Draft content:** Minor versions, checked-out items, pending moderation, and version <1.0 are NOT indexed by default.

### Microsoft Teams Connector
**Standalone** — own Azure app registration.

**Indexed:** Channel messages (incl. private), group chat messages, team/channel membership. **Opt-in:** Private/meeting chats, meeting transcripts.

**Required Application permissions:**
- `Team.ReadBasic.All`, `ChannelSettings.Read.All`, `ChannelMember.Read.All`, `ChannelMessage.Read.All`
- Optional: `Chat.Read.All`, `Calendars.Read`, `OnlineMeetings.Read.All`, `OnlineMeetingTranscript.Read.All`

**Meeting transcripts:** Requires Microsoft application access policy on the Glean app ID. Apply with `Grant-CsApplicationAccessPolicy -Global`. Can take 24-48 hours.

### OneDrive Connector
Child of Microsoft 365 suite (inherits credentials). Certificate auth only. Same 3 capabilities as SharePoint.

### Outlook Connector
Indexes most recent 5,000 messages per user. Real-time mode optional for overflow. Uses its own app registration. Requires `Mail.Read` permission.

## RBAC and Role Management

### Group-Based Permissions
Supported IdPs: Azure AD, Google Groups, Okta. Max 1,000 groups. OIDC sync: up to 3 hours.

**Process:**
1. **Admin Console → Users & permissions → User roles → User group permissions**
2. Select IdP, click "Add mapping", search for group, assign roles
3. Save changes

**Note:** Group-derived roles are read-only in Glean — must change at IdP.

### Moderator Permissions (per-feature)
- Announcements, Answers, Collections, Go Links, Pinned Results, Teams, Verification moderators

### Special Access
- **Insights Moderator** — Insights dashboard + CSV exports
- **Billing Moderator** — Credits dashboard
- **MCP Server Moderator** — Manage MCP servers, view MCP insights
- **Admin Search** — Search all company docs (requires Super Admin)
- **Sensitive Content Moderator** — DLP findings (requires Super Admin)

## Security & Network

### Static IPs to Allowlist
```
104.154.230.46/32
35.239.35.180/32
34.120.39.18/32
34.144.241.72/32
34.120.90.191/32
34.120.148.20/32
34.111.103.238/32
34.160.40.155/32
98.89.71.36/32 (AWS deployments)
```

### Best Practices
1. Enforce SSO + MFA + SCIM deprovisioning
2. Least-privilege RBAC: Setup Admin for SSO/connectors, Admin for config, Super Admin for security only
3. IP allowlisting if needed
4. Certificate credential rotation on schedule
5. Phased connector rollout with test groups
6. Pre-launch sensitivity scans (Glean Protect/Protect+)

## Connector Refresh Rates
- **Real-time/webhooks:** <5m (Slack), 5m (GitHub/Confluence)
- **API-based:** 10m incremental (SharePoint OneDrive, Box, Google Drive), 6h full (Jira)
- **People data:** 1h crawl (Azure), 3h crawl (Okta), continuous (Google Drive)
- **Teams:** 1h incremental, 30d full

## Audit Logs
`Admin Console → Users & permissions → Audit logs` — connector config changes, global config changes, crawl schedule changes. **Does NOT cover** end-user activity or crawl telemetry.

## Alerts
Email alerts (all mandatory, cannot disable):
- Failing credentials (Slack, Google Drive, GitHub, OneDrive, SharePoint, Jira, Teams, Workday)
- SSO expiry
- LLM provider errors
- Gleanbot setup errors
- GCP constraint issues
- Confluence/Jira Cloud migration

One email per day per alert until resolved.

## References
For detailed provider-specific steps, troubleshooting, and deep dives:
- SSO: `/administration/identity/sso/*`
- Connectors: `/connectors/native/*`
- Security: `/security/*`
- RBAC: `/administration/identity/roles/*`
