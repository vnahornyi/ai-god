# Runtime adapter — GitHub Copilot CLI and VS Code

HOW the shared workflow (`skills/ai-workflow`) runs in GitHub Copilot CLI and the Copilot Agent Host
in VS Code. Shared rules are not repeated here.

Verified against official GitHub and VS Code documentation on 2026-10-03. The `copilot` CLI is not
installed in this environment, so CLI commands, the available model list, and permission behavior
could not be checked live. Re-verify after a CLI, extension, or VS Code update.

## Model mapping

Copilot model availability depends on the signed-in account, plan, organization policy, and runtime
version. Choose from the current `/model` list in the CLI or the model picker in VS Code; do not pin
a model name here unless it has been confirmed in the active account.

| Class | Model selection | Effort |
|---|---|---|
| FRONTIER_REASONING | Select the strongest reasoning/coding model currently offered. Ask the developer if the ranking is unclear. | Select the highest reasoning option only when the runtime exposes it. |
| STRONG_GENERAL | Select a capable general coding model currently offered. | Use the normal/default setting unless the task needs escalation. |
| FAST_ROUTINE | Select the fastest or lowest-cost model currently offered. | Use the lowest setting when available. |

Model names, reasoning controls, and billing vary. Do not treat `Auto` as a guaranteed capability
class; confirm what it selected when the class matters.

## Run modes

Both run modes (`wf-plan`) use the STRONG_GENERAL row. A `background` run follows `wf-implement` →
`references/background.md` in a worktree made with the `worktree` skill (`wt new <branch> --from <base>`, base asked from the developer, which
also opens it in VS Code); this adapter has no stable background-agent API to start the run.

## Capability discovery

| Capability | How to tell |
|---|---|
| Current model and effort | CLI: `/model` shows available choices. VS Code: check the model picker and any exposed reasoning control. |
| Subagents | Custom agents are available in both surfaces. Invocation is model-driven; the set of agents/tools shown in the active session is authoritative. |
| Browser, signed in | Not available by default. CLI computer use is a separate opt-in capability and does not imply access to the developer's signed-in Chrome tab. |
| MCP servers | Inspect the current session's tool list or tool picker; availability depends on the active configuration and account. |
| Git, filesystem, sandbox | CLI shell and VS Code agent tools operate on the selected local workspace, subject to tool approvals. Do not assume a filesystem sandbox. |
| Worktrees | The `worktree` skill's `wt` script; VS Code's own worktree UI also works, followed by `wt setup` |
| Background / parallel | Custom-agent/subagent routing is model-driven; there is no stable user-facing wait/progress API shared by the CLI and VS Code. |
| Context / usage signal | CLI: `/context` inspects context and `/compact` summarizes it. VS Code: use the chat context indicator and start a fresh chat when the history is no longer reliable. Account usage/limits depend on the plan. |

## Subagents

Copilot custom agent definitions use `.agent.md` files. User-level agents live in
`~/.copilot/agents/`; repository agents live in `.github/agents/`. In the CLI, `/agent` opens the
agent picker, and `copilot --agent <agent-id> --prompt "..."` selects an agent for a separate
invocation. In VS Code, use the Agent Customizations editor and the active Copilot Agent Host.
Subagents can be invoked by the main agent; VS Code agent definitions must expose the `agent` tool
and allowed `agents` in their frontmatter for that route.

The runtime does not provide a separate stable API for waiting on a child, sending it a correction,
or isolating a worktree. If the current session does not offer the required agent/tool capability,
follow the inline fallback in `skills/ai-workflow/references/model-policy.md`.

## Cold reviewer

Do not use a handoff that carries the implementation conversation as an independent review. Start a
new CLI invocation or a blank VS Code chat and provide only the task, acceptance criteria, exact
diff/files, and documentation references, and tell it to load `wf-review`. A custom reviewer agent may be selected if one is already
configured; this adapter does not create one. In CLI subagent use, repository instructions are not
inherited by default; set `include-custom-instructions: true` on a reviewer agent when those rules
must apply.

## Browser

Neither surface is a connector to the developer's signed-in external browser. If the active session
does not show a browser tool backed by that browser, use the relevant skill's fallback: ask the
developer to provide the needed page contents or values. CLI computer use is documented separately
and may require explicit enablement and OS permissions. Every URL, `localhost` included, belongs in the developer's external browser,
never an in-editor preview.

Review engine: none mapped — `wf-review` and `wf-peer-review` do the bug hunt themselves.
Project skills: `install.sh` links the local overlay's `projects/<project>/skills/*` next to the global skills; their
descriptions limit them to their project.

## Context and usage signal

In CLI, use `/context` before context becomes unreliable and `/compact` when the conversation needs
a summary. In VS Code, check the context indicator; for a continuation that needs independent
context, open a new chat and carry only a self-contained task brief. Copilot plan and account limits
can change, so use the limits shown by the signed-in runtime rather than a static number.

## Start a session

**CLI:** start `copilot`, inspect the available models with `/model`, and select the required
capability. For a fresh custom-agent invocation:

```bash
copilot --agent <agent-id> --prompt "<self-contained task>"
```

For a safer shell policy, the CLI accepts tool restrictions at startup. Example:

```bash
copilot --deny-tool='shell(git push)'
```

**VS Code:** open the repository, open Copilot Chat, set the session target to **Copilot** (Agent
Host), choose Agent mode and the required model, then start a new chat. VS Code's separate **Local**
agent uses profile-based user customizations and is outside this adapter.

## Permissions

- **CLI:** shell and other tools are subject to Copilot's approval policy. `--deny-tool` can block a
  tool for the session, and a deny takes precedence over an allow. Keep direct `git push` denied;
  never grant broad shell access just to run the sanctioned script. `bin/push-ai-god` remains subject
  to the shared Git approval rule and must only be run after the exact staged set is approved.
- **VS Code:** keep terminal/tool approvals enabled and avoid broad auto-approval. The VS Code
  runtime has configurable approval controls, but this installer does not write VS Code settings or
  install a persistent git-specific deny rule. Shared `AGENTS.md` instructions still prohibit direct
  `git push`.
- This installer does not edit Copilot or VS Code settings, permissions, or authentication files.

## Skills and instructions

By default, both Copilot CLI and the Copilot Agent Host in VS Code use `~/.copilot`. The installer
links this repo's `AGENTS.md` as `copilot-instructions.md`, links each shared skill under
`skills/<name>/`, and links this adapter as `ai-god-runtime.md`. Copilot CLI's `COPILOT_HOME` can
override its config directory; it does not change the documented VS Code Agent Host location, so
the installer handles the two destinations separately.

Copilot reads repository `AGENTS.md` instructions. Per-project memory is not automatically loaded;
follow the shared instruction to read the local overlay's `memory/<project>/MEMORY.md` when the project memory exists.
The CLI and VS Code Agent Host support personal skills under `~/.copilot/skills/`. Use the active
Agent Host's user-level customizations under `~/.copilot/agents/` for personal agents. The installer
does not create or modify custom agent files.

This adapter covers the GitHub Copilot harnesses, not VS Code's separate Local agent or other IDEs.

## References

- [Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
- [Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Copilot CLI custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [Copilot CLI permissions](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools)
- [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
- [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
