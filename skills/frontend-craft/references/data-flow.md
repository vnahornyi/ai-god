# Data flow and ownership

Read this when the change creates or modifies state, derived state, context/providers, stores, caches, persistence, optimistic updates, API payloads, or anything crossing a platform boundary.

`architecture.md` decides *where code lives*. This file decides *who owns a fact* — and most of the bugs that survive type-check, lint, and a careful read of the diff are ownership bugs.

## Contents
- [Unidirectional means one owner](#unidirectional-means-one-owner)
- [Count the representations](#count-the-representations)
- [Derive, don't carry](#derive-dont-carry)
- [When a selector earns its place](#when-a-selector-earns-its-place)
- [Fallbacks are domain policy](#fallbacks-are-domain-policy)
- [Payload shape](#payload-shape)
- [Freshness has a key](#freshness-has-a-key)
- [Save races and stale entities](#save-races-and-stale-entities)
- [Review bar](#review-bar)

## Unidirectional means one owner

Not "data physically moves one way" — request/response, callbacks and acknowledgements are all fine. The rule is about authority:

1. One **authoritative owner** per fact. It publishes downstream — to selectors, derived models, DTOs, components.
2. Consumers express **intent** upstream — a command, an action, a mutation — instead of writing into the owner's state.
3. The owner validates, applies, and publishes the new state downstream again.

The failure this prevents is two places that can both write the same fact. They will disagree, and the bug will be reported as "sometimes it shows the old value", which is the hardest class of bug to reproduce.

Concrete tells in a diff:

- two independently writable sources for one value (a provider *and* a local `useState` that both accept edits);
- **reciprocal effects** — an effect syncing A→B next to an effect syncing B→A. One of them is not a source of truth; delete it, don't balance them;
- a consumer writing into another module's store or storage key directly instead of going through its public command;
- state copied out of the owner "so it can be edited", with no path back and no invalidation.

And one rule that outranks local convenience: **do not recompute a value whose semantics belong to the server.** Promotions, taxes, delivery eligibility, permissions, regulated pricing — reuse the value the backend sent. Deriving only what the consumer genuinely owns (formatting, layout, sort order) is fine; re-deriving policy is how two screens end up quoting different prices for the same product.

## Count the representations

One business fact legitimately takes several shapes: a DB row, an API DTO, an app-owned entity, a form draft, a cache entry, a view model. Each additional shape is a place the fact can go stale.

So when reviewing or designing: **list every representation this change introduces or touches, and give each one a reason** — a boundary it crosses, a lifecycle it has, a consumer that needs it in that form. A shape whose only job is to rename or regroup fields of the previous shape is not a boundary; it is a place to forget to update.

Prefer canonical types and one direct mapping at the boundary over a chain of objects that repackage the same fields.

## Derive, don't carry

If a value is cheap and deterministic to compute from data you already have, **compute it at the point of use** — do not store it on the entity, thread it through a DTO, put it in the context, or write it into the cache.

`displayPrice`, `isAvailable`, `isMarkedDown`, `fullName`, `itemCount` — one shared pure function, called where it's needed. The moment such a value is materialised into a second location, it is a second source of truth with no owner, and it will diverge exactly when a product rule changes.

Storing a derived value needs one of three justifications, stated explicitly:

- it is a **snapshot** with audit meaning (the price *at the time of order*, which must not change when the catalogue does);
- it is part of a **contract** someone else owns (an API response field, a persisted schema);
- there is a **measured** performance reason.

"It was convenient" is not on the list. Neither is "the plan said so".

## When a selector earns its place

Selectors are the right answer often enough that they get overused, and a `core/` full of one-line aliases is its own maintenance tax. The bar is **both** halves:

**(a)** the read is used at two or more call sites — or the change clearly establishes multiple consumers; **and**
**(b)** it hides something worth hiding: a deep or externally-owned structure, a normalisation, a fallback, a unit conversion, or a piece of domain interpretation.

Both true → extract, and search first for an existing selector, predicate, projector, mapper or formatter that already does it under another name. Only (a) → it's an alias; inline it. Only (b) but one call site → leave it inline until the second consumer shows up.

Selectors stay **pure and deterministic**: no IO, no mutation, no logging, no caching, no reading the environment or the clock. They take the canonical entity plus any execution context explicitly, and compute on demand. A selector that reaches for a global is a hook wearing a selector's name.

## Fallbacks are domain policy

**Never silently collapse "missing" into a legitimate value.** `?? 0`, `?? ''`, `?? []` and `|| 'â€"'` each state, as a fact, that absent data and zero data mean the same thing. Sometimes they do. When they don't, the UI confidently lies and nothing errors.

The differences that matter, and that a fallback erases:

| Erased distinction | What the user sees |
|---|---|
| no rating yet vs. rated 0 | a fresh product shown as terrible |
| price unavailable vs. free | a paid item shown as free |
| not loaded vs. empty | "nothing found" during a load |
| request failed vs. no results | a silent empty state instead of a retry |

So: keep `undefined`, return a discriminated union or a result shape, or throw — whichever the consumers need to tell the cases apart. Then make the *consumer* choose the presentation, because that's a product decision and it differs per screen.

And check every consumer that depends on the distinction, not just the visible one: metrics, analytics payloads, sort/filter comparisons, and anything that aggregates. A `?? 0` that looks harmless in a card ruins an average.

## Payload shape

**Overfetching is a finding, not a nitpick.** A response that hands consumers fields they don't need is a leak surface: internal notes, permissions, operational flags, other users' data, payment and personal fields ride along into the client bundle, into Redux devtools, into a crash report, into a log. Ask what each field in a new or widened response is *for*.

**Match client state to backend semantics.** `missing` vs `null` vs `empty`, `stale` vs `loading`, `partial` vs `complete` — if the client flattens a distinction the API makes, decide deliberately, don't discover it later.

**Nullability follows lifecycle.** Draft, unpublished, imported, legacy and published records do not have the same required fields. Do not tighten a shared type to the published-only shape because that's what your screen sees — you will break the screens that see the others, and the typecheck will happily agree with you.

**`''` vs `null` on the way out.** A cleared input yields `''`; the server usually treats `''` and `null` differently, and often validates only one. Normalise once, at the payload boundary, and confirm the server actually accepts the shape you send — this is a five-minute check that catches a whole class of "why did the field not clear" bugs.

## Freshness has a key

"We have data for X" and "we fetched data for X during this render's visit" are two different facts, and a shared provider or cache answers only the first. Every claim the UI makes *about* the entity — availability, stock, price validity, permission, "no results" — is a claim about the second. Conflating them is how a screen states something false with a straight face, using data that is genuinely real, just from before.

So a freshness flag has three properties, and it needs all three:

1. **Keyed by the requested identity**, not by a request lifecycle. `pending = isLoading` answers "is a request running", which is a fact about the network, not about whether what you are rendering describes the thing you were asked to render.
2. **Computable during render.** The identity can change in a render; anything that only updates in an effect, an idle callback, or a subscription is one or more renders late, and those renders paint the previous subject's answer.
3. **Settled by failure too.** If a flag only clears on success, a failed request leaves a permanent skeleton. Clear it in the `finally`, and let the "do we have data" check decide what to show.

**The tell in a diff:** `isLoading` (or `isFetching`, `isPending`, `status !== 'success'`) guarding a statement about the current entity, on a screen whose entity can be swapped in place. Read where that boolean is *raised*, not just where it is read — a hook that calls `setLoading(true)` inside `requestIdleCallback`, a `useEffect`, a debounce, or a query that only flips `fetchStatus` after its own effect, is false during the window that matters. The window is not a race you can dismiss as unlikely: it is every render between the identity changing and the loader starting.

**Two traps sit inside this, and both look like the fix:**

*A matching identity is not currency.* `lastFetched?.id === requestedId` says the owner holds data **about** the right entity — never that it holds today's. An app-level provider keeps its last response for an id long after that screen closed, so reopening the same entity matches on the first render and releases the gate before the new request even starts. Freshness is a property of a **request occurrence**, so it has to be recorded by that occurrence: a ref, a request id, a generation counter that the request itself sets on its own outcome. Identity match is what you compare it *against*, not what proves it.

*A request group is not your request.* Settling freshness in `Promise.all([...]).finally()` — or in the shared `catch`/`finally` around a batch — hands the decision to whichever member finishes first, including a sibling that rejected while the one you care about is still running. Anchor to the individual promise (`request.then(settle, settle)`), and let the group keep owning only what it actually coordinates.

The shape that works:

```ts
// pending until this screen's own request for this id has settled — success or failure
const isDataPending = isRequestInFlight || settledIdRef.current !== requestedId;
```

Cached data still renders — it is real data, and blanking the screen on every revisit is its own defect (`states-and-platform.md` → the state matrix). What waits for the fresh answer is the **claim**: the badge, the availability text, the "unavailable" empty state, the sizes grid. Render what you have; assert only what you have re-checked.

## Save races and stale entities

Two related failure modes, both invisible in a screenshot.

**Full-entity saves.** If the screen sends the whole entity on save, everything loaded before the user's edit is now part of the write. Leave navigation or a second save enabled during the mutation and you send a stale snapshot, overwriting whatever changed in between — the classic lost update. Prefer a narrow update with just the changed fields; if the API demands the full object, lock the mutation and refresh from the response.

**Keys that outlive their data.** Anything holding an entity — a selector result, a context value, a cache entry, a loaded record — must **carry the key it represents**, and the render must compare that key with the one the route currently asks for. Without it, a route change shows the previous entity's data as if it were the new one. With it but no recovery path, you get the silent forever-loading case described in `architecture.md` → Singleton stores keyed by one entity. Both come from the same missing idea: identity is part of the data, not a separate variable next to it.

## Review bar

Report a data-flow finding only when the change introduces a concrete risk of: wrong data shown, stale data, a race or lost update, a broken invalidation, an erased absence distinction, a second source of truth, or a derived value materialised without one of the three justifications.

Name, in the finding: the authoritative owner, the competing or bypassing write path, the failure mode, and the narrow correction. "This should use a selector" without those four is a preference.
