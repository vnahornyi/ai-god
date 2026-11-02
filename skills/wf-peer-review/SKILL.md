---
name: wf-peer-review
description: Use when the developer asks to go through someone else's pull request — walk through a colleague's PR, a PR number or URL that is not theirs.
---

# wf-peer-review — what deserves attention, and how to read the rest

The developer is the reviewer; this skill is their prep. Two outputs: a short list of what matters,
and a route through the PR. Silence about everything else — no "looks good", no style nits the
project's linter or rules do not require.

Capability: STRONG_GENERAL; FRONTIER_REASONING for security, data-loss or architectural PRs.
Read `wf-review` → `references/review-contract.md` (scope, severity, finding contract, second pass)
and `references/ai-review-guard.md` — run it on your own candidates and on every bot comment already
on the PR — and `references/ai-review-replies.md` for explaining each bot comment and for the
learning loop once the developer has answered those comments.

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
## Worth attention (N)
1. **[P1] <defect as a title>** — `file:line`
   What: … · Why it matters: <failure scenario> · Where the expectation comes from: <ticket / doc / rule / contract>
   What to raise with the author: <the point and its evidence, in your words, not a comment to paste>
…

## Not verified
- …

## How to walk this PR yourself
<the route from references/walkthrough.md, filled with this PR's files>
```

Write this report in English and translate it into the session language when you show it
(global instructions → Language); quoted code and identifiers stay verbatim.

## Posting

Nothing is posted (global instructions → Publishing): no comment, approval, change request or
resolved thread, even when the developer asks. The report explains each point; the developer writes
and posts any comment themselves.
