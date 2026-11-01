---
name: wf-retro
description: After the independent review of the developer's own implemented task, attribute every accepted finding to its cause — implementer model, skill, plan or spec — log one row in project memory, and advise what to do next: keep the setup, move implementation to another model mapping, fix a named skill, or tighten planning. Runs automatically once the developer has decided on wf-review findings. Never edits skills, adapters or code. Do not use for someone else's PR.
---

# wf-retro — what the review says about the model, the skills and the plan

Capability: STRONG_GENERAL. Runs in the orchestrating session, not the implementing context, once the
developer has accepted or rejected the `wf-review` findings — before the fixes.

Git: the global instructions' Git rules apply in full. The memory row is staged in the local overlay
repo and handed back for approval like any other change.

## Inputs — all from the conversation

- **Implementer:** the `Implemented by` line of the implementation report (model and effort as the
  runtime reported them). Missing → ask the developer once; never guess.
- **Plan:** whether the task had one; read its Business rules and stop conditions from the plan file
  (the developer deletes plans, so it is normally still there). Gone → ask once for the relevant rows.
- **Findings:** each accepted finding with severity (P0–P3) and kind. Rejected findings are counted,
  not attributed.
- **Fix rounds and escalations** during implementation (`ai-workflow` → model policy).

## Step 1 — Attribute each accepted finding

| Cause | Test | Points to |
|---|---|---|
| `model` | A rule the implementer had loaded (skill, project rule, plan row) says what to do, and the code does otherwise | The implementer's model mapping |
| `skill` | No rule covers it, or the rule as written is ambiguous, contradicts another, or produces this code when followed literally | The skill file and section |
| `plan` | The plan left the decision open, or decided it wrong | `wf-plan` / the planning session |
| `spec` | The ticket or docs miss or contradict the requirement | The product owner |

Between `model` and `skill`, quote the rule line and ask: *would a careful reader of exactly this text
write the code under review?* Yes → `skill`. No → `model`. An escalation after a failed meaningful
attempt counts as one `model` signal.

## Step 2 — Log one row

Append to `memory/<project>/implementation-log.md` in the local overlay (global instructions →
Local overlay; create it from the template below when
missing; `<project>` is the directory name under `~/Developer`). One row per task, in English.

```markdown
---
name: implementation-log
description: One row per implemented task — implementer model, review findings by cause, verdict; read by wf-retro for model and skill advice and by wf-estimate for recalibration
metadata:
  type: project
---

| Date | Task | Implementer | Plan | Dev est. h | Actual h | P0–P2 model | P0–P2 skill | P0–P2 plan | P0–P2 spec | P3 | Rejected | Escalations | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

`Dev est. h` is the plan's Development line from `wf-estimate`, and `Actual h` the developer's figure;
write `—` when either is unknown — never estimate them here. `Note` names the skill section or rule
behind each `skill` finding.

## Step 3 — Advise

Per task, always: one line per cause that occurred, with the concrete next action.

Across the **window** — the last five rows with the same implementer (model and effort); five is the
developer's rule from 2026-10-14:

| Condition in the window | Advice |
|---|---|
| Two or more tasks with an accepted P0–P2 `model` finding | Move implementation to a stronger mapping. Use the model policy's "Why switch" block and name the alternatives listed in the runtime adapter → Model mapping |
| The same skill section behind `skill` findings in two or more tasks | Change that skill: quote the rule, propose wording with "applies when / does not apply when", add or extend an `evals/` fixture, rerun the evals before staging |
| Five tasks and no accepted P0–P2 `model` finding | A cheaper mapping may be trialled: name it, run `evals/` on it first |
| Fewer than five rows | Per-task advice only; say "window n/5" |

A `plan` finding is advice for the next `wf-plan`, whatever the count. A `spec` finding is a question
for the product owner, not a model or skill signal.

## Output

To the developer, in their language (Ukrainian by default), short:

```
Implementer: <model · effort>   Window: n/5
Findings: model a · skill b · plan c · spec d · P3 e · rejected f
Advice: <one line per action, with the file or mapping named>
```

Then the staged memory row. Never edit a skill, an adapter, the plan or code from here, and never
switch the model — the developer decides, and skill changes go through the normal flow with evals.
