import { FlatList, Text } from 'react-native';
import { formatPrice } from '../lib/formatPrice';

const products = [{ id: '1', name: 'Mug', price: 12 }];

export function ProductListScreen() {
  return (
    <FlatList
      data={products}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <Text>{item.name} {formatPrice(item.price)}</Text>}
    />
  );
}
