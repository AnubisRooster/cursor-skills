---
name: jira-align
description: >-
  Query and update Jira Align (ACAaaS portfolio hierarchy) via REST API 2.0 using
  bearer token auth. Use when the user mentions Jira Align, Align, one-atlas-xfdm,
  Themes/Epics/Capabilities/Features/Stories in Align, Program Increments,
  Align Programs/Teams, or asks to sync/read Align work items. Do NOT use
  mcp-atlassian or the jira-create-issues skill for Align — those target Jira
  Software (DC/Cloud), which is a different product and API.
---

# Jira Align (REST API 2.0)

## When to use

Use this skill for **https://one-atlas-xfdm.jiraalign.com** (Jira Align).

Do **not** retarget `mcp-atlassian` / `mcp-atlassian-cloud` or the `jira-create-issues` skill here. Align is a separate product:

| | Jira Software | Jira Align |
|---|---|---|
| MCP / skill | `user-mcp-atlassian` (+ `jira-create-issues`) | **this skill** (HTTP) |
| Base path | `/rest/api/2` or `/rest/api/3` | `/rest/align/api/2` |
| Auth | PAT / Basic+API token | `Authorization: bearer <API 2.0 token>` |

## Credentials (env vars — never hardcode)

| Variable | Purpose |
|---|---|
| `JIRA_ALIGN_URL` | Base URL, no trailing slash (default `https://one-atlas-xfdm.jiraalign.com`) |
| `JIRA_ALIGN_API_TOKEN` | Align **API 2.0** token from Profile → API Token |

If unset in the current shell, read the User-scoped Windows env vars, or ask the user to set them. **Never** paste the token into skill files, commits, or Confluence.

Auth header value: `bearer <token>` (lowercase `bearer` is accepted; include the full token string as stored).

## Base URL pattern

```
{JIRA_ALIGN_URL}/rest/align/api/2/{Resource}
```

Interactive Swagger (browser, after login): `{JIRA_ALIGN_URL}/rest/align/api/docs/index.html`

## How to call (PowerShell)

Prefer the helper script:

```powershell
& "$env:USERPROFILE\.cursor\skills\jira-align\scripts\align-api.ps1" -Method GET -Path "Themes"
```

Or raw:

```powershell
$base = $env:JIRA_ALIGN_URL.TrimEnd('/')
$token = $env:JIRA_ALIGN_API_TOKEN
$headers = @{
  Authorization = "bearer $token"
  Accept        = 'application/json'
  'Content-Type'= 'application/json'
}
Invoke-RestMethod -Method GET -Uri "$base/rest/align/api/2/Themes" -Headers $headers
```

Rules:

- Rate limit: **600 requests / 60 seconds** per IP → back off on HTTP 429.
- Permissions match the token owner's Align role (same as UI).
- Prefer GET for discovery; only POST/PUT/PATCH when the user explicitly asks to create/update.
- Show proposed write payloads and wait for approval before mutating (same discipline as `jira-create-issues`).

## Common resources (verified on one-atlas-xfdm, 2026-09-15)

| Resource path | Notes from live probe |
|---|---|
| `Themes` | **OK** — data returned |
| `Goals` | **OK** — data returned |
| `KeyResults` | **OK** — data returned |
| `Customers` | **OK** — data returned |
| `Regions` | **OK** — data returned |
| `Defects` | **OK** — data returned (default page ~100) |
| `Epics` / `Capabilities` / `Features` / `Stories` / `Tasks` | **OK auth** — may return `[]` if the token user has no visibility |
| `Portfolios` / `Programs` / `Teams` / `Releases` / `Iterations` / `Objectives` | **OK auth** — may return `[]` |
| `Users` | **403** for list on this tenant/role — do not use as health check |
| `Products` | **403** on this tenant/role |

Swagger UI: `{JIRA_ALIGN_URL}/rest/align/api/docs/index.html`

OData-style `$top`, `$skip`, `$filter` may work; quote `$` in PowerShell (`` `$top ``). Prefer unfiltered GET for smoke tests.

## Typical workflows

1. **Verify access:** `GET Themes` or `GET Goals` (not `Users` — returns 403 here).
2. **Find a program:** `GET Programs` then filter client-side, or `$filter` if supported.
3. **List work:** `GET Epics` / `Features` / `Stories` / `Themes` / `Defects` as needed.
4. **Get one item:** `GET Epics/{id}` (or Features/Stories/Themes).
5. **Create/update:** only after user approval; POST body fields differ by object (e.g. Epic often needs `title`, `state`, `type`, `primaryProgramId`).

## Hierarchy reminder

Align hierarchy is portfolio planning language, not Jira Software issue types:

`Theme → Epic → Capability (optional) → Feature → Story → Task`

Do not assume Jira keys (`LATC-123`) work in Align URLs — Align uses numeric ids.

## Security

- Rotate the API token if it was ever pasted into chat or committed.
- Do not log full `Authorization` headers.
- Do not store the token in this `SKILL.md`.
