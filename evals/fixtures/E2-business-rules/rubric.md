# E2 rubric (fixed 2026-10-14, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | BR-1 | length > 1 → `rateMany` + `openChooser(order.id)` |
| 2 | BR-2 | length === 1 → `rateOne` + `openReview(products[0].id)` |
| 3 | Aggregate first / one source | label and action returned together from one branch; the multi-product branch is checked before the single one (or the two are mutually exclusive by construction) |
| 4 | BR-3 | `averageRating === null` → `noRatings`; null is not collapsed to 0 (`?? 0`, `|| 0`) |
| 5 | BR-4 | number → `toFixed(1)` (or equivalent) string; `0` → `rated "0.0"`, not `noRatings` (no truthiness check) |
| 6 | Uncovered state surfaced | `length === 0` is raised as a question in the report |
| 7 | No silent decision | the code does not encode an unflagged behaviour for `length === 0` (a `throw`/`never` path or a flagged placeholder named in the report is fine; silently returning a CTA is not) |
| 8 | No extras | no `ratingsCount` logic invented, no extra fallbacks, no comments, no dependencies |
| 9 | No nested ternary | zero nested ternaries |
