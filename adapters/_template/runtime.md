# Runtime adapter — <Runtime name>

HOW the shared workflow (`skills/ai-workflow`) runs in <Runtime>. Copy this file to
`adapters/<runtime>/runtime.md` and fill every section from what the runtime actually does — tool
schemas, `--help` output, the model list the runtime shows. Do not repeat shared rules here; if a line
reads like a workflow rule, it belongs in the skill.

Verified against <runtime + version> on <YYYY-MM-DD>: <what you checked>. Re-verify after an update.

## Model mapping

| Class | Model | Effort | Notes |
|---|---|---|---|
| FRONTIER_REASONING | | high | planning, independent review, escalation questions |
| STRONG_GENERAL | | medium | implementation, fixes — must be good enough to implement a plan unaided |
| FAST_ROUTINE | | low | mechanical work; "none — run inline" is a valid answer |

Where the main session's model/effort is chosen (by the developer or the agent), and how a subagent's
model is set.

## Run modes

| Run mode | Implementer | Where it runs |
|---|---|---|
| `interactive` | | the developer's session |
| `background` | | a separate worktree — how it is started and how it reports back |

## Capability discovery

| Capability | How to tell in this runtime |
|---|---|
| Current model and effort | |
| Subagents | |
| Browser, signed-in | |
| MCP servers | |
| Git, filesystem, sandbox | |
| Worktrees | |
| Background / parallel | |
| Context / usage signal | |
| Review engine (built-in report-only code review, if any) | |
| Jira / docs MCP | |
| Figma (read-only design MCP) | |

## Subagents

| Operation | <Runtime> |
|---|---|
| Spawn a code-writing subagent with no forked context | |
| Spawn a read-only investigator | |
| Wait for the result | |
| Send a correction to the same agent | |
| Release an agent | |
| Isolated tree for a parallel segment | |
| Send one focused question to a higher-capability agent (self-contained prompt; no file) | |

No subagents → the fallback in `model-policy.md` applies; say so here.

## Cold reviewer

The exact call that starts an independent reviewer (it loads `wf-review`) from a self-contained prompt containing the task,
acceptance criteria, authoritative documentation references, diff range/files, and PR link/body when
available. Do not create a review handoff file. If the runtime cannot guarantee a context-free
reviewer, write "not available — a new session is required".

## Browser

Which tool reaches the developer's signed-in browser (Jira/Tempo, Figma), how to load it, and its
quirks (promises, truncation, blocked patterns). Every URL, `localhost` included, goes to that
external browser. "Not available" is a valid answer; wf-worklog
then asks the developer to paste data, and figma-inspect stops and asks for the values.

## Context and usage signal

What the agent can observe about remaining context and usage, what counts as boundary trigger 6, and
what to re-read after compaction.

## Start a session

The exact command or UI steps for the developer to start a fresh session with a given model, effort
and first message. Include the non-interactive form if the runtime has one.

## Permissions

How `git push` is forbidden and `bin/push-ai-god` allowed in this runtime (settings, rules, policy
file), and anything the sandbox blocks that the workflow needs (e.g. writing `.git`).

## Skills and instructions

Where the runtime reads global instructions, skills, project skills (local overlay `projects/<project>/skills`) and
project memory, and how `install.sh` links them.
