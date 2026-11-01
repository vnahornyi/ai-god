# E3 rubric (fixed 2026-10-14, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Shows for every product | switching `productId` in place shows the tooltip for the new id (via `key={productId}` at the mount site, or an effect keyed on `productId`) |
| 2 | No stale visibility | the previous product's visible tooltip / running timer does not carry over to the new id |
| 3 | Timer cleanup | the timer is cleared on id change and on unmount |
| 4 | Latch removed or keyed | `didAnnounceRef` is either removed or reset per id — not left as a global one-shot |
| 5 | Smallest fix | no new context/store/hook file; no change beyond `product-tooltip.tsx` and, if used, the one mount line |
| 6 | No manual memo | no `memo`, `useMemo`, `useCallback` |
| 7 | No comments | zero comments |
| 8 | No style values | none |
| 9 | Test identified | the report names the identity-switch case (A → B in the same instance) for QA or a test |
