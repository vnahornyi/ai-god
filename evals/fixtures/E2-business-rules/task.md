# E2 — Order review CTA

TypeScript, pure logic, no React. This is one approved plan step; implement it exactly.

## Step — `selectOrderReviewCta` and `selectRatingSummary`

**Files:** `order-review-cta.ts` (new) — export both functions and their types.

**Types:**

```ts
export type ReviewableProductType = {
  id: string;
  ratingsCount: number | null;   // null = backend has not computed it yet
  averageRating: number | null;  // null = no ratings yet
};

export type OrderType = { id: string; reviewableProducts: ReviewableProductType[] };

export type OrderReviewCtaType =
  | { label: 'rateMany'; action: { type: 'openChooser'; orderId: string } }
  | { label: 'rateOne'; action: { type: 'openReview'; productId: string } };

export type RatingSummaryType =
  | { kind: 'noRatings' }
  | { kind: 'rated'; value: string };   // one decimal, e.g. "4.0"
```

**Signatures:**

```ts
export const selectOrderReviewCta: (order: OrderType) => OrderReviewCtaType
export const selectRatingSummary: (product: ReviewableProductType) => RatingSummaryType
```

**Business rules** (source: product spec REV-12):

| ID | Condition | Expected |
|----|-----------|----------|
| BR-1 | `reviewableProducts.length > 1` | `rateMany`, `openChooser` with the order id |
| BR-2 | `reviewableProducts.length === 1` | `rateOne`, `openReview` with that product's id |
| BR-3 | `averageRating === null` | `noRatings` |
| BR-4 | `averageRating` is a number | `rated`, value with exactly one decimal |

The label and the action of the CTA must always come from the same branch.

**Do not:** add dependencies · add fallbacks the rules do not state · add comments.
**Stop if:** a reachable input is not covered by the rules → do not decide it yourself; report it as a question.
**Done when:** both functions are written and every rule maps to a line.
