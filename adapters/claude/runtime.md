# Runtime adapter — Claude Code

HOW the shared workflow (`skills/ai-workflow`) runs in Claude Code. Shared rules are not repeated
here; if something below reads like a workflow rule, it belongs in the skill instead.

Verified against Claude Code desktop on 2026-10-13 (Agent tool schema with `model` and `effort`;
model list in the system prompt: Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5; effort levels in the
app: `low · medium · high · extra · max · ultracode`). Re-verify when the model list changes.

## Model mapping

| Class | Main session (picker) | Subagent (`model`, `effort`) | Notes |
|---|---|---|---|
| FRONTIER_REASONING | Opus 5.5 · medium | `opus`, `medium` | Planning, architecture decisions, independent review and its fix decisions, escalation questions |
| FRONTIER_REASONING — high-risk | Opus 5.5 · high | `opus`, `high` | Security, data-loss, architectural or ambiguous review/escalation |
| STRONG_GENERAL — `interactive` run mode | Sonnet 5.5 · medium | `sonnet`, `medium` | Interactive implementation and fixes: fastest measured implementer (~27 s per eval task, 77/78 — `evals/results/2026-10-14-models.md`) |
| STRONG_GENERAL — `background` run mode (**trial since 2026-10-13**) | Haiku 5.5 · extra | `haiku`, `xhigh` | Planned work the developer does not wait on: ~1.7 min, ≈1/30 of Opus cost per eval task, 75/78. Trial: **one** failed meaningful attempt ends the run; the developer decides whether to rerun on Opus 5.5 medium. No ultracode |
| FAST_ROUTINE | Haiku 5.5 · low | `haiku`, `low` | Mechanical subagents; inline is usually cheaper |

Alternative for implementation: Opus 5.5 · medium. Sonnet 5 (not 5.5) could not implement from a
clear plan — do not map it. Fable 5.1 is not available to this developer. `wf-retro` logs every
reviewed task with its implementer in project memory `implementation-log` and advises when a mapping
should change.

Ultracode is not an effort level: it makes the session orchestrate workflows of many subagents for
every substantive task, so it multiplies tokens and time and erases the cheap model's advantage. Use
the `ultracode` keyword in a single prompt for fan-out work (repo-wide audits, many-file migrations)
only.

Effort names: the app's `extra` is `xhigh` in the Agent tool; the Agent tool's `effort` accepts
`low…max`. The main session's model and effort are the developer's choice; `settings.json` →
`effortLevel` is the default (`medium`). The start instruction tells them which to pick.

## Run modes

The plan's `Run mode` (`wf-plan`) picks the implementer; `wf-implement` → `references/background.md`
holds the rules for a background run.

| Run mode | Implementer | Where it runs |
|---|---|---|
| `interactive` | Sonnet 5.5 · medium | The developer's session (switch the model in the picker), or a new session opened with it |
| `background` | Haiku 5.5 · extra (`xhigh`) | Form A or B below — never the developer's working tree |

Both forms start from a worktree made by the `worktree` skill — `wt new <branch> --from <base>
--no-open`, with the base the developer named when asked — so it sits next to the repository. Claude Code's own
worktrees (`--worktree`, the desktop worktree option, `isolation: "worktree"`) live under
`.claude/worktrees/` and branch from the repository's **default branch** unless the setting
`worktree.baseRef` is `"head"`; use them only for work based on the default branch, and run
`wt setup` inside before verifying.

**Form A — from the current session (default).** The main session creates the worktree, spawns the
run and stays free for the developer; a notification arrives when it ends:

```text
wt new <branch> --from <base> --no-open
Agent tool:
  subagent_type: "general-purpose"
  model: "haiku"
  effort: "xhigh"
  run_in_background: true
  prompt: <wf-implement → references/delegation.md prompt, with "work only inside <absolute worktree
           path>", the plan's absolute path in the main checkout, and "follow wf-implement →
           references/background.md">
```

The orchestrating session then reads the worktree's diff, stages there
(`git -C <worktree> add -- <files>`) and hands the staged set back under the Git rules.

