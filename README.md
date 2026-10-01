# mfink Cursor Skills Repository

This repository is a directory of shared Cursor skills used to standardize how teams programmatically operate tools and workflows.

## Why this exists

These skills help teams:

- Use operational tools consistently.
- Follow the same design patterns across projects.
- Reduce ad hoc workflow differences.
- Improve cross-team standardization and onboarding.

## Skills Directory

### Core Operational Skills

- [`confluence-dc-mcp`](cursor-skills/skills/confluence-dc-mcp/SKILL.md)  
  Connect and operate self-hosted Confluence Data Center via MCP with approval-first write controls.

- [`confluence-publish-html`](cursor-skills/skills/confluence-publish-html/SKILL.md)  
  Publish interactive HTML artifacts (dashboards, reports, visualizations) to Confluence, handling Data Center quirks like script stripping and the HTML macro.

- [`exec-stakeholder-deck`](cursor-skills/skills/exec-stakeholder-deck/SKILL.md)  
  Builds executive/leadership PowerPoint decks via a six-question stakeholder-analysis framework (audience, goal, priorities, motivation, objections, credibility) before drafting any slides.

- [`gitlab`](cursor-skills/skills/gitlab/SKILL.md)  
  Standard GitLab workflow for publishing updates, branching strategy, and merge request practices, plus the runbook for syncing skills to GitLab, GitHub, and Confluence.

- [`glean-setup`](cursor-skills/skills/glean-setup/SKILL.md)  
  Complete guide for setting up Glean workspace, SSO (Azure AD, Okta, Google), people data sync, connectors, RBAC, and security.

- [`graphify`](cursor-skills/skills/graphify/SKILL.md)  
  Turns any input (code, docs, papers, images, videos) into a persistent knowledge graph with god nodes, community detection, and query/path/explain tools.

- [`herdr-run`](cursor-skills/skills/herdr-run/SKILL.md)  
  Run long-lived or unattended agent jobs inside a Herdr pane so they survive terminal disconnects, lid close, and reboots, and stay observable.

- [`infra-leadership-sync`](cursor-skills/skills/infra-leadership-sync/SKILL.md)  
  Weekly Infrastructure Leadership Sync notes — scheduled Jira scrape and Confluence publish under the leadership hub.

- [`jira-align`](cursor-skills/skills/jira-align/SKILL.md)  
  Query and update Jira Align (ACAaaS portfolio hierarchy) via REST API 2.0 — Themes, Epics, Capabilities, Features, Programs, and Program Increments.

- [`jira-create-issues`](cursor-skills/skills/jira-create-issues/SKILL.md)  
  Structured Jira Epic/Story/Task creation with required fields and standardized hierarchy.

- [`latc-confluence-daily-digest`](cursor-skills/skills/latc-confluence-daily-digest/SKILL.md)  
  Daily LATC Confluence digest — scrape updates across all pillars, score and cluster them, join Jira where possible, and publish a dated digest.

- [`metron-program-dashboard`](cursor-skills/skills/metron-program-dashboard/SKILL.md)  
  Navigate and operate the Metron Engineering Intel portal — sidebar pages, Program Roadmap, FY26 pillar dependencies, and weekly Confluence-to-Metron exec summary refresh.

- [`roadmap-dashboard-html`](cursor-skills/skills/roadmap-dashboard-html/SKILL.md)  
  Generate a single self-contained, interactive HTML dashboard (Gantt, dependency DAG, schedule risks, capacity, exec summary) from a roadmap workbook.

- [`scheduled-status-report`](cursor-skills/skills/scheduled-status-report/SKILL.md)  
  Automated weekly LATC pillar status reports — query Jira for completed work and publish detailed Confluence reports with native charts plus a condensed leadership update.

- [`web-crawl`](cursor-skills/skills/web-crawl/SKILL.md)  
  Crawl an external website to discover and log pages whose titles/URLs contain bug-indicator keywords; outputs a CSV.

- [`writing-voice`](cursor-skills/skills/writing-voice/SKILL.md)  
  Rewrite and draft outbound prose (emails, chat messages, Confluence pages, status updates) in Mike Fink's voice so it reads human, not AI.

### Plannotator Skills

- [`plannotator`](cursor-skills/skills/plannotator/SKILL.md)  
  Reference for the Plannotator CLI — plan review, code review, annotating files/URLs/folders, archiving plan decisions, and exporting or sharing Guided Reviews.

- [`plannotator-annotate`](cursor-skills/skills/plannotator-annotate/SKILL.md)  
  Open Plannotator's annotation UI for a markdown file, HTML file, URL, or folder and respond to the returned annotations.

- [`plannotator-last`](cursor-skills/skills/plannotator-last/SKILL.md)  
  Open Plannotator on the latest rendered assistant message and use the returned annotations to revise or continue.

- [`plannotator-review`](cursor-skills/skills/plannotator-review/SKILL.md)  
  Open Plannotator's browser-based code review UI for the current worktree, another directory, or a pull request URL, then act on the feedback.

### Cursor Platform Skills

- [`babysit`](cursor-skills/skills-cursor/babysit/SKILL.md)
- [`canvas`](cursor-skills/skills-cursor/canvas/SKILL.md)
- [`create-hook`](cursor-skills/skills-cursor/create-hook/SKILL.md)
- [`create-rule`](cursor-skills/skills-cursor/create-rule/SKILL.md)
- [`create-skill`](cursor-skills/skills-cursor/create-skill/SKILL.md)
- [`create-subagent`](cursor-skills/skills-cursor/create-subagent/SKILL.md)
- [`cursor-blame`](cursor-skills/skills-cursor/cursor-blame/SKILL.md)
- [`migrate-to-skills`](cursor-skills/skills-cursor/migrate-to-skills/SKILL.md)
- [`sdk`](cursor-skills/skills-cursor/sdk/SKILL.md)
- [`shell`](cursor-skills/skills-cursor/shell/SKILL.md)
- [`split-to-prs`](cursor-skills/skills-cursor/split-to-prs/SKILL.md)
- [`statusline`](cursor-skills/skills-cursor/statusline/SKILL.md)
- [`update-cli-config`](cursor-skills/skills-cursor/update-cli-config/SKILL.md)
- [`update-cursor-settings`](cursor-skills/skills-cursor/update-cursor-settings/SKILL.md)

### Plugin Skill Packs

- Atlassian skills and docs: `cursor-skills/plugins-cache/cursor-public/atlassian/`
- Figma skills and docs: `cursor-skills/plugins-cache/cursor-public/figma/`
- Notion workspace skills and docs: `cursor-skills/plugins-cache/cursor-public/notion-workspace/`

## Contribution expectations

- Keep skill updates focused and traceable.
- Preserve existing directory structure when syncing.
- Use clear commit messages describing intent.
- Prefer merge requests for shared workflow changes.
