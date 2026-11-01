# E4 rubric (fixed 2026-10-14, before the first run)

| # | Check | Pass when |
|---|-------|-----------|
| 1 | Not loaded is not closed | `hours === null` shows no badge — no `hours ?? []`, `hours?.find(...)` treated as "closed", or truthiness that turns null into "closed" |
| 2 | Loaded and empty is closed | `hours` = `[]` shows the badge |
| 3 | Rule | badge when loaded hours have no entry with `weekday === today` |
| 4 | In-place switch | no badge for store B computed from store A's hours (holds by using `hours` as returned) |
| 5 | Inline | the badge is an inline `&&` / single ternary; no `render…()` helper or subcomponent for it |
| 6 | No over-engineering | no new hook, context, store, or file; `use-store-hours.ts` untouched |
| 7 | No manual memo | no `memo`, `useMemo`, `useCallback` |
| 8 | i18n | "Closed today" through `<Trans>` |
| 9 | No comments / no styles | none |
| 10 | Nested ternary | none |
