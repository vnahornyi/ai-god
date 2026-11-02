---
name: wf-estimate
description: Use when the developer asks for hours — "оціни", "скільки годин", or a number for a plan or ticket. The estimate goes to the chat only.
---

# wf-estimate — advice, not a commitment

AI does not know enough to estimate reliably; the developer decides. This skill gives a transparent
second opinion they can argue with.

## Input

- the task's plan (its §10 "Estimation inputs" and step scope fields), or
- the task description — then do a light audit first: locate the modules, count consumers of what
  will change (`rg`), check whether the contract exists. Ask for the platform/scope when unclear.

Load the project's planning skill when it exists (e.g. `<project>-planning`) for platform and pipeline
facts.

## Steps

1. Read `references/estimation.md` and follow it literally. Do not reuse numbers from an earlier
   estimate.
2. Walk "What the estimate must cover".
3. Classify the risk profile; zero the lines it rules out, with the reason.
4. Compute **Block A — raw development** and **Block B — regression pass, device testing, review
   rounds** (plus buffer and polish when they apply). Every Block B line says how it was counted.
5. Snap A+B (realistic) to the gradation, rounding up per the table. Above `7`, offer a
   decomposition; above `28`, stop and propose the split.

## Output

Only a chat message in the reference's reporting format, headed **"AI advice, not an estimate"**.
Never write the number into the plan, the ticket or any file. If the developer accepts it,
`wf-jira-task` may use it — only on their explicit word.

Capability: STRONG_GENERAL.
