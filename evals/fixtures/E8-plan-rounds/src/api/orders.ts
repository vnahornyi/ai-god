import { http } from './http';
import type { OrdersPageType } from '../types/order';

export const getOrders = (params: { page: number }): Promise<OrdersPageType> =>
  http.get('/v2/orders', { query: { page: params.page, perPage: 20 } });
