import { Pressable, Text, View } from 'react-native';

export type ChipOptionType<T extends string> = { value: T; label: string };

export type ChipFilterPropsType<T extends string> = {
  options: ChipOptionType<T>[];
  selected: T | null;
  onSelect: (value: T | null) => void;
};

export const ChipFilter = <T extends string>({ options, selected, onSelect }: ChipFilterPropsType<T>) => (
  <View accessibilityRole="tablist">
    {options.map((option) => (
      <Pressable
        key={option.value}
        accessibilityRole="tab"
        accessibilityState={{ selected: option.value === selected }}
        onPress={() => onSelect(option.value === selected ? null : option.value)}
      >
        <Text>{option.label}</Text>
      </Pressable>
    ))}
  </View>
);
