---
name: confluence-publish-html
description: >
  Publish an interactive, script-bearing HTML artifact (dashboard, report,
  visualization) to Confluence — especially self-hosted Confluence Data
  Center/Server — reliably. Use this skill whenever the user wants to "put this
  HTML on Confluence", "embed a dashboard in a wiki page", "publish an
  interactive report to Confluence", or hits the common failure where Confluence
  strips <script>/<style> or the HTML macro is disabled. Produces a page that
  links to and/or iframe-embeds the artifact, plus a macro-ready fragment, and
  gracefully handles Data Center quirks (HTML macro disabled, attachment-upload
  API failures, inline-vs-download serving). Builds on confluence-dc-mcp (for the
  MCP connection) and pairs with roadmap-dashboard-html (which produces the HTML).
---

# confluence-publish-html

Gets a **self-contained interactive HTML file onto Confluence** in a way that
actually renders — working around the fact that Confluence storage format strips
inline `<script>`/`<style>` and the HTML macro is often disabled on Data Center.

## When to use

- Publishing a dashboard/report produced by `roadmap-dashboard-html` (or any
  standalone HTML) to a Confluence page.
- The user reports "I can't publish this to Confluence" / blank embeds / stripped
  scripts.

## Input contract

| Input | Required | Notes |
|---|---|---|
| HTML file path | **Yes** | A standalone `.html` (inline CSS/JS, no external assets). |
| Target | **Yes** | Either an existing page ID, or a parent page + new title. |
| Confluence MCP | **Yes** | `mcp-atlassian` configured for the instance (see `confluence-dc-mcp`). |

## Output contract

- A Confluence page containing, in priority order:
  1. A **direct "Open dashboard" link** to the attached HTML (works with **no
     macros** — the reliable baseline).
  2. An **inline iframe embed** via the HTML macro pointing at the attachment
     download URL (renders inline *if* the HTML macro is enabled; the iframe loads
     the standalone file as its own document, so its scripts run un-stripped).
- A `*<name>*.fragment.html` — the artifact stripped of `<!DOCTYPE>/<html>/<head>/
  <body>` wrappers, ready to paste into a single HTML macro.

## Procedure

1. **Connect & confirm** the target space/parent/title (per `confluence-dc-mcp`).
   Never write without explicit approval.
2. **Create/locate the page** (`confluence_create_page` / `confluence_update_page`,
   `content_format: storage`). When updating, fetch the full storage body first
   and re-save it intact so no existing content is lost.
3. **Attach the HTML** (`confluence_upload_attachment`). If the DC instance
   rejects API uploads (a known limitation on some Data Center builds — even a
   tiny file fails), **fall back**: stage the file locally and instruct the user
   to drag-drop it via **Edit → Insert → Files and images**.
4. **Wire the body** to the attachment filename: a direct `<ac:link>` to the
   `<ri:attachment>` plus an `html` macro iframe to
   `/download/attachments/<pageId>/<filename>`.
5. **Generate the fragment** as a paste-in fallback for the HTML macro.

## Data Center caveats (handle explicitly)

- **HTML macro disabled** → iframe/fragment won't render; the direct link still
  works. Tell the user to ask an admin to enable the HTML macro if they want
  inline embedding.
- **Attachment API blocked** → upload via API returns failure; use the manual
  drag-drop fallback (don't keep retrying).
- **Inline vs download** → some instances force `.html` attachments to download.
  If the link downloads instead of opening, switch the link/iframe to the
  inline-view URL form.
- **CSS bleed** → if pasting the full fragment inline (not iframed), global CSS
  (`*`, `body`, `html`) can restyle the whole page; prefer the iframe/attachment
  route, or scope the CSS.

## Guardrails

- **Approval before any write** (create/update/attach), per `confluence-dc-mcp`.
- **Preserve others' work**: on update, always re-save the complete existing body
  with only the intended additions.
- **PII / visibility**: dashboards often embed people data — keep the page in an
  appropriately restricted space.
- **No secrets** embedded in page or attachment.

## Starter instruction

```
Use confluence-publish-html to publish <PATH_TO.html> to Confluence under parent
<PARENT_URL_OR_ID> titled "<TITLE>". Attach the file and add both a direct open
link and an HTML-macro iframe embed; also generate a paste-in macro fragment.
Confirm the destination before writing, and if attachment upload is blocked,
give me the manual drag-drop steps.
```
