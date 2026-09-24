---
name: confluence-dc-mcp
description: >
  Extend the mcp-atlassian MCP server to connect Claude/Cursor to a self-hosted
  Confluence Data Center instance. Use this skill whenever the user mentions
  Confluence Data Center, self-hosted Confluence, on-prem Confluence, Confluence
  behind a VPN, setting up Confluence MCP, Confluence personal access tokens,
  searching Confluence wiki pages, creating or updating Confluence pages from
  Claude, CQL queries, Confluence spaces, or any workflow that involves reading
  or writing documentation in a self-hosted Confluence. Also trigger when the
  user asks to extend their existing mcp-atlassian Jira setup with Confluence,
  or wants to connect Claude/Cursor to an internal wiki. Complements the
  jira-create-issues skill — both share the same mcp-atlassian MCP server process.
  When creating or updating Confluence page prose, always apply the writing-voice
  skill (Mike Fink formal Confluence voice).
---

# Confluence Data Center — MCP Skill (mcp-atlassian)

This skill governs how the agent interacts with a **self-hosted Confluence Data Center**
(or Server) instance via the `mcp-atlassian` MCP server. It complements the
`jira-create-issues` skill; both products share one MCP server process.

---

## Architecture

```
┌──────────────┐  stdio   ┌──────────────────┐  HTTPS/PAT  ┌─────────────────────┐
│ Cursor /     │◄────────►│ mcp-atlassian    │◄───────────►│ Confluence DC       │
│ Claude Code  │          │ (local process)  │             │ (on-prem / VPN)     │
└──────────────┘          └──────────────────┘             └─────────────────────┘
```

The MCP server runs locally on the user's machine (inside the VPN) and connects
to Confluence DC via its REST API using a Personal Access Token (PAT).

---

## MANDATORY: Approval before write operations

**NEVER create, update, or delete Confluence pages without the user's explicit approval.**

When the user asks to create or update a Confluence page:

1. **Draft the content** in the conversation (or as a local file) and present it to
   the user for review.
2. **Wait for explicit approval** — the user must confirm before calling
   `confluence_create_page`, `confluence_update_page`, or `confluence_delete_page`.
3. **Only then execute** the write operation.

This applies to **all write operations**: creating pages, updating page content,
adding comments, uploading attachments, moving pages, adding/removing labels, and
deleting pages.

Read operations (`confluence_search`, `confluence_get_page`, `confluence_get_page_children`,
etc.) do **not** require approval.

---

## MANDATORY: writing-voice for page prose

**Every time** this skill is used to create or update Confluence **page body text**
(titles, intros, process pages, FAQs, status notes, narrative sections), read and
apply `writing-voice` first:

`C:\Users\mfink\.claude\skills\writing-voice\SKILL.md`

(and `examples.md` beside it if present).

Rules that matter for Confluence:

- Formal Confluence. Complete sentences. Capitalize. Headings.
- Problem / ask / risk shape in the prose. No chat openers.
- No brochure AI tone. No em dashes or ornamental en dashes. No arrows in prose.
- Keep HTML form macros, dashboards, and storage/XML plumbing out of voice rules.
  Voice applies to human-readable markdown/storage prose around those artifacts.

Do **not** skip writing-voice because the page is a "draft", a form wrapper, or a
checklist. If the user can read it as Mike on Confluence, use the voice.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `CONFLUENCE_URL` | **Yes** | Base URL of your Confluence instance (e.g. `https://confluence.yourcompany.com`) |
| `CONFLUENCE_PERSONAL_TOKEN` | **Yes (DC)** | PAT from your Confluence profile |
| `CONFLUENCE_USERNAME` | Alt | Email/username for basic auth (DC < 7.9 only) |
| `CONFLUENCE_API_TOKEN` | Alt | Password/token for basic auth (DC < 7.9 only) |
| `CONFLUENCE_SSL_VERIFY` | No | Set to `false` for self-signed certificates |
| `TOOLSETS` | No | Comma-separated toolset names to enable |
| `ENABLED_TOOLS` | No | Comma-separated specific tool names to enable |
| `READ_ONLY_MODE` | No | Set to `true` to disable all write operations |

