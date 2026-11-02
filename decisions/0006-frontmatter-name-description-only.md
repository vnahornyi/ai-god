# 0006 — Skill frontmatter is `name` and `description` only

**Context.** Claude Code accepts extra frontmatter keys (`allowed-tools`, `model`,
`disable-model-invocation`, `paths`); Codex and Copilot read the same skill directories and do not
share those keys. A key one runtime honours and another ignores makes one skill behave differently
per runtime.

**Decision.** Every skill has exactly `name` (equal to its directory) and `description` (≤ 1,024
characters, "Use when…", valid plain YAML). Runtime-specific behaviour lives in the adapters.

**Consequences.** Skills stay portable across the runtimes listed in `global/AGENTS.md`. A
Claude-only optimisation (path-scoped rules, per-skill models) needs a measured win and goes into
the Claude adapter, not into a skill. `bin/lint-skills` enforces the keys.

**Source.** Agent Skills specification (`name`, `description`); root `AGENTS.md` → Size limits;
`bin/lint-skills`.
