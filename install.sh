#!/usr/bin/env bash
# Links this repo into the config dirs of the coding agents that read it.
#
#   install.sh                       # every runtime found on this machine
#   install.sh --agent copilot       # both GitHub Copilot CLI and VS Code
#   install.sh --agent claude,codex  # any comma-separated combination
#   install.sh --dry-run             # print what would change, change nothing
#   install.sh --check               # verify the links, exit 1 on any drift
#
# Idempotent. An existing real file/dir is moved to <name>.pre-ai-god, never deleted.
# Env: CLAUDE_CONFIG_DIR (default ~/.claude), CODEX_HOME (default ~/.codex),
#      COPILOT_HOME (default ~/.copilot; CLI only),
#      PROJECTS_ROOT (default ~/Developer) — where the projects named by local/memory/<project>
#      and local/projects/<project> are checked out.
#
# Private material (memory, project layer, company standards, the full Claude settings) lives in the
# git-ignored overlay local/, its own private repo. Without it only the public core is linked.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERLAY="$REPO/local"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
COPILOT_CLI_DIR="${COPILOT_HOME:-$HOME/.copilot}"
COPILOT_VSCODE_DIR="$HOME/.copilot"
PROJECTS_ROOT="${PROJECTS_ROOT:-$HOME/Developer}"

AGENT=""
MODE="install"
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="${2:?--agent needs claude|codex|copilot-cli|copilot-vscode|copilot|all}"; shift 2 ;;
    --agent=*) AGENT="${1#*=}"; shift ;;
    --dry-run) MODE="dry-run"; shift ;;
    --check) MODE="check"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$AGENT" ]; then
  found=()
  { [ -d "$CLAUDE_DIR" ] || command -v claude >/dev/null 2>&1; } && found+=(claude)
  { [ -d "$CODEX_DIR" ] || command -v codex >/dev/null 2>&1; } && found+=(codex)
  command -v copilot >/dev/null 2>&1 && found+=(copilot-cli)
  { command -v code >/dev/null 2>&1 || command -v code-insiders >/dev/null 2>&1; } && found+=(copilot-vscode)
  if [ ${#found[@]} -eq 0 ]; then
    echo "no runtime detected; pass --agent claude|codex|copilot-cli|copilot-vscode|copilot|all" >&2
    exit 2
  fi
  AGENT="$(IFS=,; echo "${found[*]}")"
fi
case "$AGENT" in
  all) AGENT="claude,codex,copilot-cli,copilot-vscode" ;;
  copilot) AGENT="copilot-cli,copilot-vscode" ;;
esac

SELECT_CLAUDE=0
SELECT_CODEX=0
SELECT_COPILOT_CLI=0
SELECT_COPILOT_VSCODE=0
IFS=',' read -r -a requested_agents <<< "$AGENT"
for agent in "${requested_agents[@]}"; do
  case "$agent" in
    claude) SELECT_CLAUDE=1 ;;
    codex) SELECT_CODEX=1 ;;
    copilot-cli) SELECT_COPILOT_CLI=1 ;;
    copilot-vscode) SELECT_COPILOT_VSCODE=1 ;;
    *) echo "unknown runtime: $agent (claude|codex|copilot-cli|copilot-vscode|copilot|all)" >&2; exit 2 ;;
  esac
done

drift=0

link() {
  local src="$1" dst="$2"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    [ "$MODE" = "check" ] && echo "ok      $dst"
    return 0
  fi
  case "$MODE" in
    check)
      echo "DRIFT   $dst -> ${src}  (now: $(readlink "$dst" 2>/dev/null || { [ -e "$dst" ] && echo 'real file' || echo missing; }))"
      drift=1
      return 0 ;;
    dry-run)
      if [ -L "$dst" ]; then echo "relink  $dst -> $src"
      elif [ -e "$dst" ]; then echo "move    $dst -> $dst.pre-ai-god, then link -> $src"
      else echo "link    $dst -> $src"; fi
      return 0 ;;
  esac
  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ]; then
    rm "$dst"
  elif [ -e "$dst" ]; then
    mv "$dst" "$dst.pre-ai-god"
    echo "moved   $dst -> $dst.pre-ai-god"
  fi
  ln -s "$src" "$dst"
  echo "linked  $dst -> $src"
}

