# E5 — draggable filter sheet

React Native 0.87 app, React 19 with the React Compiler enabled, New Architecture. Installed:
`react-native-reanimated` 4.x with `react-native-worklets`, `react-native-gesture-handler` 2.x (use the
`Gesture.Pan()` builder API), `react-native-haptic-feedback` (`trigger('impactLight')`,
`trigger('selection')`). `GestureHandlerRootView` already wraps the app. Translations use `<Trans>`
from `@lingui/react/macro`.

**The developer assigned the motion of this sheet to you for this task.** Layout styles (spacing,
colours, sizes) stay developer-owned: write none. The design has no motion spec — no durations,
curves or springs. Motion is in scope: load the `react-native-animations` skill as well.

**Request from the developer:**

1. "The filter sheet should close when the user drags it down, like a native sheet. If they let go
   without closing, it goes back up with a light haptic."
2. "And switching between the 'Brand' and 'Size' tabs inside the sheet should slide the content
   left/right."

Existing `filter-sheet.tsx` — the file to change. The sheet lives inside the catalog screen; it is
not its own navigation route.

```tsx
import { useEffect } from 'react';
import { Pressable, View } from 'react-native';
import Animated, { useAnimatedStyle, useSharedValue, withTiming } from 'react-native-reanimated';
import { scheduleOnRN } from 'react-native-worklets';
import { FilterTabs } from './filter-tabs';
import { SHEET_HEIGHT } from './filter-sheet.const';
import { styles } from './filter-sheet.styles';

type PropsType = { isOpen: boolean; onClose: () => void };

export const FilterSheet: React.FC<PropsType> = ({ isOpen, onClose }) => {
  const translateY = useSharedValue(SHEET_HEIGHT);

  useEffect(() => {
    translateY.set(withTiming(isOpen ? 0 : SHEET_HEIGHT, { duration: 300 }));
  }, [isOpen]);

  const sheetStyle = useAnimatedStyle(() => ({ transform: [{ translateY: translateY.get() }] }));

  return (
    <View style={styles.root} pointerEvents={isOpen ? 'auto' : 'none'}>
      <Pressable style={styles.backdrop} onPress={onClose} />
      <Animated.View style={[styles.sheet, sheetStyle]}>
        <FilterTabs />
      </Animated.View>
    </View>
  );
};
```

`FilterTabs` renders a tab row and the active tab's content; it is not shown and you may not edit it.
`scheduleOnRN` is imported but unused in the current file. Write the changed `filter-sheet.tsx` and
say what you did with request 2.
