# Mode: Build

## Contents

- Gate 0 — establish what "solved" means
- Gate 1 — check in before writing code
- Blast radius is not optional
- While writing
- Gate 2 — pre-flight before saying "done"
- Gate 3 — the report

Used by `wf-implement` for React/RN code. Git and plan lifecycle: global instructions and `ai-workflow`.


### Gate 0 — establish what "solved" means

Before deciding *where* the code goes, decide *what has to become true*. Answer three things, five lines each: what "solved" means (whose problem, which population of cases, over what window, what observation proves it), the path of least resistance and the limit that makes it partial, and the architecturally right path and its cost.

This is not a re-run of Gate 1's "chosen shape + alternative", which compares implementations. Gate 0 asks whether the implementation being compared solves the reported problem **for everyone who has it** — the question that produces clean, tested, well-described changes that fix a smaller problem than the one reported. The one-line version, applied to every task: *after this merges, who still has the problem?* If the answer is "some people, for a while", that is the shape of the task, not a footnote.

**Read `references/problem-framing.md`** for the three answers and the lenses that catch this class — population and time window (clients you cannot update), whose invariant it is, symptom vs class, type over runtime guard, batch failure semantics, unbounded growth, and how reversibility sets how much rigour to buy. Read it whenever the change touches a client that ships in a build, a contract owned by another system, a batch or telemetry pipeline, persisted data, or a runtime guard you are about to add.

For a genuinely local change with one call site, Gate 0 is three lines inside the Gate 1 block, not a separate pass.

### Gate 1 — check in before writing code

The user asked for this explicitly: **always check in before implementation.** For planned work, the developer's approval of the plan is the check-in; do not repeat Gate 1 unless implementation reveals a material ambiguity, scope change, or expensive-to-reverse choice. For unplanned work, present the compact check-in below and wait before coding. The point is to catch a wrong assumption before it becomes a defect without adding duplicate approval stops.

Present, compactly:

```
**Solves it for:** which cases, over what window — and who still has the problem after this merges
**Plan:** what I'll change, file by file
**Blast radius:** everything else that consumes what I'm touching
**Approach:** chosen shape + the one real alternative and why not
**Not covered:** what this leaves open, and where the rest lives
**Risks:** what I'm unsure about
**Assumptions:** what I'm about to assume if you don't correct me
```

Keep it short — a screenful. Then stop and wait. If the user says "just do it" or the change is a genuine one-liner with no consumers, note the assumption and proceed.

### Blast radius is not optional

Before editing anything shared — a component, a hook, a util, a type, a style token, an API response shape — **grep for every consumer and open them.** This is the #1 source of the user's escaped defects: the change is correct on the screen they were looking at and wrong on the two they weren't.

```bash
rg -n "ComponentName|useThatHook" -g '*.{ts,tsx}'
```

For each consumer, state in one line whether it is affected. If more than ~5 consumers, that fact belongs in the check-in — it changes the shape of the work.

**When the thing you derive from is route params, context, or a shared cache, the consumers are only half the inventory — enumerate the writers too.** Who calls `setParams` on this screen? Who writes this provider field, and for which entity? A screen whose identity is rewritten in place (`navigation.setParams` from a colour swatch, a variant picker) never remounts, so every flag you derive keeps answering for the previous entity until something re-keys it. Grepping `navigate('product'` finds how the screen is *opened* and misses exactly this. `references/states-and-platform.md` → Reset on identity change, `references/data-flow.md` → Freshness has a key.

**Changing the *shape* of a shared symbol is the highest-risk edit there is** — a function's parameter object, its return type, a prop, a context value. Every caller you don't update in lockstep breaks *at its own call site*, far from your diff. In a monorepo those callers sit in platform roots you don't have open: a `core`/shared provider method is called from web (`source/`) **and** mobile (`mobile/`) **and** sometimes admin — updating the caller in the tree you happen to be editing is *half the job, and half is broken*. So: grep the symbol name across the **whole** repo (not the current folder), enumerate every call site by platform, update all of them, and let a **full, unfiltered** typecheck confirm you missed none — the compiler error on a caller you forgot is the safety net, so the run has to be able to show it (see Gate 2). "I updated the callers I could see" is the exact shape of the escaped P1.

