# Out of scope — a generic code-smell checklist as a review baseline

**Idea.** Run every review against a catalogue of code smells (long method, feature envy, data
clumps…) so nothing structural is missed.

**Why not.** A smell is not a failure scenario. The review contract requires a concrete input and
what the user sees; the AI review guard cuts style, naming and "consider extracting" (gates 8, 10).
A smell list produces exactly the findings the guard then removes, and costs tokens on every review.
`frontend-craft` already applies principles by smell **and** threshold, in Build mode.

**Reopen when.** An implementation-log row or a shipped defect shows a structural problem a smell
check would have caught and the current review missed.
