# E6a rubric (fixed 2026-11-01, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Red loop first | a command (test or script) that asserts `o-103` → `2026-11-01` was run and shown failing before any hypothesis or fix is stated |
| 2 | Hypotheses | three to five falsifiable hypotheses are listed before the fix |
| 3 | Root cause | the report names the cause: the day is taken in UTC (`toISOString`), not in the shop's time zone |
| 4 | Fix | the day is computed in `Europe/Kyiv` explicitly (e.g. `Intl.DateTimeFormat` with `timeZone`), not by adding a fixed +2/+3 hour offset |
| 5 | DST-safe | the fix gives `2026-11-01` for `o-103` and the right day on a summer timestamp (UTC+3) — by construction (named time zone) or by a test |
| 6 | Regression test | a test at `formatOrderDay` (or `groupOrdersByDay`) fails before the fix and passes after, shown |
| 7 | Minimal | no change beyond the day computation and its test; no new dependency |
| 8 | Clean | no debug logs or throwaway scripts left in `src/` |
| 9 | Report | states the loop command, the confirmed and rejected hypotheses, and what was not verified |
