# Delegating a piece of one task

Delegate only a genuinely independent piece when the saved time or review quality clearly exceeds
the context, coordination and integration cost. Delegation never creates another segment, plan or
manifest. Avoid concurrent writers in one working tree; use a separate worktree only when the benefit
exceeds the merge cost. How to spawn, wait, correct and pick a model: the runtime adapter →
Subagents.

## Prompt — self-contained

```text
Implement this bounded part of the developer's task: <exact task>
Plan context: <path and the relevant step(s), if any>
Files you may change: <exact paths>
Shape to copy: <path:lines>
Applicable project rules: <verified concise list>
Styles: developer-owned — write no style values | assigned — every value from <source>
Stop if: <the step's stop conditions>
Done when: <observable behaviour>
Verification: <authorized check, or "none authorized">

Do not stage, commit, push, or spawn agents. Do not create plans, handoffs, manifests or other
workflow files. Stop and report if the work needs files outside this list or conflicts with the
requirements.
```

## Checking the result

1. `git status --porcelain` — the worker stayed inside its files.
2. Read the diff yourself; you own integration quality. Never claim a check passed unless it ran.
3. A correction goes to the same worker while it is active, not to a new one.
4. A piece that cannot be finished is a blocker reported to the developer, not a progress file.
