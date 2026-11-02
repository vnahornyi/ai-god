# Plan artifact template

## Contents

Sections of the template below:

- §1 Task
- §2 Context: what already exists
- §3 Problem framing & architecture decision
- §4 Implementation steps
- §5 i18n
- §6 Unit tests
- §7 Snapshot tests
- §8 Manual QA cases
- §9 Regression checklist
- §10 Scope of work (no hours)
- §11 Verification checklist (before the PR)
- §12 Open questions and follow-ups

Copy this structure. Delete nothing; write `None` / `N/A` where a section does not apply.

**Language: write the plan in English** — the implementation model reads it. The summary in chat
goes in the session language (global instructions → Language). Quote docs and tickets verbatim in
their original language.

---

```markdown
# <TASK-ID> — <Task title>

> Task plan. The implementer starts from the task request and this file; everything it needs is here.
> Generated: <YYYY-MM-DD> · Base branch: `<branch>` · Base commit: `<short sha>`
> Lifecycle: `ai-workflow` §4 — one plan, corrected in place, deleted only by the developer. Never staged.

## 1. Task

**Scope:** <platform / package / app> — confirmed with the developer, not assumed.
Locales: … · Roles: … · Admin screens: yes/no

**Goal (one paragraph):** …

**Source of truth:** <ticket> · <docs> · <Figma link + frame name>

**Acceptance criteria**
- [ ] …

**Out of scope:** …

**Styles:** developer-owned (default) | assigned to the agent by the developer on <date>

**Run mode:** background | interactive — <the reason, per `wf-plan` → run mode table>. Background:
the developer keeps these files free until the run hands back — <list from §4>.

## 2. Context: what already exists

| Area | Path | State | Use |
|------|------|-------|-----|
| … | `…` | implemented / partial / missing | reuse / extend / build |

**Reuse as-is:** `path` — why
**Lift to shared:** `path` — what moves, who else imports it
**Write new:** `path` — why it cannot be reused

**Shapes to copy:** `<kind of file>` → `path:lines`

**Rules that constrain this task** (cite the file):
- `<AGENTS.md path>`: …
- project rules / skill: …

⚠️ UNVERIFIED: <anything not confirmed in repo or docs>

## 3. Problem framing & architecture decision

**What "solved" means:** whose problem · which cases · over what window · the observation that proves it.

> **After this ships, who still has the problem?** …

**Path of least resistance:** what it is · the limit that makes it partial.
**Architecturally right path:** what it is · its cost.
**Chosen:** which, why; for "both, sequenced" — the order and what triggers the second part.

Data flow in 3–6 bullets: request → state → UI, naming the state layer this repo actually uses.

### Business rules

Every business branch the task needs. The implementer codes each row literally and decides nothing
else.

| ID | Condition (input / state) | Expected (output / behaviour) | Source |
|----|---------------------------|-------------------------------|--------|
| BR-1 | `items.length === 0` | empty state with retry hidden | ticket AC-2 |
| BR-2 | `price === null` | row hidden, not "0" | Figma frame "Card / no price" |

Invariants: … (what must hold in every state, e.g. "label and action come from the same branch")

States enumerated per input: missing · empty · zero · error · stale — each has a row, or
"not reachable because …".

Any reachable state not in this table → stop condition.

## 4. Implementation steps

Every field is filled. The implementer decides nothing that is not written here.

### Step 1 — <title>

**Goal:** <one sentence about behaviour>
**Rules:** BR-1, BR-3 (or `none` for a step with no business branch)
**Files:** `path/a.tsx` (new) · `path/b.ts` (edit)
**Copy the shape of:** `path/existing.tsx:40-85`
**Signatures / names:**
```ts
type FooPropsType = { … };
export function useFoo(id: number): FooStateType
```
**Imports:** `useBar` from `path/declaring-file` (by the declaring file, never a barrel)
**Logic:** pseudo-code or exact fragment for anything non-trivial
**Edge cases:** `[]` → empty state (BR-1) · `null` price → hide row (BR-2) · 403 → …
**Do not:** touch `path/x` · add dependencies · refactor neighbours · add style values · add comments
**Stop if:** <each ⚠️ UNVERIFIED fact or place where the code may differ> → stop, report, do not improvise
**Done when:** `<command>` passes · <observable behaviour>
**Scope:** type `new logic | port | mechanical | contract` · files new/edit/delete `2/3/0` · diff `~60–100` lines · contract change `no` · consumers `7 (web 3, mobile 4)` · check on `iOS, Android` · unknowns `…` · depends on `backend: …` · tests `1 file, ~6 cases | on request`

### Step 2 — …

## 5. i18n

New/changed strings, where each lives, every catalog it lands in, and the exact extract/compile
commands (from the project's planning skill, verified in its package scripts). Name which locale
needs human translation.

## 6. Unit tests

> Mark **proposed** when the project adds tests only on request.

| Test file | Subject | Cases |
|-----------|---------|-------|
| `…/__tests__/foo.test.ts` | `useFoo` | happy path; empty; API error; unauthorized |

Mocks needed and the existing mock helper to reuse. **Run:** `<verified command>`

## 7. Snapshot tests

| Component | States | Snapshot dir |
|-----------|--------|--------------|
| `<Foo/>` | default; loading; empty; error; long title | `…/__snapshots__/` |

**Run / update:** `<command>` · `<command> -u`

## 8. Manual QA cases

| # | Case | Preconditions | Steps | Expected |
|---|------|---------------|-------|----------|
| 1 | Happy path | … | 1. … 2. … | … |

Cover: every empty/loading/error state · offline/slow network · auth and roles · locales · the
platform matrix from §1 · themes · small/large screens · back navigation, deep links · data edges.

## 9. Regression checklist

| Touched module | Existing flow at risk | How to verify |
|----------------|----------------------|---------------|

Also: persisted/cached data and migrations · analytics events · deep links and push · back
navigation. Shared code → rows for every consuming platform, including its i18n catalogs.

## 10. Scope of work (no hours)

The developer estimates from this section; it carries no hours and no estimate.

| Step | Type | Files n/e/d | Diff | Contract | Consumers | Check on | Unknowns | Depends on |
|------|------|-------------|------|----------|-----------|----------|----------|------------|
| 1 | … | … | … | … | … | … | … | … |

**Per step, in plain words:**
- Step 1 — what has to be read and understood first · what is written · what is verified and on which platforms · who has to agree on what · what would make it longer

**Most likely to blow the scope:** …
**Not in the steps but costs time:** reading into existing logic, review rounds, device testing, regression pass, coordination with …

## 11. Verification checklist (before the PR)

- [ ] `<typecheck>` · `<lint>` · `<tests>`
- [ ] Acceptance criteria in §1
- [ ] QA §8 · Regressions §9

## 12. Open questions and follow-ups

- [ ] … [BLOCKING]
- Follow-up: …
```
