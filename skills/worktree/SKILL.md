---
name: worktree
description: Use when a task runs in the background or in parallel with the developer's work, or the developer asks to create, switch, open in VS Code or remove a worktree.
---

# worktree — parallel checkouts that are ready to run

Git rules from the global instructions apply in full. Worktree mechanics: `git worktree` (the `git
worktree add`, `list`, `remove`, `prune` commands; one branch can be checked out in only one
worktree; refs and config are shared, `HEAD` and the index are per worktree).

## Layout

- Main checkout: `~/Developer/<repo>` — the developer's tree. An agent never edits it while a
  worktree run is underway.
- Developer and planned worktrees: `~/Developer/<repo>.worktrees/<branch>` — siblings, so the main
  checkout's editor, file watchers, bundler and test runner never see their files.
- Worktrees a runtime creates on its own (an isolated subagent, a runtime's worktree option) stay where
  the runtime puts them; `wt setup` makes them ready the same way.

## The `wt` script

`scripts/wt` in this skill. Run it from anywhere inside the repository or one of its worktrees.

| Command | Does |
|---|---|
| `wt new <branch> [--from <ref>] [--no-open]` | New worktree for `<branch>`: creates the branch from `<ref>` (default: the current `HEAD`) or checks out the existing one, runs `setup`, opens it in a new VS Code window |
| `wt setup [<path>]` | Clones the git-ignored paths listed for the project from the main checkout into a linked worktree; skips what already exists; warns when a lock file differs, meaning dependencies must be reinstalled there |
| `wt open <branch>` / `wt open --main` | Opens that worktree, or the main checkout, in a new VS Code window |
| `wt path <branch>` · `wt list` | Prints the path · lists worktrees |
| `wt rm <branch>` | Removes a clean worktree; the branch stays |

What `setup` clones is the project's list, `ai-god/local/projects/<repo>/worktree-include`: one path per
line, `#` comments. Only git-ignored files under those paths are cloned — tracked files never —
using copy-on-write clones where the filesystem supports them (APFS), so large dependency trees cost
seconds and no space until changed. No list → nothing is cloned.

## Agent rules

- **Create** a worktree only for a task that needs one (a background run, parallel work, or the
  developer asked): `wt new <branch> --from <base> --no-open` with the branch name the project uses
  for the task. Creating a worktree and a branch is reversible and needs no stop.
- **Ask for the base first.** Before `wt new` for a new branch, ask the developer which branch or
  commit to cut it from — offer the plan's `Base branch` and the current branch as options — and pass
  the answer as `--from`. Never rely on the default: the current `HEAD` is often another task's branch.
- **Set up before verifying.** A worktree without its dependencies fails typecheck and tests for the
  wrong reason. Run `wt setup` inside any worktree the runtime created, and reinstall dependencies
  when `setup` warns that a lock file differs.
- **Plans travel by absolute path** — plan directories are git-ignored and absent from new worktrees.
- **One dev server per port.** Two bundlers or dev servers from different worktrees collide on the
  same port; only the worktree the developer is testing runs one, or the second gets another port.
- **Hand back, do not integrate.** The run ends with a staged diff in its worktree. After the
  developer approves and the set is committed on the worktree's branch, give them the exact
  `git merge <branch>` (or `git cherry-pick`) to run in their checkout. Never rebase or reset their
  branch.
- **Remove only on the developer's yes.** `wt rm` deletes the worktree's ignored files with it; the
  branch is kept, and deleting a branch is a separate request.

## VS Code

- One window per worktree: `wt open <branch>`, or right-click the worktree in the Source Control
  **Repositories** view → **Open Worktree in New Window**. Switch with the window switcher or **File →
  Open Recent**; `wt open --main` returns to the main checkout.
- The Repositories view lists worktrees created outside VS Code only when the developer's setting
  `git.detectWorktrees` is on — suggest it, never change editor settings.
- VS Code's own **Create Worktree** works too, but it does not run `setup`; run `wt setup` in the new
  folder afterwards. Its `git.worktreeIncludeFiles` / `git.worktreeSymlinkFolders` settings copy or
  symlink instead of cloning — prefer `wt`.
- Tracked `.vscode/` settings come with every worktree, so each window behaves like the main one once
  dependencies are in place.
