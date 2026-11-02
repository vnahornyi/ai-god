export type OrderStatusType = 'in_progress' | 'delivered' | 'cancelled' | 'returned';

export type OrderType = { id: string; createdAt: string; status: OrderStatusType; total: number };

export type OrdersPageType = { items: OrderType[]; nextPage: number | null };
