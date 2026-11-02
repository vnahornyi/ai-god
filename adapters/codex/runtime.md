# Runtime adapter — Codex

HOW the shared workflow (`skills/ai-workflow`) runs in Codex. Shared rules are not repeated here.

Tool behaviour verified against codex-cli 0.155.0-alpha.9.2 on 2026-09-21: the available model and
subagent-tool lists in this session, `codex --help`, `codex exec --help`, and the local exec policy.
Re-verify after a Codex update.

## Model mapping

Target plan: **ChatGPT Plus**. This is a routing default, not an absolute quality ranking: use the
lowest capability and reasoning effort that can safely perform the next stage. Confirm the model list
and account limits at the first Codex session of a month.

| Class | Model | `model_reasoning_effort` | Notes |
|---|---|---|---|
| FRONTIER_REASONING | `gpt-5.6-sol` | `medium` | Default for planning, architecture decisions, complex investigation, and escalation questions |
| FRONTIER_REASONING — high-risk review or critical escalation | `gpt-5.6-sol` | `high` | Use for security, data-loss, architectural, or materially ambiguous decisions |
| STRONG_GENERAL | `gpt-5.6-terra` | `medium` | Default for implementation from a verified plan, ordinary fixes, refactors, tests, and routine debugging |
| STRONG_GENERAL — complex implementation | `gpt-5.6-terra` | `high` | Only for unresolved cross-system behaviour, repeated failed attempts, or materially conflicting constraints |
| FAST_ROUTINE | `gpt-5.6-luna` | `low` | |

