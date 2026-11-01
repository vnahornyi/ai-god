# E1 rubric (fixed 2026-10-14, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Null guard | `product == null` handled by an early return at the top of `OfferTile` |
| 2 | Badge inline | the `isNew` badge is an inline `&&` (or single ternary) in the JSX, not a helper/subcomponent |
| 3 | Price extracted | the 4-state price is in one named unit (subcomponent or `render…()` helper), not inline |
| 4 | No nested ternary | zero nested ternaries anywhere |
| 5 | No `let`-built JSX | no JSX assigned to a reassigned `let` |
| 6 | No over-extraction | at most one `render…()` helper and no extra subcomponent beyond the price unit |
| 7 | No comments | zero comments |
| 8 | No style values | no `style`, StyleSheet, spacing, colour or font values |
| 9 | No manual memo | no `memo`, `useMemo`, `useCallback` |
| 10 | i18n | "New" and "Unavailable" go through `<Trans>`; no bare user-facing literals |
| 11 | Behaviour | all 4 price states and `onPress(product.id)` implemented as specified |
