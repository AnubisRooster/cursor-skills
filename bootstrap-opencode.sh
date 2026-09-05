#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# bootstrap-opencode.sh  —  macOS bootstrap for the opencode + GitNexus setup
# One-shot setup for a new Mac: installs this skill library into
# ~/.claude/skills, installs tool dependencies, and deploys the
# gitnexus-opencode plugin. Run from the root of a clone of this repo:
#
#   chmod +x bootstrap-opencode.sh && ./bootstrap-opencode.sh
#
# NOT covered here (manual, machine-specific or secret-bearing):
#   - opencode.jsonc (providers carry API keys - copy from the old machine
#     via a secure channel, or recreate from the template printed at the end)
#   - Herdr and the Windows-scheduled LATC agents (see steps printed at the end)
# ---------------------------------------------------------------------------

set -uo pipefail
SKILLS_DST="$HOME/.claude/skills"
CYAN='\033[36m'; YEL='\033[33m'; GRN='\033[32m'; NC='\033[0m'
step() { printf "${CYAN}== %s ==${NC}\n" "$1"; }
note() { printf "${YEL}  %s${NC}\n" "$1"; }

mkdir -p "$SKILLS_DST"

step "1/5 Installing skills to $SKILLS_DST"
for dir in cursor-skills/skills cursor-skills/skills-cursor; do
  for d in "$dir"/*/; do
    name="$(basename "$d")"
    cp -R "$d" "$SKILLS_DST/" && echo "  $name"
  done
done
# Plugin packs (prefixed to avoid generic-name collisions)
for pack in atlassian figma notion-workspace; do
  for d in cursor-skills/plugins-cache/cursor-public/$pack/*/skills/*/; do
    name="$(basename "$d")"
    case "$pack" in
      atlassian)      dst="atlassian-$name" ;;
      notion-workspace) dst="notion-$name" ;;
      *)              dst="$name" ;;
    esac
    cp -R "$d" "$SKILLS_DST/$dst" && echo "  $dst"
  done
done
echo "  skills installed: $(ls -1 "$SKILLS_DST" | wc -l | tr -d ' ')"

step "2/5 Installing GitNexus CLI"
if command -v gitnexus >/dev/null 2>&1; then
  echo "  already installed: $(gitnexus --version)"
elif command -v npm >/dev/null 2>&1; then
  npm install -g gitnexus 2>&1 | tail -1
else
  note "npm not found - install Node 22+ from https://nodejs.org (or brew install node), then rerun"
fi
command -v gitnexus >/dev/null 2>&1 || note "gitnexus install failed - try: npm i -g gitnexus (needs no C++ toolchain on macOS)"

step "3/5 Installing graphify (uv tool)"
if ! command -v uv >/dev/null 2>&1; then
  note "installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh 2>&1 | tail -1
  export PATH="$HOME/.local/bin:$PATH"
fi
uv tool install --upgrade graphifyy 2>&1 | tail -2

step "4/5 Deploying gitnexus-opencode plugin"
PLUGIN_DST="$HOME/.config/opencode/plugins"
mkdir -p "$PLUGIN_DST"
if [ -f tools/gitnexus-opencode.js ]; then
  cp tools/gitnexus-opencode.js "$PLUGIN_DST/" && echo "  deployed from repo tools/"
  [ -f tools/gitnexus-opencode.json ] && cp tools/gitnexus-opencode.json "$HOME/.config/opencode/" && echo "  plugin config deployed"
else
  note "vendored plugin missing - build once:"
  note "  git clone https://github.com/antomy-gc/gitnexus-opencode && cd gitnexus-opencode && npm install && npm run build && cp dist/gitnexus-opencode.js $PLUGIN_DST/"
fi

step "5/5 MCP + permissions"
cat <<'EOF'
  Add to ~/.config/opencode/opencode.jsonc (merge with your providers).
  NOTE (macOS): no "cmd /c" wrapper - call gitnexus directly.

  "mcp": {
    "gitnexus": {
      "type": "local",
      "command": ["gitnexus", "mcp"],
      "enabled": true,
      "environment": { "GITNEXUS_MCP_READ_ONLY": "1", "GITNEXUS_MCP_DEFAULT_MAX_TOKENS": "3000" }
    }
  },
  "permission": {
    "gitnexus_query": "allow", "gitnexus_context": "allow", "gitnexus_impact": "allow"
  }
EOF

printf "\n${GRN}== MANUAL STEPS REMAINING ==${NC}\n"
cat <<'EOF'
  1. opencode.jsonc providers (API keys) - copy from the old machine securely
  2. Restart opencode (config is load-once)
  3. Optional Herdr:  curl -fsSL https://herdr.dev/install.sh | sh
     (macOS supported; see skills/herdr-run/SKILL.md for the pattern)
  4. Scheduled LATC agents are Windows Task Scheduler jobs - on a Mac they
     would need launchd/cron equivalents, and the digest workflow also needs
     the corporate VPN. Skip unless you truly want them here.
  5. Per-repo GitNexus graphs: gitnexus analyze <repo>   (local, ~40s, free)
  6. Optional (web-crawl skill): pip install playwright && playwright install chromium
EOF
