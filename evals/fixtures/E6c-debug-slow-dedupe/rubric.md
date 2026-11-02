# E6c rubric (fixed 2026-11-01, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Measure first | a timing harness on the realistic input (`makePages()`) was run and its number shown before any change |
| 2 | Hypotheses | three to five falsifiable hypotheses are listed before the fix |
| 3 | Root cause | the report names the cause: `dedupeById` scans the kept list for every item (quadratic) |
| 4 | Fix | linear dedupe (a `Set` or `Map` of seen ids) that keeps the first occurrence and the original order |
| 5 | Behaviour kept | a test proves uniqueness, first-occurrence and order on input with cross-page duplicates, passing before and after the fix |
| 6 | After number | the same harness is rerun after the fix and the before/after numbers are reported |
| 7 | Minimal | no unrelated optimisation (`filter`, `flat`, page building untouched); no new dependency |
| 8 | Clean | no debug logs left in `src/`; a kept harness is named as such or removed |
| 9 | Report | states the harness command, before/after numbers, confirmed and rejected hypotheses, and that device timing was not verified |
