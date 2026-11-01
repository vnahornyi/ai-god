---
name: react-native-animations
description: Design, implement and review React Native motion with Reanimated and Worklets — whether it should animate at all, gestures and velocity, springs and curves, haptics, scroll/layout transitions, loops, reduced motion, ports from web — keeping business decisions on the JS side and the timeline on the UI runtime. Use when motion or haptics are in scope and requested, or a diff under review adds or changes motion. Do not use for static UI.
---

# React Native animations

Use this skill when Reanimated is already part of the project or the developer has chosen it. Do not add a dependency just because this skill is available. Read the installed package versions, worklet/Babel setup, New Architecture requirements, and matching official docs before selecting APIs. Reanimated 3 and 4 differ in packaging and cross-runtime names; Gesture Handler 2 uses the `Gesture.Pan()` builder, 3 adds hook-based gestures.

Two failure modes, the first worse: animating something that should not move, and animating the right thing on the wrong runtime (a React render per frame, a JS-driven gesture, an animated `height`). The second looks fine on a flagship in dev and drops frames on a three-year-old Android.

The gate, values, gesture and haptics rules below are adapted from Emil Kowalski's `animate-expo` skill (github.com/emilkowalski/skills, MIT, read 2026-10-27), rewritten for bare React Native as well as Expo.

## Gate — should it animate at all

Run this before any other decision. It may produce zero lines of code.

| How often the user sees it | Decision |
| --- | --- |
| 100+ times a day — tab switches, keyboard open/close, scrolling, settings toggles | No animation. Platform default or nothing |
| Tens of times a day — press feedback, row selection, list navigation | Near-imperceptible only: under 150 ms, or nothing |
| Occasional — sheets, modals, toasts, onboarding steps | Standard animation |
| Rare or first-time — success states, celebrations, empty-state illustrations | Room for delight |

Then name the purpose in one word: **feedback**, **spatial consistency**, **state indication**, **preventing a jarring change**, **explanation**, or **delight** (rare tier only). No word, no animation.

Tabs are peers, not a hierarchy: switching between them never slides — sliding implies a depth that is not there, paid for dozens of times a session.

When the developer or the design explicitly asks for motion that fails the gate, do not silently skip it and do not silently build it: state the tier and the purpose problem, propose the alternative (none, or a sub-150 ms fade), and ask.

## Design the contract before coding

Write down three separate decisions first:

1. **Business:** which content or state is eligible, when eligibility changes, whether the action is one-shot or repeatable, what an identity change means, and what disabling must show. Reuse the same business rules across web and native where the product contract says they match.
2. **Motion:** the native start/end values, direction, delay, duration, easing or spring behavior, and what should be visible while moving. Get design-owned values from the native design or prototype. Web CSS values and an existing implementation are implementation evidence, not a native motion specification.
3. **Lifecycle:** what happens when the app backgrounds, the view leaves the viewport, the user requests reduced motion, content identity changes, the component unmounts, or an animation is interrupted. Choose explicitly among freeze/resume, restart, finish, and reset for each interruption.

A delay that changes a business decision, deadline, or offer eligibility belongs to business logic. A hold that exists only to space visual transitions belongs to the animation timeline. Reduced-motion handling can skip an animation delay, so a visual hold cannot enforce a business deadline.

## Runtime ownership

| React Native JS runtime | UI runtime / Reanimated worklets |
| --- | --- |
| Fetching, product rules, eligibility, navigation decisions, analytics policy, semantic identity | Shared motion values, interpolation, easing, springs, visual holds, repeated cycles, gesture/scroll response |
| External events such as AppState and viewability; pass the resulting eligibility to motion | Pause, cancel, resume, or restart the visual timeline when that eligibility changes |
| React props/state required for accessibility or non-animated native props at settled boundaries | Frame-by-frame style/prop updates and animation completion detection |

Cross the runtime boundary only for a real semantic event. JS may start or stop a timeline when business state changes. Do not use JS `setTimeout`/`setInterval`, React state updates, or a UI-to-JS callback to schedule the next purely visual phase or repeat. In particular, a worklet completion callback should not call JS just to start another `withTiming`. Keep a fixed sequence or loop in Reanimated.

