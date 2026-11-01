---
name: wf-peer-review
description: Walk through someone else's pull request for the developer — report only what deserves attention, skip everything else, then give a step-by-step route through this PR's own files so the developer can review it themselves. Use for "пройдись по PR", "глянь чужий PR", a colleague's PR number or URL. Never posts comments unless explicitly told. Do not use for the developer's own change (wf-review).
---

# wf-peer-review — what deserves attention, and how to read the rest

The developer is the reviewer; this skill is their prep. Two outputs: a short list of what matters,
and a route through the PR. Silence about everything else — no "looks good", no style nits the
project's linter or rules do not require.

Capability: STRONG_GENERAL; FRONTIER_REASONING for security, data-loss or architectural PRs.
Read `wf-review` → `references/review-contract.md` (scope, severity, finding contract, second pass)
and `references/ai-review-guard.md` — run it on your own candidates and on every bot comment already
on the PR, and run its learning loop once the developer has answered those comments.

## Steps

1. **Fetch the PR** read-only (`gh pr view`, `gh pr diff`, or the hosting MCP): title, description,
   base, head, file list, existing review threads. Never check out over the developer's work: use a
   separate worktree or read the diff remotely.
2. **Intent.** Ticket through Jira MCP, docs through the docs MCP, the project's rules and skills
   (local overlay `projects/<project>/`). The description is a claim to verify, not the requirement.
3. **Bug hunt** with the runtime's built-in code-review command on the PR (runtime adapter → Review
   engine), report-only — nothing posted, nothing changed. Candidates only.
4. **Contract pass** — what the engine does not know: acceptance criteria met, business rules,
   API/type contract and its other consumers (`rg` importers of every changed shared symbol), missing
   loading/empty/error states, i18n holes, tests that would pass on the old code, description vs diff.
5. **Second pass** — kill every candidate the contract says to kill, then run every survivor and
   every bot comment already on the PR through `wf-review` → `references/ai-review-guard.md`. Keep
   only what passes. Mandatory: a guessed premise in this report becomes a wrong review comment from
   the developer.

## What counts as "deserves attention"

A bug or regression · a broken API/type contract · a ticket rule not implemented · shared or core code
changed without its consumers handled · security or data loss · a missing state · an i18n hole ·
tests that do not test the change · the description claiming something the diff does not do · a
violated project rule. Nothing else is reported.

## Output

```markdown
## Варто звернути увагу (N)
1. **[P1] <defect as a title>** — `file:line`
   Що: … · Чому важливо: <failure scenario> · Джерело очікування: <ticket / doc / rule / contract>
   Питання автору: "<polite, ready to paste>"
…

## Не перевірено
- …

## Як пройти цей PR самому
<the route from references/walkthrough.md, filled with this PR's files>
```

Language: the developer's (Ukrainian by default); quoted code and identifiers stay verbatim.

## Posting

Never post, approve, request changes or resolve threads on your own. Only when the developer
explicitly asks: show the exact comment texts and their anchors, then post them as asked.
