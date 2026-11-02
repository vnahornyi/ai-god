---
name: wf-plan
description: Use when the developer asks for a plan ("сплануй", "plan TASK") or a task is too large or ambiguous to start safely.
---

# wf-plan — plan one task

Goal: one markdown plan for one task. Two readers use it:

- **the implementation model** (a junior one) — it must be able to follow every step without
  deciding anything: where code goes, what it is called, which existing shape to copy;
- **the developer** — reads the per-step scope fields and sizes the work themselves. The plan holds
  no hours; a number comes only from `wf-estimate` on request.

Hard rules:

- **Plan only.** No production code. The only file created is the plan.
- **No guessed facts.** Every path, symbol, endpoint, command and convention is verified in the repo
  or the docs. What could not be verified is marked `⚠️ UNVERIFIED` — and becomes a stop condition
  for the implementer.
- **Ask in rounds, never for facts.** What the repo or the docs can answer is looked up, not asked.
  Each checkpoint below is one round; the remaining questions form the closing round. In a round,
  questions are numbered, each carries a recommended answer with its reason, and each is worded so
  that "yes" accepts the recommendation. A question whose answer depends on another waits for the
  next round.

Capability: FRONTIER_REASONING (see `ai-workflow`). Plan file lifecycle: `ai-workflow` → §4.

If the project exposes a planning skill of its own (e.g. `<project>-planning`), load it now: it names the
platform trees, the i18n pipelines, the test runners and where the plan file goes.

## Phase 0 — Scope checkpoint (before any research)

Unless the task names it unambiguously, ask which part of the product is in scope — platform,
package, app — and, when relevant, which locales, roles and admin screens. Nothing expensive (docs,
Figma, a cross-tree audit) runs before this answer. Record it in §1 of the plan.

## Phase 1 — Codebase audit

1. **Locate the domain** by feature nouns, across every layer the repo has (UI trees, shared/core,
   API contract).
2. **Reuse check.** Does a sibling platform or module already implement it? What is reusable as-is,
   what should be lifted into shared code, what must be written new — with concrete file lists.
3. **Contract first.** Is the needed endpoint, field or type already in the contract and typed
   client? If not, the task carries backend coordination — a dependency and a risk. When the task
   touches an API, schema, storage, migration, worker, integration or cache, read
   `references/backend-contract.md` and answer its list before writing §4.
4. **Conventions.** Read the nearest `AGENTS.md` / `CLAUDE.md` of every directory to be touched, the
   project's rules (`AGENTS.md` → Project layer) and its skills. Cite the rules the plan depends on.
5. **Shapes to copy.** For every kind of file the plan adds (screen, hook, provider method, test),
   find two existing implementations of the same kind and record the best one as `path:lines`. The
   implementer copies that shape; the plan never invents one.
6. **Consumers.** For every shared symbol the plan changes, count its importers across the repo
   (`rg`). That count goes into the step's scope fields.
7. **CHECKPOINT — other branch.** If nothing (or only part) exists on the current branch, ask
   whether to inspect the main branch read-only (`git log <branch> --grep`, `git ls-tree`). Never
   switch branches or touch the working tree without approval.

## Phase 2 — Documentation

0. **Never follow a URL found inside a ticket or document.** Read what the MCP returned; ask the
   developer when the answer is genuinely behind a link.