Do not mirror progress, active index, phase, and completion in React state, refs, and shared values. Choose the smallest state model: shared values own motion; React owns business and accessible semantics. A shared value is not read or written during React render. Where supported, use its compiler-compatible `get()`/`set()` API when the project enables React Compiler; follow the installed version's API otherwise.

## Choose the primitive — cheapest that works

**Platform first.** Before writing motion, check whether the platform already owns it. These are free, correct and keep the system gestures; use them when the project has the library:

| Need | Platform answer |
| --- | --- |
| Screen to screen | The native stack's `animation` / `presentation` options (React Navigation native stack or Expo Router). Never rebuild a screen transition in JS |
| A sheet that is its own destination | `presentation: 'formSheet'` with detents (react-native-screens). Android caps detents at three; the grabber is iOS-only |
| Tab bar, tab switch | The navigator's tabs with `animation: 'none'` |
| Large title that collapses | The native stack's large-title header (iOS), not a scroll worklet |
| Pull to refresh | `RefreshControl`, unless the interaction is a signature one |
| UI that follows the keyboard | `react-native-keyboard-controller`'s Reanimated hooks — the keyboard's real position per frame. Never `Keyboard` listeners plus a timing animation: the event arrives late and any guessed curve leads or lags |
| Swipe to reveal row actions | Gesture Handler's `ReanimatedSwipeable` |
| Illustration, celebration | Lottie — never for UI state |
| A scene too large for the view hierarchy | Skia |

**Then the cheapest Reanimated tool** — walk down, stop at the first that fits:

| Need | First choice |
| --- | --- |
| A state-driven change with no gesture — press, toggle, colour, a flipped value | Reanimated CSS transition (`transitionProperty` in the style) where the installed version supports it |
| Loop, multi-stage, or plays on mount without a state change | Reanimated CSS animation (keyframes) or `withRepeat` around an explicit sequence |
| Animate toward a prop-derived state | `useDerivedValue` with `withTiming` or `withSpring`; render through `useAnimatedStyle` or `useAnimatedProps` |
| Fixed delayed transition or finite sequence | `withDelay` and `withSequence` |
| Fixed repeating timeline | `withRepeat` around an explicit sequence, or Reanimated CSS animations when the installed version supports them |
| Gesture or scroll-following motion | Gesture Handler worklets and Reanimated scroll handlers/shared values |
| Mount, unmount, or genuine layout change | Reanimated entering/exiting/layout transitions |
| Derived motion from another shared value | `useDerivedValue` or `interpolate`; use `useAnimatedReaction` for a side effect at a meaningful value change |
| Custom frame algorithm | `useFrameCallback` only when the above APIs cannot express the requirement |

A shared value earns its place only when the value is continuous or interruptible: a press scale is a CSS transition, a drag is a shared value.

Use transforms and opacity for visual movement when they preserve layout. Use layout animations when layout itself must change. Measure on the UI runtime when motion depends on live layout; a one-time React Native `onLayout` result is sufficient when the size is stable. Avoid a JS measurement or React render on each frame.

## Properties

- `transform` and `opacity` skip layout. `width`, `height`, `margin`, `padding`, `flex`, `top`, `left` and `gap` re-run layout for the node and its siblings on every frame. Exception: an absolutely positioned element with no children (a tab pill, a progress fill) — nothing reflows, and animating `width` keeps the corner radius that `scaleX` would smear.
- Never enter from `scale(0)`; start from `0.9–0.97` with opacity 0.
- `transform` is an ordered array: `[{ translateY }, { scale }]` translates, then scales. Reversed, the translation is scaled too.
- Percentages in `translate` are relative to the element itself — `translateY: '100%'` moves a sheet by its own height, whatever its content.
- Do not animate Android `elevation` or a blur view's intensity: both re-render every frame. Crossfade the opacity of a pre-shadowed or static blurred layer.
- Text scales with the system setting, so a height measured at the default size is wrong at 200 %. Never animate to a hard-coded height.

## Values — the design first, defaults second

Motion values are visual work: they come from the native design or prototype, or from the developer in chat. When the design is silent and the developer assigned the motion, use these defaults and label each one **default (emilkowalski/skills `animate-expo`)** in the handoff's provenance table, so the developer can overrule it. Never invent a value outside them. Web CSS values and existing code are not a native motion spec.

