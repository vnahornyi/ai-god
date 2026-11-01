# Motion review

Loaded by `wf-review` / `wf-peer-review` (through `frontend-craft` → Mode: Review) when a diff adds or
changes motion, gestures or haptics in React Native. The review contract, severity scale and the AI
review guard still decide what reaches the developer; this file only says what to look for.
Adapted for React Native from Emil Kowalski's `review-animations` standards
(github.com/emilkowalski/skills, MIT, read 2026-10-27).

## Two kinds of finding — keep them apart

1. **Defects** — runtime, correctness or accessibility. They have a failure scenario you can state:
   frames dropped on a named device class, a gesture that steals the scroll, a callback that fires
   for the wrong identity, movement with reduced motion on. Report them on the normal severity scale.
2. **Feel** — a curve, a duration, a missing bounce. A value that differs from this skill's
   defaults is **not** a defect when the design or the developer set it: check the design node, the
   ticket and the PR description first. Without such a source it is an opinion — label it as one,
   P3 at most, and give the default with its source.

## Defects — check by name

| Look for | Why it breaks | Narrow fix |
| --- | --- | --- |
| React state set inside a gesture `onUpdate`, a scroll handler or a frame callback | One React render per frame; jank on mid-range Android | shared value + `useAnimatedStyle` |
| A UI-to-JS call (`scheduleOnRN`/`runOnJS`) inside `onUpdate` or a scroll handler | 60–120 bridge calls a second | call from `onEnd`, or `useAnimatedReaction` at a threshold |
| `PanResponder`, or core `Animated` driven by a finger | the gesture waits on the JS thread | Gesture Handler + Reanimated |
| Animated `height`/`width`/`margin`/`padding`/`flex`/`top`/`left` on a node with children or in flow | layout pass for the node and its siblings every frame | `transform` + `opacity`, fixed container + clip |
| Animated `elevation` or blur intensity | re-rendered every frame on Android | crossfade a static layer |
| `entering` on a `FlatList`/`FlashList` row | recycled rows re-animate while scrolling | animate the container, or `itemLayoutAnimation` |
| A shared value read or written during render | stale snapshot; a re-render replays the write | `get()`/`set()` in worklets, handlers, effects |
| A pan inside a scroll view with no `activeOffsetX`/`activeOffsetY` | the pan steals scrolls; reads as a scroll bug | declare the axis |
| A gesture that does not capture the current value on start | grabbing mid-animation teleports the element | store the on-screen value in `onStart`/`onActivate` |
| A builder gesture or layout-animation builder created on every render, in a project without the React Compiler | recognizer reattached mid-drag; builder churn | `useMemo` or module scope (with the compiler, neither by hand) |
| Completion callback acting without checking `finished` | a cancelled animation still closes, navigates or deletes | guard on `finished`, and on identity when it can change |
| Movement with no reduced-motion behaviour, where the motion moves or scales | vestibular accessibility; system setting ignored | `useReducedMotion` / `reduceMotion`, keep fades |
| An animation to a hard-coded height around text | wrong at large system text sizes | measure, or animate a transform |
| A haptic per frame, on scroll, on an entrance the user did not cause, or as the only feedback | noise; invisible to users with haptics off | one per action, at the causal moment, with a visual |
| A haptic fired from an animation's completion instead of its cause | lags the visual and reads as a glitch | fire at the snap or detent |
| A screen transition or tab switch rebuilt in JS | loses the native back gesture and platform behaviour | native stack options; `animation: 'none'` for tabs |
| `Keyboard` listeners driving a timing animation | leads or lags the real keyboard curve | keyboard-controller's per-frame position |
| A JS timer (`setTimeout`/`setInterval`) scheduling the next purely visual phase | drifts while JS is busy | `withDelay`/`withSequence`/`withRepeat` on the UI runtime |

## Feel — opinions unless a source is missing or contradicted

- Motion on a 100+/day action (tab switch, keyboard, settings toggle) or with no nameable purpose —
  `SKILL.md` → Gate. This one can be a real finding when the ticket or design does not ask for it.
- Ease-in on an entering or interactive element; a weak built-in easing on a deliberate animation.
- A UI duration over 300 ms with no stated reason; a navigation transition overriding the platform.
- `scale(0)` or a pure fade where the design shows movement.
- Timing where a finger was involved (no velocity handoff), or a spring bouncing with no momentum.
- A dismissal decided by distance alone; a hard stop at a boundary.
- Enter and exit of a toast going different directions.

## Preferred fixes, in order

Propose the earliest that resolves the finding — the narrowest change, never the rewrite you would
prefer:

1. Delete the animation (high frequency, no purpose).
2. Reduce it — shorter, smaller, fewer properties.
3. Move it to the UI runtime or to transform/opacity.
4. Fix the easing or hand the velocity to a spring.
5. Make it interruptible — start from the current value.
6. Accessibility — reduced motion, haptics paired with a visual.

## What the review cannot see

Feel, velocity handoff and haptic timing cannot be confirmed from a diff. Say which were inferred from
code, and name the device checks for the author: flick, interrupt mid-flight, reverse, release build
on the slowest supported Android.
