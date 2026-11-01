# Background run — implement without blocking the developer

A plan with `Run mode: background` is implemented while the developer keeps working on something
else. How to start it and which model runs it: runtime adapter → Run modes. The rules below hold in
every runtime.

## Isolation

- **Own working tree.** A separate worktree on its own branch cut from the base the developer names
  when asked, never the developer's checkout — two writers in one tree corrupt each other's diffs and
  staging. Create and prepare it with the `worktree` skill (`wt new <branch> --from <base> --no-open`; `wt setup` inside a
  worktree the runtime created) before the first verification command.
- **The plan travels by absolute path.** Plans live in a git-ignored directory, so a new worktree
  does not contain them. Name the plan's absolute path in the main checkout in the start prompt.
- **Hands off the plan's files.** §2 and the steps list every file the run touches; the developer
  does not edit those files meanwhile. Needing a file outside that list is a stop condition.
- **No shared devices or servers.** A background run verifies with commands — typecheck, lint,
  tests — and leaves simulators, devices, dev servers and the browser to the developer. Work that
  needs them is interactive by definition.

## During the run

- It follows `wf-implement` in full: stop conditions, business rules, verification, the report.
- It never waits on a question in the background. A stop condition or an undecided state ends the
  run with the question in the report; the rest of the work stays as it is.
- It never escalates on its own. A failed meaningful attempt (one under a trial mapping) ends the run
  with the failure, the hypothesis tried and the evidence in the report; whether to rerun on a
  stronger mapping is the developer's decision.
- It reports once, at the end. The developer's main session gets no progress chatter.

## Handing back

1. The staged diff and report live in the run's worktree, under the Git rules (a background
   subagent never stages — its orchestrating session stages in that worktree after reading the diff).
2. The developer approves the staged set; only then is it committed on the run's branch.
3. Bringing the branch into the developer's branch is the developer's call: give the exact
   `git merge` (or `git cherry-pick`) command; never rebase or reset their branch.
4. After the merge, the worktree is removed on the developer's yes; the plan stays (`ai-workflow`
   §4), then review and retro follow as usual.