# Removes links in $1 that point into this repo at something that no longer exists.
prune_stale() {
  local dir="$1" entry target
  [ -d "$dir" ] || return 0
  for entry in "$dir"/* "$dir"/.[!.]*; do
    [ -L "$entry" ] || continue
    target="$(readlink "$entry")"
    case "$target" in "$REPO"/*) ;; *) continue ;; esac
    [ -e "$target" ] && continue
    case "$MODE" in
      check) echo "STALE   $entry -> $target"; drift=1 ;;
      dry-run) echo "unlink  $entry (stale -> $target)" ;;
      *) rm "$entry"; echo "unlink  $entry (stale -> $target)" ;;
    esac
  done
}

# Project skills (projects/<p>/skills/<name>) for Claude go into the project's own .claude/skills,
# so they load only in that project — and only when that path is git-ignored there.
install_project_skills_claude() {
  local pdir p proj skill name
  for pdir in "$OVERLAY"/projects/*/; do
    [ -d "${pdir}skills" ] || continue
    p="$(basename "$pdir")"
    proj="$PROJECTS_ROOT/$p"
    if [ ! -d "$proj" ]; then
      echo "skip    $p: $proj not found"
      continue
    fi
    for skill in "${pdir}"skills/*/; do
      name="$(basename "$skill")"
      if ! git -C "$proj" check-ignore -q ".claude/skills/$name" 2>/dev/null; then
        echo "skip    $proj/.claude/skills/$name: not git-ignored in $p"
        continue
      fi
      link "${skill%/}" "$proj/.claude/skills/$name"
    done
    prune_stale "$proj/.claude/skills"
  done
}

# Personal skills (local/skills/<name>) are private and global: linked next to the public skills in
# every runtime.
link_personal_skills() {
  local dir="$1" skill
  for skill in "$OVERLAY"/skills/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    link "${skill%/}" "$dir/$(basename "$skill")"
  done
}

# Runtimes without a git-ignored project skills dir get project skills next to the global ones;
# each project skill's description limits it to its project.
link_project_skills_flat() {
  local dir="$1" skill
  for skill in "$OVERLAY"/projects/*/skills/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    link "${skill%/}" "$dir/$(basename "$skill")"
  done
}

# ~/.claude/settings.json is the overlay's full file (base policy + personal keys such as autoMode,
# which Claude Code reads only from user settings). First install copies the public base.
install_claude_settings() {
  local base="$REPO/adapters/claude/settings.base.json" own="$OVERLAY/claude/settings.json"
  if [ ! -f "$own" ]; then
    case "$MODE" in
      check) echo "DRIFT   $own missing (install copies $base)"; drift=1; return 0 ;;
      dry-run) echo "create  $own from $base" ;;
      *) mkdir -p "$(dirname "$own")"; cp "$base" "$own"; echo "created $own from $base" ;;
    esac
  fi
  link "$own" "$CLAUDE_DIR/settings.json"
  [ -f "$own" ] || return 0
  # Every base permission must survive in the personal file.
  if ! python3 -I - "$base" "$own" <<'PY'
import json, sys
base, own = (json.load(open(p)) for p in sys.argv[1:3])
missing = [f"{k}: {r}" for k in ("allow", "deny")
           for r in base.get("permissions", {}).get(k, [])
           if r not in own.get("permissions", {}).get(k, [])]
for m in missing:
    print(f"DRIFT   local settings lack permissions.{m}")
sys.exit(1 if missing else 0)
PY
  then drift=1; fi
}

# ~/.claude/skills is a real directory of per-skill links, so what Claude Code writes there itself
# (claude.ai skill sync into synced/, its .trash) stays out of this repo.
install_claude_skills() {
  local dir="$CLAUDE_DIR/skills" skill
  if [ -L "$dir" ]; then
    case "$MODE" in
      check) echo "DRIFT   $dir is a symlink (now: $(readlink "$dir")), expected a directory of per-skill links"; drift=1; return 0 ;;
      dry-run) echo "replace $dir symlink with a directory of per-skill links" ;;
      *) rm "$dir"; mkdir -p "$dir"; echo "replaced $dir symlink with a directory" ;;
    esac
  fi
  for skill in "$REPO"/skills/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    link "${skill%/}" "$dir/$(basename "$skill")"
  done
  link_personal_skills "$dir"
  prune_stale "$dir"
}

