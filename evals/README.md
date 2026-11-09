# Skill evals

Small fixed tasks that measure whether a skill change helps the STRONG_GENERAL implementer, compared
with FRONTIER_REASONING on the same task. Rerun after any change to `frontend-craft`, `wf-plan` or
`wf-implement`; rerun E5 after any change to `react-native-animations`; rerun E6 after any change to
`wf-debug`; rerun E7 after any change to `wf-review` or its references and E8 after any change to
`wf-plan`; rerun the routing eval after any change to `ai-workflow`, a skill description or the
global instructions' routing section.

## Layout

- `fixtures/<id>/task.md` — what the implementer receives. Nothing else from this directory is given to it.
- `fixtures/<id>/rubric.md` — binary checks, fixed before the first run. Never edit a rubric to fit a result; add a new fixture instead.
- `results/<date>-<label>.md` — one table per run set: `fixture × run × rubric item`.

## Running

1. For each fixture, spawn implementers per the runtime adapter → Model mapping: STRONG_GENERAL ×2,
   FRONTIER_REASONING ×1. Each gets the brief below and writes only into its own run directory
   outside this repo (a scratch directory).
2. Grade each run against its fixture rubric and `fixtures/process-rubric.md`, pass/fail per item,
   with the line that decides it. The runtime refuses report files from subagents, so grade the
   report from the returned text.
3. Write the result table; compare with the previous result set.

Brief:

```text
Implement the task in <abs path>/task.md. Read only that file from its directory.
Load the frontend-craft skill in Build mode: read <skills dir>/frontend-craft/SKILL.md, then
references/mode-build.md, then whatever those tell you to read for this task.
The developer approved this task file as the plan: do not wait for a Gate 1 check-in.
There is no repository to typecheck or test: skip Gate 2 commands and say so in the report.
Write files only into <run dir>. Do not stage, commit, push or spawn agents.
Finish with the Gate 3 report as your final message; do not write a report file.
```

## Debugging fixtures (E6)

`E6a`–`E6c` carry a small Node project in `src/` (and `CHANGELOG.md` for E6c). Copy the fixture's
`src/` (and changelog) into each run directory first; the brief points at `task.md` and the run
directory. Run once without the skill ("work as you normally would") as the baseline, then with
`wf-debug` on STRONG_GENERAL and FRONTIER_REASONING. Add "The developer is away: do not wait for
answers to questions, record them in the report."

## Routing eval

`evals/routing/cases.md` holds 30 prompts and the key; extract the prompt column into a file outside
the repo and give each runner the brief at the bottom of `cases.md` (FRONTIER_REASONING,
STRONG_GENERAL and the background mapping, one run each). Save each returned table and grade with
`python3 evals/routing/grade.py <run>.md ...`.

On Claude Code, measure real loads instead: `evals/routing/run_real.py --model <alias> --out <run>.md`
runs one fresh session per prompt with Skill and Read only, and writes a table for `grade.py` plus a
raw load log. Keep both under `results/raw/` with the commit they measured: a score that cannot be
regraded cannot be compared.

## Review and planning fixtures (E7, E8)

`E7-spec-axis` is a diff (`src/promo.ts`) against a ticket with planted spec defects; the runner is
the second cold reviewer with `Axis: spec` (`wf-review` → Spec axis), told not to run the review
engine. `E8-plan-rounds` is a small React Native tree in `src/` and a planning request; the runner
follows `wf-plan`, the developer is away, and the report carries the question rounds exactly as they
would be sent, with the plan written to the run directory. Run each on STRONG_GENERAL and
FRONTIER_REASONING; for a skill change, add the previous version of the skill (`git archive <commit>
skills/<name>`) on FRONTIER_REASONING as the comparison.

