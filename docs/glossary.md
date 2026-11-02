# Glossary

One line per workflow term, in our own words, with the file that owns the full definition. Skills
use these terms as written here; a skill that needs more than the line points to the owner instead
of defining the term again.

## Routing and models

| Term | Meaning | Owner |
|---|---|---|
| stage skill | The one `wf-*` skill that decides what a task may do: plan, implement, debug, review, ticket, retro | `ai-workflow` → routing table |
| domain skill | A skill about a technology or area (`frontend-craft`, `react-native-animations`, `seo`…) loaded beside the stage skill when its trigger matches | `ai-workflow` → routing table |
| capability class | A model tier named by what it must do — FRONTIER_REASONING, STRONG_GENERAL, FAST_ROUTINE — mapped to concrete models only in the adapters | `ai-workflow/references/model-policy.md` |
| run mode | `interactive` (the developer is waiting or the work needs a device or back-and-forth) or `background` (independent, command-verified, decision-free) | `wf-plan` → Phase 3; adapter → Run modes |
| adapter | The one file per runtime that maps capabilities, models, subagents and the browser to that runtime's tools | `adapters/<runtime>/runtime.md` |
| local overlay | The private repo at `local/` with memory, project layers, company standards and personal settings; never copied into the public tree | `global/AGENTS.md` → Local overlay |
| project layer | Always-on rules and project skills for one repo, kept in the overlay | `global/AGENTS.md` → Project layer |

## Planning

| Term | Meaning | Owner |
|---|---|---|
| plan | The single disposable file a planned task may have; corrected in place, deleted by the developer, never staged | `ai-workflow` §4; decision 0001 |
| BR row | A row in a plan's §3 Business rules: one business branch, its expected behaviour and its source | `wf-plan` → Phase 3 |
| stop condition | A point where the implementer must stop and ask: every unverified fact and every place the code may differ from the plan | `wf-plan` → Phase 3 |
| scope fields | The per-step facts the developer sizes work from: change type, files, diff size, consumers, platforms, unknowns, people, tests | `wf-plan` → Phase 3 |

## Review and retro

| Term | Meaning | Owner |
|---|---|---|
| cold review | A review in a context that did not write the change and holds only task facts and source references | `wf-review` → Independence; adapter → Cold reviewer |
| Spec axis | The second cold reviewer that checks the diff against acceptance criteria and BR rows only | `wf-review` → Spec axis |
| review engine | The runtime's built-in code-review command, used report-only for the bug hunt | adapter → Review engine |
| severity | P0–P3 by impact if shipped, not by size of the fix | `wf-review/references/review-contract.md` → Severity |
| kind | What a finding's fix is — architecture, security, contract, complex, mechanical, other — used to route the fix | `review-contract.md` → Severity |
| finding cause | Why an accepted finding happened: `model`, `skill`, `plan`, `spec` or `check` | `wf-retro` → Step 1 |
| automated check | A deterministic gate — lint rule, type, test, hook, permission deny — as opposed to a model's review | `docs/writing-for-agents.md` → Match the form to the failure; `wf-retro` → `check` |
| implementation log | The project memory file with one row per reviewed task: implementer, findings by cause, verdict | `wf-retro` → Step 2 |

## Writing for agents

| Term | Meaning | Owner |
|---|---|---|
| pointer | A line that names material outside the context and says when to reach it | `docs/writing-for-agents.md` → Pointers and descriptions |
| primary bias | The default shortcut a skill exists to correct, stated in its first line | `docs/writing-for-agents.md` → Primary bias to correct |
| rule class | default, decision-changing, conflict-resolver, micro-decision, trigger, checklist-only, framing — decides what may be cut | `docs/writing-for-agents.md` → Rule classes |
| red loop | One command that fails on this bug and will pass once it is fixed | `wf-debug` → Phase 1 |
