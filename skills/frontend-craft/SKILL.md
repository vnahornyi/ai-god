---
name: frontend-craft
description: Use when React or React Native code is in scope of a plan, an implementation or a review; the active stage names the mode (plan, build, review).
---

# Frontend Craft

Goal: work that reaches QA with zero defects. Not "it compiles" — nothing left for a tester to find.

The user is a senior engineer with a heavy workload. Their failure mode is not bad architecture; it is **small, visible things slipping through under time pressure** — a shared component broken on a screen they never opened, a `console.log`, a hardcoded string, a spacing that drifted from the design. This skill exists to be the pair of fresh eyes they don't have time to be.

## Project conventions outrank this skill

Before applying anything here, check for `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, project skills, and the surrounding code's actual idiom. Where a project has a rule, follow the project. This skill is the default when the project is silent — it is not a mandate to reshape someone's codebase.

If a project skill covers the same ground (e.g. a memoization policy, a planning workflow), defer to it and use this skill only for what it doesn't cover.

**A company implementation standard outranks both, when present.** It lives in the local overlay
(global instructions → Local overlay → `company/implementation-standard.md`) and applies to every
implementation task. Read it before Build mode on anything non-trivial. Without it, this skill and
the project's own rules are the standard.

## House style

These apply to every line written or reviewed.

### Nested ternaries: prohibited

Do not write nested ternary expressions anywhere in JavaScript or TypeScript, including JSX, assignments, and return expressions. Use `if`/`else`, `switch`, early returns, or a named derived value/component instead. A single ternary is acceptable only for a simple two-way choice.

### Conditional rendering: extract only what earns a name

A simple condition stays inline: `{isOpened && <Badge />}` or one two-way ternary. Wrapping that in a `render...()` function adds a name and a jump for nothing.

Extract when the branch stops being readable in place — nested conditions, three or more states, a `switch` over a union, or JSX long enough to hide the layout around it. Then give it a name: a subcomponent when it has its own data or could stand alone, a local `render...()` helper invoked where the UI belongs (`{renderOfferState()}`) when it mostly reads the component's locals. Helpers stay pure and use `const`; early returns and `switch` belong inside them.

Whole-output guard states (`if (!data) return <Empty />`) stay as early returns at the top of the component. Never assemble JSX through a mutable `let` reassigned across `if` branches.

### Function signatures: named arguments, bare results

A function with three or more parameters, or with any boolean flag parameter, takes one object with named fields: `pickBarcode({ barcodes, frame, isUpright })`, never `pickBarcode(barcodes, frame, size, null, true)`. A positional `true` or `null` at the call site says nothing about what it switches.

A function that returns one value returns that value, not an object around it: `string | undefined`, not `{ rawValue }`. When "nothing found" and "found, but empty" must stay different, encode it in the value (`undefined` vs `''`), not in a wrapper.

Does not apply when the signature is fixed by a library or a language callback (`onFrame(frame)`, `array.map((item, index) => …)`), or when the function returns several values the caller uses together.

### Comments: default to zero

**The default number of comments in new code is zero.** Not "few" — zero, until a specific line earns one. The author is a senior engineer reading their own codebase daily. A comment that explains something they can read off the code in two seconds is an insult and a maintenance liability: it rots the moment the code changes while the comment doesn't. Their real PRs run hundreds of lines with zero comments. That is the target, not an accident.

**The test — one question, applied per comment:** *does this sentence carry business or domain knowledge that is nowhere in the code?* A backend quirk, a legal rule, a product decision, an external bug, a constraint discovered the hard way. If yes, write it. If it describes mechanism — what the code does, when it runs, what it returns, why the pattern is the pattern — delete it. There is no third category, and "it helps the reader" is not an exemption; a reader who needs the mechanism explained is helped by a better name, an extracted function, or an early return.

**Delete on sight:**
- Restating the code (`// map over the items`, `// reset state before fetching`)
- Section labels (`// --- helpers ---`, `// handlers`, `// consts`)
- Narrating the change (`// added retry logic`, `// updated per feedback`) — that is the commit message
- JSDoc whose `@param`/`@returns` only re-type the signature in prose
- Explaining a language or framework mechanism (`// cleanup runs on unmount`, `// useRef keeps the value between renders`) — the reader knows React
- Restating a guard (`// skip if no id`) sitting above `if (!id) return;`
- Placeholders with no blocker (`// TODO: improve later`)

**Earn its place:**
- `// Backend clamps count to 0 when it is below 3, so 2 is the smallest real value`
- `// Using ~ as separator because _ can appear inside values`
- `// iOS 17 reports the wrong inset here; measured value is off by the status bar`
- `// TODO: waiting on the worker to expose the discount field`

Notice what all four have in common: a person who reads the whole file still could not have known this.

