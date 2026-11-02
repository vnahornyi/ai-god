# 0007 — No generic rule packs without an observed failure

**Context.** Rule packs distilled from books (Clean Code, refactoring catalogues, smell lists) are
easy to add and read as authoritative. mattpocock/agent-rules-books publishes such packs; its own
criticism notes that the evidence behind them is a single LLM-judged run.

**Decision.** ai-god carries project-specific rules and rules tied to an observed failure or an
eval. A generic pack, or a rule from one, is adopted only after a session, PR or log row shows the
failure it prevents, and only with an eval that shows it helps.

**Consequences.** Skills stay smaller and do not argue with project rules. Useful patterns from
packs (the "primary bias" line, the mini format) are adopted as writing practice, not as rules.

**Source.** mattpocock/agent-rules-books `docs/CRITICISM.md` §1, §4; root `AGENTS.md` → Changing a
skill; `docs/writing-for-agents.md` → Changing a skill.
