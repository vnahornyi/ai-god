# Maintaining ai-god

This file is for work on this repo itself. The instructions every session gets, in every repo, are
`global/AGENTS.md`; they still apply here (Git rules, routing, the local overlay).

## One home per meaning

| Meaning | Home |
|---|---|
| Invariants for every runtime | `global/AGENTS.md` |
| What to do and when, agent-neutral | `skills/<name>/` |
| How a runtime does it; concrete model names | `adapters/<runtime>/` |
| Anything private (memory, project layer, company standards, personal settings) | `local/` — its own repo, never copied here |
| Measurements | `evals/` |
| Why a settled choice was made; ideas rejected and when to reopen them | `decisions/` |
| Workflow terms | `docs/glossary.md` |

A meaning written in two homes is a bug: keep the one the table names and point to it.

## Before staging

- `bin/lint-skills` and `bin/check-public` pass. The pre-commit hook runs both; a failure is fixed,
  never bypassed.
- `install.sh --check` passes after any change to links, `install.sh` or settings.
- A change that adds or removes instruction text reports `bin/token-report` before and after.

## Changing a skill

- Cite the observed failure (a session, a PR, an `implementation-log` row) or the eval the change
  fixes. A change with neither is not made.
- Adding, renaming or removing a skill updates the `ai-workflow` routing table in the same change;
  `bin/lint-skills` fails on a skill the router does not name.
- Rerun the evals `evals/README.md` names for the files you touched. Never edit a rubric to fit a
  result; add a fixture instead.
- Size limits, enforced by `bin/lint-skills`: frontmatter `name` (equal to the directory) and
  `description` only, description ≤ 1,024 characters (Agent Skills spec); body ≤ 500 lines (Anthropic
  skill-authoring guidance) and ≤ 5,000 tokens, counted as 20,000 characters, because Claude Code
  keeps only the first 5,000 tokens of an invoked skill after compaction. Reference files over 100
  lines open with `## Contents`. Put the rules that matter most at the top of a body.
- How to write and change anything an agent reads: `docs/writing-for-agents.md`. Agent-neutral
  wording: `README.md` → "Writing agent-neutral skills".
