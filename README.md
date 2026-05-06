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

- [`gitlab-skill`](cursor-skills/skills/gitlab/SKILL.md)  
  Standard GitLab workflow for publishing updates, branching strategy, and merge request practices.

- [`confluence-dc-mcp`](cursor-skills/skills/confluence-dc-mcp/SKILL.md)  
  Connect and operate self-hosted Confluence Data Center via MCP with approval-first write controls.

- [`jira-create-issues`](cursor-skills/skills/jira-create-issues/SKILL.md)  
  Structured Jira Epic/Story/Task creation with required fields and standardized hierarchy.

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