**Tip:** If the user already has `mcp-atlassian` configured for Jira, add the
`CONFLUENCE_*` env vars to the **same** server entry — both products share one process.

---

## MCP config snippets

### Cursor (Settings → AI → MCP Servers)

| Setting | Value |
|---|---|
| Server name | `mcp-atlassian` |
| Command | `uvx mcp-atlassian` |
| `CONFLUENCE_URL` | `https://confluence.yourcompany.com` |
| `CONFLUENCE_PERSONAL_TOKEN` | `<your-confluence-pat>` |

### Claude Code / Claude Desktop (`~/.claude/mcp_servers.json`)

```jsonc
{
  "mcp-atlassian": {
    "command": "uvx",
    "args": ["mcp-atlassian"],
    "env": {
      "JIRA_URL": "https://jira.yourcompany.com",
      "JIRA_PERSONAL_TOKEN": "your-jira-pat",
      "CONFLUENCE_URL": "https://confluence.yourcompany.com",
      "CONFLUENCE_PERSONAL_TOKEN": "your-confluence-pat"
    }
  }
}
```

Config file locations:
- **Windows (installer):** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

---

## Generating a Personal Access Token

1. Log in to your Confluence DC instance.
2. Click your avatar → **Profile** → **Personal Access Tokens**.
3. Click **Create token**. Name it (e.g. `claude-mcp`), set an expiry.
4. Copy the token immediately — it won't be shown again.

> If the instance runs Confluence DC < 7.9, PATs are not available. Fall back to
> HTTP basic auth with `CONFLUENCE_USERNAME` + `CONFLUENCE_API_TOKEN`.

---

## Available tools

### Pages

| Tool | Description |
|---|---|
| `confluence_search` | Search content with CQL or simple text |
| `confluence_get_page` | Get a page by ID, or by title + space key |
| `confluence_get_page_children` | List child pages and folders |
| `confluence_get_page_history` | Get version history for a page |
| `confluence_get_page_diff` | Unified diff between two page versions |
| `confluence_create_page` | Create a new page in a space (**requires approval**) |
| `confluence_update_page` | Update page title, body, or parent (**requires approval**) |
| `confluence_delete_page` | Delete a page — moves to trash (**requires approval**) |
| `confluence_move_page` | Move a page to a new parent or space (**requires approval**) |

### Comments

| Tool | Description |
|---|---|
| `confluence_get_comments` | Get comments on a page |
| `confluence_add_comment` | Add a comment to a page (**requires approval**) |
| `confluence_reply_to_comment` | Reply to an existing comment thread (**requires approval**) |

### Labels & Attachments

| Tool | Description |
|---|---|
| `confluence_get_labels` | Get labels on a page |
| `confluence_add_label` | Add a label to a page (**requires approval**) |
| `confluence_upload_attachment` | Upload a single attachment (**requires approval**) |
| `confluence_upload_attachments` | Upload multiple attachments (**requires approval**) |
| `confluence_get_attachments` | List attachments on a page |
| `confluence_download_attachment` | Download an attachment |
| `confluence_delete_attachment` | Delete an attachment (**requires approval**) |
| `confluence_get_page_images` | Get all images as base64 inline content |

### Users

| Tool | Description |
|---|---|
| `confluence_search_user` | Search for Confluence users |

> **`confluence_get_page_views` is Cloud-only.** Do not call it on Data Center.

---

## CQL (Confluence Query Language) reference

Used by `confluence_search`. Basic syntax:

```
field operator value [AND|OR field operator value ...]
```

### Key fields on Data Center

| Field | Type | Description |
|---|---|---|
| `type` | keyword | `page`, `blogpost`, `comment`, `attachment` |
| `space` | keyword | Space key (e.g. `"ENG"`, `"HR"`) |
| `title` | text | Page title |
| `text` | text | Full-text body content |
| `label` | keyword | Labels attached to content |
| `creator` | user | Username who created the content |
| `contributor` | user | Any user who edited the content |
| `lastModified` | date | When content was last updated |
| `created` | date | When content was created |
| `ancestor` | number | Any ancestor page ID (recursive) |

