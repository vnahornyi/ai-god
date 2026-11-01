# States, accessibility, platform, and content

Most escaped UI defects are not in the code that was written — they're in the code that wasn't. The happy path gets built; empty, error, offline, long-text, small-screen, and second-locale get discovered by a tester or a user.

Treat this file as the list of things that must exist before a screen is finished.

## Contents
- [The state matrix](#the-state-matrix)
- [Normalized values and validity feedback](#normalized-values-and-validity-feedback)
- [Content edge cases](#content-edge-cases)
- [Accessibility](#accessibility)
- [Platform differences](#platform-differences)
- [Lifecycle and races](#lifecycle-and-races)
- [Text and localization](#text-and-localization)
- [Design fidelity](#design-fidelity)

## The state matrix

For every screen and every data-dependent component, all of these have a defined appearance. "Not designed yet" is an open question for the check-in, not a reason to ship nothing.

| State | What must exist |
|---|---|
| **Loading — first time** | Skeleton or spinner. Layout must not jump when data arrives |
| **Loading — refresh** | Existing content stays visible; a subtle indicator. Never blank the screen on a refetch |
| **Loading — pagination** | Footer indicator; the list doesn't scroll-jump |
| **Empty** | Explains *why* it's empty and what to do next. A blank screen reads as a bug |
| **Empty after filtering** | Different from empty overall — offer to clear the filter |
| **Error — recoverable** | Human-readable message + retry that actually retries |
| **Error — fatal** | Doesn't crash the app; error boundary with a way out |
| **Offline** | Distinguished from a server error. Say "no connection", offer retry, and retry automatically on reconnect |
| **Partial data** | Optional fields missing: no `undefined`, no "null", no empty gap |
| **Stale data** | If showing cached data, say so when it matters (prices, availability) |
| **Success** | Confirmation the action worked — the absence of an error is not feedback |

Interactive elements need: default, pressed/hover, focused, disabled, loading. A button that fires a request must be disabled or show a pending state, or double-tap sends two requests — a real, frequently-shipped bug.

## Normalized values and validity feedback

If a value is transformed anywhere on its way to being accepted — trimmed, lowercased, stripped of formatting, coerced to a number — then **every surface that tells the user whether the value is acceptable must judge the transformed value**, not the raw one.

Miss this and the UI and the submit path disagree about the same input: the field is marked invalid while submit accepts it, or marked valid while submit rejects it. The mismatch type-checks, lints, and passes every existing test, because nothing in the codebase asserts that the two agree. It surfaces on the paste case, which is exactly the case the normalization was written for.

The surfaces that count as "telling the user": validity checkmarks and icons, inline error text, a disabled/enabled submit button, character counters, and any colour or border state keyed to validity.

**Both directions are bugs:**

| Where the transform runs | Where validity is judged | Result |
|---|---|---|
| submit only | raw value | field looks invalid, submit works — user is told to fix something that isn't broken |
| on change (state mutated) | raw value | agrees, but the input jitters and the cursor jumps mid-typing |
| submit + blur | normalized value | correct |

**Do not fix the disagreement by transforming inside `onChange`.** Writing a transformed value back into state on every keystroke makes the input fight the user: characters that get stripped never appear, and in React Native the cursor jumps when the controlled value differs from what the input holds. Keep raw state during typing, and instead:

- evaluate the validity indicator against the normalized value — pass a normalizer (or a normalizing predicate) into the field component rather than duplicating the rule at the call site, and
- write the normalized value back on `blur`, guarded so a no-op change doesn't touch state, and
- keep the submit path normalizing regardless — it is the only guarantee that survives a field that was never blurred.

**Ask during the check-in, not after:** does anything normalize this value before validating or submitting it? If yes, name the surfaces that display validity and confirm each reads the same normalized value. Cover it with a test that feeds the padded/unformatted input and asserts *both* the indicator and the accept decision — a test that only asserts submit will keep passing while the UI lies.

## Content edge cases

Test each screen against these; they're cheap to check and they're what a tester finds first:

- Longest realistic string in every text slot (names, titles, addresses) — and in the longest supported language, which is usually not the one you developed in
- Single character / single word
- Very large numbers, and zero, and negative
- Missing image, missing avatar, missing optional section
- One item in a list; hundreds of items
- The user's own record vs. someone else's (permissions)
- Very long unbroken string (a URL, a token) — does it overflow the container?

How to find the cases a component was never built against — the value map, a plausible-value
catalog for names, numbers, plurals, money, time and images, and what each break looks like on
screen: `references/worst-case-data.md`.

## Accessibility

Not a compliance chore — these are the same properties that make automated tests possible and that make the UI work for someone using it one-handed on a train.

- **Touch targets ≥ 44×44pt (iOS) / 48×48dp (Android).** A 20px icon needs padding or `hitSlop`. This is the single most common a11y defect.
- Every interactive element has an accessible label. Icon-only buttons are invisible to a screen reader without one.
- Role/state exposed: is it a button, a link, a checkbox? Is it selected, disabled, expanded?
- Text contrast ≥ 4.5:1 (3:1 for large text). Check in dark mode too — dark themes fail contrast more often.
- Support system font scaling. Fixed-height containers with scalable text is the standard breakage; test at the largest accessibility text size.
- Respect reduce-motion: replace movement with a fade, don't just shorten it.
- Focus order follows visual order; a modal traps focus and returns it on close.
- Never encode meaning in color alone (error state, status dots) — pair it with an icon or text.
- Web: real semantic elements. A `<div onClick>` is not a button — no keyboard, no role, no focus.

## Platform differences

| Concern | iOS | Android |
|---|---|---|
| Back | Swipe from left edge; must not break mid-flow | Hardware/gesture back — every screen and modal must handle it |
| Safe areas | Notch, home indicator, status bar | Cutouts, gesture nav bar, varied status bar heights |
| Keyboard | `KeyboardAvoidingView` behavior differs; check inputs at the bottom of a form | `windowSoftInputMode` matters; test scroll-into-view |
| Shadows | `shadow*` props | `elevation` — write both or the card looks flat on one platform |
| Fonts | Different default family and metrics; vertical centering drifts | |
| Scroll | Bounce/overscroll | Different momentum; no bounce by default |
| Permissions | Prompt once, then it's Settings-only | Runtime prompts, "don't ask again" state |
| Haptics/sound | Different conventions | |

**Anything platform-specific must be verified on both.** "Works on iOS" is half a result. If only one can be checked, say so explicitly in the report rather than implying both.

Also check: dark mode, landscape (if supported), smallest supported screen, tablet/large screen if in scope, RTL if the app ships an RTL locale (RTL breaks paddings, icons, and animation directions — `start`/`end` instead of `left`/`right`).

## Lifecycle and races

These produce bugs that are intermittent, unreproducible on demand, and therefore expensive:

- Background → foreground: does data refresh? Is a token still valid? Did a timer keep running?
- Navigating away mid-request: cancel it, or guard the state update.
- Fast double-tap on a navigation action: does it push the screen twice?
- Rapid successive queries (typing in search): can an older response land after a newer one and win?
- Deep link straight into the middle of a flow: does required state exist, or does it crash?
- Session expiry mid-flow: is the user dumped to login with their work lost?
- Rotation / re-mount: is in-progress form state preserved?
- Every subscription, listener, timer, and animation started in an effect has a cleanup returning from that effect.

### Reset on identity change — the defect that looks fine on the screen you tested

A component instance can outlive the *thing* it represents. When it takes an **identity prop** — a product id, user id, route param — and that prop can change **without a remount**, every piece of instance-scoped state is still describing the *previous* identity until something resets it: `useState`, `useRef` latches, running timers, animations, subscriptions, and in-flight responses.

The trap is that it passes every casual test. You open one product, it works. The switch to a *second* product — the path that breaks — is the one you didn't try, and because navigation often *does* remount, the bug hides in exactly the cases where the same instance is reused: an in-place deep link to a sibling item, an "other colours" swap, a carousel that just changes the id prop.

**The tell that in-place switching is a real flow, not a hypothetical:** a companion hook or sibling already guards for it — a `previousIdRef`, a `setState(null)` when the id changes, a request-id/generation counter, an `AbortController` keyed to the id. If one half of a feature resets on identity change and the other half doesn't, the half that doesn't is the defect. (This is precisely how it slips: the fetch hook resets, the view component's `didAnnounceRef` doesn't.)

**Three failure modes, worst last:**
1. *Stale display* — content or visibility computed for identity A is shown over identity B.
2. *Orphaned async/timers* — a timer, animation, subscription, or fetch response tied to A fires into B's render.
3. *Dead one-shot latch* — a `didAnnounceRef` / `didInitRef` / `hasAnimatedRef` set `true` for A stays `true`, so B **and every later identity** silently never get the behaviour. This is the nastiest: nothing errors, the screen you tested looks right, and the feature is quietly dead everywhere else.

**The audit** — for any component or hook that takes an identity prop, list every `useState`, every ref that latches or holds identity-specific data, every timer/interval/animation/subscription, every in-flight request, **and every derived flag computed from a loading boolean**. For each, answer one question: *does it reset or cancel when the identity prop changes?* Anything that doesn't is either a bug or a component that must be keyed.

Derived flags are the entry people forget, because they look stateless. `const isPending = isLoading` holds no state of its own — but the hook behind `isLoading` does, and that hook raises it *after* the identity changed (in an effect, an idle callback, a debounce). For the renders in between it still reports the previous identity's answer, so anything gated on it paints stale content while looking, in the diff, like a pure derivation. Key such a flag to the requested identity instead: `data-flow.md` → Freshness has a key.

**Find the in-place writers before you trust the remount.** Grepping the navigations *into* a screen tells you how it is opened, not how its params change afterwards. `navigation.setParams` (and `router.replace`, `history.replaceState`, a parent re-rendering the same instance with a new prop) rewrites the identity with no remount, and it is usually written far from the screen — in a colour swatch, a variant picker, a tab strip. Grep the writers, not just the openers:

```bash
rg -n "setParams|\.replace\(|navigate\('screen'|push\('screen'"
```

**Two fixes, plus a better-than-either:**
- `key={identity}` at the mount site — remounts the whole instance, so all state and timers reset for free. The right default when the component is cheap and nothing needs to survive the switch.
- `useEffect(reset, [identity])` inside — when a remount is too expensive or something must persist. It has to clear timers and cancel in-flight work too, not just reset state.
- Best: *derive* from the identity + props instead of storing. State that's computed can't go stale, and a latch you never added can't get stuck.

**The test that catches it** — mounting once never reproduces this. Cover two transitions: switch identity *while the effect/timer is mid-flight or the UI is visible*, and switch identity *after* the one-shot behaviour has already fired for the first identity. Assert the second identity gets its own fresh behaviour.

## Text and localization

- **No user-facing string literals in components.** Every one goes through the i18n layer, including error messages, empty states, accessibility labels, and placeholder text.
- Every new key added to *every* locale file, not just the default. A missing key usually renders the raw key in production.
- Never concatenate translated fragments — grammar and word order differ. Use interpolation with named placeholders.
- Plurals through the plural API, not `count === 1 ? 'item' : 'items'`.
- Dates, times, numbers, and currency through the locale formatter. Hardcoded `MM/DD/YYYY` is wrong in most of the world.
- Layout must survive translated text being 30–50% longer.

## Design fidelity

Applies only when the developer assigned visual work for this task (`figma-inspect`). By default the diff adds no style values — `mode-build.md` → Styles.

The gap between "looks right" and "is right" is where polish defects live:

- Values come from design tokens. A literal `16` that happens to equal `spacing.md` will drift the moment the token changes.
- Compare against the design at the same zoom: spacing between elements, corner radii, border widths, font weight and line height, icon sizes.
- Check the states the design file specifies — pressed, disabled, error — not just the default frame.
- Compare against a *neighbouring existing screen* too. Consistency with the shipped app matters more than pixel-matching a frame that was drawn in isolation.
