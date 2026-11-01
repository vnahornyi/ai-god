# Performance

The rule that governs everything below: **measure, then change.** A performance edit without a before-number is a guess, and guesses accumulate as complexity that nobody can later remove because nobody knows what it bought.

State budgets, not adjectives. "Feels laggy" is a bug report; "list scroll drops to 42fps on Android mid-tier with 300 items" is something you can close.

## Contents
- [Budgets](#budgets)
- [Diagnose before optimizing](#diagnose-before-optimizing)
- [Re-renders and memoization](#re-renders-and-memoization)
- [Lists](#lists)
- [Animations](#animations)
- [Images](#images)
- [Startup and bundle](#startup-and-bundle)
- [Network](#network)

## Budgets

| Metric | Target | Notes |
|---|---|---|
| Frame budget | 16.6ms (60fps), 8.3ms on 120Hz | Anything on the JS thread during a gesture competes with this |
| Screen transition | interactive < 300ms | Show the shell immediately; never block navigation on a fetch |
| Cold start (RN) | < 2s to first meaningful screen | Measure on a real mid-tier Android device, not a simulator |
| List scroll | no dropped frames at 60fps | Test with a realistic worst-case item count, not 10 items |
| Web LCP / INP | LCP < 2.5s, INP < 200ms | Mobile web on 4G, not desktop localhost |
| Interaction feedback | < 100ms | Anything slower needs a visible pending state |

Test on the worst device you support. iPhone-only testing hides most performance bugs.

## Diagnose before optimizing

Match the symptom to the tool:

- **UI freezes during interaction (RN)** → the JS thread is blocked. React DevTools Profiler, or a Systrace/Perfetto capture. Look for long tasks, not for missing `useMemo`.
- **Janky animation** → is it driven on the JS thread? Reanimated worklets / `useNativeDriver` move it to the UI thread and the jank usually disappears entirely.
- **Slow list** → item render cost × items rendered. Check virtualization is actually active and item height is stable.
- **Everything re-renders on every keystroke** → state is too high in the tree. React DevTools "Highlight updates".
- **Slow cold start** → module-level side effects and eager imports. Check what runs at import time.
- **Web: slow load** → Lighthouse + bundle analyzer, in that order.

## Re-renders and memoization

Re-renders are cheap; the work inside them isn't. A component re-rendering 20 times a second is only a problem if its render does something expensive. Fix the expensive thing first.

Order of remedies, cheapest and most durable first:

1. **Move state down.** If typing in a search box re-renders a whole screen, the input's state belongs to the input's subtree.
2. **Lift content out via `children`.** A component that re-renders doesn't re-render `children` passed from above — this removes whole subtrees from the update path with zero memo calls.
3. **Split contexts.** One context holding `{user, theme, cart}` re-renders every consumer when any part changes. Separate by change frequency.
4. **Then** memoize.

**If the project runs the React Compiler (React 19), do not hand-write `useMemo`/`useCallback`/`memo`** — the compiler handles it, and manual memo adds noise plus a chance of a stale closure. Check for `babel-plugin-react-compiler` before adding any.

Without the compiler, memoize when:
- The value is a dependency of a `useEffect` and an unstable identity would re-run it (a correctness issue, not perf).
- The value is passed to a `memo`'d child or a virtualized list's `renderItem`.
- The computation is genuinely heavy (parsing, big sort/filter, date formatting over many items).

Not when: the value is a primitive, the child isn't memoized anyway, or "just in case". `useMemo` on `{a, b}` passed to a plain component costs more than it saves.

`memo()` on a component whose props include an inline object, array, or arrow function does nothing. Check the call site before adding it.

## Lists

- Virtualize above ~50 items on RN, ~100 on web. Below that, virtualization overhead can be a net loss.
- **RN**: prefer FlashList where available; otherwise `FlatList` with `keyExtractor` (stable ids, never index when the list can reorder), and `getItemLayout` when item height is fixed — it eliminates measurement passes.
- `renderItem` must be a stable reference. Without the React Compiler, memoize the item component too — an inline arrow in `renderItem` defeats both; with the compiler, write neither by hand.
- No inline styles, no `.filter()`/`.map()`/`.sort()` in the render path of a list screen — compute the data once, above.
- Nested scrollables (a `FlatList` inside a `ScrollView`) render everything and silently kill virtualization. Use the list's own `ListHeaderComponent`/`ListFooterComponent` instead.
- Keys must be stable across renders and unique across the list. Index keys plus reordering equals wrong item state — a classic invisible regression.

## Animations

- **RN**: Reanimated worklets, or `useNativeDriver: true` with the Animated API. Anything driven from JS will stutter the moment the JS thread does real work.
- Animate transform and opacity. Animating width/height/layout forces layout passes; on the web that means reflow, on RN it means a bridge round-trip per frame.
- Gesture-driven animation must run on the UI thread — otherwise it lags behind the finger, which reads as broken rather than slow.
- Respect reduced-motion. See `states-and-platform.md`.
- On unmount, cancel animations and timers, or you get "state update on unmounted component" and, worse, an animation that keeps a component alive.

## Images

The most common cause of both jank and memory crashes on mobile.

- Never render a 3000px asset into a 100px slot. Request a sized variant from the CDN.
- Set explicit dimensions so layout doesn't shift when the image lands.
- RN: use a caching image library where the project has one; set `resizeMode` deliberately.
- Web: `srcset`/`sizes`, modern formats, `loading="lazy"` below the fold, `width`/`height` attributes to reserve space.
- Placeholder while loading and a defined fallback when it fails — a broken image icon is a defect.

## Startup and bundle

- Nothing expensive at module scope. A module-level `new SomeSDK()` or a top-level `await` runs before the first pixel.
- Lazy-load routes/screens that aren't the entry point; lazy-load heavy dependencies (charts, video, maps, date libraries with locale data) at the point of use.
- Check what a new dependency costs before adding it. A 300KB library for one function is a regression you can't see in review.
- Web: code-split by route, keep the critical path small, avoid duplicated dependencies from mismatched versions.

## Network

- Cache and dedupe via the query layer — two components asking for the same resource should produce one request.
- Waterfalls: a fetch that starts only after another finishes doubles latency. Parallelize what's independent.
- Paginate; never fetch an unbounded list.
- Cancel in-flight requests on unmount and on rapid re-query (search-as-you-type), or a stale response will overwrite a fresh one — a race that only shows on slow networks and is nearly impossible to reproduce later.
- Debounce user-driven queries with the project's existing debounce value; if there is none, ask — the delay is a product decision.
- Optimistic updates need a defined rollback. Without one, a failed mutation leaves the UI lying.
