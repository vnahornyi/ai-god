# Mode: Review

Used by `wf-review` and `wf-peer-review` for React/RN diffs, after their own steps.


**Independent review is separate from implementation** (`wf-review`): use a fresh context at FRONTIER_REASONING, which decides each finding's fix. Its prompt contains the task and acceptance criteria, authoritative documentation references, PR reference, and diff scope — never implementation reasoning or candidate findings. Never review in the context that implemented the change. The contract below is the same in both cases.

**Read `wf-review` → `references/review-contract.md` first — before the diff.** It carries the scope rules, the severity scale, the finding contract, and the two things a review most often gets wrong: reviewing an incomplete scope, and reporting candidates that don't survive a second look.

The four things that must happen every time, in order:

1. **Fix the scope.** Working tree (staged + unstaged + **untracked**, read in full — `git diff` never shows a new file) or an explicit `<base>..<head>`. Snapshot `git status --porcelain` and re-check it before reporting.
2. **Establish intent before judging.** The diff tells you what changed, never whether it was right or complete. Task/ticket acceptance criteria → `CLAUDE.md`/`AGENTS.md` → authoritative docs via MCP → surrounding code. The plan is implementation context, not the acceptance criteria. If you can't state in three sentences what this was supposed to do, the review is **blocked** — say so instead of reviewing the parts you understood.

   Then ask the question the diff cannot answer: **after this merges, who still has the reported problem?** A change can be correct in every line and still cover a smaller population than the one that has the bug — clients that never update, data already written, callers added next month, the other platform. This is the most expensive finding a review can produce and the one most often missed, because the code reads as finished and the description reads as thorough. `references/problem-framing.md` has the lenses; a description made entirely of ✅ and arguments in favour is itself a tell.
3. **Read the code *around* the diff.** Most real defects live in the interaction between new and existing code, not inside the new lines.
4. **Kill your own findings before reporting them.** Is the anchor inside the change, or pre-existing? Does a guard, a type, a caller, or a test already prevent it? Does the ticket actually ask for the behaviour you're calling a bug? A finding that applies a rule where `references/examples-house-style.md` says "Does not apply when" is not a finding.

Order findings by **P0 → P3**, and within a severity by what hurts: correctness → regression risk → missing states → a11y/platform → performance → structure → style. Structure and style go last and stay short; a review that leads with naming preferences buries the bug.

For each finding: `file:line`, what breaks, the concrete input or state that breaks it, and **where the expectation came from** — ticket, doc, project rule, or the contract in the code. A finding you can't state a failure scenario for is an opinion — label it as one or drop it. Propose the narrow fix, never the refactor you'd prefer; see `references/architecture.md` → Smallest change that solves it, which applies to what you *ask* for as much as to what you write.

Explicitly check the same pre-flight categories as Gate 2 (`mode-build.md`); they're what reviews miss too.

**Test files and shared mocks are part of the diff, not its appendix.** Run the two checks in `review-contract.md` → Classify before you load on every review: test hygiene against `references/testing.md` (restores in `afterEach`, no state leaking through a shared `__mocks__`), and a test that pins each bug the change claims to fix.

**A diff that adds a route or a screen has two findings that hide in plain sight**, because neither shows up in the rendered result the author tested: the missing gate (a deep-linkable route that never checks the feature setting its sibling platform checks) and the shared-store key race (two screens served by one singleton store keyed by a single id). Look for both by name before commenting on anything else in the file.

**A diff that touches a store, a provider, a cache or a payload** gets `references/data-flow.md`: two writers for one fact, a derived value materialised into a second home, a `?? 0` that erases "missing", a full-entity save that can lose an update.

**A diff that adds or changes motion, gestures or haptics** in React Native gets the `react-native-animations` skill → `references/motion-review.md`. It separates runtime defects from feel opinions; a value that only differs from that skill's defaults is not a finding when the design or the developer set it.

**A diff that adds or changes a component rendering data** gets `references/worst-case-data.md` → Review: find the rendered values, then ask which plausible worst case each one was never built against.

Don't run the full suite by default — that's the build pre-flight's job, not a reviewer's. Run something targeted only when a candidate can't be confirmed otherwise, and judge a red check before you report it: a failing snapshot or suite can be the author's environment — stale generated artifacts, a locale catalog that was never recompiled — rather than their code. Reproduce, or say explicitly that you didn't.

Close with the outcome stated plainly — **findings / no findings / blocked** — what you couldn't verify from the diff alone, and the caveats (docs you couldn't reach, commands you didn't run, a tree that moved mid-review).

---

## Mode: acting on review comments

Working someone else's review comments is not Build with a shorter prompt. Comments arrive in three kinds, and mixing them up is what turns a cleanup round into a new argument.

**Triage every open comment before touching code**, and put the triage in front of the user. A comment from an AI reviewer goes through `wf-review` → `references/ai-review-guard.md` first, and the guard's learning loop runs once the developer has posted their replies:

1. **Already fixed.** Re-check each comment against the *current* head, not against the commit it was written on. A review round is often days old and later commits addressed half of it; re-implementing those is churn, and the correct output is a reply pointing at the line that already does it. Reviewers say so themselves when they re-run — read their latest comment before their first. **In a stack, "current head" is ambiguous until you prove the chain is in order** — sync the branches first (`references/stacked-branches.md`), then re-triage; a stale parent manufactures both false "already fixed" and false "still broken" verdicts, and either one sent to a reviewer costs more trust than the original defect.
2. **Owner's call about the owner's module.** Layering, file granularity, where tests live, which runner, how a shared method behaves — when the person who owns that module states the rule, implement it. This is not the place to defend your version.
3. **Behaviour change.** Read the **sibling platform and the ticket before complying.** If the current code matches how the other platform already behaves, the request is a product decision to diverge, not a defect report — answer with the sibling's `file:line`, and let the user decide. Silently making mobile behave differently from web because a reviewer asked is how two platforms drift apart one PR at a time.

**Fix the property, not the repro.** A comment hands you a scenario; the scenario is a test case for an invariant, never the specification. Before writing the fix, state the invariant in one sentence — *freshness means this screen's own request for this identity has settled*, *the badge may only assert what has been re-checked* — and then ask which **other** states violate it. A fix built to make the quoted repro pass will hold for that repro and fail on its siblings, and the next review round arrives with one of them. This is the same point-fix pattern that produces a ticket's fourth reopening; being the one who closes it does not make it different.

**Then review your own fix before pushing it.** Writing a fix from a reviewer's sentence inherits that sentence's narrowness, and an author reading their own patch is still in Build mode: they check that it does what they meant. Re-enter Mode: Review on the diff — scope, intent, kill-your-own-findings — and specifically enumerate how the new guard can be *wrong*, not just whether it fixes the named case: a stale value that still matches the key, an error path that never clears it, a second instance, a group of requests where only one is the one you meant. Skipping this is how a fix for a P2 ships its own P2.

A comment asking for less diff — formatting churn, unrelated fixture swaps, editor config — is a real fix, not a style quibble: revert those files to base and re-apply your feature hunks on top of the base formatting. Verify afterwards that the file's diff is only your hunks, and never re-run the formatter over it.

End the round with the same shape as Gate 3, plus, per comment: fixed / already fixed on head (with the line) / needs the user's decision — and a draft reply for the threads you are not closing with code.