The same bar holds for JSDoc: written by people for people, saying why it was done, why this way and when it is needed — as short as possible. `@param` lines that only restate the signature fail it. A team PR guide in the local overlay (`company/pr-guide.md`) wins where it says more.

**When a project convention forces a comment** — an `AGENTS.md` that mandates JSDoc on exports or a note above every `useEffect` — satisfy it in **one line that carries the domain why**, and nothing more. The convention is a floor, not an invitation. Do not expand it into a narration of what the effect subscribes to, when it re-runs, and why cleanup is or isn't needed; that is exactly the noise this section exists to prevent. Write `// Backend TTL is 5 min, so a shorter foreground refresh would just re-read a cached value` — not `// Runs on mount and when productId changes. Holds no state, so no cleanup needed.`

Same rule when editing existing code: never add explanatory comments to make a diff easier to review. The diff is not the artifact, the code is. Say it in the PR description instead.

Bad / good / over-applied examples for the rules above: `references/examples-house-style.md`.

### Composition: compound components and functional style

Composition is a ladder — plain props → compound components → composer + providers → lifted state behind a contract. **Start at plain props and climb only on demonstrated friction**, never for consistency or a source you might need later. But when the friction is real, climb properly: a fifth boolean prop or a callback threaded through three layers is the cost of the higher rung without the benefit.

The house shape at rung 2 and above: a root owns state and provides context, parts read from that context and take no props, assembled into a namespace at one entry point. Logic lives in pure functions outside React — selectors that derive rather than store.

Read `references/composition.md` before building or reviewing any non-trivial component; it has the ladder with climb signals, the anatomy of each rung, the naming that tells a reader which rung they're on, and the cases where plain props are the right answer.

This is a **shape**, not a folder taxonomy or a framework. Express it in the project's own structure and idiom — never introduce a foreign layer scheme into a codebase that already has one.

## Pick the mode

Load only the mode the active stage needs:

| Stage skill | Mode file |
|---|---|
| `wf-plan` | `references/mode-plan.md` |
| `wf-implement` | `references/mode-build.md` — gates 0–3, pre-flight, report |
| `wf-review`, `wf-peer-review` | `references/mode-review.md` — React/RN review checks and acting on review comments |

## Asking vs. assuming

The user wants to be pushed to think, and wants a second opinion offered — not a stream of blocking questions. Calibration:

- **Ask and wait** at Gate 1 for unplanned work, and whenever two approaches are genuinely defensible and the choice is expensive to reverse (new dependency, new abstraction, contract change, state-ownership move) — including when a reviewer's request would make one platform diverge from its sibling. The developer's approval of an existing plan already satisfies Gate 1 unless implementation exposes a material new decision.
- **Assume, state, and continue** for anything reversible. Put the assumption in the report.
- **Never** ask a question you could answer by reading the codebase. Go read it — including the sibling platform's implementation and the API's route definitions, which are code too.

## Reference material

Load these when the work touches them — don't read all of them by reflex.

| File | Read when |
|---|---|
| `references/problem-framing.md` | **Read at Gate 0**, and in Plan mode before deciding the shape. What "solved" means, least-resistance vs architecturally right, version skew, trust boundaries, type-over-guard, batch failure, cardinality, reversibility |
| `references/data-flow.md` | Stores, providers, caches, payloads, derived state, selectors, fallbacks, save races |
| `references/composition.md` | **Read for any non-trivial component.** Compound components, functional style, selectors, file/naming conventions |
| `references/architecture.md` | Structuring components/hooks/state, deciding whether to abstract, any SOLID/DRY/pattern question |
| `design-patterns` skill | All 22 GoF patterns as TS/JS/React shapes: symptom → pattern table, look-alikes, when not to |
| `figma-inspect` skill | Any UI built from a design: the layer inventory and coverage table for the skeleton; exact values only when visual work is assigned |
| `references/performance.md` | Lists, animations, re-render complaints, slow startup, bundle size, memoization decisions |
| `references/states-and-platform.md` | Any UI work: loading/empty/error/offline, lifecycle/identity-reset, a11y, iOS vs Android, RTL, i18n |
| `references/worst-case-data.md` | A component that renders data — names, counts, prices, dates, images, lists: map every rendered value to its limit, feed plausible worst cases, report what breaks |
| `react-native-animations` skill | Motion, gestures or haptics in scope — building them, or reviewing a diff that adds or changes them |
| `references/regression.md` | Planning, and before every Gate 2 — blast-radius method and the QA checklist generator |
| `references/testing.md` | Writing or reviewing tests (Jest + Testing Library) |
| `references/examples-house-style.md` | **Before writing or reviewing component code.** Bad / good / over-applied pairs for ternaries, conditional rendering, function signatures and comments, each with "does not apply when" |