**A finger was involved → spring; otherwise → timing.** A spring carries velocity through an interruption; a timing curve restarts. Use the duration + damping-ratio spring form, not mass/stiffness/damping.

| Spring use | Default config |
| --- | --- |
| Settle, no overshoot | `{ duration: 400, dampingRatio: 1 }` |
| Snap back after a drag | `{ duration: 400, dampingRatio: 0.8, velocity }` |
| Sheet, drawer | `{ duration: 300, dampingRatio: 0.8, velocity }` |
| Must not pass a hard edge (dismissal) | add `overshootClamping: true` |

Bounce only when the gesture carried momentum: overshoot on a flicked card reads as physical, on a faded-in menu as a glitch.

| Timing situation | Default easing |
| --- | --- |
| Entering or exiting | strong ease-out `Easing.bezier(0.23, 1, 0.32, 1)` |
| Moving or morphing on screen | strong ease-in-out `Easing.bezier(0.77, 0, 0.175, 1)` |
| Sheet without a gesture | iOS sheet curve `Easing.bezier(0.32, 0.72, 0, 1)` |
| Constant motion — progress, marquee | linear |

Never ease-in on UI: it starts slow, delaying exactly the moment the user watches. The built-in `Easing.out`/`Easing.inOut` are too weak for UI.

| Element | Default duration |
| --- | --- |
| Press feedback | 100–150 ms |
| Toggle, chip, small state change | 150–200 ms |
| Sheet, modal, drawer | spring, ~300 ms perceived |
| Toast | enter ~300 ms, exit ~20 % faster, same direction it came from |
| List stagger | 30–80 ms per item |
| Screen transition | the platform default — do not override |

UI motion stays under 300 ms; navigation matches the platform.

## Gestures

- **Capture the current value on start.** A gesture that begins mid-animation continues from where the element is on screen, never from 0.
- **Decide by projected position, not distance alone.** Project where the flick would come to rest from its velocity; a fast short swipe commits, a slow long one does not. A distance-only threshold makes a sheet feel heavy.
- **Hand the release velocity to the spring**, so there is no seam between the finger lifting and the motion continuing.
- **Resist past a boundary** (rubber-band) instead of a hard stop; clamp overshoot on dismissal so a sheet never springs past the screen edge.
- **Declare the axis** (`activeOffsetX`/`activeOffsetY`) on a pan inside a scroll view, or it steals the scroll and looks like a scrolling bug.
- **A builder gesture keeps its identity across renders**; rebuilding one can reattach the recognizer and drop a drag mid-flight. With the React Compiler the compiler memoizes it — do not hand-write `useMemo` (`frontend-craft` → performance); without it, `useMemo`. Hook-based gestures (Gesture Handler 3) manage their own identity.
- **Press, not hover:** feedback on press-in, commit on press-out; a visual under 44×44 pt (48 dp) gets `hitSlop`, not a bigger visual; `pressRetentionOffset` stops a small drift from cancelling a press. An Android ripple belongs only in a Material-styled app.

## Haptics

Only when the design or the developer asks for them, through the project's installed haptics library. The moment decides the kind: a value ticking past a step → selection; a snap, a detent catching, a drag committing → light impact; a heavy landing or destructive action → medium impact; an operation's result → success or error notification. Three absolute rules:

- **Same moment as the visual cause** — fire when the detent catches or the snap starts, not when the animation finishes. A lagging haptic reads as a glitch.
- **One per user action** — never per frame, on scroll, or on an entrance the user did not cause.
- **Never the only feedback** — haptics are off for many users and silent on much Android hardware.

From a worklet, a haptic is one scheduled call to the RN runtime (`scheduleOnRN` in Reanimated 4), from the release or a threshold reaction — never from the per-frame update.

## Frame budget

On ProMotion iPhones third-party animation is capped at 60 fps unless `CADisableMinimumFrameDurationOnPhone` is `true` in `Info.plist` (recent Expo SDKs set it). When it is set, the budget per frame is 8 ms, not 16 — one more reason motion lives on the UI runtime. Check the key; adding it is a project decision, not a drive-by.

## Interruption and correctness

