---
name: gitlab-skill
description: >
  Use this skill for GitLab repository operations that should be performed
  consistently across teams: creating and updating files, branching strategy,
  merge request workflows, and repository standardization tasks. Also covers
  publishing/synchronizing Cursor skills across the LATC GitLab repo, the GitHub
  mirror, and the Confluence skills catalog. Apply when users ask to publish
  skills, sync operational docs, open MRs, push a SKILL.md to GitLab/GitHub, or
  automate codebase updates in self-hosted or cloud GitLab.
---

# GitLab Operational Skill

This skill defines a standard way to use GitLab for operational automation and
shared documentation updates.

## Purpose

Use GitLab as a controlled delivery layer for operational artifacts (such as
`SKILL.md` and `README` files) so teams execute the same workflows, with the
same review expectations, and the same structure.

## When to use

Trigger this skill when the user asks to:

- Create/update repository files in GitLab.
- Publish or synchronize skill documentation.
- Create feature branches and merge requests.
- Standardize repository structure for shared operational assets.

## Standard workflow

1. Confirm target repository and branch strategy (`main` direct vs MR flow).
2. Read current files before modifying anything.
3. Apply focused changes with clear commit messages describing intent.
4. Prefer branch + merge request for shared/team-visible repositories.
5. Verify results (changed files, commit SHA, remote branch/MR link).

## Guardrails

- Never force-push unless explicitly requested.
- Never rewrite shared history by default.
- Preserve existing unrelated changes in the repo.
- Avoid committing secrets or tokens in tracked files.
- Ask for confirmation before destructive operations (delete/rename at scale).

## Repository conventions for this project

- Keep mirrored assets under `cursor-skills/`.
- Keep original folder hierarchy when syncing sources.
- Treat `SKILL.md` as executable operational guidance and `README` as context.
- Make changes traceable and reviewable through concise commits.

---

## Publishing / syncing Cursor skills (LATC runbook)

When asked to "push/publish/update a skill," keep these four locations in sync.
The local copy is the source of truth.

| Location | Path / target |
|---|---|
| **Local (source of truth)** | `~/.cursor/skills/<skill>/SKILL.md` |
| **GitLab** | repo `latc/users/mfink` (host `gitlab.xpaas.lenovo.com`) → `cursor-skills/skills/<skill>/SKILL.md` |
| **GitHub (mirror)** | repo `AnubisRooster/cursor-skills` → `cursor-skills/skills/<skill>/SKILL.md` |
| **Confluence** | "TPM Skills Catalog" page `625860644` (space `LATC`) → attachment named `<skill>-SKILL.md` |

Notes:
- GitHub is a **mirror** of the same `cursor-skills/` layout — there is no separate
  `github` skill; use this skill for both.
- Not every skill is on the Confluence catalog. Only update the Confluence
  attachment if a `<skill>-SKILL.md` attachment already exists on page `625860644`
  (or the user asks to add it).
- Some skills (e.g. `scheduled-status-report`) live in the repos but are not
  installed locally; sync from wherever the user points to as the source.

### Safe sync sequence (idempotent, handles a moving remote)

Use an existing local clone if present (e.g. `C:\Users\mfink\mfink-gitlab` for
GitLab), otherwise clone fresh. For each remote:

1. `git fetch <auth-url> main` then `git reset --hard FETCH_HEAD` (start from the
   live remote tip — avoids stale-base surprises).
2. Copy the updated local `SKILL.md` into `cursor-skills/skills/<skill>/SKILL.md`.
3. `git add -A` → commit with inline identity → push to the auth URL.
4. If the push is rejected as **non-fast-forward**, repeat from step 1. **Never
   force-push** to recover.

## Authentication & push mechanics

- **GitLab:** a clone's `origin` typically carries **no credentials**, so a plain
  `git push` prompts for a username and fails. Push to a **tokenized URL**:

  ```
  git push "https://oauth2:<TOKEN>@gitlab.xpaas.lenovo.com/latc/users/mfink.git" HEAD:main
  ```

  Use the same form for `fetch`. Set `GIT_TERMINAL_PROMPT=0` so a missing/blocked
  credential **fails fast** instead of hanging on a GUI credential dialog
  (symptom: `fatal: could not read Username` / `User cancelled dialog`).
- **GitHub:** a public clone needs no credentials; `push` uses cached credentials
  (Windows Credential Manager) for the `AnubisRooster` account. No token URL needed.
- **Never modify global git config.** Set identity per-command:

  ```
  git -c user.name='Mike Fink' -c user.email='mfink@lenovo.com' commit -m "..."
  ```

## Agent execution notes (Cursor)

- Run git against the **internal GitLab host with the sandbox disabled**
  (`required_permissions: ["all"]` on the shell call). Sandboxed git invocations
  to the internal host (and sometimes plain local-repo reads) hang and return
  "no exit status." Quick allowlisted commands are unaffected.
- Tokens used for tokenized push URLs are transient — pass them inline on the
  command; do not write them into tracked files or the repo.

## Confluence attachment caveat (cross-ref `confluence-publish-html`)

The skills catalog stores each skill as a page **attachment** (`<skill>-SKILL.md`).
The Confluence Data Center attachment-upload endpoint can reject **all** uploads
to a page even while reads and *delete* still succeed.

- If `confluence_upload_attachment` returns `success: false` for the file — and a
  tiny probe file also fails — it's a **server-side block**, not your file.
- **Do not delete the existing attachment first** to "force a clean re-upload":
  if the subsequent upload is also blocked, the attachment is left missing.
- When blocked: retry later, or have the user upload via the Confluence UI
  (attachments icon). Keep the filename exactly `<skill>-SKILL.md`.
- `confluence_upload_attachments` (plural) and a fresh filename hit the same block
  — they are not workarounds.

## Expected outcome

Teams can programmatically and consistently use operational tools according to
our design patterns, with clear governance and cross-team standardization.
