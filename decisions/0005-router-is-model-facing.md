# 0005 — The router is loaded by the model, not invoked by the user

**Context.** mattpocock/skills keeps its router user-invoked (`disable-model-invocation`), so it
costs nothing until called. Our skills are routed for a mixed fleet: the background implementer is
a smaller model, and stage choice (plan, implement, debug, review) changes what it may do.

**Decision.** `ai-workflow` is model-invoked and loaded first for every task request; it names the
one stage skill, the domain skills and the capability class. A pure question skips it.

**Consequences.**
- Every task pays the router body (≈1.6k tokens) once.
- Routing is measured, not assumed: the routing eval went 24 → 30 / 27 → 29 / 27 → 29 of 30 after
  router v2 (2026-11-02).
- Where a request had no route (cases 24–26 at baseline), models picked no stage or the wrong one; a
  user-invoked router would leave every request in that state unless the developer called it.

**Source.** `skills/ai-workflow/SKILL.md`; `evals/routing/`; `evals/results/2026-11-01-v2-baseline.md`;
AIGOD-v2 audit of mattpocock/skills.
