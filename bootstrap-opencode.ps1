# ---------------------------------------------------------------------------
# bootstrap-opencode.ps1
# One-shot setup for a new machine: installs this skill library into
# ~/.claude/skills, installs the tool dependencies, and deploys the
# gitnexus-opencode plugin. Run from the root of a clone of this repo:
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\bootstrap-opencode.ps1
#
# NOT covered here (manual, machine-specific or secret-bearing):
#   - opencode.jsonc (providers carry API keys - copy from the old machine
#     via a secure channel, or recreate from the template printed at the end)
#   - Herdr + scheduled LATC tasks (see steps printed at the end)
# ---------------------------------------------------------------------------

$ErrorActionPreference = "Continue"
$SkillsDst = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force -Path $SkillsDst | Out-Null

Write-Host "== 1/5 Installing skills to $SkillsDst ==" -ForegroundColor Cyan
# Core + Cursor platform skills (copy as-is)
foreach ($d in @("cursor-skills\skills", "cursor-skills\skills-cursor")) {
  Get-ChildItem $d -Directory | ForEach-Object {
    Copy-Item $_.FullName -Destination $SkillsDst -Recurse -Force
    Write-Host "  $($_.Name)"
  }
}
# Plugin packs (prefixed to avoid generic-name collisions)
$pub = "cursor-skills\plugins-cache\cursor-public"
foreach ($d in (Get-ChildItem "$pub\atlassian" -Directory | ForEach-Object { Get-ChildItem "$($_.FullName)\skills" -Directory })) {
  Copy-Item $d.FullName -Destination "$SkillsDst\atlassian-$($d.Name)" -Recurse -Force
}
foreach ($d in (Get-ChildItem "$pub\figma" -Directory | ForEach-Object { Get-ChildItem "$($_.FullName)\skills" -Directory })) {
  Copy-Item $d.FullName -Destination "$SkillsDst\$($d.Name)" -Recurse -Force
}
foreach ($d in (Get-ChildItem "$pub\notion-workspace" -Directory | ForEach-Object { Get-ChildItem "$($_.FullName)\skills" -Directory })) {
  Copy-Item $d.FullName -Destination "$SkillsDst\notion-$($d.Name)" -Recurse -Force
}
Write-Host "  skills installed: $((Get-ChildItem $SkillsDst -Directory).Count)"

Write-Host "== 2/5 Installing GitNexus CLI ==" -ForegroundColor Cyan
if (Get-Command gitnexus -ErrorAction SilentlyContinue) {
  Write-Host "  already installed: $(gitnexus --version)"
} else {
  # npm 11.x: use global install (npx -y crashes on npm 11)
  npm install -g gitnexus 2>&1 | Select-Object -Last 1
}
if (-not (Get-Command gitnexus -ErrorAction SilentlyContinue)) {
  Write-Host "  FAILED - try: pnpm install -g gitnexus (or install pnpm first)" -ForegroundColor Yellow
}

Write-Host "== 3/5 Installing graphify ==" -ForegroundColor Cyan
if (Get-Command uv -ErrorAction SilentlyContinue) {
  uv tool install --upgrade graphifyy 2>&1 | Select-Object -Last 2
} else {
  Write-Host "  uv not found - install from https://docs.astral.sh/uv/ then rerun" -ForegroundColor Yellow
}

Write-Host "== 4/5 Deploying gitnexus-opencode plugin ==" -ForegroundColor Cyan
$pluginDst = "$env:USERPROFILE\.config\opencode\plugins"
if (Test-Path "$PSScriptRoot\tools\gitnexus-opencode.js") {
  New-Item -ItemType Directory -Force -Path $pluginDst | Out-Null
  Copy-Item "$PSScriptRoot\tools\gitnexus-opencode.js" $pluginDst -Force
  Copy-Item "$PSScriptRoot\tools\gitnexus-opencode.json" "$env:USERPROFILE\.config\opencode\" -Force -ErrorAction SilentlyContinue
  Write-Host "  deployed from repo tools/"
} else {
  Write-Host "  build it once: git clone https://github.com/antomy-gc/gitnexus-opencode; cd gitnexus-opencode; npm install; npm run build; copy dist\gitnexus-opencode.js $pluginDst\" -ForegroundColor Yellow
}

Write-Host "== 5/5 MCP + permissions ==" -ForegroundColor Cyan
Write-Host @"
  Add to ~/.config/opencode/opencode.jsonc (merge with your providers):

  "mcp": {
    "gitnexus": {
      "type": "local",
      "command": ["cmd", "/c", "gitnexus", "mcp"],
      "enabled": true,
      "environment": { "GITNEXUS_MCP_READ_ONLY": "1", "GITNEXUS_MCP_DEFAULT_MAX_TOKENS": "3000" }
    }
  },
  "permission": {
    "gitnexus_query": "allow", "gitnexus_context": "allow", "gitnexus_impact": "allow"
  }
"@

Write-Host ""
Write-Host "== MANUAL STEPS REMAINING ==" -ForegroundColor Yellow
Write-Host @"
  1. opencode.jsonc providers (API keys) - copy from old machine securely
  2. Restart opencode (config is load-once)
  3. Optional Herdr:  irm https://herdr.dev/install.ps1 | iex
     + logon autostart (see skills\herdr-run\SKILL.md)
  4. Scheduled LATC tasks: run each skill's setup_*.ps1 (needs VPN + API keys)
  5. Per-repo GitNexus graphs: gitnexus analyze <repo>  (local, ~40s, free)
"@
