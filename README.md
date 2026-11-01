# ai-god

Single source of truth for my coding-agent setup: global instructions, skills with their
references, the cross-session workflow and per-runtime adapters. Shared content is written once and
linked into Claude Code, Codex, and GitHub Copilot CLI and VS Code. Runtime configuration directories
only hold symlinks into this repo.

Everything private — project memory, project rules and skills, company standards, personal settings
— lives in a git-ignored local overlay, `local/`, which is its own private repo. The public tree
works without it; `bin/check-public` keeps the overlay's material out of public commits.

## Architecture

```
                         SHARED — what, when, why
   global/AGENTS.md (invariants: git, facts, memory, overrides)
   skills/ai-workflow   (router: stage → skill, domain triggers, capability classes, plan lifecycle)
   skills/wf-*          (stages: plan, implement, review, peer-review, estimate, jira-task, worklog)
   skills/*             (domain knowledge: frontend-craft, figma-inspect, design-patterns, …)
   local/ (private overlay, git-ignored): memory/<project>, projects/<project> (rules.md + project
          skills, linked only into that project), company/, claude/settings.json, public-denylist.txt
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
    adapters/claude       adapters/codex       adapters/copilot
    Claude Code            Codex                 Copilot CLI + VS Code
    runtime + settings     runtime + rules       runtime capabilities
```

Three kinds of rule, three homes:

| Kind | Example | Lives in |
|---|---|---|
| Shared invariant | never invent facts · commit only on approval · never push · plan is self-contained · review is independent · worklog is never padded · architecture checked against the real code | `AGENTS.md`, skills |
| Runtime-specific | how to use subagents and models · browser tools · permissions and sandbox · worktrees · context signal · how a session is started | `adapters/<runtime>/runtime.md` (+ settings/rules) |
| Model-specific | planning and higher-risk review need frontier reasoning · implementation and routine review need a strong general model · mechanical work needs a fast one | `skills/ai-workflow/references/model-policy.md` by class; concrete models only in the adapters' "Model mapping" |

The workflow is the invariant; runtime and model are details. One runtime is used at a time and the
developer switches between them deliberately (month to month). A task started in one continues in the
other, using the task conversation and repository state. A planned task has one temporary plan file
while implementation is active; no state, handoff, segment, review, or escalation files exist.

`global/AGENTS.md` tells every runtime to load `ai-workflow` first. The router names one stage skill and
only the domain skills its triggers allow — "review this PR" loads `wf-review` (+ `frontend-craft`
review mode for React), not planning, estimation or worklog. Skill descriptions are always in
context, so they stay short and say when **not** to load.
The workflow never recommends another runtime; independence comes from a fresh session.

```
PLANNING ─▶ IMPLEMENTING ─▶ INDEPENDENT REVIEW ─▶ APPROVED FIXES (if any) ─▶ DONE
 FRONTIER      STRONG           FRONTIER decides each fix ─▶ STRONG implements it
                                fresh context; no implementation history
```

- Human setup: this file.
- Agent runbook (hand it to any supported runtime to install/verify for you): [`INSTALL.md`](INSTALL.md).

## Layout

