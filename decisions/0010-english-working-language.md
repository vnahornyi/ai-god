# 0010 — English is the working language; the session window is translated

**Context.** Skills, plans and subagent prompts mixed English and Ukrainian. Mixed text costs tokens
to translate in the model's head, makes rules harder to grep and lint, and ties the public tree to
one developer's language.

**Decision.** Everything written — files, plans, memory, commit and PR text, subagent prompts and
reports, reasoning — is English. Only the session window is translated: replies use
`session_language` from the private `local/profile.md`, and Jira text and Tempo descriptions use
`ticket_language`, which a project's `rules.md` may override. The developer writes in any language.

**Consequences.** Skill descriptions and the router trigger on English phrasing; the routing eval
keeps Ukrainian prompts as test inputs to show that routing still works. `bin/lint-skills` fails on
non-English text in the public tree (test inputs under `evals/` are exempt). Locale-specific test
data and code-style examples live in the overlay (`local/style/`).

**Source.** The developer, 2026-11-02; `global/AGENTS.md` → Language.
