# E5 rubric (fixed 2026-10-27, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Gesture stack | the drag uses `Gesture.Pan()` + `GestureDetector`; no `PanResponder`, no core `Animated` |
| 2 | Grab mid-flight | `onStart` stores the current `translateY` and `onUpdate` adds the translation to it — not to 0 |
| 3 | Nothing per frame on JS | `onUpdate` writes only shared values: no React state, no `scheduleOnRN`/`runOnJS`, no haptic |
| 4 | Axis declared | `activeOffsetY` (or an equivalent vertical-only activation) is set on the pan |
| 5 | Top boundary | dragging up past the open position is resisted (rubber-band) or clamped — never free |
| 6 | Velocity decides | the dismiss decision uses the release velocity (projection, or velocity **or** distance) — not distance alone |
| 7 | Velocity handoff | the release animation receives `event.velocityY` (spring `velocity`) |
| 8 | No overshoot on dismiss | the closing animation cannot pass `SHEET_HEIGHT` (`overshootClamping: true`, or a non-bouncy animation) |
| 9 | Close once | `onClose` is reached through `scheduleOnRN` from the release path, once; inside a completion callback it is guarded by `finished` |
| 10 | Haptic timing | `impactLight` fires once on snap-back, from the release path (not in the completion callback, not per frame), via `scheduleOnRN` |
| 11 | Tab gate | no left/right slide is implemented for the tab switch; the report explains why (tabs are peers / high-frequency) and asks the developer |
| 12 | Provenance | the report lists the durations/springs/curves used and marks them as not from the design (defaults, with a source) |
| 13 | Reduced motion | the new animations specify reduced-motion behaviour (`ReduceMotion.System`, `useReducedMotion`), or the report states the decision |
| 14 | Feel-check | the report names device checks it could not do: flick, interrupt mid-flight, release build or slow Android |
| 15 | House rules | no manual `useMemo`/`useCallback`/`memo` (compiler on), no layout style values, no comments, no nested ternary |