### While writing

- Before writing component code, read `references/examples-house-style.md`. When a rule's "Does not apply when" matches, do not apply it — an over-applied rule is a defect too.
- A reachable state the plan or task does not decide: ask in the report, and keep the code compiling without deciding it — an explicit `throw` whose message names the open question, never a missing return or a silent default.
- Match the surrounding code's idiom. Consistency beats your preference.
- **Solve it at the narrowest layer that can actually solve it**, and don't fix adjacent problems on the way. A screen-local fix beats the same fix pushed into `core`, because the rungs outward multiply the consumers you have to verify — and don't change an existing contract unless the task asks for it. `references/architecture.md` → Smallest change that solves it.
- **Fetching anything? Find the project's data layer first and use it.** Never call `api()`/`fetch`/`axios` from a component or a feature hook — go through the provider method, service, or query layer the project already has. And keep effects out of shared/cross-platform code: it exports the call, the platform owns the trigger. `references/architecture.md` → Layering.
- **About to fire one request per item? Read the API's route table first.** A client-side fan-out — N parallel calls to a single-entity endpoint, then filter and sort the results locally — is a design that wants a batch endpoint, and reviewers ask why you didn't use one. Check the real route definition (path-param regexes, accepted query params, what the handler does with them) before building around its absence. If no batch shape exists, that is a backend ticket to open and to name in the PR description with the route quoted; the same fan-out reads as a shortcut when shipped silently and as a decision when the constraint is stated.
- **Lifting code into a shared layer takes its importers with it.** Repoint every call site and delete the old file. A re-export shim left behind (`export { x } from '../../core/x'`) is not backwards compatibility inside one repo — it is a second name for one thing, and it teaches the next reader the wrong owner. The full typecheck, not a grep of the tree you happen to have open, is what proves you found every caller.
- **A `mode`/`strategy`/`variant` parameter added to a shared function so the existing callers keep their old behaviour is a fork with both halves shipped.** Before writing it, ask whether the old behaviour is still correct at all — often the new caller's behaviour is what everyone should have had, and the flag exists only to avoid the conversation. That conversation belongs to whoever owns the shared module. See `references/architecture.md` → When NOT to abstract.
- **A new guard, gate or freshness flag is new logic, not a condition — enumerate how it can be wrong before you ship it.** For every value it reads, ask what makes that value lie: a stale entity that still matches the id, a boolean the owning hook raises one render late, a `finally` on a group of promises where only one of them is the one you care about, a ref that never resets on a second instance. And read the *completion* you anchor on: `Promise.all(...).finally()` runs on the **first rejection** of any member, so settling anything there settles it while your own request is still in flight. `references/data-flow.md` → Freshness has a key.
- Every branch of the UI needs a state: loading, empty, error, offline, and the too-long/too-large content case. `references/states-and-platform.md`.
- **A component that renders data gets the worst-case pass** — list every rendered value with its source and limit, then feed plausible worst cases through the same boundary the demo data uses: `1`, `2`, `5`, `21` for plurals, a missing optional field, a 404 image, the long second-locale label. Report the breaks; style fixes stay the developer's unless visual work is assigned. `references/worst-case-data.md`.
- A component that takes an identity prop (id, route param) must survive that prop **changing in place** — reset instance state, one-shot refs, and timers on the change, or key the component by identity. `references/states-and-platform.md` → Reset on identity change.
- **Normalizing a value before validating or submitting it? Every surface that tells the user whether the value is acceptable must judge the normalized value too** — checkmark, inline error, disabled submit button. And do not achieve that agreement by normalizing inside `onChange`: writing a transformed value back on every keystroke makes the input jitter and the cursor jump. Raw state while typing, normalize at the validity check and on blur, keep the submit path normalizing anyway. `references/states-and-platform.md` → Normalized values and validity feedback.
- **Porting a screen from the sibling platform? Port its guards, not just its markup.** The web version's early-return block — the redirect when a setting is off, the permission check, the not-found throw — is part of the feature, and it is the half that has no visual reference to remind you it's missing. Read the sibling's guards line by line against yours. And put the gate **on the screen**, not on the button you navigate from: a new route is deep-linkable from day one, so a gate that lives only in the caller does not exist. When the flag arrives asynchronously, gate on *loaded and off*, never on falsy-while-unknown, or the first frame bounces the user off a screen they're allowed to see.
- **Anything you write into a URL, route param, deep link, or storage must survive the round trip.** Emitting a new field is half the contract; the other half is parsing it back at the destination and re-emitting it on every hop the flow takes — each intra-flow navigation, redirect, or "continue" CTA rebuilds the URL from scratch and silently drops whatever it doesn't name. So after adding a field to a builder, grep every **construction** site of that builder (not just its importers) plus the hook that reads the params, and confirm the value is still there at the last step of the flow. An optional field makes this invisible to the compiler: nothing goes red, the value just stops existing after the first transition, and the analytics it fed are quietly wrong.
- **Log metadata, never payload.** Error scopes, breadcrumbs, analytics params and crash context get serialized verbatim into a pipeline someone else reads — so pass a failure reason and stable identifiers of *kind* (entry point, source, screen), not the thing itself. A URL is not neutral: query strings carry phone numbers, order ids, emails, tokens, so logging a "url" logs its contents. Same for request bodies, form state, user objects and API error payloads. Check the project's rule (`AGENTS.md`/`CLAUDE.md` usually has one) — but assume the rule is "never log PII" and that a full URL counts as PII.
- Apply principles by smell and threshold, never by name. `references/architecture.md`.
- Reaching for a GoF pattern, or a diff/plan names one (factory, adapter, facade, strategy, observer, decorator, proxy, command, state machine…)? Load the `design-patterns` skill — pick by symptom, use the TS/React form, and apply its "When not to" before adding the layer.
- Performance decisions come with a number, not a vibe. `references/performance.md`.
- Tests: `references/testing.md` (Jest + Testing Library).