install_claude() {
  echo "== Claude Code ($CLAUDE_DIR)"
  link "$REPO/global/AGENTS.md" "$CLAUDE_DIR/CLAUDE.md"
  install_claude_settings
  install_claude_skills
  link "$REPO/adapters/claude/runtime.md" "$CLAUDE_DIR/ai-god-runtime.md"
  local dir name slug
  [ -d "$OVERLAY/memory" ] || echo "skip    memory: no $OVERLAY/memory"
  for dir in "$OVERLAY"/memory/*/; do
    [ -d "$dir" ] || continue
    name="$(basename "$dir")"
    slug="$(printf '%s' "$PROJECTS_ROOT/$name" | tr '/.' '--')"
    link "${dir%/}" "$CLAUDE_DIR/projects/$slug/memory"
  done
  install_project_skills_claude
}

install_codex() {
  echo "== Codex ($CODEX_DIR)"
  link "$REPO/global/AGENTS.md" "$CODEX_DIR/AGENTS.md"
  link "$REPO/adapters/codex/runtime.md" "$CODEX_DIR/ai-god-runtime.md"
  # Per-skill links: ~/.codex/skills also holds Codex's own .system skills.
  local skill rules
  for skill in "$REPO"/skills/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    link "${skill%/}" "$CODEX_DIR/skills/$(basename "$skill")"
  done
  link_personal_skills "$CODEX_DIR/skills"
  link_project_skills_flat "$CODEX_DIR/skills"
  prune_stale "$CODEX_DIR/skills"
  for rules in "$REPO"/adapters/codex/rules/*.rules; do
    link "$rules" "$CODEX_DIR/rules/$(basename "$rules")"
  done
  prune_stale "$CODEX_DIR/rules"
}

install_copilot() {
  local name="$1" dir="$2" skill
  echo "== $name ($dir)"
  link "$REPO/global/AGENTS.md" "$dir/copilot-instructions.md"
  link "$REPO/adapters/copilot/runtime.md" "$dir/ai-god-runtime.md"
  for skill in "$REPO"/skills/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    link "${skill%/}" "$dir/skills/$(basename "$skill")"
  done
  link_personal_skills "$dir/skills"
  link_project_skills_flat "$dir/skills"
  prune_stale "$dir/skills"
}

# The leak gate runs before every commit in this clone (.githooks/pre-commit → bin/check-public).
install_hooks() {
  local current
  current="$(git -C "$REPO" config --get core.hooksPath || true)"
  [ "$current" = ".githooks" ] && { [ "$MODE" = "check" ] && echo "ok      core.hooksPath=.githooks"; return 0; }
  case "$MODE" in
    check) echo "DRIFT   core.hooksPath is '${current:-unset}', expected .githooks"; drift=1 ;;
    dry-run) echo "config  core.hooksPath=.githooks" ;;
    *) git -C "$REPO" config core.hooksPath .githooks; echo "config  core.hooksPath=.githooks" ;;
  esac
}

install_hooks
if [ "$SELECT_CLAUDE" -eq 1 ]; then install_claude; fi
if [ "$SELECT_CODEX" -eq 1 ]; then install_codex; fi
if [ "$SELECT_COPILOT_CLI" -eq 1 ]; then install_copilot "GitHub Copilot CLI" "$COPILOT_CLI_DIR"; fi
if [ "$SELECT_COPILOT_VSCODE" -eq 1 ]; then install_copilot "GitHub Copilot in VS Code" "$COPILOT_VSCODE_DIR"; fi

if [ "$MODE" = "check" ]; then
  [ "$drift" -eq 0 ] && echo "all links in place" || { echo "drift found — run install.sh" >&2; exit 1; }
fi