| Repo path | What it is | Claude Code | Codex | Copilot CLI and VS Code |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Maintenance rules for this repo (read by sessions working inside it) | — | — | — |
| `global/AGENTS.md` | Global instructions | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | `~/.copilot/copilot-instructions.md` |
| `skills/<name>/` | Skills (`SKILL.md` + `references/` + `scripts/`) | `~/.claude/skills/<name>` (per skill; the directory itself is real, so claude.ai skill sync and `.trash` stay out of the repo) | `~/.codex/skills/<name>` (per skill, next to Codex's `.system`) | `~/.copilot/skills/<name>` |
| `adapters/claude/runtime.md` | How the shared workflow runs in Claude Code | `~/.claude/ai-god-runtime.md` | — | — |
| `adapters/codex/runtime.md` | How the shared workflow runs in Codex | — | `~/.codex/ai-god-runtime.md` | — |
| `adapters/copilot/runtime.md` | How the shared workflow runs in both Copilot interfaces | — | — | `~/.copilot/ai-god-runtime.md` |
| `adapters/_template/runtime.md` | Skeleton for a new runtime's adapter | — | — | — |
| `adapters/claude/settings.base.json` | Public Claude policy (deny `git push`, allow `bin/push-ai-god`, plugins); copied into `local/claude/settings.json` on first install | via `local/claude/settings.json` → `~/.claude/settings.json` (`--check` verifies every base entry is there) | — | — |
| `adapters/codex/rules/*.rules` | Codex execpolicy (forbid `git push`, allow `bin/push-ai-god`) | — | `~/.codex/rules/*.rules` | — |
| Copilot tool approvals | Runtime-managed; installer does not edit user settings | — | — | CLI flags and VS Code approval controls |
| `bin/push-ai-god` | The only push an agent may run: `main` of this repo and of `local/`, fast-forward only, after `bin/check-public` | run by path | run by path | run by path |
| `bin/check-public` | Leak gate: generic rules, the private denylist and identifiers from project checkouts; run by the pre-commit hook and the push script | run by path | run by path | run by path |
| `bin/lint-skills` | Frontmatter, size, link, router-coverage and leak-name checks for every skill | run by path | run by path | run by path |
| `bin/token-report` | Always-loaded, per-skill and per-flow instruction sizes (overlay names redacted) | run by path | run by path | run by path |
| `.githooks/pre-commit` | Runs `bin/check-public --staged` and `bin/lint-skills` (`core.hooksPath`, set by `install.sh`) | — | — | — |
| `evals/` | Fixed tasks, rubrics and results for measuring skill changes (`evals/README.md`) | not linked | not linked | not linked |
| `local/projects/<project>/rules.md` | Always-on project rules | read via `AGENTS.md` → Project layer | same | same |
| `local/projects/<project>/skills/<name>/` | Project skills | `~/Developer/<project>/.claude/skills/<name>` (only if git-ignored there) | `~/.codex/skills/<name>` | `~/.copilot/skills/<name>` |
| `local/projects/<project>/checkout` | Path of the project checkout; `bin/check-public` reads its identifiers | — | — | — |
| `local/projects/<project>/worktree-include` | Git-ignored paths `wt setup` clones into a new worktree (`skills/worktree`) | read by the script | same | same |
| `local/memory/<project>/` | Project memory, `MEMORY.md` index | `~/.claude/projects/<slug>/memory` (auto-loaded) | not linked — `AGENTS.md` tells the runtime to read it | not linked — `AGENTS.md` tells the runtime to read it |
| `local/company/` | Company standards the skills read when present (implementation standard, PR guide, estimation) | read via `AGENTS.md` → Local overlay | same | same |
| `local/public-denylist.txt` | Private regexes for `bin/check-public` (names, orgs, ticket prefixes, internal domains) | — | — | — |

Only `adapters/` and runtime permission files are runtime-specific. The Copilot adapter covers both
the CLI and the VS Code Agent Host; their model, context, and approval controls still differ.

Project-scoped skills inside a project repo (e.g. `<project>/.claude/skills`) stay in that repo and are not
mirrored here.

## Install on a new machine

```bash
git clone git@github.com:vnahornyi/ai-god.git ~/Developer/ai-god
```

```bash
~/Developer/ai-god/install.sh --dry-run
```

```bash
~/Developer/ai-god/install.sh
```

With no `--agent`, it installs for each detected runtime: Claude Code, Codex, the Copilot CLI on
`PATH`, and VS Code when its `code` command is on `PATH`. Pick explicitly with `--agent claude`,
`--agent codex`, `--agent copilot-cli`, `--agent copilot-vscode`, `--agent copilot` (both Copilot
interfaces), or `--agent all`.

- Existing real files are moved aside to `*.pre-ai-god`, never deleted.
- Projects outside `~/Developer`: `PROJECTS_ROOT=/path ./install.sh`.
- Non-default config dirs: `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, and `COPILOT_HOME` are respected for
  the CLI. The VS Code Copilot Agent Host uses `~/.copilot`.
- Restart the runtime after installing — it reads instructions and skills at session start.
- VS Code support here targets the GitHub Copilot Agent Host. VS Code's separate Local agent uses
  profile storage and is not configured by this installer.

## Verify

```bash
~/Developer/ai-god/install.sh --check
```

Prints `ok` / `DRIFT` / `STALE` per link and exits 1 on any drift. Run it after pulling a change that
adds, renames or removes a skill, rules file or memory dir — then `install.sh` to fix.

The Codex push ban can be checked on its own:

```bash
codex execpolicy check --rules ~/Developer/ai-god/adapters/codex/rules/ai-god.rules git push origin main
```

## Updating

Edit through the symlinks or directly here — it is the same file. The agent stages changes and
stops. Once the developer approves that staged set in chat, the agent commits and pushes it itself
with `bin/push-ai-god` (`global/AGENTS.md` → Git rule 7). This exception covers this repo and its `local/`
overlay only; in every other repo pushing stays the developer's.

`git push` itself stays blocked for agents everywhere, including here. The script takes no arguments,
runs `bin/check-public` on the public commits, pushes only `main` to `origin` in each of the two
repos, and refuses on a leak, when staged changes are uncommitted or when `origin/main` has diverged.

- New skill → `skills/<name>/SKILL.md`, then `install.sh` (Codex and Copilot use per-skill links).
- New project memory → `local/memory/<project>/MEMORY.md`, then `install.sh`.
- Project rules or skills → `local/projects/<project>/rules.md`, `local/projects/<project>/skills/<name>/`,
  plus `local/projects/<project>/checkout` with the checkout path, then `install.sh`. `<project>` is
  the directory name under `~/Developer`. Add the project's names and ticket prefix to
  `local/public-denylist.txt`.
- `~/.claude/settings.json` is `local/claude/settings.json`: the desktop app and plugin installs write
  into it, so a diff there is expected in the overlay repo. Public policy changes go to
  `adapters/claude/settings.base.json` and are copied into the local file.
- Rename or delete a skill → `install.sh` prunes dangling runtime links.

## Switching runtime (e.g. monthly)

1. In the old runtime, leave a concise task summary in the conversation. Keep the single plan file only if implementation is incomplete; no handoff file is needed.
2. Link the new runtime and verify:

   ```bash
   ~/Developer/ai-god/install.sh --agent copilot
   ```

   ```bash
   ~/Developer/ai-god/install.sh --check
   ```

3. First session in the new runtime: compare its adapter's "Model mapping" with the models it
   actually offers; update the table if it drifted (stage the change like any other).
4. Continue each open task from its task conversation and its one plan file, if it is still being implemented.

## Adding a runtime

When a new agent runtime appears, the skills do not change. Add:

1. `adapters/<runtime>/runtime.md` from `adapters/_template/runtime.md`, every section filled from the
   runtime's real tools and `--help`, with the verification date.
2. Its push restriction and sanctioned-script allowance in the runtime's native permission format
   under `adapters/<runtime>/`. If the runtime cannot enforce these rules, document that limitation
   in its adapter and preserve the approval prompts.
3. An `install_<runtime>` function in `install.sh` linking `global/AGENTS.md` (or the runtime's instruction
   file), each skill, and the adapter as `ai-god-runtime.md`; link a permission file when the runtime
   has one, and add the runtime to `--agent` and auto-detection.
4. A row in the Layout table above and in `global/AGENTS.md` → "Runtime adapter".
5. The acceptance run: verify a cold implementation can continue from the single task plan, then run an independent review from a self-contained prompt with no implementation history.

## Writing agent-neutral skills

All supported runtimes read the same `SKILL.md` format: YAML frontmatter with `name` and `description`, a
markdown body, relative links into `references/` and `scripts/`.

1. **Frontmatter:** only `name` (kebab-case, matches the dir) and `description`. Keep `description`
   **≤ 1024 characters** — the stricter limit wins.
2. **Name the capability, not the tool.** "Spawn a subagent and wait for it", "load the
   `frontend-craft` skill", "run JS in the signed-in browser tab" — not `Agent`,
   `subagent_type`, `SendMessage`, `mcp__claude-in-chrome__*`, `spawn_agent`.
3. **When the tool call genuinely matters, put it in both adapters**, not in the skill: the skill
   names the operation ("spawn a cold reviewer"), each `adapters/<runtime>/runtime.md` says how, and
   what to fall back to when the capability is missing.
4. **Capability classes, never model names.** A stage "requires FRONTIER_REASONING"; the adapters'
   "Model mapping" says which model that is today. Updating a model touches two tables, no skill.
5. **Instruction files:** say `AGENTS.md` / `CLAUDE.md` (projects may have either), and "global
   agent instructions" for this repo's `global/AGENTS.md`.
6. **Context that must survive a session** goes into one compact prompt in the conversation (or the
   task's single plan file) per `ai-workflow` → Moving context — never "the next agent will know",
   never a handoff file.
7. **Scripts** are plain POSIX-ish bash/python with no agent dependency.

Check a skill change mechanically before staging (the pre-commit hook runs it too):

```bash
~/Developer/ai-god/bin/lint-skills
```

It enforces the frontmatter, size and link rules from the root `AGENTS.md` → "Changing a skill", the
router coverage, and the leak scan for runtime tool and model names. Allowed hits: the calibration note
in `wf-estimate/references/estimation.md` (it names the model the estimates were measured on) and the
TemPad Dev tool names in `figma-inspect` (an MCP server, the same in every runtime).

## Project-local paths the skills write

`wf-plan` writes one temporary plan per planned task under the project's `.claude/plans/` (a
project's planning skill may name another git-ignored path, e.g. `app/.claude/plans/` in a monorepo). No
workflow state, segment, handoff, review or escalation files exist. Worklog config lives in
`.claude/worklog.json`, governed by `wf-worklog`. `.claude/` is a directory name, not a Claude
dependency — all supported runtimes share it.
