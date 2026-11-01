# E1 — OfferTile

React Native app, React 19 with the React Compiler enabled. Translations use `<Trans>` from
`@lingui/react/macro`. Styles are developer-owned: write no style values.

Write `offer-tile.tsx` exporting `OfferTile`.

Existing modules you may import (do not write them):

```ts
// ./types
export type PriceType = { regular: number; discounted: number | null };
export type ProductType = { id: string; title: string; isNew: boolean; price: PriceType | null };

// ./badge          export const Badge: React.FC<React.PropsWithChildren>
// ./price-skeleton export const PriceSkeleton: React.FC
// ./format-price   export const formatPrice: (value: number) => string
```

Props:

```ts
type PropsType = {
  product: ProductType | null;
  isQuoteLoading: boolean;
  onPress: (productId: string) => void;
};
```

Behaviour:

1. `product` is `null` → render nothing.
2. Pressable card; pressing calls `onPress(product.id)`.
3. Title text.
4. When `product.isNew`, a `Badge` with the text "New".
5. Price area:
   - `isQuoteLoading` → `PriceSkeleton`;
   - otherwise `product.price` is `null` → text "Unavailable";
   - otherwise `discounted` is not `null` → discounted price, then the regular price (marked as the old price for accessibility);
   - otherwise → regular price.
