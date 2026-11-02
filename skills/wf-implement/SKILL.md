---
name: wf-implement
description: Use when asked to implement an approved plan, continue an implementation, or make a direct small fix — "реалізуй план", "зроби", "fix".
---

# wf-implement — one task, one change

Git: the global instructions' Git rules apply in full — stage, show, stop; never push. The plan
lifecycle is `ai-workflow` §4. Neither is repeated here.

Capability: STRONG_GENERAL (the runtime adapter may map it to a trial model; then escalate after
**one** failed attempt — `ai-workflow` → `references/model-policy.md`).

## Phase 0 — Sources and scope

1. Read the plan if one exists. Check its architecture against the code it claims to extend: open the
   "shape to copy" and one more implementation of the same kind. A plan that puts code in the wrong
   layer, calls the transport where the project uses provider methods, puts effects in shared code,
   or names a pattern without a symptom is wrong on that point: stop, show the plan's claim, what the
   code does and the correction, get agreement, fix the same plan in place.
2. `git status -sb` and the branch. Never work on `main`/`master`; leave unrelated changes alone and
   unstaged; no routine stash.
3. Load once: `AGENTS.md`/`CLAUDE.md` of the touched paths, the project's rules and skills,
   `frontend-craft` (Build mode) for React/RN. Precedence: project rules and skills → `frontend-craft`
   → the plan. The plan says *what*; it has no authority over *how*.

## Phase 1 — Implement

- **Only traceable changes.** Every line traces to the plan, the task, the docs, the design, or the
  developer's approval in chat. Anything else is not written — ask.
- **Stop conditions in the plan are hard.** When one fires (a ⚠️ UNVERIFIED fact differs, the code
  does not look as described), stop, report what you found, do not improvise.
- **Business rules are implemented literally.** Each row of the plan's Business rules table maps to
  a branch with the row's condition. When the rows together cover every value of the type
  (`null` and a number), the last row is the remaining branch — no redundant check. A state the
  code can reach that no row covers is a stop condition: ask, do not choose, and keep the code
  compiling without deciding it — an explicit `throw` whose message names the open question, never a
  missing return or a silent default. Without a plan, a business choice the task text does not make
  is the same question.
- **UI: logic and skeleton only by default.** Styles are the developer's: no spacing, sizes,
  colours, fonts, radii, shadows, animations, inline styles, new style files, values copied from
  neighbouring code, or placeholders. Build structure, states, handlers, navigation, data flow,
  i18n'd text and accessibility from `figma-inspect`'s coverage table. Visual work only when the
  developer assigned it for this task — then every value carries its source.
- Work inline by default. Delegate only an independent piece when it clearly pays for its
  coordination: `references/delegation.md`.
- **Run mode** comes from the plan (`interactive` or `background`); a direct fix without a plan is
  interactive. A background run follows `references/background.md` — its own worktree, the plan by
  absolute path, questions in the final report instead of waiting.
- When stuck, escalate per the model policy with one concrete question and the verified evidence;
  never grind. When the rest is mechanical, say `DE-ESCALATE`.

## Phase 2 — Verify, stage, stop

1. Run only the checks the developer and the repo authorize; batch them; read full output; report
   what ran and what did not. Do not write tests where the repo requires approval first.
2. Pre-flight the whole diff: dev leftovers, hardcoded strings, unintended API/signature changes,
   new `any`/casts, unrequested dependencies, unrelated formatting, behaviour absent from the
   task/plan, style values in a developer-owned-styles task.
3. Stage the exact task files (never the plan), show `git diff --cached --stat` and the full staged
   diff, explain behaviour, affected consumers, verification and remaining human QA, and give the
   rule trace `BR-id → file:line → test or QA case` for every row the plan lists. Open the report with
   `Implemented by: <model · effort>` as the runtime reports them, for `wf-retro`. Stop.
4. **Draft the author's PR comments** on key decisions and on places likely to raise questions (the
   team PR guide in the local overlay, `company/pr-guide.md`, may say more and wins). List them
   in the report, each anchored `file:line`, one to three plain sentences in the developer's voice:
   a choice a reviewer would question (module-level state, a guard that lives elsewhere, a platform
   difference, a deliberately skipped case) and the fact that settles it. The developer posts them;
   never post them yourself.
5. After the developer approves the staged set: leave the plan in place (`ai-workflow` §4), then hand off to `wf-review` in a
   cold context. Accepted findings are fixed directly, without a fixes plan.
