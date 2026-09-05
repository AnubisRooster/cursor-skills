---
name: herdr-run
description: >
  Run long-lived or unattended agent jobs (digest publishers, crawlers, report
  builders, watchers) inside a Herdr pane so they survive terminal disconnects,
  lid close, and reboots, and stay observable (working/blocked/done). Use when
  a job runs longer than a few minutes, is launched by a scheduler, or must be
  inspected after the fact. Requires the Herdr CLI (herdr.dev).
---

# /herdr-run

Run an unattended job inside a Herdr pane and wait for its completion sentinel.

## When to use

- Scheduled agents (Task Scheduler fires the wrapper, not python directly)
- Multi-minute local jobs (crawls, pytest suites, `graphify --watch`)
- Anything that must survive a dropped terminal or laptop sleep
- Any run whose failure would otherwise be silent (exit 0 but no output)

## The pattern (reference implementation: `run_agent_via_herdr.ps1`)

```
1. ensure headless server:   herdr status -> if not running: Start-Process herd.exe server -WindowStyle Hidden
2. create labeled workspace: herdr workspace create --cwd <dir> --label "job-<stamp>" --no-focus
3. dispatch:                 herdr pane run <paneId> "<command>"
4. wait for sentinel:        herdr pane wait-output <paneId> --regex <sentinel> --timeout 2700000
5. read the tail:            herdr pane read <paneId> --lines 40
6. close pane on success, LEAVE OPEN on failure (inspection)
7. write a run log           (C:\Users\<user>\.herdr-pilot\job-<stamp>.log)
```

## Hard-won rules

- **Sentinel tokens must be SHORT** (`Digest DONE`, `SUCCESSFULLY`, `Report FAILED`).
  Pane output wraps long lines; `pane wait-output` matches one rendered row at a
  time, so long phrases get split and never match.
- **Wait on failure sentinels too** (`FAILED|ERRORS`), not just success - the
  scripts these wrappers commonly host exit 0 even when the agent inside failed.
- **Env vars come from the server process, not the caller.** Start the server at
  logon (HKCU Run key: `"...\herdr.exe" server`) so it inherits persistent user
  env vars (API keys). Verify once with a pane that echoes var presence.
- **One workspace per run, labeled with a stamp** - the Herdr TUI becomes the
  audit trail. Close the pane only on success.
- **Timeout of 45 min** is a good ceiling for LLM-agent jobs with internal retries.
- Scheduled-task wiring: point the task action at
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File <wrapper.ps1>`
- Windows Herdr is beta; expect Defender noise on first server start.

## Install (once per machine)

```powershell
irm https://herdr.dev/install.ps1 | iex          # Herdr CLI
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" `
  -Name "HerdrServer" -Value "`"C:\Users\<user>\AppData\Local\Programs\Herdr\bin\herdr.exe`" server" `
  -PropertyType String -Force
```

## Live examples validated 2026-09-04

- LATC Confluence Daily Digest: dispatched 16:12, sentinel `Digest DONE` at
  16:23, Confluence pageId 685749031 published, pane auto-closed.
- Weekly Pillar Status Report (3 pillars): dispatched 16:39, all sentinels
  matched by 17:00, six pages published.
- Caught a real silent failure the old scheduler hid: Cursor SDK deprecated
  model `grok-4.5`; scripts exited 0 while publishing nothing. The pane made
  the error visible immediately.