**Form B — a separate desktop session**, when the developer wants to watch the run or it is long:
run `wt new <branch> --from <base>` (it also opens the worktree in VS Code), start a new desktop session with that
worktree folder as its folder, pick Haiku 5.5 · extra, and send:

```text
Implement <absolute plan path> in background run mode (wf-implement → references/background.md).
Do not create workflow files.
```

That session stages in its worktree; the app notifies when it finishes. Project skills git-ignored
in the main checkout still load there: Claude Code reads them through from the main checkout.

Developer convenience: `alias wt=~/Developer/ai-god/skills/worktree/scripts/wt` in the shell profile
(the developer's change to make).

## Capability discovery

At session start, from what this session actually has — never from memory:

| Capability | How to tell |
|---|---|
| Current model | The system prompt states the model; effort is not visible — assume the developer's default (`settings.json` → `effortLevel`) |
| Review engine | The built-in `code-review` skill (`/code-review`), report-only: never `--comment`, `--fix` or `--post` |
| Jira / Confluence | Atlassian MCP (`getAccessibleAtlassianResources` once for the cloud id, then `getJiraIssue`, `searchJiraIssuesUsingJql`, `createJiraIssue`) |
| Figma | Figma's Dev Mode MCP server (read tools only, see `figma-inspect`), or the source the overlay's `figma-source.md` names; third-party Figma-to-code and design-in-Figma skills are not used |
| Subagents | `Agent` tool present; its `model` enum lists the aliases available |
| Deferred tools (browser, MCP) | Listed by name in system reminders; load schemas in one batch with `ToolSearch` before calling |
| Browser, signed-in | `mcp__claude-in-chrome__*` (real Chrome, logged-in sessions) |
| Browser, in-app | `mcp__Claude_Browser__*` — not used: the global instructions require the external browser, localhost included |
| MCP servers | `mcp__<server>__*` tools, plus server instructions in the system prompt |
| Git, filesystem | `Bash`, `Read`, `Edit`, `Write` |
| Worktrees | The `worktree` skill's `wt` script (sibling of the repo, branched from `HEAD`); Claude Code's own (`isolation: "worktree"`, `EnterWorktree`) branch from the default branch — see Run modes |
| Background / parallel | `Agent` runs in background by default; several `Agent` calls in one message run in parallel |
| Context / usage signal | See below |

## Subagents

| Operation | Claude Code |
|---|---|
| Spawn a code-writing subagent | `Agent` with `subagent_type: "general-purpose"`, `model` and `effort` per class |
| Spawn a read-only investigator | `Agent` with `subagent_type: "Explore"` (cheaper, cannot edit) |
| Wait for the result | `run_in_background: false` when the next step depends on it |
| Send a correction to the same agent | `SendMessage` to its id or name — context intact, far cheaper than a new spawn |
| Isolated tree for a parallel segment | `isolation: "worktree"` (auto-cleaned when unchanged; merging back is on you) |
| Escalate one question | `Agent` with `model: "opus"`, `effort: "medium"` (`"high"` for high-risk), prompt = one self-contained question with verified evidence; answer only, do not edit code |
| De-escalate mechanical work | `Agent` with `model: "haiku"`, `effort: "low"` — or do it inline when it is a few commands |

A subagent starts cold: nothing of this conversation reaches it. Do not rely on it loading project
instructions or skills on its own — the brief names every rule file and skill it must read. Every brief carries the Git rule that subagents never stage, commit
or push.

## Cold reviewer

Independent review in the same runtime without a new session (developer said `stay`):

```text
Agent tool:
  subagent_type: "general-purpose"
  model: "opus"
  effort: "medium"            # "high" for high-risk changes
  run_in_background: false
  prompt: "You are the independent reviewer. Load the wf-review skill and follow it. Scope: <working
           tree | base..head | PR URL>. Task: <request and acceptance criteria, neutral>. Sources:
           <Jira key, docs ids> — retrieve them yourself. Project: <name>; styles were
           <developer-owned | assigned to the agent>. Do not edit files, stage, commit, push or spawn
           agents. Return findings and what you could not verify."
```

Pass only task facts and source references, never the implementer's analysis or candidate findings.
Use no file-backed handoff or review artifact. Label reduced capability or same-context review
honestly; never call an implementer's own self-check independent.

## Browser

Always Claude in Chrome — the developer's real, signed-in browser — for every URL, including a local
dev server on `localhost`. Load `tabs_context_mcp`, `navigate`, `javascript_tool`, `computer`,
`get_page_text` in one `ToolSearch` batch; start with `tabs_context_mcp {createIfEmpty: true}`, work
in a new tab and close it when done. The in-app browser is not used.

Quirks the shared recipes rely on: `javascript_tool` supports top-level `await` in this version, but
output truncates at a few thousand characters; strings that mention browser storage primitives are
blocked. Synthetic DOM events do not reach apps that check `isTrusted` (Figma) — use `computer`
clicks. `computer` does `wait` and `screenshot`.

## Context and usage signal

- The session receives a running token budget ("tokens left") and is told when context will be
  summarised. Treat **less than ~25% of the context window left, or an announced compaction**, as
  boundary trigger 6: summarize the exact next action, completed work, and open decisions in the
  conversation. *Implementation artifact — this threshold is a starting point, not measured.*
- Compaction keeps the session alive but drops detail: after one, re-read the task request and its plan if implementation is still underway, then inspect
  the current diff before continuing.
- Usage (plan limits) is not visible to the agent. When the developer mentions limits, treat it as
  trigger 6.

## Start a session

Claude Code has no agent-side way to open a session. The start instruction is for the developer:

```
Open a new Claude Code session in <repo> (desktop: new session; terminal: `claude`),
pick <model for the class> at <effort>, and send:
"Continue <task> from <plan path, if implementation is still underway>; inspect the current diff and do not create workflow files."
```

When `command -v claude` finds the CLI, the terminal form is
`cd <repo> && claude --model <alias> "<same prompt>"` — *unverified here: the CLI was not installed on
2026-09-16; check `claude --help` before printing it.*

## Permissions, plugins and hooks

- `~/.claude/settings.json` is the local overlay's `claude/settings.json`, which carries every entry of
  the public policy `adapters/claude/settings.base.json` (`install.sh --check` verifies it) plus
  personal keys such as `autoMode`, which Claude Code reads only from user settings: `git push`,
  `git add .`/`-A`, amend, `--no-verify`, rebase, `reset --hard`, `git stash` (push, save, pop, apply, drop, clear)
  and branch deletion denied — stash push added after two eval runs stashed to test old code
  (flags written after other arguments are covered for `add` and `commit` only). Also denied: staging
  or committing without naming files (`commit -a`, `add -u`, `add :/`), hook bypass through `git -c`,
  `gh pr merge`/`close` and `gh api` writes; `gh api` reads and GraphQL queries stay allowed. These
  are prefix patterns, so a reordered or wrapped command can still slip past: the Git rules stay binding,
  `bin/push-ai-god` allowed. The desktop app and `claude plugin install` write into it (theme,
  `switchModelsOnFlag`, `enabledPlugins`, marketplaces), so those diffs land in the overlay repo —
  commit there what reproduces the setup, and copy an entry into the base when it is public policy.
- `switchModelsOnFlag: false` — when a request is flagged and refused, do not switch the session to
  a fallback model automatically.
- No hooks of our own. Rely on the conversation summary for continuity; no handoff file.

## Skills and instructions

- Skills: `~/.claude/skills/<name>` → `ai-god/skills/<name>` (per-skill links). claude.ai skill sync is off (`syncClaudeAiSkills: false` in the overlay's
  settings): only this repo's skills, the plugins' and the app's built-in ones are listed. Invoked with the `Skill` tool by name. Project
  skills: `~/Developer/<project>/.claude/skills/<name>` → `ai-god/local/projects/<project>/skills/<name>`.
- Global instructions: `~/.claude/CLAUDE.md` → `ai-god/global/AGENTS.md` (the root `AGENTS.md` holds
  only this repo's maintenance rules, so a session inside ai-god loads the global file once). Project `CLAUDE.md` and
  `AGENTS.md` files are read from the repo.
- Project memory: auto-loaded from `~/.claude/projects/<slug>/memory` → `ai-god/local/memory/<project>`.
