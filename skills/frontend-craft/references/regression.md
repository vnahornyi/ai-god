# Regression control

## Contents

- Blast radius — do this before editing, not after
- Indirect blast radius
- Generating the manual QA checklist
- The self-review pass
- Reporting honestly


The premise: a defect found by a tester is a process failure, not a normal part of development. The tester's job is to confirm quality, not to discover it.

The dominant escape route is **the change that was correct on the screen you were looking at, and wrong on the two you weren't.** Everything here is built around closing that route.

## Blast radius — do this before editing, not after

For every symbol you're about to modify — component, hook, util, type, constant, style token, API response shape, translation key — find every consumer and read it.

```bash
rg -n "\bComponentName\b" -g '!*.snap'
rg -n "\buseThatHook\b|\bformatThing\b"
rg -n "from ['\"].*path/to/module" -g '*.ts*'      # who imports the module
```

Then, per consumer, answer in one line:

```
OfferTile.tsx        — passes `size` explicitly, unaffected
SearchResults.tsx      — relies on the old default of `size`, WILL CHANGE
CheckoutSummary.test   — snapshot will need updating
```

Signals that the change is bigger than it looks, and belong in the check-in:
- More than ~5 consumers
- Any consumer in a different feature/module from the one you're working in
- The symbol is exported from a shared/design-system/core package
- You're changing a **default value**, a **prop's optionality**, or a **return shape** — these break callers silently, with no type error
- You're changing something a test relies on but no screen imports directly

**Widening a type is safe; narrowing it isn't.** Adding an optional prop is safe *for existing callers*; changing what happens when it's absent is not.

But "safe for callers" is not "done". An optional field added to a shared emitter — a URL builder, a route-param object, an event payload, a persisted record — buys silence from the compiler, and that silence is the risk: the field now needs a **reader** and needs to be **re-emitted** at every hop of the flow, and nothing will go red if it isn't. Grep the builder's **call sites**, not just its importers, and trace one real flow end to end. The field that is emitted at step 1 and dropped at step 2 fails as wrong data, not as an error.

## Indirect blast radius

Things that break without appearing in any grep:

| Change | Also affects |
|---|---|
| Style token / theme value | Every screen using it — visual, invisible to the compiler |
| Shared z-index, spacing scale, container height | Layouts elsewhere |
| API request/response shape | Other screens reading the same endpoint; cached data of the old shape |
| Cache key or query key | Deduping/invalidation elsewhere; stale entries from a previous app version |
| Persisted storage shape | **Existing installs** — old data must still parse. Migration or a version guard |
| Navigation route name/params | Deep links, push-notification targets, analytics, back-stack behavior |
| New query/route param on a multi-step flow | Every later step that rebuilds the URL — attribution dies at the first transition that doesn't forward it |
| Anything logged, scoped onto an error, or sent as an analytics payload | The log pipeline and everyone reading it — a URL or body carries PII into it |
| Translation key rename | Every locale file |
| Global provider or context value | Everything below it re-renders; check perf-sensitive screens |
| Shared error/loading component | Every screen that renders it |
| Dependency version bump | Peer deps and native modules — RN bumps are never local |

Persisted data deserves special suspicion: your device has the new shape because you developed against it. A real user upgrading has the old one.

## Generating the manual QA checklist

Produced at the end of every Build, for the user to run *before* handing to a tester. Derive it, don't template it:

1. **The change itself** — the exact thing that was asked for, verified in the UI.
2. **One case per consumer** from the blast-radius list — this is the highest-value section and the one most often skipped.
3. **The state matrix** for any touched screen (see `states-and-platform.md`): empty, error, offline, long content.
4. **The identity-switch case**, if a touched component takes an id/route param that can change in place: open identity A, switch to B *in the same instance*, confirm B shows its own state and A's timers/badges/one-shot behaviours neither leak into B nor suppress it. See `states-and-platform.md` → Reset on identity change.
5. **The round trip**, if this change added a param to a URL, route or stored record: walk the flow to its last screen and read the URL/record there — the field must still be present, with its original value.
6. **The indirect list above**, for anything that applies.
7. **Platform pass** — both OSes if anything platform-touching changed; dark mode; largest system font.
8. **Anything the automated tests do not cover** — say plainly what isn't covered rather than implying it is.

Format each item so it's executable without thinking:

```
1. Cart → apply a promo code → expect discount row and updated total
2. Search results (uses the same PriceLabel) → prices still show currency symbol
3. Product detail with no network → error state with working Retry, not a blank screen
4. Android: hardware back from checkout → returns to cart, does not exit the app
```

Cut anything generic. "Test the main flows" tells the reader nothing and hides the items that matter.

## The self-review pass

Run this as a distinct step, after the code is written and the checks are green — **not while writing.** Build-mode attention is on making it work; review-mode attention is on what's wrong. Trying to do both at once is exactly how the small stuff survives.

Read the entire diff top to bottom as if reviewing a stranger's PR you'll be accountable for, and ask:

- Would I approve this?
- What would a picky reviewer flag first?
- Which line here would I be embarrassed by in three months?
- What did the ticket ask for that I can't point to in this diff? *(Re-read the ticket line by line — half-done requirements are one of the top escape categories.)*
- What's here that the ticket didn't ask for? (Scope creep is also a regression risk)
- Which part did I write while tired or in a hurry?

Then the concrete sweep — the categories in SKILL.md Gate 2: dev leftovers, consumers, UI fidelity, text/l10n, integration completeness.

`git diff` on the whole branch, not just the last edit. Things left behind three commits ago are invisible when you only look at what you touched most recently.

## Reporting honestly

- If something couldn't be verified — a platform you can't run, a flow needing backend state, a device you don't have — **say so explicitly.** An unverified item silently included in "done" is worse than an admitted gap, because nobody re-checks it.
- If a test was skipped or a check not run, say which and why.
- If a decision was a guess, mark it as one.

The goal is that the user knows exactly which parts are solid and which need their eyes. That trust is what makes the whole process faster than doing it manually.