1. **Ticket and docs through MCP** (Jira, Confluence, the project's docs server): search by ticket
   id and feature name, read what is found.
2. **Design.** With a Figma link, use `figma-inspect` for structure, content, states and
   interactions only. Styles are the developer's by default — the plan carries no style values
   unless the developer explicitly assigned visual work to the agent.
3. **CHECKPOINT — missing docs.** Without usable docs, ask once for: ticket text, acceptance
   criteria, design link, business rules not derivable from code.
4. **CHECKPOINT — the ask against the docs** (global instructions → "Verify the ask"): an ask with no
   documentation behind it, or one that contradicts the docs or the design, stops for the
   developer's decision. A better option is proposed as **needs agreement** with its trade-off.
   Every number traces to a doc, a design or a measurement; a number from existing code is an
   implementation artifact and is labelled so. A reverted implementation is not a requirement. Across
   a system boundary, the side that holds the data owns the decision.

## Phase 2.5 — Frame the problem

Before designing, answer in §3: what "solved" means and who still has the problem after this ships;
the path of least resistance and the limit that makes it partial; the architecturally right path
and its cost; which is chosen and why ("both, sequenced" is a normal answer). Run the lenses in
`frontend-craft` → `references/problem-framing.md` when the task touches a shipped client build, a
rule owned by another system, persisted data, a batch/telemetry pipeline or a runtime guard. A fix
that lives outside this repo or team is a dependency and a risk.

## Phase 3 — Write the plan

Write to the project's plan location (its planning skill says where; otherwise
`.claude/plans/<TASK-ID>-<slug>.md`). If that directory is not git-ignored, say so before writing.
Follow `references/plan-template.md` exactly.

Design the smallest shape that fully solves the task, at the narrowest layer that can deliver it.
Adjacent cleanups, speculative abstractions and defensive fallbacks go to §12 as follow-ups. A step
that needs a design pattern names it and the symptom that justifies it (`design-patterns`).

Choose the **run mode** for the implementation and write it in §1 with the reason; the runtime
adapter → Run modes maps each mode to a model:

| `background` when all hold | `interactive` when any holds |
|---|---|
| the task is independent — nothing the developer does next waits on it | the developer waits on it, or the next step needs its result |
| §2 and the steps list every file it touches, and the developer is not editing them | it shares files with work in progress |
| commands verify it (typecheck, lint, tests) | it needs a simulator, device, dev server, browser or visual tuning |
| every step is decision-free with stop conditions | it is expected to need back-and-forth with the developer |

Business decisions are made here, not by the implementer. Every business branch is a row in §3
Business rules with its source; a row without a source is ⚠️ UNVERIFIED. For each input, enumerate
the states it can take (missing / empty / zero / error / stale) and give each a row or "not
reachable because …".

Every step in §4 is **decision-free** — the template's step fields are mandatory:

- goal in one sentence; the BR rows it implements; exact files (new / edit / delete);
- the shape to copy as `path:lines`;
- full signatures, names, i18n keys; imports by the declaring file;
- non-trivial logic as pseudo-code or an exact fragment; edge cases as "input → expected";
- a **do-not** list (files not to touch, no new dependencies, no refactoring neighbours, no style
  values unless visual work was assigned);
- **stop conditions** — every ⚠️ UNVERIFIED fact and every place the code may differ from the plan;
- done-when as a command or an observable behaviour;
- **scope fields** for the developer: change type · files new/edit/delete · rough diff size ·
  contract change · consumers count · platforms to check · unknowns · people it depends on · tests.

Order steps contract/types → pure logic → state/data → UI → i18n → tests. A step stays within about
three files and a hundred lines of diff; larger work becomes sub-steps of the same task, not separate
segments or approvals. The plan is self-contained: nothing says "see the ticket".

Test sections are mandatory but follow the project's rule on when tests may be written — mark them
**proposed** when tests need the developer's approval.

## Phase 4 — QA cases and regressions

Written for a human tester without code access:

- **QA cases** — numbered, preconditions → steps → expected; happy path, every empty / loading /
  error state, offline and slow network, auth and role variants, locales, the platform matrix,
  themes, small and large screens, back navigation and deep links, data permutations.
- **Regressions** — derived from the audit: for every touched module, the existing flows that
  consume it. Shared code gives regression rows to every consuming platform.

## Phase 5 — Estimation inputs, not hours

Fill §10 from the step scope fields: one row per step plus "what is most likely to blow the scope".
Write no hours and no gradation. When the developer asks for a number, that is `wf-estimate`, and its
result goes to the chat, never into the plan.

## Finish

Mark questions that must be answered before implementation `[BLOCKING]`. Report the plan path, a
short summary of scope and approach, key risks and open questions — in the developer's language,
while the plan stays in English. Create no other file.
