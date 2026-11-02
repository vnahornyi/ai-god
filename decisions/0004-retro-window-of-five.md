# 0004 — Retro advice uses a window of five tasks per implementer

**Context.** One review finding says little about a model or a skill; a mapping change made on one
bad task wastes money or quality. Advice needs a window large enough to separate a pattern from
noise and small enough to react within weeks.

**Decision.** `wf-retro` logs one row per task and advises over the last five rows with the same
implementer (model and effort): two tasks with an accepted P0–P2 `model` finding → a stronger
mapping; the same skill section behind `skill` findings in two tasks → change that skill with an
eval; five clean tasks → a cheaper mapping may be trialled after evals. Fewer than five rows gives
per-task advice only.

**Consequences.** The number five is the developer's rule from 2026-10-14, not a measurement; it is
revisited when the log has enough rows to measure variance. `plan`, `spec` and `check` findings are
acted on per task, outside the window.

**Source.** `wf-retro` → Step 3; the developer, 2026-10-14.
