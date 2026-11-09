import { Text, View } from 'react-native';

export function Toast({ message }: { message: string }) {
  return (
    <View accessibilityRole="alert">
      <Text>{message}</Text>
    </View>
  );
}
