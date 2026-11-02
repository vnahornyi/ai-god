---
name: ai-workflow
description: Use first for every task request — plan, implement, fix, debug, review, PR walkthrough, estimate, Jira ticket, worklog, worktree — to pick the one stage skill, the domain skills and the capability class. A pure question that needs no tool use goes without it.
---

# AI workflow — router

Without this router a session loads whatever skill a description resembles, or none, and skips the
stage's discipline. Pick the stage, load only that stage's skill plus the domain skills its trigger
names, and nothing else. Concrete models and runtime operations live in the runtime adapter (`AGENTS.md` → Runtime
adapter).

## 1. Stage → skill

| The developer asks | Load | Do not load |
|---|---|---|
| "сплануй", "plan TASK", task too large/ambiguous to start | `wf-plan` | `wf-estimate` (unless a number is asked), review, worklog skills |
| "реалізуй план", "зроби", a direct small fix | `wf-implement` | planning, estimate, review skills |
| "чому падає", "не працює", "debug", a crash, a failing or flaky test, slower or janky since a change — the cause is unknown | `wf-debug`; the fix it leads to is staged through `wf-implement` Phase 2 | `wf-plan` |
| "зроби ревʼю", review my diff / my PR | `wf-review` | planning, implementation, estimate, worklog skills |
| Automatically, once the developer has decided on the `wf-review` findings of their own task | `wf-retro` | planning, implementation, estimate, worklog skills |
| "пройдись по PR", someone else's PR | `wf-peer-review` (it reads `wf-review` → `references/ai-review-guard.md` and `references/ai-review-replies.md` directly) | `wf-review` itself; planning, implementation, estimate, worklog skills |
| "глянь коментарі", "що відповісти", review threads or a bot's review on the developer's own PR | `wf-review` → `references/ai-review-guard.md` and `references/ai-review-replies.md` (and `frontend-craft` → acting on review comments for React/RN) | planning, implementation, estimate, worklog skills |
| "оціни", "скільки годин" | `wf-estimate` | review, worklog skills |
| "створи jira задачу", "опиши таску" | `wf-jira-task` | implementation, review, worklog skills; `wf-estimate` only when a number is asked |
| "залогуй", "закрий день", Tempo, timesheet | `wf-worklog` | everything else |
| A pure question that needs no tool use | no stage skill; a domain skill only when the question is in its area (`seo` for organic search) | every `wf-*` skill |
| Work on the ai-god repo itself (a skill, an adapter, the router) | the repo's root `AGENTS.md` and `docs/writing-for-agents.md`; `wf-implement` for the change | third-party skill-writing skills |

A request that spans stages runs them in order (plan → implement → review → retro), loading each
stage's skill when that stage starts.

## 2. Domain triggers

Load a domain skill only when the active stage skill or the actual files in scope trigger it:

| Trigger | Skill |
|---|---|
| React / React Native code in scope | `frontend-craft` (only the mode the stage needs) |
| Reanimated, gestures, haptics, layout/scroll motion — building it, or a diff under review that adds or changes it | `react-native-animations` (review: its `references/motion-review.md`) |
| A Figma link or UI that must follow a design | `figma-inspect` — never a third-party Figma-to-code or design-in-Figma skill |
| A plan, diff or question names a design pattern, or a growing switch/prop explosion | `design-patterns` |
| Organic-search impact of a web change | `seo` |
| A background run, parallel work in another checkout, or "worktree" / switching worktrees / opening one in VS Code | `worktree` |
| On-device ML speed, Core ML / ANE, camera-rate vision | `apple-neural-engine`, `realtime-vision-pipeline` |
| Any review output — `wf-review`, `wf-peer-review`, the runtime's review engine, or an AI reviewer's comments on a PR | `wf-review` → `references/ai-review-guard.md`: every finding or comment passes its gates before it reaches the developer; `references/ai-review-replies.md` → learning loop runs once the developer has answered |
| Project-specific skills | Whatever the project exposes (local overlay `projects/<project>/skills`, linked into the project) |

## 3. Stage → capability class

| Stage | Class |
|---|---|
| Planning, contract or architecture decisions | FRONTIER_REASONING |
| Debugging — hypotheses and the root-cause call | FRONTIER_REASONING |
| Implementation from an agreed plan | STRONG_GENERAL |
| Independent review — severity and the fix decision for every finding | FRONTIER_REASONING |
| Fixing accepted findings, exactly as the review decided | STRONG_GENERAL |
| Estimate, Jira ticket text, retro | STRONG_GENERAL |
| Mechanical steps, evidence collection, worklog script output | FAST_ROUTINE or inline |

Implementation also has a **run mode** — `interactive` (the developer waits or iterates) or
`background` (independent, runs while the developer does other work) — chosen in the plan by
`wf-plan`; the runtime adapter → Run modes maps each to a model and says how a background run starts.

Escalation, de-escalation, review→fix routing and fallbacks: `references/model-policy.md`.

## 4. Plan lifecycle — the only place it is defined

- A direct, small request gets no plan file.
- A planned task gets exactly one plan file, written by `wf-plan` after planning. An epic gets one
  plan per task the developer asks to plan, never an epic overview.
- One task is one implementation segment. Correct the same plan in place after agreement; never a
  `-v2`, a handoff, a fixes plan, a state, segment, review or escalation file.
- Never delete a plan — the developer deletes plans themselves. After implementation, authorized
  verification and the developer's approval of the complete staged diff, run independent review, then
  `wf-retro`, which reads the plan's Business rules. Review findings and fixes stay in the
  conversation; the only file retro writes is its row in the project's `implementation-log` memory.
- Never stage or commit a plan.

## 5. Every change is traceable

Each line written must trace to the task, the plan, documentation, the design, or the developer's
approval in chat. What traces to none of them is not written: stop and ask. Styles are the
developer's by default — see `figma-inspect`.

## 6. Moving context

- Continue from the task conversation, the plan if one exists, `git status` and the current diff.
  Do not re-verify facts the plan already verified.
- A context switch (new session, cold subagent, near a usage limit) carries one compact prompt: the
  exact next action, completed work, open decisions, source links, verification so far. No file.
- Recommend a new session only when it improves independence, capability or context quality.
  Independent review always runs cold. The developer steers with `stay`, `switch` or `auto`.
