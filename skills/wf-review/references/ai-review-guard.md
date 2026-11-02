# AI review guard — cutting unrealistic review comments

## Contents

- The gates
- What survives
- When producing a review yourself

Use this on every comment that comes from an AI reviewer — someone else's bot on the developer's PR,
the runtime's review engine, or your own candidate list before it is reported. A comment survives only
if it passes every gate below. The gates are ordered by how often bot reviews fail them.

`review-contract.md` → Judging someone else's claim says *how* to work a claim (premise, concern,
current head, answer both). This file says *which claims to cut*. Drafting replies to cut comments,
the developer's voice, the learned cases and the learning loop live in `ai-review-replies.md`.

Process basis: AI remarks are checked in the context of the module before they reach the PR author.
A bot review forwarded unchecked breaks that rule; the developer may cite it in a reply. A team PR
guide in the local overlay (`company/pr-guide.md`) may state the rule; cite it when present.

## The gates

**1. Premise checked in the source, not guessed.** "If `useFrameOutput` returns a new output…",
"may be stale", "could rebuild the session" — a conditional is not a premise. Open the library in
`node_modules`, the provider, the style file, the route table, the repo's PR template, and read what it does. A comment whose
premise is false is cut, whatever its concern sounds like; keep only the narrowest true version, if any.
"The test does not pin the bug" is checked by running the test against the pre-fix code: red there
means it pins it, whatever format it asserts.
A claim that a crash guard is redundant ("already guarded upstream", "only called from X") is checked
against the crash's own stack frame, not the call graph: a guard at the entry does not cover a read
further down when anything in between can release the object — emitted events, listeners, callbacks,
third-party code. Removing a guard that a production trace asked for needs that trace re-read.

**2. Compared with base.** Run the same reading on the base branch. Behaviour that existed before the
diff — the same guard, the same log level, the same toast, the same torch effect — is not a finding of
this PR unless the diff makes it materially worse. At most it is a separate task, labelled pre-existing.

**3. Reachable in this app.** Follow the whole cycle, not one branch: guards further up
(`isActive`, a lock, `disabled` while pending), the configured formats and options, the lifecycle
(focus, background, unmount), the platform. A state the configuration never produces — an empty value
from a fixed-length checksummed barcode format, an `AbortError` from a request that is never aborted —
is not a scenario.

**4. A concrete failure with its rate.** Input → what the user sees → how often. "Up to 30 fps" has to
survive the step that turns the camera off; "a second toast" has to survive the lock. A claim without
a reproducible path is a question to the author, never "Важливо".

**5. Blast radius counted, not asserted.** "Used by several screens" requires `rg` over the callers:
name them. Two callers in the same module is not "several screens".

**6. Project rules beat generic advice.** Check the project's `AGENTS.md` and skills before accepting a
"best practice": React Compiler memoization rules, `useState` only for render state, no opportunistic
refactors, the ticket's scope. Advice that contradicts a project rule is cut and the rule is cited.

**7. Neighbouring code read before naming or structure claims.** "The name misleads", "this is not the
guide frame" — open the styles, the layout, the sibling component. A naming claim refuted by the
layout is cut.

**8. Severity matches impact.** Style, naming and "consider extracting" have no severity — they are
optional suggestions at most. "Важливо" / P1 / HIGH needs gates 1–4 passed with a user-visible failure.

**9. Scope is the ticket's.** Extracting a shared helper across modules the ticket does not touch,
changing monitoring levels, renaming for taste — out of this PR. Say "separate task" and move on.
Refactors (renames, file decomposition, structure changes) and side changes belong in separate PRs
(and in the team PR guide, local overlay `company/pr-guide.md`, when present).
Polish that no product or design requirement asks for is out of scope, however cheap it looks.
Release-process advice — staged rollout, shipping a risky change in a separate release, when to run
a pre-launch report — is the developer's release decision, not a finding on the diff.

**10. No abstraction for an ideal.** A suggestion that adds a layer, a split or a composition only to
make a name or a structure "purer" — with no failure it removes — is cut. So is a swap to a shared
or global helper that makes the code or test heavier for consistency's sake: a test wrapper with 30+
providers where four are needed, a snapshot that grows with it.

## What survives

Real findings usually look like this: a test that leaks fake timers on failure, a bug fix without a
test that pins it, one author contradicting themselves in the description, a shared hook whose behaviour change is not
explained. They are cheap to verify and cheap to fix — accept them without argument.

Confirmed by the developer's 👍 so far: a lock file not regenerated after a dependency bump, a
safety check present in one lane but missing in its sibling lane, a non-obvious build flag without a
one-line why, a wrong command in a doc, a local mock duplicating the global one, a lint warning the PR
itself introduced, a missing test case for the input shape the change is about. A 👍 is not proof:
"redundant crash guard" was once accepted and the crash shipped again (gate 1).

## When producing a review yourself

Run the same gates on your own candidates before reporting them (`review-contract.md` → Second pass).
A review that would be cut by this file is the review the developer has to defend against.
