# Mode: Plan

Used by `wf-plan` for React/RN tasks; the plan template there is the output format.

Produce a plan the user can hand to themselves next week and still execute. Investigate first — never plan against an imagined codebase.

1. **Read the real thing.** Find the existing implementation of anything similar. If a sibling platform (web vs mobile) already solved it, read that first — divergence is a bug unless justified.
2. **Map the surface.** Which screens, components, hooks, API contracts, and types are involved. Name files.
3. **Frame the problem before designing.** What "solved" means (whose problem, which cases, over what window, what observation proves it), the least-resistance path and its limit, the architecturally right path and its cost. `references/problem-framing.md`. A plan that skips this designs the fix that is easiest to write rather than the one that closes the problem — and it is a plan, so nobody downstream will re-open the question.
4. **Decide the shape.** State ownership (server-state vs client-state vs local), component boundaries, where the data transform lives. See `references/architecture.md`.
5. **List what could break.** See `references/regression.md` — this is the section the user actually needs.
6. **Fill the scope fields, not hours** — consumers, platforms, unknowns and the risk that drives the upper bound. A number comes only from `wf-estimate`, in chat.

End with the open questions that would change the plan if answered differently.
