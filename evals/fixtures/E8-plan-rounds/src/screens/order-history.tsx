import { useEffect, useState } from 'react';
import { FlatList, Text } from 'react-native';
import { Trans } from '@lingui/react/macro';
import { getOrders } from '../api/orders';
import type { OrderType } from '../types/order';

export const OrderHistoryScreen = () => {
  const [orders, setOrders] = useState<OrderType[]>([]);
  const [nextPage, setNextPage] = useState<number | null>(1);

  const loadMore = () => {
    if (nextPage === null) return;
    getOrders({ page: nextPage }).then((page) => {
      setOrders((current) => [...current, ...page.items]);
      setNextPage(page.nextPage);
    });
  };

  useEffect(loadMore, []);

  return (
    <FlatList
      data={orders}
      keyExtractor={(order) => order.id}
      onEndReached={loadMore}
      ListEmptyComponent={<Text><Trans>No orders yet</Trans></Text>}
      renderItem={({ item }) => <Text>{item.id}</Text>}
    />
  );
};