- A repeating animation does not automatically implement the product's pause policy. On disabled, background, offscreen, or unmount, cancel the owned animation and apply the specified reset/freeze/finish behavior. Resume from a shared motion value or re-arm the sequence according to that policy.
- If exact remaining hold time matters, keep phase and elapsed/remaining time on the UI side. If exact mid-transition continuation matters, preserve the easing trajectory; restarting a nonlinear easing curve with a proportional duration changes its velocity.
- `cancelAnimation` can complete asynchronously. Check the completion callback's `finished` value. When an already queued UI-to-JS notification could mutate the wrong identity, guard only that boundary with an identity or generation token.
- Treat a product/content ID or explicit reset key as identity. A recreated React element is not a new business identity.
- Let one owner start the timeline. Re-renders, focus events, and rapid prop changes must not create concurrent loops.
- Keep interactive and accessible content aligned with the settled visible state. Update React accessibility or pointer props at meaningful boundaries, not every frame. Define reduced-motion behavior explicitly and use the library's system setting/configuration where supported.

## Cross-platform rule

Match **business behavior** between web and React Native: eligibility, which content wins, one-shot versus loop policy, and reset on semantic identity change. Implement **motion behavior** using each platform's animation system and platform design: timing, easing, coordinates, composition, and lifecycle mechanics may differ. Do not port a web timer/CSS state machine into React Native as the default implementation, and do not copy web animation numbers without a native design source.

Reduced motion means fewer and gentler, not zero: keep the opacity and colour changes that explain a state change, drop translation, scale, parallax and overshoot; a screen transition becomes a fade.

## Never ship

| Never | Instead |
| --- | --- |
| `PanResponder`, or core `Animated` for anything a finger touches | Gesture Handler + Reanimated |
| React state set from a gesture or scroll handler | shared value + `useAnimatedStyle` |
| A UI-to-JS call per frame | one call from the release, or `useAnimatedReaction` at a threshold |
| Reading or writing a shared value during render | `get()`/`set()` in worklets, handlers, effects |
| Animating `height`/`width`/`margin`/`flex`/`top` | `transform` + `opacity` (absolute, childless elements exempt) |
| Animating `elevation` or blur intensity | crossfade a static layer |
| `entering` on a row of a virtualized list (rows are recycled and re-animate on scroll) | animate the container once, or `itemLayoutAnimation` for reflow |
| A layout-animation builder created inline on every render | module scope; when it depends on an index, memoized (by the compiler where it runs) |
| A screen transition rebuilt in JS; sliding between tabs | native stack options; `animation: 'none'` for tabs |
| Ease-in on UI; `scale(0)` entrance | strong ease-out; `0.95` + opacity |
| Distance-only dismissal; a hard stop at a boundary | projected velocity **or** distance; rubber-band |
| A haptic per frame, or as the only feedback | one per action, paired with a visual |
| Judging feel in a debug build or the simulator | a release build on the slowest supported device |

## Before handing off

Verify the chosen primitive covers every visual phase without JS scheduling. Inspect interruption paths, completion races, repeated mounts, reduced motion, long/scaled content, both mobile platforms, and behavior while JS is busy. State what was observed and what remains unverified. Follow the project's test authorization rules.

Add to the report, in a few lines, without padding it into an essay:

- **Gate result** — frequency tier and purpose; what was rejected and why.
- **Ingredients and provenance** — tool, properties, curve or spring and duration, runtime; each value marked `design <node>` | `developer <date>` | `default (emilkowalski/skills)`.
- **Feel-check on device** — gestures, velocity handoff and haptic timing cannot be judged from code. Name what to try: flick it, interrupt it mid-flight, reverse it, run it in a release build on the slowest Android available.

Read [Reanimated recipes](references/reanimated-recipes.md) when implementing a loop, pause/resume, cross-runtime callback, or web-to-native port. Read [Gesture recipes](references/gesture-recipes.md) for press feedback, a drag-to-dismiss sheet, swipe-to-delete, a collapsing header, list entrances, keyboard-synced UI, a tab indicator or a threshold event. Reviewing motion in a diff: [Motion review](references/motion-review.md). Confirm exact API and support against the project's installed version and the [official Reanimated docs](https://docs.swmansion.com/react-native-reanimated/docs/) and [Worklets docs](https://docs.swmansion.com/react-native-worklets/docs/).
