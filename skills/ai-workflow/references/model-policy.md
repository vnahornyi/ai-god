# Model policy — capability classes

## Contents

- Capability classes
- Stage policy
- Review → fix routing
- Escalation triggers
- De-escalation
- Why switch
- Fallback matrix
- Objective

Shared skills name a **capability class**, never a model. The runtime adapter maps each class to a
concrete model and reasoning effort for that runtime (adapter → "Model mapping"). Updating a model
means editing one adapter table, not a skill.

## Capability classes

**FRONTIER_REASONING** — the strongest reasoning the runtime offers, at high effort.
Planning with unresolved product or architecture decisions · difficult debugging · independent
review and the fix decision for every finding ·
cross-platform architecture · resolving a substantive conflict between requirements and code.

**STRONG_GENERAL** — a strong coding model at medium effort.
Implementation that follows a verified plan · tests · refactoring · straightforward debugging ·
fixes after review · normal code investigation.

**FAST_ROUTINE** — a fast, cheap model at low effort.
Trivial edits · formatting · mechanical transformations (renames, catalog regeneration, fixture
updates) · simple documentation · repetitive changes · file operations · evidence collection that is
a script plus copying its output.

A runtime may map two classes to the same model with different effort; then moving between those
classes means a new session at the other effort, not a new model.

A class is a floor for quality, not a ceiling for thinking time. When one task mixes classes, the
hardest part sets the class for the session; the mechanical rest is delegated down only when the
runtime can do so cheaply (a subagent with a lower model) — otherwise it is done in place.

## Stage policy

| Stage | Class | Notes |
|---|---|---|
| PLANNING | FRONTIER_REASONING | Framing and contract decisions are where a cheap mistake becomes an expensive plan |
| IMPLEMENTING | STRONG_GENERAL | Implement and inspect the complete task diff; escalate per triggers |
| IMPLEMENTING — mechanical steps | FAST_ROUTINE, or inline without a subagent | Do not delegate unless it saves more than it costs |
| REVIEWING | FRONTIER_REASONING | Fresh, independent context; assigns severity and decides the fix for every finding |
| FIXING | STRONG_GENERAL | Implements the fixes the review decided — section below |
| JIRA TICKET TEXT | STRONG_GENERAL | Reads a plan or a lightly researched task; never writes code |
| PEER REVIEW (someone else's PR) | STRONG_GENERAL; FRONTIER_REASONING for security, data-loss or architectural PRs | Report only what deserves attention |

## Review → fix routing

The independent review runs at FRONTIER_REASONING and owns the judgement: it assigns every finding's
`severity` and `kind` and decides its fix — what changes, where, and the expected behaviour after.
Severity mapping from `wf-review` → `references/review-contract.md`: P0 and P1 → BLOCKER · P2 → HIGH ·
P3 → MEDIUM · closing notes with demonstrated impact → LOW.

The FIXING session runs at STRONG_GENERAL for every severity and implements the accepted fixes exactly
as the review decided them. It does not re-judge severity or choose another fix. When a decided fix
does not hold — the code differs from the finding, the fix breaks something else, or it needs a choice
the finding does not settle — it stops and brings that one finding back to the developer with the
evidence; the developer decides whether the reviewer answers it.

## Escalation triggers

Escalate to FRONTIER_REASONING when any holds:

- the same failure persists after **2 meaningful attempts** (an attempt is meaningful when it tested a
  different hypothesis, not the same fix re-typed) — **1** attempt when the runtime adapter marks the
  STRONG_GENERAL mapping as a trial;
- a stop condition written in the plan fires (a fact marked ⚠️ UNVERIFIED turns out different, or the
  code does not look the way the plan describes);
- the implementation contradicts the plan, or the plan turns out to be wrong;
- tests expose an architectural mismatch rather than a local bug;
- several valid approaches exist with materially different trade-offs;
- the change must cross a system boundary the plan did not cover;
- API or data ownership is unclear;
- behaviour becomes inconsistent across platforms;
- debugging requires reasoning across several independent systems.

Before escalating, formulate one question with enough verified evidence to answer it without repeating the exploration. Send it inline to a suitable fresh agent or ask the developer; do not create an escalation file.

## De-escalation

Say it when the remaining work no longer needs the current class:

```
DE-ESCALATE
Remaining: <what is left>
Why it is mechanical: <one line>
Recommended: STRONG_GENERAL | FAST_ROUTINE
```

Then follow the developer's override (`auto` → hand off at the next meaningful boundary, not mid-edit).

## Why switch

Never recommend a switch because a model is "stronger". The only test:

> Does the next operation need a capability class the current session does not efficiently provide —
> or independence the current context cannot provide?

No → do not switch. Yes → the recommendation carries:

```
Current: <class>   Required: <class>
Reason: <the concrete fact — the finding, the failure, the stage change>
Benefit: <what gets better>
Trade-off: <extra usage, a new session, developer waiting>
```

## Fallback matrix

| Wanted | Unavailable → | Then |
|---|---|---|
| FRONTIER_REASONING for planning, implementation escalation, complex fixes | STRONG_GENERAL | Continue with an explicit **reduced-confidence** notice in the response |
| FRONTIER_REASONING for a high-risk independent review, an architecture decision, security-sensitive reasoning | — | **Stop and ask the developer**: wait for the limit to reset, or accept a reduced-confidence review (labelled so in the response) |
| STRONG_GENERAL | FRONTIER_REASONING | Use it; note the cost. Never block on a *stronger* model |
| STRONG_GENERAL | FAST_ROUTINE only | Stop for implementation; FAST_ROUTINE may do evidence collection and formatting |
| FAST_ROUTINE | anything stronger | Use it, or do the work inline without a subagent |
| Subagents | — | Do the work inline; say so |
| Fresh session for review | cold subagent (adapter → "Cold reviewer") | Allowed; label it in the response |
| Cold subagent for review | — | Stop — a review from the implementing context is not independent. Ask the developer to open a new session |

## Objective

Minimise total model usage + developer waiting + rework + duplicated context + review blind spots,
subject to correctness, architecture quality, independent review, reproducibility and auditability.
Five cheap agents that misread the task cost more than one strong one: when in doubt at a decision
point, pay for reasoning; when in doubt on a mechanical step, do not.