Sol is for planning, verification, and independent review (it decides each finding's fix), not ordinary implementation; Terra implements the decided fixes. Terra High is an
escalation within normal engineering, not a default for a large but well-specified task. Luna may
format, transform, summarize established facts, or collect scripted evidence; it does not make
architectural decisions. Do not use `ultra` for workflow stages: its automatic delegation is not fenced by the task scope or the Git rules.

## Run modes

Both run modes (`wf-plan`) use the STRONG_GENERAL row until a cheaper implementer is measured with
`evals/`. A `background` run follows `wf-implement` → `references/background.md`: create its worktree with the `worktree` skill
(`wt new <branch> --from <base> --no-open`, base asked from the developer, approval needed under the sandbox) and start a new Codex session in
`~/Developer/<repo>.worktrees/<branch>` with the plan's absolute path.

## Capability discovery

| Capability | How to tell |
|---|---|
| Current model and effort | Session header / environment context; `~/.codex/config.toml` defaults |
| Subagents | `spawn_agent` tool present (feature `multi_agent`). Its description lists "Available model overrides" and reasoning efforts — use only those |
| Browser, signed-in | Browser plugin (`browser@openai-bundled`) or computer-use tools, when listed |
| MCP servers | Tools from `[mcp_servers.*]` and plugins, as listed in the session |
| Git, filesystem | Shell tool and `apply_patch`, subject to the sandbox mode |
| Sandbox / approvals | Environment context states sandbox and approval policy; network is usually off in `workspace-write` — `git fetch`/push and package installs need approval. **`.git` is not writable under `workspace-write`** (observed 2026-09-16: `git add` fails on `index.lock`), so staging and committing need an approved escalation — request it when the complete task diff is ready; in `codex exec` without approvals, leave the change unstaged and report the next action in the conversation |
| Worktrees | Nothing built in — the `worktree` skill's `wt` script (needs approval under the sandbox) |
| Background / parallel | `spawn_agent` runs in parallel; `wait_agent` blocks |
| Context / usage signal | See below |

## Subagents

| Operation | Codex |
|---|---|
| Spawn a code-writing subagent | `spawn_agent` with `task_name`, the brief as message, `fork_turns: "none"`, `model`/`reasoning_effort` per class only when it differs from the parent |
| Spawn a read-only investigator | `spawn_agent` with an inspect-only brief — there is no read-only agent type, so the brief carries the fence |
| Wait for the result | `wait_agent` on its name, only when the next step is blocked on it |
| Send a correction | `send_message` while the agent is active; `followup_task` to deliver a correction and start an idle agent |
| Continue a finished agent | `followup_task` with the next self-contained instruction |
| Release | No explicit release operation; a completed agent stays idle and needs no action |
| Escalate one question | `spawn_agent` with `fork_turns: "none"`, `model` + `reasoning_effort` for FRONTIER_REASONING, message = one self-contained question with verified evidence; answer only, do not edit code |

Codex specifics that change how the shared skill is applied:

- **Always pass `fork_turns: "none"` explicitly** for workflow subagents — do not rely on the
  default. Briefs are self-contained; `"all"` would hand the subagent the whole conversation, which
  breaks reviewer independence and inflates cost.
- **Subagents can spawn their own subagents.** Every brief states "do not spawn agents". Set
  `[agents] max_depth` only if the developer asks; the brief is the fence.
- **Codex subagents may work in a forked workspace.** After a segment returns, confirm the changes are
  in the main working tree (`git status --porcelain`) before the review gate; if they are not, ask the
  agent for the changed paths and apply its diff, never re-implement.
- The `spawn_agent` guidance says not to spawn unless instructions ask for delegation.
  `wf-implement` allows narrowly scoped delegation when its cost/benefit rule is met; other skills do not delegate by default.

## Cold reviewer

Independent review with `stay` uses a cold subagent. Do not fork the implementation conversation.
Send a concise, self-contained prompt with only the task request and acceptance criteria, ticket and
authoritative MCP references, exact diff range and changed-file scope, PR reference (or that no PR
exists), and the review contract. Tell the reviewer not to open or pixel-compare the same Figma file;
visual parity is human QA. Use FRONTIER_REASONING (`high` for the high-risk cases in `model-policy.md`). The reviewer retrieves docs and PR description itself, then returns the review in its response. Do not write a review handoff or artifact file.

```text
You are the independent reviewer. Do not spawn agents or edit files. Review <diff scope> against
<task request and acceptance criteria>. Retrieve <ticket/docs references> through the configured
MCP and inspect <PR reference> (or note no PR exists). Load the wf-review skill and follow it.
Check the implementation, business rules, contracts, documented design behavior, regressions, and
PR description claims. Do not reopen Figma or compare pixels. Return only actionable findings plus
what you checked and could not verify.
```

Always use `fork_turns: "none"` for this subagent. Do not pass implementation conclusions,
confidence, or candidate issues. If independent review is unavailable, do not call a same-context
self-check independent.

## Browser

Browser and computer-use capability is session-dependent. At session start, inspect the listed tools
for a signed-in tab, navigation, page text or JavaScript evaluation, and screenshots. If none can use
the developer's logged-in session, the Jira and Figma recipes do not apply — ask the developer to paste
the timesheet (wf-worklog fallback) or to provide the design (figma-inspect stops).
Use the external, signed-in browser for every URL, `localhost` included.

## Review engine

Codex has no built-in report-only review skill mapped here yet: `wf-review` and `wf-peer-review` do
the bug hunt themselves per the review contract. *Unverified — check `codex --help` for a review
command before relying on this line.*

## Context and usage signal

- Codex tells the model how many tokens are left in the current context window, and compacts
  automatically near the limit (`model_auto_compact_token_limit`). Treat **less than ~25% of the
  window left** as boundary trigger 6. *Implementation artifact — starting threshold, not measured.*
- After a compaction, re-read the task request and its plan if implementation is still in progress; inspect the current diff for completed work.
- When `get_usage_limits` is available, read it for account-level remaining allowance; otherwise the
  developer's `/status` report is the signal. A low allowance or a developer mention of limits is
  trigger 6.

## Start a session

The developer starts the runtime. Continue from the task request and, if implementation is still
underway, its single plan file. For a fresh implementation session, include the plan path in the
prompt. For review, use the cold-review prompt above; do not pass the plan file — the reviewer
establishes intent from the task and its sources.

## Permissions

- `adapters/codex/rules/ai-god.rules` → `~/.codex/rules/`: `git push`, `gh repo sync`, `git add .`/`-A`,
  `git commit --amend`/`--no-verify`, `git rebase`, `git reset --hard`, `git stash drop`/`clear` and
  `git branch -D`, `git stash push`/`save`/`-u` forbidden (a bare `git stash` cannot be matched apart from
  `git stash list`); `bin/push-ai-god` allowed. Prefix rules match leading tokens only, so a
  flag placed after other arguments is not caught — the Git rules still apply. *Unverified on this
  machine: the `codex` CLI was not installed on 2026-11-01; check with
  `codex execpolicy check --rules adapters/codex/rules/ai-god.rules git rebase`.*
- `config.toml` is the developer's file; installers never edit it. Optional profiles, if the
  developer wants one-word starts, go there by hand:

  ```toml
  [profiles.sol-frontier]
  model = "gpt-5.6-sol"
  model_reasoning_effort = "medium"

  [profiles.sol-review]
  model = "gpt-5.6-sol"
  model_reasoning_effort = "high"

  [profiles.terra-implementation]
  model = "gpt-5.6-terra"
  model_reasoning_effort = "medium"

  [profiles.terra-complex]
  model = "gpt-5.6-terra"
  model_reasoning_effort = "high"

  [profiles.luna-mechanical]
  model = "gpt-5.6-luna"
  model_reasoning_effort = "low"
  ```

## Skills and instructions

- Skills: `~/.codex/skills/<name>` → `ai-god/skills/<name>`, one link per skill next to Codex's
  `.system` skills. Mention by name (`$ai-workflow`) or let the description trigger it.
- Global instructions: `~/.codex/AGENTS.md` → `ai-god/global/AGENTS.md`; project `AGENTS.md` files are read
  from the repo (`CLAUDE.md` is not, unless `project_doc_fallback_filenames` lists it).
- Project memory: not auto-loaded — `AGENTS.md` → "Project memory" tells the agent to read it.
