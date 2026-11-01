# Reanimated recipes and decision checks

These are design recipes, not a substitute for the installed version's API documentation. Reanimated 4 uses a separate Worklets package and supports `scheduleOnRN`/`scheduleOnUI`; older projects may expose `runOnJS`/`runOnUI` instead. Verify imports, worklet transformation, and New Architecture compatibility before copying syntax.

## A business state triggers motion

Let JS compute a pure business result such as `isEligible` or `visibleContentId`. Send the resulting scalar to Reanimated when it changes. Let a derived value animate to the target, and let animated styles or props read that value. Do not store each intermediate value in React state.

For a simple show/hide transition in a version with `get()`/`set()`:

```tsx
const progress = useDerivedValue(() =>
  withTiming(isVisible ? 1 : 0, { duration: motionDurationMs }),
);

const animatedStyle = useAnimatedStyle(() => ({
  opacity: progress.get(),
  transform: [{ translateY: (1 - progress.get()) * travelDistance }],
}));
```

The React prop changes only for a business or visibility reason. Reanimated computes the frames. Use a spring when the physical response is part of the design. Avoid manual `useCallback` or `useMemo` as an animation optimization; follow the project's React Compiler policy.

## A fixed visual cycle

For a cycle with a hold at each endpoint, model the full timeline on one shared value. This example has a **restart-from-initial** policy when `isVisible` becomes true. It is deliberately unsuitable for an exact freeze/resume contract.

```tsx
useEffect(() => {
  if (!isVisible) return;

  progress.set(0);
  progress.set(
    withRepeat(
      withSequence(
        withDelay(holdMs, withTiming(1, { duration: moveMs, easing: Easing.linear })),
        withDelay(holdMs, withTiming(0, { duration: moveMs, easing: Easing.linear })),
      ),
      -1,
      false,
    ),
  );

  return () => cancelAnimation(progress);
}, [holdMs, isVisible, moveMs, progress]);
```

The JS effect arms or cancels the timeline on an external visibility change. Reanimated owns every hold, transition, and repeat. For a one-shot transition, use one `withDelay(..., withTiming(...))` and stop after it settles. If each endpoint has different behavior, compose explicit segments or use a small UI-side phase machine; do not send completion to JS solely to arm the next segment.

Do not use `withRepeat(..., reverse: true)` as a shortcut for reversing a higher-order composition. Explicitly animate back to the starting value in the sequence, and verify the installed version's modifier support.

## Pause and resume are product choices

| Policy | Motion action |
| --- | --- |
| Reset | Cancel, set the specified initial value, arm a new timeline when eligible |
| Freeze and resume | Cancel without resetting; retain UI-side phase and remaining hold time; resume from the shared value and remaining trajectory |
| Finish | Cancel, set the target, and publish the settled semantic state if needed |
| Stop at current value | Cancel and keep the partial value until a later business event |

`cancelAnimation` stops future frames but does not turn a repeated sequence into a resumable clock. A plain `withDelay` restarted after cancellation starts a fresh delay. If the requirement promises exact remaining hold time, record the hold's start/deadline in UI-side state using an appropriate monotonic clock from the installed API. For a linear transition, remaining distance can determine proportional remaining duration. For nonlinear easing or springs, restarting from the current value with a fresh curve is a behavior change; preserve the intended trajectory or obtain agreement to restart it.

AppState and viewport events originate outside Reanimated. Convert them to a small eligibility signal for the UI timeline. Avoid JS timers used only to track visual holds. Unmount cancels owned work and removes external listeners.

## Worklet to JS boundary

A timing/spring completion callback is a worklet. It can set shared values and start the next visual segment on the UI runtime. If it must update React accessibility state, navigate, or emit an approved business event, send one semantic notification through the installed Worklets bridge. In Reanimated 4 that may be `scheduleOnRN`; older projects use their supported bridge. Do not directly call an ordinary JS closure from a worklet.

Check `finished` before acting. Cancellation can happen after a completion notification was queued for JS. If that notification could affect a different product, route, or animation instance, pass an identity or generation token and validate it at the JS boundary. Avoid parallel copies of the entire animation state just to implement this guard.

`useAnimatedReaction` is appropriate when a shared value crosses a meaningful threshold or reaches a settled state. Its reaction must not write the same shared value that its prepare function reads; that can create a reaction loop. Do not bridge every frame to JS.

## Layout and visibility

- When the size is stable after layout, measure once with `onLayout` and pass the scalar into a shared value. When motion must follow live UI layout, use Reanimated's UI-side `measure` with an animated ref if supported.
- Keep the viewport's layout size stable when sliding content. Translate the visual layers; do not recompute container height on every frame unless the design explicitly animates layout.
- A parent rerender often creates new React element objects. Reset by semantic ID or explicit key, not by comparing `ReactNode` references.
- Pause offscreen repeated motion according to the visibility contract. On remount or list-cell reuse, verify the new identity starts in the correct state.

## Reduced motion and timing ownership

Use Reanimated's `useReducedMotion` or animation `reduceMotion` configuration where the installed version supports it; specify the alternative visual behavior. Some modifiers can skip their visual delay under reduced motion. Never rely on `withDelay` to enforce a business cooldown, eligibility deadline, or minimum time a legal/product message must remain visible. Those belong to the business layer and must behave consistently across platforms.

## Review scenarios

For a looping or interruptible component, check: initial state; first hold; every endpoint; one-shot completion; repeated cycles; disable/re-enable; background/foreground; offscreen/onscreen; pause during a hold and mid-transition; unmount; rapid identity change; list-cell reuse; reduce motion; accessibility and pointer state; and a busy JS runtime. A smooth `withTiming` frame does not prove the cycle remains correctly timed when JS is busy.

Official API references: [withDelay](https://docs.swmansion.com/react-native-reanimated/docs/animations/withDelay/), [withSequence](https://docs.swmansion.com/react-native-reanimated/docs/animations/withSequence/), [withRepeat](https://docs.swmansion.com/react-native-reanimated/docs/animations/withRepeat/), [cancelAnimation](https://docs.swmansion.com/react-native-reanimated/docs/core/cancelAnimation/), [useAnimatedReaction](https://docs.swmansion.com/react-native-reanimated/docs/advanced/useAnimatedReaction/), [useReducedMotion](https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion/), and [scheduleOnRN](https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnRN/).
