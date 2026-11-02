---
name: wf-review
description: Use when the developer asks to review their own change ("зроби ревʼю", "review my diff/PR", a staged diff, a commit range) or to answer review comments and bot reviews on their own PR.
---

# wf-review — review your own change, cold

Capability: FRONTIER_REASONING — the review assigns severity and decides the fix for every finding;
the fixing session only implements it (`ai-workflow` → model policy). Read `references/review-contract.md` before the diff.

## Independence

The review never runs in the context that implemented the change. Launch a fresh session or a cold
subagent (runtime adapter → Cold reviewer) whose prompt holds only:

- the developer's request and acceptance criteria, stated neutrally;
- ticket and documentation identifiers (Jira / docs MCP) — the reviewer retrieves them itself;
- the exact scope: working tree, `<base>..<head>`, or the PR number/URL;
- the project (so its rules and skills under the local overlay's `projects/<project>/` apply) and whether styles
  were developer-owned or assigned to the agent.

Never pass implementation reasoning, confidence or candidate findings. Without a cold context, say
so and offer a new session or a clearly labelled non-independent check.

**Spec axis.** When the task has acceptance criteria or plan Business rules, launch a second cold
reviewer in parallel, the same way and with the same facts, plus the prompt line `Axis: spec`. A
direct fix without them skips it. The Spec reviewer runs only "Spec axis" below; the main reviewer
runs the Steps.

## Steps (inside the cold context)

1. **Fix the scope** per the contract — untracked files read in full; snapshot `git status`.
2. **Establish intent** from the ticket, docs and project rules before reading code.
3. **Bug hunt — run the runtime's built-in code-review command** (runtime adapter → Review engine)
   on the same scope, at medium effort, high for high-risk changes, in its report-only form: nothing
   is posted to the PR and nothing is changed. Treat its output as candidate findings. When the
   runtime has no such command, do the bug hunt yourself per the contract.
4. **Add what the review engine does not know:**
   - acceptance criteria and documented business rules — each one implemented, or a finding (the
     Spec reviewer owns this when the Spec axis runs);
   - the PR description's claims against the diff;
   - the project's rules and skills (barrels, data-access layering, i18n pipelines…);
   - style provenance (contract → "Style provenance");
   - "after this merges, who still has the problem?" (`frontend-craft` → `references/problem-framing.md`);
   - for React/RN, the review checks in `frontend-craft` (Review mode).
5. **Second pass** — kill every candidate the contract says to kill; merge duplicates between
   the review engine and step 4. Then run every survivor through `references/ai-review-guard.md`;
   a finding the guard cuts is not reported. This step is mandatory — the developer acts on this
   report, so a guessed premise here becomes a wrong instruction on their PR.
6. **Report** one list, P0 → P3, each with `file:line`, failure scenario, source of the expectation,
   the narrow fix, and `severity`/`kind` for fix routing. End with exactly one outcome — findings /
   no findings / blocked — plus what was not verified.

## Spec axis (inside the second cold context)

Read the ticket, the acceptance criteria and the plan's Business rules first, then the diff. Report
three kinds, each quoting the spec line it rests on:

- **missing or partial** — a requirement with no code, or code that covers only some of its cases;
- **unrequested** — behaviour the diff adds that no spec line asks for;
- **implemented wrong** — code that does something other than what the line says.

A line too vague to judge is reported as a spec gap, not guessed. Run every finding through
`references/ai-review-guard.md` (Step 5) and report it as in Step 6, under a separate **Spec**
heading. The orchestrating session relays both reports unchanged; where they name the same line it
keeps one and says so.

## After the review

Findings go to the developer in the conversation. Fix nothing until they decide; accepted findings are
fixed directly (no fixes plan), exactly as the review decided them (`ai-workflow` → model policy →
Review → fix routing). Once
they have decided, the orchestrating session runs `wf-retro` before the fixes.
