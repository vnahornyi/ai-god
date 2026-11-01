# Gesture and interaction recipes

Starting shapes for the interactions that come up most, adapted from Emil Kowalski's `animate-expo`
recipes (github.com/emilkowalski/skills, MIT, read 2026-10-27). Every number below is a **default**
for when the design is silent — label it so in the handoff (`SKILL.md` → Values). Check each API
against the installed versions before copying: the code assumes Reanimated 4 with
`react-native-worklets` and Gesture Handler's `Gesture.Pan()` builder.

`haptic(kind)` stands for the project's installed haptics call (`react-native-haptic-feedback`,
`expo-haptics`, or a project wrapper). Add it only when the design or developer asks for haptics.

**React Compiler:** the recipes wrap builders in `useMemo` for projects without the compiler. Where
the compiler runs, drop the `useMemo` — it memoizes them (`frontend-craft` → performance).

**Gesture Handler 3:** the builder still works but is legacy. A hook-based gesture takes one config
object, `onStart` becomes `onActivate`, `onEnd` becomes `onDeactivate`, and `success` becomes the
inverted `event.canceled`. The hook owns its identity, so the `useMemo` goes away.

## Contents

- [Two worklets used everywhere](#two-worklets-used-everywhere)
- [Press feedback](#press-feedback)
- [Drag-to-dismiss sheet inside a screen](#drag-to-dismiss-sheet-inside-a-screen)
- [Swipe to delete](#swipe-to-delete)
- [Collapsing header](#collapsing-header)
- [List entrances](#list-entrances)
- [Keyboard-synced UI](#keyboard-synced-ui)
- [Tab or segmented indicator](#tab-or-segmented-indicator)
- [Toast](#toast)
- [Firing once at a threshold](#firing-once-at-a-threshold)

## Two worklets used everywhere

Projection says where a flick was going, so a quick short swipe commits and a slow long one does
not. Rubber-banding makes a boundary resist instead of stopping dead.

```ts
// Exponential-decay rest position (the UIScrollView model), not v²/2a.
function project(velocity: number, decelerationRate = 0.998) {
  'worklet';
  return ((velocity / 1000) * decelerationRate) / (1 - decelerationRate);
}

function rubberband(overshoot: number, dimension: number, constant = 0.55) {
  'worklet';
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

A function called from a worklet needs `'worklet'` as its first line, or it throws on device while
working in the debugger.

The curves the recipes share, at module scope:

```ts
const EASE_OUT = Easing.bezier(0.23, 1, 0.32, 1);
const EASE_IN_OUT = Easing.bezier(0.77, 0, 0.175, 1);
```

## Press feedback

Touched tens of times a day, so it passes the gate only because it is near-imperceptible: 3 % scale,
~120 ms. A state flip twice per press, not per frame — a CSS transition is the whole implementation.

```tsx
const [isPressed, setIsPressed] = useState(false);

<Pressable
  onPress={onPress}
  onPressIn={() => setIsPressed(true)}
  onPressOut={() => setIsPressed(false)}
  hitSlop={12}
  pressRetentionOffset={16}
>
  <Animated.View style={[styles.scale, isPressed && styles.pressed]}>{children}</Animated.View>
</Pressable>

const styles = StyleSheet.create({
  scale: {
    transform: [{ scale: 1 }],
    transitionProperty: 'transform',
    transitionDuration: '120ms',
    transitionTimingFunction: 'cubic-bezier(0.23, 1, 0.32, 1)',
  },
  pressed: { transform: [{ scale: 0.97 }] },
});
```

## Drag-to-dismiss sheet inside a screen

If the sheet is its own destination, use the native stack's `formSheet` instead and stop here.

```tsx
const translateY = useSharedValue(0);
const startY = useSharedValue(0);

const pan = useMemo(
  () =>
    Gesture.Pan()
      .activeOffsetY([-10, 10])
      .onStart(() => {
        startY.set(translateY.get());
      })
      .onUpdate((event) => {
        const next = startY.get() + event.translationY;
        translateY.set(next >= 0 ? next : rubberband(next, SHEET_HEIGHT));
      })
      .onEnd((event) => {
        const projected = translateY.get() + project(event.velocityY);
        if (projected > SHEET_HEIGHT * 0.4) {
          translateY.set(
            withSpring(
              SHEET_HEIGHT,
              { duration: 300, dampingRatio: 1, velocity: event.velocityY, overshootClamping: true },
              (finished) => {
                if (finished) scheduleOnRN(onClose);
              },
            ),
          );
          return;
        }
        translateY.set(withSpring(0, { duration: 300, dampingRatio: 0.8, velocity: event.velocityY }));
        scheduleOnRN(haptic, 'impactLight');
      }),
  [onClose],
);

const sheetStyle = useAnimatedStyle(() => ({ transform: [{ translateY: translateY.get() }] }));
const backdropStyle = useAnimatedStyle(() => ({
  opacity: interpolate(translateY.get(), [0, SHEET_HEIGHT], [1, 0], Extrapolation.CLAMP),
}));
```

What separates it from a bad drag:

- `onStart` captures the on-screen value — grabbing the sheet mid-animation must not teleport it.
- The decision uses the projected position, so a flick dismisses after a few pixels.
- The release velocity goes into the spring — no seam between finger and motion.
- Dismissal clamps overshoot, or the sheet springs past the bottom and flashes a gap.
- The backdrop derives from the same shared value, so it cannot drift out of sync.
- The haptic fires as the snap-back starts, not when it lands.

## Swipe to delete

When the row only reveals action buttons, use `ReanimatedSwipeable`. Build this only for
swipe-to-commit with momentum.

```tsx
const x = useSharedValue(0);
const startX = useSharedValue(0);

const pan = useMemo(
  () =>
    Gesture.Pan()
      .activeOffsetX([-10, 10])
      .onStart(() => {
        startX.set(x.get());
      })
      .onUpdate((event) => {
        x.set(Math.min(0, startX.get() + event.translationX));
      })
      .onEnd((event) => {
        if (x.get() + project(event.velocityX) < -SWIPE_THRESHOLD) {
          x.set(
            withTiming(-ROW_WIDTH, { duration: 200, easing: EASE_OUT }, (finished) => {
              if (finished) scheduleOnRN(onDelete, id);
            }),
          );
          return;
        }
        x.set(withSpring(0, { duration: 300, dampingRatio: 1, velocity: event.velocityX }));
      }),
  [onDelete, id],
);
```

Closing the gap is the list's job: `itemLayoutAnimation={ROW_CLOSE}` with
`const ROW_CLOSE = LinearTransition.duration(200)` at module scope. Without `activeOffsetX` the pan
steals vertical scrolls.

## Collapsing header

```tsx
const scrollY = useSharedValue(0);
const onScroll = useAnimatedScrollHandler((event) => {
  scrollY.set(event.contentOffset.y);
});

const titleStyle = useAnimatedStyle(() => ({
  opacity: interpolate(scrollY.get(), [0, 60], [1, 0], Extrapolation.CLAMP),
  transform: [{ translateY: interpolate(scrollY.get(), [0, 60], [0, -12], Extrapolation.CLAMP) }],
}));
```

Never collapse by animating the header's `height` — a layout pass for the header and everything below
it on every scroll frame. Fixed-height container, translate the content, clip with `overflow:
'hidden'`. `Extrapolation.CLAMP` is not optional: without it, opacity goes negative on a long scroll.
On iOS, prefer the native large-title header when it fits the design.

## List entrances

```tsx
function Row({ index }: { index: number }) {
  const entering = useMemo(() => FadeInDown.duration(250).delay(index * 40), [index]);
  return <Animated.View entering={entering}>{/* … */}</Animated.View>;
}
```

Only for a short, non-virtualized list the user asked for and is waiting on. Never `entering` on a
`FlatList`/`FlashList` row: recycled rows re-animate as they scroll back in.

## Keyboard-synced UI

```tsx
const { height } = useReanimatedKeyboardAnimation();
const footerStyle = useAnimatedStyle(() => ({ transform: [{ translateY: height.get() }] }));
```

Needs `react-native-keyboard-controller` and its `KeyboardProvider` at the root. The keyboard rides a
private system curve; only its real per-frame position matches it.

## Tab or segmented indicator

```tsx
const x = useSharedValue(0);
const width = useSharedValue(0);

useEffect(() => {
  const layout = layouts[activeKey];
  if (!layout) return;
  x.set(withTiming(layout.x, { duration: 250, easing: EASE_IN_OUT }));
  width.set(withTiming(layout.width, { duration: 250, easing: EASE_IN_OUT }));
}, [activeKey, layouts]);

const pillStyle = useAnimatedStyle(() => ({
  transform: [{ translateX: x.get() }],
  width: width.get(),
}));
```

`layouts` comes from `onLayout`, once — not per frame. The pill is absolute and childless, so
animating `width` is the sanctioned exception. Ease-in-out because it moves across the screen. The
selection haptic fires on the press, not when the pill lands. The tab *content* does not slide.

## Toast

```tsx
const TOAST_ENTER = FadeInDown.duration(300).easing(EASE_OUT);
const TOAST_EXIT = FadeOutDown.duration(250).easing(EASE_OUT);
```

Builders at module scope. It leaves the way it came, a little faster than it arrived, and sits above
the safe-area inset.

## Firing once at a threshold

A detent, a snap, a pull-to-refresh arming — compare on the UI runtime, call JS only on the crossing:

```tsx
useAnimatedReaction(
  () => pullDistance.get() > REFRESH_THRESHOLD,
  (isArmed, wasArmed) => {
    if (isArmed !== wasArmed) scheduleOnRN(haptic, 'impactLight');
  },
);
```
