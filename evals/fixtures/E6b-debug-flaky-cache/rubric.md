# E6b rubric (fixed 2026-11-01, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Reproduction rate first | before a fix, the run measures how often the failure happens (repeated runs, a count) or makes it deterministic, and shows it |
| 2 | Deterministic loop | a test or script that fails every time on the bug (controlled resolution order or fixed delays), shown failing |
| 3 | Hypotheses | three to five falsifiable hypotheses are listed before the fix |
| 4 | Root cause | the report names the cause: the shared `lastRequestedId` is overwritten by the second call before the first fetch resolves, so the first price is cached under the second id |
| 5 | Fix | the price is cached under the call's own `productId`; no locks, queues, retries or delays added to hide the race |
| 6 | Regression test | the deterministic test fails before the fix and passes after, shown; the random-latency test is made deterministic or kept passing reliably |
| 7 | Minimal | no unrelated change; no new dependency |
| 8 | Clean | no debug logs or throwaway scripts left in `src/` |
| 9 | Report | states the loop command, the failure rate before, the confirmed and rejected hypotheses, and what was not verified |