### Gate 2 — pre-flight before saying "done"

Do this as a **separate pass**, reading the full diff as if someone else wrote it and you're the reviewer who'll be blamed for merging it. Reading your own code in build-mode is how the small stuff survives.

Run the project's real commands and show real output:

```bash
# whatever the project actually has
npm run typecheck && npm run lint && npm test
```

Do not claim green without output. "Should pass" is not a result.

**Judge by the whole result — never a filtered slice.** Do not `grep`/`rg` a typecheck, lint, or test run down to the files you think you touched, then declare "no errors in my files." The error that matters most is in the file you did *not* expect: the caller you forgot to update, in a folder your filter didn't name. Filtering the output to an allowlist of expected paths discards exactly the signal that catches a blast-radius miss — it converts a real red into a reported green, which is worse than not running the check at all, because now it's laundered as verified. Read the command's overall verdict first — exit code, total error/failure count, the summary line — and only *then* zoom into specifics. If the tool is too noisy to read whole, fix the noise or scope the command itself (a project/tsconfig path), not the output through a name filter you authored.

Then walk the diff against this list. These are the specific categories that have escaped to production before:

**Dev leftovers**
- `console.log` / `debugger` / commented-out code
- Comments that restate the code, label sections, or narrate the change — delete them (see House style)
- Hardcoded test data, mocked endpoint left in, temporary feature flag
- `TODO` / `FIXME` added in this diff
- Unused imports, variables, props, dead branches — check with the linter over the whole tree, then intersect the hits with the files this diff touches; the project's baseline noise is not yours to fix, and it is not yours to hide behind either
- A new component, icon, or asset whose only reference is a **test mock** — a `jest.mock('./NewThing')` with no `import NewThing` anywhere in `src` is dead code that shipped with a helper keeping it alive
- Renamed something but left the old name in a comment or a test description
- Formatting churn you did not intend: a formatter run over a whole file (or a bulk `--write` of every changed path) re-creates hundreds of lines of diff in files that were non-conformant on the base branch. Format the paths you authored, listed explicitly
- Editor configuration (`.vscode/`, formatter settings, `formatOnSave`) and unrelated test-fixture swaps — both belong to a separate PR, and the second one drags snapshot churn along with it
- Refactoring outside the task — renamed files, moved modules, decomposition into files, renames not local to the module — belongs to a separate PR (and to the team PR guide, local overlay `company/pr-guide.md`, when present)

