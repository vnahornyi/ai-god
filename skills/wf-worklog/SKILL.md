---
name: wf-worklog
description: Use when the developer asks to log or audit worked hours — "залогуй", "закрий день", "розкинь години", Tempo, timesheets.
---

# Worklog Planner

Turn a day of commits into a defensible timesheet: which ticket, how many hours, and the text to paste.

The developer is not trying to inflate anything. They are trying to reconstruct where the day actually went, from evidence that is systematically incomplete — commit messages carry the wrong ticket, editor-time trackers miss most of the real work, and half the day never touches git at all. This skill exists to close that gap honestly, not to make numbers reach a target.

## The one rule that matters

**Never invent work to fill hours.** If the evidence plus the developer's answers do not reach the target for the day, say so and ask what is missing. Do not distribute the shortfall across tickets to make the day look full.

This is not pedantry. A padded row is the one a reviewer finds — a ticket with 3h logged on a day whose only commit touched nine files for fourteen minutes stands out immediately, and it discredits the honest rows around it. Underfilling a day is recoverable; a fabricated row is not.

The same applies in reverse: when the evidence supports **more** hours than a ticket's estimate allows, propose the real number and flag the estimate, rather than trimming to fit.

## Capability

Three kinds of work, priced differently (skill `ai-workflow` → model policy):

- **Evidence collection** — `collect_commits.sh`, Jira/Tempo fetches, copying numbers: FAST_ROUTINE work. Delegate it down when the runtime makes that cheap; never spend frontier reasoning on it.
- **Reconstruction and audit** — steps 3–8: STRONG_GENERAL. Escalate to FRONTIER_REASONING only when reconciliation is genuinely tangled: several bucket tickets, evidence that conflicts across a week, or corrections to time already logged.
- **Output formatting** — step 9 tables: mechanical, no extra reasoning pass.

A worklog is its own stage (WORKLOG). It needs the commits and the tracker, not the implementation or review context — run it in any session.

## Setup

Config lives at `.claude/worklog.json` in the repo. Read `references/config.md` for the schema and how to bootstrap it from scratch — do that on first run in a new project, then confirm the values with the developer before relying on them.

If there is no config and the developer wants to get going immediately, you can run once on defaults (8h target, English, ticket key inferred from branch/commit prefixes) — but say that you are doing so, and offer to write the config afterwards so the next run is faster.

## Workflow

### 1. Gather the git facts

Run `scripts/collect_commits.sh <since> <until>` from the repo root. It sweeps all branches and remotes, filters to the configured author emails, excludes merges and notes, and prints per commit: date, hash, ticket prefix, tracker time tag, change volume, and the meaningful changed paths.

Read the file paths, not just the messages. Paths are the strongest signal for what was actually worked on, and they are what lets you catch a commit filed under the wrong ticket.

For a week, run the same script across the range and keep the per-day grouping.

### 2. Load the Jira and Tempo picture

When a Jira MCP is connected, use it for ticket metadata (summary, status, estimate, time spent, description) — it is faster and needs no browser. The developer's own per-day Tempo totals still come from the Tempo timesheet in the signed-in browser.

Use a browser tool that drives the developer's real, signed-in browser and can run JavaScript in a tab — your runtime adapter names it (`AGENTS.md` → "Runtime adapter" → Capability discovery). No such tool → say so and ask the developer to paste the timesheet; never guess. The developer is already authenticated, so same-origin `fetch` against the Jira REST API from any page on the Jira host is the fastest path — far faster than clicking through the UI. `references/jira-tempo.md` has working recipes for the calls you need, including the async pattern that the JS tool requires.

Pull, for every ticket that appears in the commits:
- summary, status, assignee
- original estimate, time spent, remaining
- the description (you need its bullet list later)
- the issue type and parent — a sub-task or Defect is never the log target (see step 6)

Then pull what is **already logged** for the period, per day per ticket. Existing logs matter even on a fresh planning run: the developer may have logged part of the day already, and proposing hours on top of that double-counts.

The Tempo timesheet URL is in the config. Page through it week by week when you need the developer's own per-day totals — shared tickets (release tickets, planning tickets) carry other people's worklogs too, and the Jira API cannot separate them. The timesheet can; the API cannot. Use the API for ticket metadata and the timesheet for "what did *this person* log".

### 3. Identify bucket tickets

A bucket ticket is one that collects fixes belonging to *other* tickets — QA results, post-demo stabilisation, defect round-ups. They are the single biggest source of misattributed time, because every commit during that period gets the bucket's key in its message while the work itself belongs elsewhere.

Detect them by summary against the configured keywords, then **ask the developer to confirm** before treating a ticket as a bucket. A ticket that merely sounds like a bucket but is a real self-contained task should not be dismantled.

When a bucket is confirmed, read its description and split the bullet list. Each bullet usually maps to the feature ticket it is fixing — a bullet about badge layout belongs to the badges ticket, a bullet about modal styling to the modal ticket. Match bullets to tickets by comparing the bullet text against other tickets' summaries and descriptions, and by which files the related commits touched. Propose the mapping; let the developer approve or correct it.

What stays on the bucket is the genuinely cross-cutting work — the odd one-off fix, general localisation, snapshot regeneration that spans everything.

### 4. Ask the batch of questions

Ask everything at once. A single message the developer answers in one pass respects their time far more than a drip of one-at-a-time prompts. There is no cap on how many questions — completeness beats brevity here, because every question you skip becomes a guess you have to make silently.

Always ask:

