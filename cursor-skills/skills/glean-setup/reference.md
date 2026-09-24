# Glean Setup — Quick Reference

## Azure Entra ID SSO Setup (OIDC)

### Prerequisites
- Global Admin / Application Admin / Cloud Application Admin in Azure
- Admin or Setup Admin role in Glean
- Tenant backend domain (from `app.glean.com/admin/about-glean`)

### Azure Portal Steps
1. Azure AD → App registrations → New registration
   - Name: `Glean SSO`
   - Supported accounts: Single tenant
   - Redirect URIs: `https://<tenant_id-be.glean.com>/authorization-code/callback?isExtension=1` and `https://<tenant_id-be.glean.com>/authorization-code/callback`

2. API permissions → Add permission → Microsoft Graph → Delegated
   - `openid`, `email`, `offline_access`, `profile`

3. Grant admin consent (Enterprise applications → Glean SSO → Permissions)

4. Certificates & secrets → New client secret (24 months) → Copy value

5. Overview → Copy Application (client) ID and Directory (tenant) ID

### Glean Admin Console
1. `Users & permissions → Single sign-on (SSO) → Select Azure SSO`
2. Paste: Client Secret, Expiration Date, Application ID, Directory ID
3. Click Save
4. After provisioning → Click "Switch to Azure SSO"

### CWS Mode (before provisioning)
- Add redirect URI: `https://apps-be.glean.com/central_sso/authorization-code/callback`
- After provisioning, replace with tenant-specific URIs

## Azure Entra ID People Data Sync

### Separate app registration: `Glean People`

1. App registrations → New registration
   - Name: `Glean People`
   - Single tenant, no redirect URI

2. API permissions → Microsoft Graph → Application permissions
   - `User.Read.All`, `GroupMember.Read.All`

3. Grant admin consent

4. Certificates & secrets → New client secret → Copy value

5. Copy Application ID + Directory ID

6. Glean: `Users & permissions → People data → Select Azure` → paste all 3 values → Enable crawl

## Microsoft 365 (SharePoint/OneDrive) Certificate

```bash
openssl genrsa -out tempprivatekey.key 2048
openssl pkcs8 -topk8 -inform PEM -outform PEM -in tempprivatekey.key -out privatekey.key -nocrypt
openssl req -new -key privatekey.key -out request.csr
openssl x509 -req -days 365 -in request.csr -signkey privatekey.key -out certificate.crt
```

Upload `certificate.crt` to the app registration. Paste `privatekey.key` content in Glean.

## Microsoft Teams Required Permissions
```
User.Read.All
GroupMember.Read.All
Team.ReadBasic.All
ChannelSettings.Read.All
ChannelMember.Read.All
ChannelMessage.Read.All
```
Optional for chats/transcripts: `Chat.Read.All`, `Calendars.Read`, `OnlineMeetings.Read.All`, `OnlineMeetingTranscript.Read.All`

## Email Domains
**Required for SSO:** Notify Glean support of ALL email domains users will authenticate from (e.g., `company.com`). SSO fails without pre-registered domains.

## Static IPs (allowlist)
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

## Common Errors
| Error | Fix |
|---|---|
| Code 13 | Verify Directory ID, Application ID, Client Secret |
| Code 14 | Populate Email, Name, Title, Department, Manager in Entra ID |
| "You can't get there from here" | Amend Conditional Access policy |
| Stuck after SSO | Verify email domains registered with Glean |
| "Certificate not authorized" | Upload cert to ALL app registrations (multi-app tenants) |
