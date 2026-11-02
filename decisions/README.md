# Decisions

Why ai-god is shaped the way it is, so a settled question is not argued again in every session.

A decision gets a record when it is at least one of:

- **hard to reverse** — changing it touches every skill, adapter or the developer's habits;
- **surprising without context** — a newcomer (person or model) would "fix" it back;
- **a real trade-off** — the other option has genuine merit, and we chose against it.

Each record: context, decision, consequences, source — 30 lines at most. A record is changed only
by a new record that names the one it replaces.

`out-of-scope/` holds ideas we looked at and did not adopt, with the condition that would reopen
them. Before proposing one of those again, read its file.

| # | Decision |
|---|---|
| [0001](0001-no-handoff-or-state-files.md) | No handoff, state, segment, review or fixes-plan files |
| [0002](0002-ai-never-pushes.md) | The AI never pushes; commits go through the staged index |
| [0003](0003-styles-are-the-developers.md) | Style values are the developer's unless visual work is assigned |
| [0004](0004-retro-window-of-five.md) | Retro advice uses a window of five tasks per implementer |
| [0005](0005-router-is-model-facing.md) | The router is loaded by the model, not invoked by the user |
| [0006](0006-frontmatter-name-description-only.md) | Skill frontmatter is `name` and `description` only |
| [0007](0007-no-generic-book-rule-packs.md) | No generic rule packs without an observed failure |
| [0008](0008-no-ai-estimates.md) | No estimation skill; the developer estimates |
| [0009](0009-nothing-is-posted.md) | Nothing is posted on the developer's behalf |
| [0010](0010-english-working-language.md) | English is the working language; the session window is translated |

| Out of scope | Reopen when |
|---|---|
| [Subagents that commit, merge or push](out-of-scope/auto-commit-subagents.md) | only the developer changes the Git rules |
| [Code-smell checklist as a review baseline](out-of-scope/fowler-smell-baseline-in-review.md) | a missed structural defect is on record |
| ["Call the Skill tool" phrasing](out-of-scope/call-the-skill-tool-phrasing.md) | a routing miss traces to wording |
| [Changesets or a CHANGELOG](out-of-scope/changesets.md) | ai-god is installed by version |
