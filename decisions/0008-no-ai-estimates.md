# 0008 — No estimation skill; the developer estimates

**Context.** `wf-estimate` produced hour numbers from a plan and a company scale. The developer's
judgement after using it: the numbers never matched reality, and producing them cost a planning-sized
read of the task every time. Estimating time is a call that rests on what only the developer knows —
the team, the codebase's surprises, the week ahead.

**Decision.** There is no estimation skill. A plan's §10 "Scope of work" gives the developer what to
estimate from: per step, what has to be read, written, verified and agreed, on which platforms, and
what would make it longer. No skill writes hours, gradations or an estimate, even when asked; a
ticket carries only the developer's own number.

**Consequences.** Estimate requests route to no skill and point to §10. `wf-retro` logs the
developer's estimate and actual hours when they give them, so a later pattern can still be seen.
The company estimation scale stays in the overlay for the developer's own use.

**Source.** The developer, 2026-11-02; `wf-plan` → Phase 5; `ai-workflow` → routing table.
