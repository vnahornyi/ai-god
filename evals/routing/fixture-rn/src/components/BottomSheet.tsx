import Animated, { useAnimatedStyle, useSharedValue } from 'react-native-reanimated';
import type { ReactNode } from 'react';

export function BottomSheet({ children }: { children: ReactNode }) {
  const offset = useSharedValue(0);
  const style = useAnimatedStyle(() => ({ transform: [{ translateY: offset.value }] }));
  return <Animated.View style={style}>{children}</Animated.View>;
}