1. **Which tickets did you actually work on today?** This is the primary source of truth. The commit prefixes are a cross-check against this answer, not a replacement for it. When they disagree, surface the disagreement rather than silently picking one.
2. **What did you do that produced no commits?** Reviews of other people's PRs, meetings, calls, design review, manual QA, debugging that led nowhere, research. The developer fills this in themselves — do not try to derive it from GitHub or a calendar unless they ask you to.
3. **Anything committed today that you actually did on another day** — only when the timing looks odd (a large commit landing at the start of a day, a gap followed by a burst).

Ask conditionally:

- When a ticket looks like a bucket → confirm, and confirm the bullet→ticket mapping.
- When a day has no commits at all → ask what the day was spent on. Do not silently borrow work from an adjacent day.
- When a commit's paths do not match its ticket's subject → ask which ticket it belongs to, and offer the path-map entry so the question does not recur.
- When the day involves a build or release step → ask whether it goes to the release ticket. Builds are periodic, not daily; suggest, never assume.

### 5. Reconstruct the hours

Tracker tags in commit messages (`#time 1h 22m`, WakaTime-style) count only active editor time. They are a **floor**, not a measurement, and they under-count unevenly: a task built mostly in the editor comes out roughly right, while design-comparison work, on-device QA, and build cycles come out at a fraction of reality. Treating the tag as the answer produces exactly the distorted picture this skill exists to fix.

So use the tags as a **proportion** — the relative split between tickets is usually sound even when the absolute numbers are not — and scale that proportion up to the day, accounting for the work that happens outside the editor:

- reading the spec, comparing against the design
- running the app; QA passes on each platform the change touches (iOS, Android, web — a change touching all three costs roughly triple the verification time of one)
- debugging, device testing, reproducing a defect
- waiting on and verifying builds
- reviewing your own diff, reading through regenerated snapshots
- ramp-up on an unfamiliar library or API — learning that happens *inside* the task is part of the task

Show your reasoning per ticket, in one short line: tracker time → proposed time, and why the gap. `1h 20m tracked → 3h — Figma comparison, iOS+Android verification, 40 snapshot diffs reviewed`. The developer can then correct a specific factor instead of arguing with a total.

Then apply the day's shape:

- Target is the configured norm (default 8h), and the configured minimum (default 7h) is the floor for a normal working day.
- Subtract fixed daily entries (daily standup and similar) before distributing the rest.
- Never propose more than the target for a day without saying so explicitly.
- If you land under the minimum, **say you are under and ask what is missing** — that is question 2 again, asked with a specific number attached.

### 6. Check each proposed ticket before you commit to it

These are warnings, not blockers. The developer decides; your job is to make sure they decide knowing:

- **Issue is a sub-task or a Defect** — time is never logged to these. A sub-task or Defect is a fix for a parent story or task, so the entry goes to that parent. Name the defect key in the entry text, and never propose the sub-task or Defect as the ticket. Zero logged time on such a sub-task is expected, not a gap.
- **Status is Done or Closed** — Tempo often refuses to log here, and the entry may silently fail.
- **Assignee is someone else** — logging into a colleague's ticket lands the overrun on their record.
- **No estimate set** — time logged into an unestimated ticket reads as unaccounted work.
- **Proposed hours exceed the remaining estimate** — say by how much, and what the ticket would end up at.
- **The day would exceed the target**, or the entry falls on a weekend.

### 7. Forecast completion, and say when to re-estimate

For each active ticket, compare what the commits show as implemented against the ticket description's scope, and estimate roughly how far along it is. Then extrapolate: at the current rate of hours per unit of scope, where does this ticket land?

When the projection overshoots the estimate, say so plainly and recommend the action — request a re-estimation, or decompose the ticket if the scope has genuinely grown beyond what was estimated. Raising this while the ticket is still open is a normal engineering conversation; raising it after it closes at 300% is an awkward one. The value of this step is entirely in its timing.

### 8. Audit what is already logged

Whenever logs exist for the period, check them against the same evidence and report:

- entries on a ticket the day's commits do not support
- entries sitting on a sub-task or Defect issue — propose moving them to the parent story or task
- entries that look padded to fill a ticket's remaining estimate — a large entry on a day whose evidence for that ticket is a single small commit is the classic shape
- days over the target, days under the minimum, weekend entries, working days with nothing logged
- tickets now past their estimate, with the overrun quantified

Propose specific corrections — from ticket, to ticket, day, hours — and let the developer approve. Never present a correction as already done.

### 9. Output

Two tables. Nothing else is needed, and extra prose gets in the way of copying.

**Operations table** — one row per entry to create, ordered by day:

| # | Day | Ticket | Hours | Text |
|---|-----|--------|-------|------|

The text is the worklog description, and it should be genuinely useful: name the components, screens, and files touched, and what changed about them. `Fixed styles` tells a reviewer nothing and invites questions. Two or three specific sentences make the entry self-evidently real and are what makes a 3h entry read as 3h of work. Write them in the configured language — this is the one place where matching the project's working language matters, since these strings land in the tracker for other people to read.

**Summary table** — one row per ticket:

| Ticket | Log | Days | Spent now | Will be | Estimate | Action |
|--------|-----|------|-----------|---------|----------|--------|

Include the full ticket URL (from the configured Jira base) so each row is one click away. Close with the day totals and any warnings from steps 6–8.

Do not write to Tempo. The developer enters these themselves — the output is built for that, and it keeps them in control of what lands on their record.

## Reference files

- `references/config.md` — config schema, bootstrap procedure, path-map maintenance
- `references/jira-tempo.md` — browser recipes for Jira REST and the Tempo timesheet
