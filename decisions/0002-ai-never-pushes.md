# 0002 — The AI never pushes; commits go through the staged index

**Context.** A push publishes work and is hard to take back; a commit made without the developer
seeing the exact set mixes unreviewed changes into history. Text rules alone are not enough: a
model can skip a line of instructions.

**Decision.**
- No `git push` in any form. The developer pushes; the agent gives the command.
- The default is stage, show the full staged diff, propose a message, and stop. A "yes" commits
  that staged set only. `autoapprove` lifts the stop for one task, never for push or rewrites.
- No amend, rebase, `reset --hard`, `--no-verify`, stash or branch deletion without asking.
- The single exception: ai-god and its overlay, after an approval of the staged set, push through
  `bin/push-ai-god`, which runs `bin/check-public` and pushes fast-forward only.
- The mechanical parts are also denied in each runtime's permission layer where one exists.

**Consequences.** Every commit has a staged set the developer saw. A runtime without a permission
layer (Copilot) keeps text-only rules — documented in its adapter. Evals showed agents reach for
`git stash` to compare old code; that is now denied too (2026-11-02).

**Source.** `global/AGENTS.md` → Git rules 1–7; `adapters/claude/settings.base.json`;
`adapters/codex/rules/ai-god.rules`; `evals/results/2026-11-01-v2-baseline.md` → E6.