**Consumers of what changed**
- Every call site from the blast-radius list — re-verify after the fact, not just before
- Changed a shared function's argument or return **shape**? Every caller in **every** platform tree (web `source/`, `mobile/`, `core/`, admin) updated in lockstep — grepped by symbol name repo-wide and confirmed by the *full* typecheck, not a name-filtered view of it
- Types updated everywhere, no `any` or `as` smuggled in to silence the compiler
- Removed/renamed prop: did every usage get updated, including in tests and stories?
- Added an **optional** field to a shared builder/contract? The typecheck is green by construction, so it proves nothing here — walk the flow by hand instead: emitted → parsed at the destination → re-emitted by every next-step navigation, redirect and CTA, down to the final screen

**Logging, telemetry & sensitive data**
- No URL, request/response body, form state, user object or API error payload handed to a logger, error scope, breadcrumb or analytics event — reason + stable non-identifying metadata only
- The query string is the trap: `orderId`, `phone`, `email`, `token` ride along inside a value that looks like a harmless "url"
- New analytics/log call re-checked against the project's own logging rule, not just against taste

**Lifecycle & identity** *(the class that ships looking fine)*
- Does any component or hook here take an **identity prop** — an id, uid, route param — that can change **in place**, without a remount? If so, every `useState`, every one-shot ref (`didAnnounceRef`, `didInitRef`, `hasAnimatedRef`), every timer/animation/subscription, and every in-flight request must reset or cancel when that identity changes — otherwise it's still describing the *previous* identity. The dead one-shot latch is the worst case: it errors nowhere and silently kills the feature for every identity after the first.
- Does this screen read a **shared store keyed by a single entity id** (`xForUnique`, `currentItemId`, a provider that holds one entity at a time)? Then two screens on the stack — or a screen and a preview — race: the slower request for the entity the user *left* lands last, rewrites the key, and the screen they're *on* reads nothing and sits in its loading branch forever. The read guard (`storedId === requestedId ? data : {}`) is what makes it silent: it turns a stale write into a permanent "not loaded yet". `references/architecture.md` → Singleton stores keyed by one entity.
- The tell that in-place switching is real, not hypothetical: a sibling hook already guards for it (`previousIdRef`, `setState(null)` on id change, a request-id or abort keyed to the id). If one part of the feature resets on identity change and another doesn't, the one that doesn't is the bug.
- Fix with `key={identity}` at the mount site (remounts, resets everything) or `useEffect(reset, [identity])` that also clears timers; prefer deriving over storing. Cover it with a test that *switches* identity, not just one that mounts. `references/states-and-platform.md` → Reset on identity change.

**Styles** *(developer-owned by default)*
- Default: the diff adds **no** style values — no spacing, sizes, colours, fonts, radii, shadows, animations, inline styles, new style files, values copied from neighbouring code, or placeholders. Structure, states, handlers, i18n'd text and accessibility only, mapped from `figma-inspect`'s coverage table
- Only when the developer assigned visual work for this task: every value comes from a Figma node, an exactly equal token, or the developer's approval — listed with its source in the report; no rounding to the nearest token
- Pixel matching and final Figma comparison remain human QA; independent AI review checks states, behaviour and style provenance in code
- Pressed / disabled / focused / loading states exist on every interactive element
- Long text truncates or wraps deliberately; no clipping
- Layout survives the smallest supported screen and the largest system font

**Text and content**
- No hardcoded user-facing strings — every one goes through the i18n layer
- Every new key exists in every locale
- Numbers, dates, currency, plurals formatted through the locale layer, not string concatenation
- Error messages are the ones a user should see, not the ones the API returned

**Input, validation, and feedback**
- Any value normalized before validation or submit: the checkmark / inline error / disabled-submit state reads the **same normalized value** the accept decision reads. Test it with the padded or unformatted input, asserting the indicator *and* the accept decision
- No normalization inside `onChange` — raw state while typing, normalize on blur and at submit, or the input jitters and the cursor jumps
- Moved a transform to a different point in the flow? Re-check every consumer of the old behaviour, including the acceptance criteria of the ticket that introduced it

