# Ticket template

Write the headings and text in `ticket_language`, translating the headings below. Keep every
heading; write `—` where a section does not apply.

```markdown
**Title:** <verb + object, ≤ 80 chars>

## Context
Why: the user or business problem. Links: docs, design (frame name), epic.

## Scope
- behaviour, screens, platforms included

## Out of scope
- …

## Acceptance criteria
- conditions a user or QA can observe — not "code is written" (a plain bullet list, no checkboxes)

## Work plan
| # | Block | What I do | What takes time here | Share |
|---|---|---|---|---|
| 1 | Reading into current logic | how <module> works today, its tests | legacy X, two platforms | ~10% |
| 2 | Agreeing the contract | field `…` with backend (who) | waiting for an answer | ~5% |
| 3 | Implementation: <part 1> | … | … | … |
| 4 | Implementation: <part 2> | … | … | … |
| 5 | Tests | scenarios covered | … | … |
| 6 | Device testing | iOS (…), Android (…), browsers | device matrix | … |
| 7 | Regression | existing flows using the changed code | … | … |
| 8 | Review and rework | ~N rounds expected | … | … |
| 9 | Release / docs | if applicable | … | … |

## Dependencies & risks
- risk → effect on the estimate (e.g. "field missing in API → next gradation")
```

Drop the **Share** column when there is no number the developer gave or accepted. The ticket has
no estimate section: the developer sets the estimate in the tracker's own field.