### Example CQL queries

```cql
type = page AND space = "ENG"
type = page AND text ~ "Kubernetes deployment"
type = page AND lastModified > now("-7d")
ancestor = 12345678 AND type = page
type = page AND space = "ENG" AND label = "architecture" AND lastModified > now("-30d")
```

**DC-specific notes:**
- Space keys are **case-sensitive** (usually uppercase).
- Personal spaces use `~username` and must be quoted.
- `content.property` field is Cloud-only.

---

## LATC Space — Pillar Page Structure

### LATC Jira governance reference

Before proposing Jira-automation behavior for LATC workflows, cross-check against:

- `Jira Usage at LATC` (`pageId=551394388`)

This page defines current hierarchy semantics (including Feature usage), workflow expectations, and resolution guidance. Treat it as the source of truth when skill logic and legacy habits conflict.

### Standard section layout

```
Pillar Homepage              ← pillar overview: vision, scope, deliverables, timeline, KPIs
├── 00-Regular Updates       ← status/progress updates, biweekly reports
├── 01-Resources & Working Model  ← team roster, headcount, working agreements, processes
├── 02-Architecture          ← architecture designs, system diagrams, design decisions
├── 03-Components            ← component-level specs, scopes, technical docs
└── 0x-...                   ← pillar-specific extensions
```

### Known pillar homepages in LATC (page IDs)

| Pillar | Homepage title | Page ID |
|---|---|---|
| Data, Context & Memory | `Data, Context & Memory` | `616882006` |
| Operations & Infrastructure | `Operations & Infrastructure` | `616882009` |

### Navigation pattern — use section-aware CQL

```cql
ancestor = <homepageId> AND title ~ "02-Architecture"
ancestor = <homepageId> AND title ~ "00-Regular Updates"
```

**Known section page IDs for Operations & Infrastructure:**

| Section | Page ID |
|---|---|
| `00-Regular Updates - INFRA` | `632542364` |
| `01-Resources & Working Model - INFRA` | `632542365` |
| `02-Architecture - INFRA` | `632542366` |
| `03-Components - INFRA` | `632542367` |

**Known section page IDs for Data, Context & Memory:**

| Section | Page ID |
|---|---|
| `00-Regular Updates - DCM` | `622810939` |
| `01-Resources & Working model - DCM` | `622811020` |
| `02-Architecture - DCM` | `622811149` |
| `03-Components - DCM` | `622811129` |
| `04-Cross Pillar Contracts - DCM` | `622813427` |
| `05 - Enterprise Knowledge Factory (EKF)` | `630653389` |

---

## Data Center vs Cloud key differences

| Area | Cloud | Data Center |
|---|---|---|
| Auth | API token (email + token) | Personal Access Token |
| URL format | `*.atlassian.net/wiki` | Custom domain (no `/wiki` suffix typically) |
| Content API | v2 (`/wiki/api/v2/...`) | v1 (`/rest/api/content/...`) — handled automatically |
| Page Analytics | Available | **Not available** — skip `confluence_get_page_views` |
| SSL | Managed by Atlassian | May need `CONFLUENCE_SSL_VERIFY=false` |
| Network | Internet-accessible | Requires VPN / local network access |

---

## Troubleshooting

| Symptom | Likely cause & fix |
|---|---|
| No Confluence tools appear | `CONFLUENCE_URL` / `CONFLUENCE_PERSONAL_TOKEN` not set; restart after updating config |
| SSL: CERTIFICATE_VERIFY_FAILED | Add `"CONFLUENCE_SSL_VERIFY": "false"` to env |
| 401 Unauthorized | PAT expired — generate a new one |
| Connection refused / timeout | VPN not connected |
| 403 Forbidden | PAT user lacks space permissions |
| `confluence_get_page_views` error | Cloud-only — do not use on DC |

---

## Useful references

- mcp-atlassian source: https://github.com/sooperset/mcp-atlassian
- Confluence DC REST API: https://developer.atlassian.com/server/confluence/confluence-server-rest-api/
- Cursor MCP docs: https://docs.cursor.com/mcp