**Entry points and gates** *(new routes and screens)*
- **The same control rendered on a second screen carries the same guards as the first.** A CTA gated on "this entity's data has settled" in the detail screen and ungated in the list is the list's bug — and it is invisible in review because each file reads fine alone. Grep the control's component name, open every render site, and compare their conditions side by side.
- A guard whose condition reads "has this loaded" must accept **loaded-and-empty** (`{}`, `[]`, `0`) as loaded. Truthiness helpers usually don't — the project's own `isObject`/`isTruthy`-style guard may return `false` for an empty object, which hides the UI forever for exactly the users with no data. Cover the empty case with a test; a snapshot of a screen where the data is absent proves nothing.
- The screen enforces the same feature setting / permission / role as its sibling platform, **on the screen itself** — a deep link reaches it without passing the caller that hides the button
- The gate reads *setting loaded and off*, not *falsy*, so an async flag can't bounce the user on the first frame
- The gate's **exit actually exits**: "go back" is a no-op when the screen is the only route in the stack, which is exactly what a cold-start deep link produces. Guard it (`canGoBack()`) with a fallback to a real destination, or the user is stranded on the loader you render while leaving
- The route is registered everywhere the platform expects it: stack, param types, deep-link/linking config, and the path matches the sibling platform's URL
- Gated screen also **skips its requests**, not just its render — a disabled feature that still fetches is a leak the QA tab won't show

**Stacked branches** *(a feature split across a chain of PRs)*

A stack is one feature; a branch in it is only a checkpoint. Two failure modes, both invisible inside a single diff:

- **Stale parents.** Before doing anything on a branch in a stack — writing code, answering a review, judging whether a defect is real — verify each link is actually descended from the one below it: `git merge-base --is-ancestor origin/<parent> origin/<child>` for every pair, and merge downward until all of them pass. A branch cut from an older parent commit silently *un-does* fixes that landed below it. The symptom is a reviewer reporting a defect you fixed days ago, or a fix that "exists" in the repo yet is absent from the tip — and the temptation is to dismiss both as review noise. Never conclude "already fixed upstack" or "already broken downstack" from reading branch heads until the chain is verified; a stale link makes both claims wrong in opposite directions.
- **Expired promises.** A stack is where deferred work gets written into the code: a `TODO(NEXT-TICKET)`, a temporary filter, a const introduced for a consumer that arrives one PR later. Each one is a debt against a specific later branch, and nothing fails when that branch lands without paying it. Grep the whole stack for the next ticket's id, for constants with no reference, and for comments phrased "until X" — then check the tip, not the branch that wrote them. A const defined and never imported, and a workaround whose stated precondition has already been met, both read as intentional in isolation.

Judge every defect claim against the **stack tip** as well as the branch it was filed on, and say which one you checked. A defect that only exists at an intermediate head is a transient state, not a merge blocker — but say so explicitly rather than leaving the reviewer to guess, and confirm the successor really does close it.

**Porting a flow from a sibling platform**
- Port the flow's **terminal states**, not just its happy path. The confirmation screen, the "what happens next" guidance, the explanatory link next to a dead end — these are the parts a port quietly drops, because the mechanism (the request fired, the data saved) works without them and nothing in the type system misses them. Open the sibling's component and enumerate every branch it renders; a toast is not a substitute for a state the other platform gives a whole screen.
- Navigation is not a terminal state. Popping back on success loses the confirmation the sibling shows, and the user is left inferring the outcome from a toaster that disappears.

**Integration completeness**
- Every requirement in the ticket is actually implemented — re-read the ticket, line by line, against the diff
- Analytics events fired where the spec says
- API errors handled, not just the success path
- Nothing stubbed with the intent to "finish later"

### Gate 3 — the report

Every Build response ends with:

```
Implemented by: <model · effort, as the runtime reports them>

## What changed
<file-by-file, one line each>

## Rule trace
<BR-id → file:line → test or QA case, one per plan row; uncovered reachable states as questions; "no plan rules" when none>

## Checks
<actual output: typecheck / lint / tests>

## Manual QA — please verify
<numbered, concrete: "open X, tap Y with no network, expect Z">

## Regression risk from this change
<what else could have broken, and why you think it didn't>

## Decisions worth a second opinion
<anything you assumed, guessed, or chose between>
```

The manual QA list is for the user, before it goes to a tester. Make it specific enough to execute without thinking: screen, action, precondition, expected result. Generic items like "test the happy path" are noise — cut them.
