# Writing for agents

The standard for anything an agent reads in this repo: global instructions, skills, references,
adapters, plan templates. Read it before adding or changing one. Sources are named per section; the
ideas are adapted, not copied, from mattpocock/skills (`writing-for-agents`, `retro`, MIT),
obra/superpowers (`writing-skills`), mattpocock/agent-rules-books (rule compression, MIT, by Maciej
Ciemborowicz), Anthropic's "Skill authoring best practices" and "Effective context engineering for AI
agents", and Claude Code's skills and memory documentation.

## Contents

- Pointers and descriptions
- The two budgets
- Where a piece of text belongs
- Steps end on a completion criterion
- Degrees of freedom
- Match the form to the failure
- Leading words and positive phrasing
- Pruning
- Primary bias to correct
- Rule classes
- What it costs
- Changing a skill

## Pointers and descriptions

A pointer is any line that names material outside the context and says when to reach it: a skill's
`description`, a line in `AGENTS.md`, a link in a skill. Whether the agent follows it depends on the
pointer's wording, not on what sits behind it. A must-have reference behind a vague pointer is a
reliability bug; sharpen the pointer before inlining the reference.

A skill description says **when** to use the skill, never **how** it works: an agent that reads a
summary of the procedure in the description tends to act on the summary and skip the body. Write it in
the third person or as "Use when …", put the developer's real trigger words first, give one trigger per
distinct case (synonyms are one case), and stay under 1,024 characters. Routing between neighbouring
skills belongs to the `ai-workflow` table; a description that repeats the table is a second source of
truth.

Sources: mattpocock `writing-for-agents` (context pointers); superpowers `writing-skills` (description
says when, not the workflow); Anthropic best practices (third person, what + when, 1,024 chars).

## The two budgets

Every line spends one of two budgets. **Context load**: text that sits in every session (global
instructions, skill descriptions) costs attention on every turn whether it fires or not. **Cognitive
load**: what the developer must remember exists. Moving material behind a pointer trades the first for
the price of one pointer line.

Source: mattpocock `writing-for-agents`.

## Where a piece of text belongs

Three tiers, by how soon the agent needs it: steps in the file, reference in the file, reference in a
separate file behind a pointer. Inline what every path through the skill needs; move to a reference
what only some paths reach. Keep a concept's definition, rules and caveats together.

Mechanical limits, enforced by `bin/lint-skills`: body ≤ 500 lines and ≤ 5,000 tokens, reference
files over 100 lines open with `## Contents`, and every reference is linked from `SKILL.md` directly —
an agent that follows a chain of references tends to preview the second file instead of reading it.
After compaction Claude Code keeps only the first 5,000 tokens of each invoked skill, so the rules that
must survive go first.

Sources: mattpocock `writing-for-agents` (information ladder, sprawl); Anthropic best practices (500
lines, one level deep, contents over 100 lines); Claude Code skills docs (compaction keep).

## Steps end on a completion criterion

Each step says how the agent knows it is done. A vague end ("once you understand the module") invites
finishing early; a checkable one ("one command that already fails on this bug, run and shown") does
not. Demanding criteria ("every touched consumer listed") drive thoroughness better than adjectives.
When a criterion cannot be sharpened and the agent still rushes, hide the later steps behind a real
context boundary — a separate skill or a subagent.

Source: mattpocock `writing-for-agents`.

## Degrees of freedom

Match specificity to fragility. Open judgement (reviews, design) gets heuristics. A preferred shape
with variation gets a template or pseudocode. A fragile or exact sequence gets a script with no knobs —
run, not read. A deterministic operation is a script, never prose the agent re-derives each time.

Source: Anthropic best practices.

## Match the form to the failure

| Observed failure | Form of the fix |
|---|---|
| A mechanical rule broken (a command, an import shape, a file location) | a permission, hook, lint rule or script — not a sentence |
| A rule broken under pressure (time, sunk cost, "just this once") | a short prohibition with the positive target and the red flags that precede it |
| Output of the wrong shape | a positive recipe or template |
| A required element left out | a mandatory field in the template |
| Behaviour that depends on a condition | a rule tied to an observable predicate ("when the diff touches …") |

Mechanical first: a rule a runtime can enforce lives in the runtime's permissions, the repo's lint or a
script, and the text keeps one line pointing at it.

