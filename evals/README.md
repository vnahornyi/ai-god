# Skill evals

Small fixed tasks that measure whether a skill change helps the STRONG_GENERAL implementer, compared
with FRONTIER_REASONING on the same task. Rerun after any change to `frontend-craft`, `wf-plan` or
`wf-implement`; rerun E5 after any change to `react-native-animations`.

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
