# Framing the problem before choosing a solution

The failure this file exists to prevent: a change that is clean, typed, tested, and well-described — and that solves a **different problem** than the one reported, or solves it for a **smaller population** than the one that has it.

Nothing else catches this class. The compiler can't: the diff is internally consistent. Review usually can't: reviewers judge the code in front of them against the intent the author stated, and the author stated the intent they had. Tests can't: they assert the behaviour the author decided to build. The only thing that catches it is asking what "solved" means **before** deciding where to put the code.

The trap is that the normal engineering instincts all point the same wrong way at once. Fixing at the place the symptom was observed feels local and low-risk. Adding a guard feels defensive and responsible. Shipping the narrow diff feels disciplined. Each of those is a good instinct — `architecture.md` → Smallest change that solves it is built on them — and none of them is a substitute for establishing what has to become true.

> **The hinge.** "Smallest change that solves it" chooses *among solutions that actually solve it*. It is not a licence to pick the narrowest thing that makes the symptom disappear. Establish the outcome first; **then** climb the ladder from the inside out.

## Contents
- [The three answers](#the-three-answers)
- [Lenses](#lenses)
- [Choosing between the paths](#choosing-between-the-paths)
- [Reporting the trade-off](#reporting-the-trade-off)
- [Worked example](#worked-example)
- [Sources](#sources)

## The three answers

Before writing code — and, in Plan mode, before writing §4 of the plan — produce these three, in writing, in this order. Five lines each is enough. They go in the Gate 1 check-in and later in the PR description.

### 1. What does "solved" mean?

Not "the bug goes away." Answer four things concretely:

- **Whose problem is it** — the end user, the developer, the on-call, the analyst reading a dashboard, the next person to touch this module. Different owners want different fixes, and the requester is often not the owner.
- **Which population of cases** — all users, users on the current app build, users who paste an email, one admin screen, one endpoint. Count it if you can; a grep is a count.
- **Over what window** — from the moment this merges, or from the moment the last affected client updates, or never for data already at rest.
- **What observation would prove it** — a log that stops, a metric that starts arriving, a query that returns rows, a test that fails on the old code and passes on the new. If you cannot name the observation, you do not yet know what you are fixing.
- **What it costs while it persists** — one line. Whether the remainder is a rounding error or a live incident is what decides how much a partial fix is worth, and whether a blunt instrument (a forced update, a backfill, a rollback) is proportionate. Silent data loss and a wrong dashboard are not the same severity as a broken checkout, and neither is the same as an annoyance.

**The test that catches most of it:** describe the fix to someone who only knows the symptom, and have them ask *"and after this ships, who still has the problem?"* If the honest answer is "some people, for a while", that is not a footnote — it is the shape of the task, and it usually means the change belongs somewhere else or in more than one place.

### 2. The path of least resistance

Name it explicitly, even when you are not going to take it. Usually: the change nearest to where the symptom appeared, in the tree you already have open, touching the fewest files and no contracts.

Then name **the limit that makes it partial** — the thing it does not cover. Every least-resistance fix has one; if you cannot find it, you have not looked. Common limits: it only covers the callers that exist today; it only covers clients that ship it; it only covers the entry point you tested; it leaves the data already written untouched.

A least-resistance path is legitimate when it hits the brief, introduces no debt the team can't see, and stays understandable to whoever inherits it. If it fails those, you did not take the short path — you moved the cost onto someone later, when it will be more expensive.

### 3. The architecturally right path

Name it, and name its cost honestly: files touched, contracts changed, platforms to re-QA, coordination with another team, whether it needs a backend or a release.

**The cost is a fact to check, not a feeling to assume** — and it is the number that decides the task, so guessing it high is how the right path gets dismissed in one sentence. Before writing "needs backend coordination", go and look: is the service in this repo or a sibling you can open? Is the validation a schema file you could edit? Is the endpoint's handler thirty lines? A change that reads as expensive from the frontend often turns out to be a ten-line edit in a JSON schema two directories away. The inverse matters too — "just add a column" is not cheap when the table has a billion rows. Cite what you found, with the path.

If you find yourself writing "there is no difference, the local fix *is* the right one" — good, that is a real and common answer. Write the sentence anyway. It costs one line and it is the line that proves you looked.

**Produce all three even when the answer is obvious.** The two minutes are not for you; they are so that the human can see what was traded away. A change presented with only its chosen path reads as a recommendation nobody can audit — and that is exactly how a partial fix gets merged with a confident description.

## Lenses

Run these against the task. They are diagnostic, not a checklist to satisfy — most will not apply. Each is a question, the tell that it applies, and the move.

### Population and time window — who still has this after we ship?

**The single highest-yield lens, and the one most often skipped.** A fix only reaches the code that runs it. That is trivially true and constantly forgotten.

**The tell:** the change lives in a client — a mobile app build, a cached web bundle, a device SDK, a script someone copied. Or it lives in code that reads data written by something else.

**Why it bites hardest on mobile:** app releases are not deployments. Users defer updates, disable them, or sit on a build for months; a fraction never updates at all. So a client-side fix has an indefinite tail during which the old behaviour is still in production, generating the same incident. Server and client are never atomically deployed, which means a version-skew window always exists — the only question is how long and who absorbs it.

**The move:** if the affected population includes clients you cannot update, the durable fix is on the side you *can* deploy. Ship the client fix too — it stops the bleeding for new builds and it is usually right on its own merits — but do not describe it as closing the incident. Name the tail explicitly.

**Then find the tail's bound — it is rarely all-or-nothing.** Most shipped apps have a lever that shortens it, and it is worth two minutes to find out which one this codebase has: a minimum-supported-version gate that forces an update, an optional-update prompt, a server-driven feature flag or kill switch, a config endpoint the old build already polls. Grep for `minSupportedBuild`, `forceUpdate`, `maintenance`, the version/config endpoint, the update screen.

Finding one does not mean using it. It converts "the old builds will keep doing this forever" into "we are choosing to let them" — a decision with its own price, and usually a disproportionate one: forcing an entire user base to update is what you spend on a breaking change or a security fix, not on a metrics pipeline. State it that way. **The reason to look is that both possible answers sharpen the report** — either there is a lever and the tail is a policy choice with a named cost, or there is none and the tail is a fact. Vague ("some old versions, for a while") is the only wrong answer.

The same lens applies to data at rest: a validation fix does not repair rows already written. If bad data exists, a fix has two halves, and the migration half is the one that gets forgotten.

### Whose invariant is this? — the trust boundary

**The tell:** you are about to write a check in one system that enforces a rule owned by another. A regex in the client mirroring the server's schema. A length limit in the UI mirroring a column width. A client-side permission check.

**The move:** the rule must be enforced where it is owned — at the boundary of the system that cannot be bypassed. A copy on the other side is a **convenience**, never a guarantee, and it must be labelled as one. Two consequences follow, and both are easy to get wrong:

- A mirrored rule is a contract duplicated in two places with nothing keeping them in sync. It will drift. If you write one anyway, it needs a comment naming the source of truth, and ideally a generated type or a shared schema instead of a hand copy.
- A mirrored rule that *silently drops* data is worse than no check: it converts a loud failure into missing data nobody notices. If the client discards something, that must be observable.

Client-side checks are for **user experience** — telling someone their email is malformed before they submit. They are never the enforcement.

### Symptom, cause, or the thing that let the cause exist?

Walk the chain back until you reach something you can change that prevents the whole class, not the instance. Three or four steps is usually enough; the point is the direction, not the number.

**The tell you stopped too early:** your fix names a specific value, endpoint, screen, or field. "Fix the one call that passes a query string" is an instance. "The API accepts a shape that cannot express the invariant" is the class.

**The limit of this lens, stated honestly:** the chain assumes a roughly linear cause and effect, and real failures often have several interacting causes. Do not force a single root cause when there are two; and do not use "the real root cause is upstream" as a reason to ship nothing. The usual correct answer is *both* — instance now, class as a named follow-up.

### Can the type make this impossible instead of the runtime checking it?

**The tell:** you are adding a runtime validation, a guard, a defensive branch, or an `if (!valid) return` to catch a mistake that a shape could have prevented at compile time.

**The move:** ask whether the illegal state can be made unrepresentable. Parse the untrusted thing once, at the boundary, into a type that cannot hold a bad value — then everything downstream is correct by construction and needs no checks at all. The concrete forms this takes in a TS codebase:

- A union that admits a loose member (`string | StructuredThing`) where only the structured one carries the information you need — remove the loose member instead of validating what came through it.
- A parameter typed `string` where a literal, a branded type, or a template-literal type would reject the wrong value.
- A "validate then use" pair — `isValidX(v)` followed by `use(v as X)` — where `parseX(v): X | null` removes the cast.

The payoff is not elegance. A runtime guard protects the callers that run it; a type protects the callers that don't exist yet, which is the population that actually causes regressions.

### What does the containing system do with one bad item?

**The tell:** the change produces or consumes a batch, a queue, a bulk endpoint, a stream, a background flush.

**The move:** find out whether one malformed item fails the item or the whole batch. All-or-nothing batch handling turns a single bad record into a total outage of that pipeline — the poison-pill shape: one item blocks the other 999, and retries re-send the poison forever. If that is what you found, the durable fix is per-item handling on the consumer (accept the good, reject and log the bad), not preventing every possible bad item on every producer.

This is doubly true for **telemetry, logging, and analytics ingestion**: those pipelines must degrade, never fail closed. A monitoring system that stops recording because one field was malformed removes the visibility you would need to notice.

### Does this grow without bound?

**The tell:** the change adds something keyed by a value that varies per user, per request, per entity — a cache, a `Set`/`Map` on a long-lived object, a metric label or tag, a log line in a hot path, a stored key.

**The move:** name the bound. For in-memory structures on an object that lives as long as the app, "bounded by the number of distinct code paths" is a real answer and "bounded by the number of requests" is a leak.

For **metrics specifically** this is a hard rule, not a preference: a label/tag value is a time series. Identifiers — user id, order id, request id, a concrete URL — must never be label values; the dimension has to be a normalized template (`/users/:id`, not `/users/8134`). A change that emits a concrete path into a metric is a cardinality incident whether or not the value passes validation.

### Why does the current thing exist?

**The tell:** you are about to remove, bypass, or "simplify" something whose purpose isn't obvious — a flag, a branch, an odd encoding option, a seemingly redundant check.

**The move:** find out why it is there before removing it. `git log -S` on the exact string, the PR that introduced it, the ticket. Odd-looking code in a shipped product is frequently a bug fix whose reason is invisible in the diff — a platform quirk, an old client, a backend that only accepts one shape. If you cannot find the reason, say so out loud rather than deleting silently, and preserve the behaviour by default.

### How reversible is this? — and therefore how much rigour to buy

Match the effort to the cost of being wrong. Most decisions are two-way doors: ship, learn, change it. A few are one-way and deserve a conversation before code.

**Two-way (decide and go, note the assumption):** an internal function's shape, a component's props, a local state decision, anything behind one call site, anything you can revert in one commit.

**One-way-ish (stop and ask):** a persisted data format or storage key, an API contract other clients depend on, anything shipped into an app build that users won't update, a public URL or deep-link shape, a metric name or dimension a dashboard will accumulate history under, a dependency added, a shared abstraction other teams will build on.

The asymmetry is the point: over-thinking a two-way door is a small waste, under-thinking a one-way door is paid for over years. This is also the honest answer to "should I take the least-resistance path?" — for a two-way door, usually yes, and say so; for a one-way door, the least-resistance path needs an explicit decision from whoever owns the contract.

## Choosing between the paths

Once the three answers exist, the choice is usually mechanical:

1. **If the least-resistance path does not cover the population from answer 1, it is not a candidate on its own.** It can still be the right thing to ship *first* — it usually is — but the report must say what remains uncovered and where the rest lives.
2. **If both cover it, take the narrower one.** Tie-breakers, in order: fewest files touched, least contract change, lowest operational risk, easiest to revert. Not fewest lines.
3. **If the right path is out of scope for this task** — it needs another team, another repo, a release, a migration — do not silently do half and describe it as whole, and do not down-tools either. Ship the covered part, open the follow-up with a concrete description, and name both in the report.
4. **If the two paths disagree about *where* the fix goes** (client vs server, runtime vs type, instance vs class), that is not a style preference — it is the substance of the task, and it goes to the human before implementation, not into the PR description afterwards.

**The most common correct answer is "both, sequenced."** Instance now, class next; client now, server durably; guard now, type when the migration lands. Sequencing is a real answer and it should be stated as one, with the order and the reason.

## Reporting the trade-off

The chosen path is one line. What was traded away is the part the reader cannot reconstruct.

State plainly, in the check-in and again in the PR description:

- what "solved" means here, and **who still has the problem after this merges**;
- the alternative you did not take, and the one reason;
- what this does *not* cover, and where the rest lives (ticket, follow-up, another team).

**The anti-pattern to avoid by name:** a description that argues for the change. A wall of ✅ checkboxes, a paragraph defending each decision, a "considered alternatives" section written to close the question rather than open it — these read as thorough and function as a case for the defence. A reviewer's job is easier when the description says what is uncovered. If your description contains no sentence a reviewer could disagree with, you have written an argument, not an assessment.

Same rule applies in Review mode, pointed at someone else's change: before commenting on the code, ask whether the change solves the reported problem for everyone who has it. A partial fix with a confident description is the most expensive thing that passes review.

## Worked example

**Reported:** a request-timing telemetry endpoint returns 400 and no timing data is recorded. Cause found quickly: the batch carries a `path` field, one entry contained a full URL with a query string, the endpoint's schema rejected it — and the endpoint rejects the **whole batch** on one bad entry.

**What was built:** the two API callers that passed a string URL were rewritten to pass the structured tuple, and the client gained a helper that strips the query string, re-validates `path` against a copy of the server's regex, drops non-matching entries, and logs a deduplicated warning. Clean, tested, typed, described in detail.

**What the three answers would have surfaced:**

1. *Solved for whom, over what window?* — for users on **builds shipped after this merges**. Every existing build keeps sending the same malformed `path` for as long as it is in use, which for a mobile app is months. Checking the tail's bound found a real lever — the app polls a version endpoint and hard-blocks builds below `minSupportedBuild` — but spending a forced update of the whole user base on a telemetry bug is plainly disproportionate, so the tail stays by choice. Both halves belong in the report: the change does not close the incident, and the option that would close it costs more than the incident does.
2. *Least resistance* — fix the two callers, guard the metric-building code. Limit: covers only callers that exist today and only clients that ship it.
3. *Architecturally right* — (a) the ingestion endpoint validates per entry and drops the bad ones instead of failing the batch, which fixes it for every client version forever; (b) the API's `urlData` type stops accepting a bare `string`, so a concrete URL cannot reach the metric by construction.

**Which lenses fired:** *population and time window* (the decisive one — old builds); *whose invariant* (a client-side copy of the server's schema, drifting by construction, silently discarding telemetry); *containing system* (all-or-nothing batch — the poison-pill shape, in a pipeline that should degrade rather than fail closed); *type over runtime* (the `string | UrlData` union is what let the value through, and no runtime guard protects the call site written next month); *unbounded growth* (the metric field is a database tag, and the regex happily accepts `/orders/123456/`, so the guard does not protect cardinality at all — only the tuple discipline does).

**What the report should have said:** ship the caller fixes now; the incident closes only when the endpoint validates per entry; the client-side regex mirror should be dropped once the type change lands, because it duplicates a contract across a trust boundary and buys nothing the type doesn't.

Note what is *not* wrong with the original: the code quality, the tests, the narrowness of the diff. The instincts were right and the framing was missing. That is what makes this class expensive — it does not look like a mistake at any point where someone would normally look for one.

## Sources

Alexis King, *Parse, don't validate*; Yaron Minsky, *Make illegal states unrepresentable*; Malte Ubl,
*Version Skew*; AWS, partial batch responses; Prometheus label cardinality guidance; one-way vs
two-way door decisions; Martin Fowler, *Technical Debt Quadrant*; Richard Bown, *path of least
resistance*; 5 Whys and its limits. Links: this file at ai-god commit `ac54a7c`.
