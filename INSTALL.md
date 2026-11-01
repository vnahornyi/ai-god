# Install runbook — for the agent

You are a coding agent asked to install, repair or verify the
`ai-god` setup on this machine. Follow these steps in order. The human-facing version is
`README.md`; read it only if a step here is unclear.

## Ground rules

- **Never push, never commit** in this repo while installing. Installing changes symlinks in the
  agents' config dirs, not files in the repo.
- **Never delete** an existing config file. `install.sh` moves real files to `*.pre-ai-god`; leave
  those for the developer to review.
- **Do not edit** runtime settings, VS Code profile settings, auth files, or anything under `.system`.
- Anything you are unsure about — stop and ask. A wrong link is silent: the agent just loads stale
  instructions.

## 1. Locate the repo

```bash
test -d ~/Developer/ai-god/.git && git -C ~/Developer/ai-god status -sb
```

Missing → ask the developer before cloning:
`git clone git@github.com:vnahornyi/ai-god.git ~/Developer/ai-god`.

The private overlay is a separate repo cloned into `~/Developer/ai-god/local` — only the owner has
it; ask the developer for its URL. Without it the install links the public core only (memory and
project layers are skipped, and a personal `local/claude/settings.json` is created from the base).

Dirty or behind → report it; do not pull, stash or reset on your own.

## 2. Decide which agents

Default is every runtime detected on the machine. If the developer named one, pass `--agent claude`,
`--agent codex`, `--agent copilot-cli`, `--agent copilot-vscode`, `--agent copilot` (both Copilot
interfaces), or `--agent all`. Note which runtime **you** are — you will ask the developer to restart
it at the end. The VS Code target is GitHub Copilot's Agent Host, not VS Code's separate Local agent.

## 3. Preview

```bash
~/Developer/ai-god/install.sh --dry-run
```

Show the developer the output. Call out every `move` line explicitly — those are real files that
will be moved aside to `*.pre-ai-god`. Wait for a yes if there is any `move`; otherwise proceed.

## 4. Install

```bash
~/Developer/ai-god/install.sh
```

Add `--agent …` if chosen in step 2. Add `PROJECTS_ROOT=…` if the developer's projects are not in
`~/Developer`.

## 5. Verify

```bash
~/Developer/ai-god/install.sh --check
```

Must end with `all links in place`. Then spot-check what actually loads:

- **Claude Code:** `ls -la ~/.claude/CLAUDE.md ~/.claude/skills ~/.claude/settings.json ~/.claude/ai-god-runtime.md`
- **Codex:** `ls -la ~/.codex/AGENTS.md ~/.codex/skills ~/.codex/rules ~/.codex/ai-god-runtime.md`, and confirm the push ban:
  `codex execpolicy check --rules ~/.codex/rules/ai-god.rules git push` → `"decision":"forbidden"`.
  If `codex` is not on `PATH`, say so and skip this check rather than hunting for the binary.
- **GitHub Copilot CLI:** `ls -la "${COPILOT_HOME:-$HOME/.copilot}"/copilot-instructions.md "${COPILOT_HOME:-$HOME/.copilot}"/skills "${COPILOT_HOME:-$HOME/.copilot}"/ai-god-runtime.md`.
- **GitHub Copilot in VS Code:** `ls -la ~/.copilot/copilot-instructions.md ~/.copilot/skills ~/.copilot/ai-god-runtime.md`; select the Copilot Agent Host and confirm the global instructions appear in its references.

Every `SKILL.md` must still parse — frontmatter with `name` and a `description` ≤ 1024 chars:

```bash
for f in ~/Developer/ai-god/skills/*/SKILL.md ~/Developer/ai-god/local/projects/*/skills/*/SKILL.md; do awk '/^description:/{sub(/^description: /,""); print length($0), FILENAME; exit}' "$f"; done
```

Then read the runtime adapter for the runtime you are (`~/.claude/ai-god-runtime.md`,
`~/.codex/ai-god-runtime.md`, or `~/.copilot/ai-god-runtime.md`) and check its "Model mapping"
against the models this session can actually see. Report any model in the table that is not
available — do not edit the table yourself.

## 6. Report

Tell the developer, briefly:

1. Which agents were linked, and the `--check` result.
2. Any `*.pre-ai-god` files created, with paths — they decide whether to delete them.
3. Anything skipped and why.
4. **Restart required:** instructions and skills load at session start, so the current session
   (yours included) still runs on the old ones.

## Repair

`--check` shows `DRIFT` or `STALE` → run `install.sh` again (same flags), then `--check`. A `DRIFT`
on a real file means something replaced a symlink with a copy: diff the copy against the repo file
and show the developer the difference before re-running, so no local edit is lost.
