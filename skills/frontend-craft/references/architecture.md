# Architecture, principles, and patterns

Principles are diagnostic tools, not goals. Nobody's code got better because it "follows SRP" — it got better because a function stopped doing three unrelated things and became testable. So: never invoke a principle by name as justification. Name the concrete smell, the threshold it crossed, and the fix.

The most expensive failure mode here is the opposite of messy code: **premature abstraction**. A factory, an interface, and a strategy registry where two functions were needed is harder to delete than duplication is to tolerate. When in doubt, duplicate and wait.

## Contents
- [Smallest change that solves it](#smallest-change-that-solves-it)
- [When NOT to abstract](#when-not-to-abstract)
- [Component smells](#component-smells)
- [Hook smells](#hook-smells)
- [State ownership](#state-ownership)
- [Narrow interfaces](#narrow-interfaces)
- [Layering](#layering)
- [Functional style in React](#functional-style-in-react)
- [Patterns that actually pay off in React](#patterns-that-actually-pay-off-in-react)
- [TypeScript smells](#typescript-smells)

## Smallest change that solves it

Solve the reported problem at the **narrowest layer that can actually solve it**, and move outward only when the narrow option is demonstrably insufficient — not when it merely feels less elegant.

> **First, establish what "actually solve it" means.** This ladder chooses among solutions that close the problem for everyone who has it; it is not a licence to pick the narrowest thing that makes the symptom disappear. A fix in the screen where the bug was observed does not reach the other caller, the other platform, the data already written, or the app builds that will never update. Answer "after this ships, who still has the problem?" *before* climbing — `problem-framing.md`. Skipping that step and then applying this section is precisely how a partial fix gets shipped with a confident description.

The ladder, innermost first: **the screen or component that reported the bug → its feature folder → a shared UI primitive → a hook → `core`/shared logic → the API contract.** Each rung outward multiplies the consumers you must verify (see the blast-radius rule in the main skill) and the surface a regression can appear on. A fix in one screen is reviewable in a minute and revertible in one commit; the same fix pushed into `core` is a cross-platform change with a QA pass on both apps.

So, in order of preference: config and constants, then wiring at the call site, then a targeted conditional in the feature, then a new prop on the shared thing, then a change to the shared thing's behaviour, then a contract change. **Keep existing contracts unless the task asks to change them** — an API shape, a provider's public methods, a component's props are promises to callers you are not reviewing.

When several solutions are genuinely valid, the tie-breakers are: **fewest files touched, least contract change, lowest operational risk, easiest to revert.** Not fewest lines — a slightly longer local fix beats a clever one-line change to something shared.

Two corollaries, both about restraint:

- **Do not fix adjacent problems.** If it doesn't block the requested change, it is not in this change. Note it in the report so the user can decide; a bugfix diff that also refactors two neighbours is a diff nobody can review, and it makes the revert dangerous.
- **Do not add abstractions, fallback paths, or cross-layer behaviour the task didn't require.** A defensive `?? []` "just in case", a retry nobody asked for, a new adapter for one caller — each is speculative, untested, and permanent. See `data-flow.md` → Fallbacks are domain policy for why the defensive fallback is the worst of the three.

This is the counterweight to everything else in this file. The rest of it tells you what good structure looks like; this section says the task in front of you is usually not the moment to install it.

## When NOT to abstract

**Rule of three.** Two similar things are a coincidence. Extract on the third — by then you can see which parts actually vary.

**Duplication is cheaper than the wrong abstraction.** Two code paths that look alike but change for different reasons must stay separate. Ask: "if requirement A changes, does B have to change too?" If no, they were never duplicates. A `Card` used by checkout and by search results will diverge; sharing it means every checkout change risks search.

**A parameter added to a shared function to serve one caller is a signal to fork it.** Especially a boolean. `formatPrice(value, isCompact, withCurrency, forExport)` is four functions wearing a trench coat.

The variant that looks responsible and isn't: a `mode`/`strategy` parameter whose *default preserves the old behaviour* for the existing callers while the new caller opts in. It reads as careful — nothing breaks — but it ships two behaviours for one concept and makes every future caller choose a side, in a module they don't own. Before writing it, ask the module's owner the only question that matters: **is the old behaviour still correct?** Often the new caller's behaviour is what everyone should have had, and the flag existed only to avoid asking.

**Config objects that only ever get one shape are not extensibility.** Delete the indirection.

## Component smells

| Smell | Threshold | Fix |
|---|---|---|
| Component does fetching + transforming + navigation + rendering | more than 2 of those | Move data to a hook, keep the component about layout |
| Boolean props | 3+, or any two that are mutually exclusive | Two components, or a `variant` union |
| Prop drilling | passed through 3+ levels untouched | Composition (`children`/slots) first; context only if genuinely cross-cutting |
| Nested ternary expressions | Any nested ternary in JavaScript or TypeScript, including JSX and non-render logic | `if`/`else`, `switch`, early returns, or named derived values/components |
| Component file size | ~200 lines of JSX, or 3+ distinct visual sections | Extract sections as local components in the same file first — only move to separate files when reused |
| Props interface | 10+ props | The component has multiple responsibilities, or should take `children` |
| Props that configure the component's internals (`showHeader`, `renderFooter`, `modalContent`) | any | Compound component — the caller should own structure. See `composition.md` |
| `useEffect` writing state derived from props/state | any | Compute during render; derived state in an effect is a re-render and a stale-value bug waiting |
| `useEffect` with a "sync two sources of truth" job | any | One of them isn't a source of truth. Delete it |

**Open/closed, concretely:** if adding a new variant means editing a `switch` inside the component *and* editing its props type *and* editing every consumer, the extension point is in the wrong place — pass the varying part in (a render slot, a component prop) instead of enumerating variants inside.

**Substitution, concretely:** a component that accepts `onPress` but silently ignores it in one variant, or a hook whose return type is the same but whose contract changes by argument, breaks callers who reasoned from the type. Make the difference visible in the type.

## Hook smells

- **Returns 4+ unrelated values** → it's two hooks. Cohesion test: would any caller use half the return and ignore the rest? If yes, split.
- **Takes a callback that it only calls in one branch** → the caller should own that branch.
- **Name doesn't say what it does** (`useData`, `useLogic`, `useHelper`) → the boundary is wrong; you couldn't name it because it doesn't have one job.
- **Contains `if (Platform.OS === ...)` around most of its body** → two hooks with a shared type, or a `.ios.ts`/`.android.ts` split.
- **Depends on navigation, route params, and global state, and is used by one screen** → it's screen code. Leave it in the screen; a hook used once that isn't testable in isolation bought nothing.

## State ownership

Decide ownership before writing anything. Most React state bugs are ownership bugs.

1. **Server state** — anything that came from an API. Owned by a query layer (TanStack Query, RTK Query, SWR). Never copy it into local state "so I can edit it" without an explicit reason; that copy will go stale.
2. **URL / route state** — anything that should survive a refresh or a deep link: filters, tabs, selected id, pagination. Owned by the router.
3. **Global client state** — genuinely cross-screen and non-server: session, theme, feature flags, cart-in-progress. Keep it small. Every addition here is a new way for two screens to disagree.
4. **Local state** — everything else. Default here. Move it up only when a second consumer actually exists.

### Singleton stores keyed by one entity

A store that holds **one entity at a time plus the key it belongs to** (`productReviews` + `productReviewsForUnique`, `currentOrder` + `currentOrderId`) is a cache with room for exactly one tenant. It is fine while one screen uses it, and it races the moment two do — two screens on the stack, or a screen and a preview of the same thing.

The read side usually looks safe: `storedKey === requestedKey ? data : {}`. That guard is correct and it is also what makes the failure silent. The write side is last-writer-wins, so a slow request for the entity the user *left* can land after the fast one for the entity they're *on*; the key now names the wrong entity, the guard withholds the data, and the current screen cannot tell "superseded" from "still loading". It waits forever, with no error anywhere.

Ranked fixes:

1. **Key the cache, not the store** — a record by id. The race disappears instead of being handled.
2. **Ignore superseded results at the write boundary** — the method drops its own response when its key is no longer the active one (needs a request-id or abort the store can see).
3. **Recover on the read side** — the focused screen notices its own load settled yet the store doesn't answer for its key, and reloads. Bound it (once per key) so it can never become a request loop, and remember only the focused screen may do it.

Reviewing this: the tell is a provider exposing `<thing>` next to `<thing>ForUnique`, consumed by more than one screen. Ask what the second screen renders when the first one's request wins the race.

**Derived values are not state.** Compute them. If the computation is expensive, that's a memo question (see `performance.md`), not a state question.

**Form state** belongs to the form, not to global state, until submit.

Ownership across representations, selectors, fallback semantics, and save races live in `data-flow.md`. Read it whenever the change touches a store, a cache, a provider, or a payload.

## Narrow interfaces

Every caller should depend on what it uses and nothing more. The smells, all of which show up as "why did changing X break Y":

- **Prop bags.** A component taking a whole entity to render two of its fields now re-renders on every field, and cannot be reused where only those two exist. Pass the two.
- **Kitchen-sink context.** A provider exposing fifteen values makes every consumer a subscriber to all fifteen. Split by concern, or expose selectors that let a consumer subscribe narrowly.
- **Generic `options` objects** whose properties are only meaningful in some combinations. That's a discriminated union pretending to be a config.
- **Full-entity saves** where a command with the changed fields would do — see `data-flow.md` → Save races.

The fix is usually a narrower type at the boundary, not a new layer: a view model, a command shape, or a focused hook. When you widen a shared interface to serve one caller, that's the signal to fork it instead (see `When NOT to abstract`).

**Substitution across implementations:** when several things satisfy one contract — component variants, provider implementations, strategy handlers — each must honour what callers reasoned from the type. An implementation that throws on valid base-contract input, ignores a required field, narrows the accepted values, or returns a different empty/error shape forces every caller to special-case it. In TypeScript, structural assignability is not semantic compatibility; the compiler will accept it and the caller will still break.

## Layering

Three responsibilities, one direction of dependency. The names below are descriptive — **use whatever the project already calls these**:

```
ui        components, screens — knows about layout and interaction, nothing about endpoints
domain    hooks, business rules, mapping — knows about the app's concepts
data      api clients, storage, SDK wrappers — knows about transport and shape-on-the-wire
```

UI may depend on domain; domain may depend on data; nothing depends upward. The practical test: **can you change an API response field name and touch only the data layer (plus a mapper)?** If a field name from the backend appears inside JSX, the layering is decorative.

### Never call the transport from a component or a hook

Before writing a single request, **find where this project already puts its API calls** — a provider method, a service class, a query hook, a generated client, a repository module. Open two or three existing calls and copy that shape exactly. Reaching for the raw `api()` / `fetch` / `axios` from inside a component or a feature hook is the single most common way an AI-written change is architecturally wrong while still passing type-check and lint.

It stays wrong even when it is shorter, even when the call is one line, and even when a written plan told you to do it. A plan that says "call the api directly from the hook" is describing an outcome, not sanctioning a shortcut around the project's data layer — implement the outcome the project's way, and say in your report that you deviated from the plan and why.

The symptom to catch in review: a hook that imports the transport, holds the endpoint string, and knows the response shape. That hook is now three layers at once, and the next endpoint change has to find it.

### Effects belong to the platform layer, not the shared one

Shared code — a cross-platform `core`, a `common` package, anything imported by more than one runtime — should export **the call and the pure logic**, not the lifecycle that triggers them. `useEffect`, timers, subscriptions, `AppState`/visibility listeners, storage access, and constructors wiring them up are platform concerns: they belong in the web or the mobile layer, where the platform's own primitives live.

The reason is not purity for its own sake. An effect in shared code hard-codes *when* the request fires, and the two platforms rarely agree on when — mobile has backgrounding and screen focus, web has tab visibility and route changes. Ship the mechanism from shared code and let each platform own the trigger, and both stay honest. Ship the effect and the second platform will either fight it or fork it.

### The shared layer is the intersection of its consumers, not the union

`core`/`common`/`shared` holds what **every** consumer imports. A helper that exists for one platform's constraint — repairing a deep link before handing it to the system browser, sniffing whether a URL has a native route — is that platform's code even when its subject matter (a URL both platforms build) is shared. Put it in that platform's tree and let the shared layer keep only the builder they both call.

The check is mechanical, so run it instead of reasoning about it: after adding a file to the shared layer, grep its export name across each consumer root. Hits from one root only means it does not belong there. Getting this wrong is not a style loss — a shared module accretes single-platform branches until nobody can change it without testing both apps.

Server DTOs stop at the data layer. Map to app-owned types once, at the boundary. This is the single highest-leverage structural rule in a frontend codebase — it makes backend changes a one-file problem.

Once a codebase has more than a handful of screens, slicing by feature tends to beat slicing by file type — but this is a decision a codebase makes once. **Never restructure someone's project as a side effect of a feature task**; work within the existing scheme, and raise reorganization as its own proposal if it's genuinely warranted. Whatever the scheme, cross-feature imports go through a feature's designated entry point; a deep import into another feature's internals is a coupling bug.

## Functional style in React

The house style and its concrete idioms live in `composition.md` — read that for how it's actually written here. The React-specific constraints that belong with the architecture rules:

- **Pure render.** No mutation, no I/O, no `Date.now()`/`Math.random()` during render.
- **Immutability across boundaries.** Never mutate props, state, or arrays received from props. `[...items]` before `.sort()` — `.sort()` and `.reverse()` mutate in place, and the resulting bug is invisible until a memo fails to invalidate. Local mutation of a local accumulator inside a pure function is fine.
- **Pure helpers over inline logic.** Transformation logic goes in a pure function outside the component, wherever the project keeps non-React logic: trivially testable, and it stops being re-created every render.
- **Total functions.** Handle every case of a union; exhaustive `switch` with a `never` check so a new variant is a compile error rather than a blank screen.
- **Data-in, data-out over side effects.** A function that returns the new value is testable; one that sets state is not.

- **No hidden inputs.** Clock, randomness, locale and flags are arguments of a pure function, read by the caller at the edge.

**Skip:** currying for its own sake, point-free style that hurts stack traces, custom `compose`, `fp-ts`, recursion over flat data, class-based OOP hierarchies in a React tree. Full take/skip list with reasons: `composition.md` → FP toolbox.

## Patterns that actually pay off in React

**Composition follows the ladder in `composition.md`** — plain props, then compound components, then composer + providers, then lifted state. Read it before reaching for anything below; most of what the table describes is a lower-leverage answer to a problem a rung already solves.

| Pattern | React shape | Use when |
|---|---|---|
| Custom hook as strategy | `useSomething()` swapped by caller | Same UI, different data/behavior source |
| Adapter | Mapper at the data boundary | Always, for API responses |
| Facade | One module wrapping an SDK (analytics, push, storage) | Any third-party SDK — it also makes the SDK mockable and replaceable |
| Provider | Context + hook, exported together, provider not exported raw | Cross-cutting concerns only; every provider is a re-render boundary |
| Factory | Function returning one of N implementations | Only when N ≥ 3 *and* selection is at runtime. Otherwise a `switch` at the call site is clearer |
| Observer / event bus | — | Rarely. In React, this is usually state in the wrong place. Justify it explicitly |
| Singleton | Module-level instance | Fine for clients (api, storage). Not for state — it's untestable and survives across tests |

If you reach for a Gang-of-Four name, first write the version without it. If the plain version reads worse, use the pattern; if it reads the same, you just added a layer.

The full catalog — all 22 patterns with the abstract idea, the TS/JS form, the React analogue, the justifying symptom and the look-alikes — is the `design-patterns` skill (`references/creational.md`, `structural.md`, `behavioral.md`). This table stays the short list of what pays off here; the thresholds above still win over that skill's catalog.

## TypeScript smells

- `any` → almost always. `unknown` + narrowing where the shape is genuinely unknown.
- `as` assertion → you're overriding the compiler. Each one needs a reason in a comment, or a type guard instead.
- `!` non-null → same. Handle the null.
- Optional props that are actually required in half the variants → discriminated union.
- Enum-like string unions duplicated in three files → one exported type.
- Types written by hand for API responses that a generator/schema could produce → drift risk; note it.
