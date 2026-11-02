export type PromoType = { code: string; kind: 'percent' | 'fixed'; value: number; expiresAt: number };

export type OrderType = {
  subtotal: number;
  deliveryFee: number;
  isFirstOrder: boolean;
  promo: PromoType | null;
};

export type ApplyResultType =
  | { ok: true; order: OrderType }
  | { ok: false; error: 'code_invalid' | 'code_expired' };

export type DiscountLineType = { label: string; amount: number };

const WELCOME_PROMO: PromoType = { code: 'WELCOME10', kind: 'percent', value: 10, expiresAt: Infinity };

export const applyPromo = (
  order: OrderType,
  input: string,
  catalog: PromoType[],
  now: number,
): ApplyResultType => {
  const entered = input.trim();
  const promo = catalog.find((candidate) => candidate.code === entered);
  if (!promo) return { ok: false, error: 'code_invalid' };
  if (promo.expiresAt < now) return { ok: false, error: 'code_invalid' };
  return { ok: true, order: { ...order, promo } };
};

export const withWelcomePromo = (order: OrderType): OrderType =>
  order.isFirstOrder && order.promo === null ? { ...order, promo: WELCOME_PROMO } : order;

export const discountOf = (order: OrderType): number => {
  if (order.promo === null) return 0;
  if (order.promo.kind === 'fixed') return order.promo.value;
  return ((order.subtotal + order.deliveryFee) * order.promo.value) / 100;
};

export const totalOf = (order: OrderType): number =>
  Math.max(0, order.subtotal + order.deliveryFee - discountOf(order));

export const discountLine = (order: OrderType): DiscountLineType | null => {
  if (order.promo === null) return null;
  return { label: 'Discount', amount: discountOf(order) };
};
