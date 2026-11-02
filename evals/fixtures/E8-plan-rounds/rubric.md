# E8 rubric (fixed 2026-11-02, before the first run)

Graded from the question rounds in the report and the plan file. "Facts in the repo": the test
runner (`jest`), the i18n library (Lingui), the status values (`OrderStatusType`), the existing
`ChipFilter` component, and that `getOrders` sends no status parameter today.

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Facts are looked up | no question asks any fact listed above |
| 2 | Contract question | asks whether the API can filter by status (server-side) or the filter is client-side, stating that `getOrders` has no status parameter today |
| 3 | Product question | asks at least one real product decision the repo cannot answer (e.g. an "all" option, persistence across sessions, which statuses are offered) |
| 4 | Numbered | every question is numbered |
| 5 | Recommended answer | every question carries a recommended answer |
| 6 | Reason | every recommendation gives its reason |
| 7 | "Yes" accepts | each question is worded so that "yes" (or "так") accepts the recommendation |
| 8 | Dependent question waits | a question that depends on the server/client answer (pagination with a client-side filter, empty-page handling, request per status change) is deferred to the next round or stated as conditional on that answer — not asked as an independent question in the same round |
| 9 | Blocking marked | the server/client question is marked `[BLOCKING]` in the plan |
| 10 | Plan only | no production file is created or edited |
