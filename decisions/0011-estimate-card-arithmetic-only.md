# 0011 — A personal estimate card may add up the developer's numbers

**Context.** Decision 0008 removed the estimation skill because generated hours never matched
reality. A review of logged time then found that the developer's own estimates left out PR review,
snapshots and defects, with no named risks. A plan's §10 gives the inputs, but nothing checks that an
estimate is complete.

**Decision.** This narrows 0008. "No skill writes or suggests hours" stands, and so does §10 of a
plan. A personal skill in the local overlay may structure an estimate, require each kind of work to
be filled or declared not needed, and add up numbers the developer entered. It never proposes,
pre-fills, rounds or adjusts a number, and it has no percentage buffer.

**Consequences.** The router sends estimate requests to that skill when the overlay has one and to no
skill otherwise. Routing eval cases for hour questions expect it. `wf-plan` is unchanged.

**Source.** The developer, 2026-11-09; supersedes the sentence "There is no estimation skill" in 0008.
