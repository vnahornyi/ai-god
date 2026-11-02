# 2026-11-02 — English working language, no publishing, no estimation skill, private worklog and style

Changes measured: `global/AGENTS.md` gains Language (English everywhere; the session window and
tickets follow `local/profile.md`) and Publishing (nothing is posted); Ukrainian triggers removed
from the router and descriptions; `wf-estimate` removed and `wf-plan` §10 became "Scope of work";
`wf-worklog` moved to the overlay (`local/skills/`) with Dayflow evidence; house-style code pairs
and locale worst-case data moved to `local/style/`; `ai-review-replies` explains each comment
instead of drafting a reply. Routing key for cases 10, 11 and 13 changed with the estimation skill.

## Routing eval

| # | Opus | Sonnet | Haiku |
|---|---|---|---|
| 7, 8 peer PR | ✓ ✓ | ✓ ✓ | ✗ ✗ strict — wrote "wf-review (references only)" |
| 10, 11 hours | ✓ ✓ | ✓ ✓ | ✓ ✓ |
| 14, 15 worklog | ✗ ✗ strict — `wf-worklog` loaded, listed as "other" | ✗ ✗ same | ✓ ✓ |
| 26 jank since release | ✗ | ✗ | ✗ |
| all other cases | ✓ | ✓ | ✓ |
| **Total (strict)** | **27/30** | **27/30** | **27/30** |
| Total, reading the misses above as loads of the right skill | 29/30 | 29/30 | 29/30 |

Every model routes Ukrainian prompts correctly with English-only triggers. The strict misses are not
wrong routes: in 14–15 the worklog skill is loaded but, now that it is a personal skill and not a
stage in the router, two models list it as "other"; in 7–8 Haiku names the guard references in a
form the grader does not strip. Changing the key for 14–15 or the grader for the Haiku form needs
the developer's agreement (`evals/README.md`: never edit a rubric to fit a result).

## E1–E5

| Fixture | s1 | s2 | o1 |
|---|---|---|---|
| E1 (11) | 11 | 11 | 11 |
| E2 (9) | 9 | 9 | 9 |
| E3 (9) | 9 | 9 | 9 |
| E4 (10) | 10 | 10 | 9 — #2: throws on `hours = []` as an open question instead of showing the badge |
| E5 (15) | 15 | 14 — #13: reduced motion not addressed | 15 |
| **Total (54)** | **54** | **53** | **53** |

Step 0 baseline 54 / 53 / 53 (met); step 9 run 54 / 54 / 54. The two misses are in items this change
does not touch: E5 #13 has moved between runs in every set, and the E4 o1 throw follows the
"undecided reachable state" rule, which did not change. P1 and P2 pass in all 15 runs.

## E7, E8

| | Sonnet | Opus |
|---|---|---|
| E7 Spec axis (11) | 10 (item 6, known fixture defect) | 10 (same) |
| E8 plan rounds (10) | 7 — closing round: Q7 has no recommendation, Q5/Q7 are "what / which", Q4 has no reason | 9 — R1.Q7 is a "which" question |

E8 was 8 / 10 before; the closing round stays the weak spot on both mappings. The Opus planner read
`local/profile.md` and wrote its questions in the session language, as the Language section asks.

## Sizes

| Load | Before | After |
|---|---|---|
| Global instructions | 9,535 chars | 10,862 (Language and Publishing sections) |
| Skill descriptions | 3,550 (20 skills) | 3,287 (18 public skills) |
| Review / plan / implement flows | 86,136 / 79,589 / 66,058 | 86,312 / 79,863 / 65,868 |