Sources: superpowers `writing-skills`; mattpocock `retro` (mechanical → check, judgement → standard);
Claude Code skills docs (rules that must hold every time belong in a hook).

## Leading words and positive phrasing

Reuse a compact term the model already knows (*tracer bullet*, *seam*, *red* for a test that fails on
the bug) instead of restating a definition at every site; the repeated word anchors the behaviour.
Coin a new term only with a definition, and keep each term in one sense across the repo
(`docs/glossary.md` when it exists).

State the target behaviour. A prohibition puts the forbidden behaviour into context; keep prohibitions
for hard guardrails (the Git rules) and pair each with what to do instead.

Source: mattpocock `writing-for-agents` (leading words, negation).

## Pruning

- **One source of truth** per meaning. A repeated rule costs tokens and inflates its weight; point to
  the owner instead.
- **The environment is a source.** Do not restate what `package.json`, a config file or `--help`
  answers in one lookup; write down what no file confesses — the reason, the gotcha, the convention.
- **No-ops.** A sentence the model already obeys without being told changes nothing; delete the whole
  sentence. Whether it is a no-op is settled by an eval run, not by debate.
- **Sediment.** Stale layers settle because adding feels safe and removing risky. Every edit is a
  chance to remove a line that no longer bears on the skill.
- **No time-sensitive text** in instructions; keep dated provenance in a note or an eval result.

Sources: mattpocock `writing-for-agents`; Anthropic best practices (concise, consistent terms, no
time-sensitive information).

## Primary bias to correct

Every skill opens its body with one line naming the default shortcut the model takes without it
("Without this skill the agent …"). It sits first, so compaction keeps it, and it is the yardstick for
pruning: a rule that serves no bias the skill names is a candidate to cut.

Source: agent-rules-books mini format.

## Rule classes

Classify rules before cutting a skill down:

| Class | Keep rule |
|---|---|
| default — the model follows it unprompted | remove only with eval evidence that it is a default |
| decision-changing — changes architecture, data, error or scope decisions | always keep |
| conflict-resolver — settles a trade-off between two good rules | always keep |
| micro-decision — a repeated local choice the model gets wrong | keep while evals show the miss |
| trigger — applies only in a risky area | keep, worded as a condition |
| checklist-only — useful as a final scan | move to the skill's final checklist |
| framing — context, not an instruction | move to a reference or cut |

Record each cut with its class and the eval run that justified it, so it can be reverted from one
table.

Source: agent-rules-books `_rule-workbench/PROCESS.md`.

## What it costs

Always-loaded and early text is billed mostly as a cached prefix, so the real cost of a surplus rule is
attention, not money: every extra line is noise around the lines that matter, and recall falls as
context grows. Aim for the smallest set of high-signal lines that makes the right behaviour likely.
Editing the global instructions mid-session rebuilds the cached prefix once. Measure with
`bin/token-report`.

Sources: Anthropic "Effective context engineering" (smallest set of high-signal tokens, context rot);
prefix-cache mechanics.

## Changing a skill

1. **Observed failure.** Name the session, PR or `implementation-log` row where the skill failed, or the
   eval it fails. No failure, no change.
2. **Red.** Reproduce it in an eval (an existing fixture or a new one with a rubric fixed before the
   run) and watch it fail on the current text.
3. **Green.** Write the smallest change that fixes that failure, in the form the table above names.
4. **Loopholes.** Rerun; read how the agent got around the rule, close it, rerun.
5. **Every mapped model.** Run the evals on the models the adapters map to the stages that use the
   skill; a rule that works for the frontier model may need more for the smaller one.

While iterating:

- Read the run transcripts or reports, not only the final files: wasted steps point at text that
  misleads.
- When every run writes the same helper or takes the same multi-step detour, bundle it as a script.
- Generalise from the failing fixture; a fix that only passes that fixture is overfitting.
- Explain why a rule exists instead of raising its volume; a run of capitals is a sign the reason is
  missing.
- For a change judged by quality rather than a binary rubric, compare the two outputs blind.

Sources: superpowers `writing-skills` (no skill change without a failing test first); Anthropic best
practices (evaluations first, test with every model you use); Anthropic `skill-creator` (transcripts,
bundled scripts, generalise, explain the why, blind comparison); mattpocock `SCOPE.md` (observed
failure).
