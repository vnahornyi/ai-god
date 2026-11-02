---
name: wf-debug
description: Use when something is broken, crashing, flaky or slower than before and the cause is unknown — "чому падає", "не працює", "debug", a crash report, a failing or flaky test, a performance regression.
---

# wf-debug — find the cause before touching the code

Without this skill the agent reads code, settles on the first plausible theory and patches it; the
patch often fixes a neighbour of the bug, and nothing proves the reported symptom is gone.

The leading word is **red**: one command that fails on *this* bug and will pass once it is fixed.
No red command, no theory.

Capability: FRONTIER_REASONING for the hypotheses and the root-cause call (`ai-workflow`). Git: the
global rules apply; the fix is staged through `wf-implement` Phase 2 — stage, show, stop.

## Redact first

Commands, logs and captured requests carry secrets. Write `<REDACTED>` in their place in anything you
show, build loops on environment variables rather than pasted credentials, and quote only the lines
that carry the signal. When the redacted output is not enough, say so and ask.

## Phase 1 — Build a red loop

This phase is the skill; everything after it consumes the loop. Spend the effort here.

Ways in, roughly in this order (React Native specifics: `references/loops-rn.md`):

1. A failing test at the seam that reaches the bug, with the project's own test command.
2. A script that calls the function with the captured input and asserts the symptom.
3. A replay of a captured request, response or event log through the code path in isolation.
4. A device or simulator loop: a scripted trigger (deep link, launch argument) plus a filtered log.
5. For a crash: the symbolicated stack frame and the input that reaches that frame.
6. A bisect harness when the bug appeared between two known states (`git bisect run <loop>`).
7. A differential loop: the same input through the old and the new version, outputs compared.
8. Last: a structured human-in-the-loop script (`scripts/hitl-loop.sh`) when only a person can
   trigger it.

Tighten the loop: faster (narrow the scope), sharper (assert the user's symptom, not "did not
crash"), deterministic (pin time, seed randomness, fake the network). A flaky bug needs a higher
reproduction rate, not a perfect repro: loop the trigger many times, add load, inject delays at the
suspected race, until it fails often enough to debug.

**Done when** you can name one command that you have already run and shown (redacted) that:
- [ ] asserts the user's exact symptom and drives the real code path;
- [ ] gives the same verdict every run, or a stated, high failure rate for a flaky bug;
- [ ] runs in seconds;
- [ ] runs without a person, except through `scripts/hitl-loop.sh`.

When no loop can be built: stop, list what you tried, and ask for one of — access to the environment
that reproduces it, a captured artifact (log, trace, recording with timestamps), or permission for
temporary instrumentation in a build the developer controls.

## Phase 2 — Reproduce and minimise

Run the loop and confirm it shows the failure the developer described, not a nearby one; capture the
exact symptom (message, wrong value, timing). Then cut inputs, callers, config and steps one at a
time, rerunning after each cut. **Done when** removing any remaining element makes the loop pass.

## Phase 3 — Hypotheses

Write three to five ranked hypotheses before testing any. Each is falsifiable: "If X is the cause,
changing Y makes the bug disappear (or Z makes it worse)." A hypothesis without a prediction is
discarded. Show the list to the developer — they often know what changed — and carry on with your
ranking if they are away.

## Phase 4 — Instrument

Each probe tests one prediction; change one variable at a time. Prefer a debugger or REPL; otherwise
targeted logs at the boundaries that separate the hypotheses, every one tagged with one prefix such
as `[DEBUG-7c1e]` so cleanup is one search. Never log everything and grep.

Performance: measure before changing anything — a timing harness or profiler on a realistic input,
in a release build on the slowest supported device for UI work — and keep the before number. No
"faster" without a before and an after.

## Phase 5 — Fix with a regression test

1. Turn the minimised repro into a test at a **correct seam**: one that exercises the bug the way the
   real call site does. When the project needs the developer's approval for new tests, propose the
   test and wait for the yes.
2. Watch it fail. If you forced the failure by editing code or a fixture, compare against the
   untouched copy to prove the edit took effect.
3. Apply the smallest fix that the confirmed hypothesis explains; neighbouring cleanups become
   follow-ups.
4. Watch the test pass, then rerun the original, unminimised loop.

No correct seam (the only reachable test is too shallow to show the real pattern) is itself a
finding: report it instead of writing a test that proves nothing.

## Phase 6 — Clean up and report

- [ ] The original loop is green.
- [ ] The regression test passes, or the missing seam is reported.
- [ ] A search for the debug prefix finds nothing.
- [ ] Throwaway harnesses are deleted or kept outside the repository.

Report to the developer: the symptom, the loop command, the confirmed hypothesis and the rejected
ones, the fix with `file:line`, the test, before/after numbers for performance, and what was not
verified. The proposed commit message names the root cause. Then stage through `wf-implement`
Phase 2.

Adapted from mattpocock/skills `diagnosing-bugs` (MIT) for this workflow and React Native.
