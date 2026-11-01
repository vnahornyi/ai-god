# Project config

## Contents

- Schema
- Bootstrapping on first run
- Rotating tickets
- Maintaining the path map
- Multiple repos


Lives at `.claude/worklog.json` in the repo root. Everything is optional — the
defaults noted below apply when a key is absent — but the more of it is filled
in, the fewer questions the developer has to answer on every run.

## Schema

```jsonc
{
  "jira": {
    "base_url": "https://acme.atlassian.net",
    "project_keys": ["PROJ", "OPS"],
    "account_id": "712020:b14f...",            // the developer's Jira accountId
    "tempo_timesheet_url":
      "https://acme.atlassian.net/plugins/servlet/ac/io.tempo.jira/tempo-app#!/my-work/week?date={date}&type=LIST"
  },

  "author": {
    "emails": ["dev@example.com", "dev@work.example.com"]
  },

  "day": {
    "target_hours": 8,        // default 8 — what a full day should come to
    "min_hours": 7,           // default 7 — below this, ask what is missing
    "workdays": [1,2,3,4,5]   // 1=Mon. Entries outside these days get flagged
  },

  "language": "uk",           // language for worklog descriptions; default "en"

  // Entries that recur every working day. Use `summary_pattern` rather than a
  // fixed key when the ticket rotates (a new one each month) — see below.
  "fixed_daily": [
    { "summary_pattern": "Planning {month} {year}", "minutes": 30 }
  ],

  "release_ticket": {
    "summary_pattern": "Build and release {month} {year}",
    "only_before_release": true    // builds are periodic, not daily — suggest, never assume
  },

  "bucket_keywords": [
    "test results", "post-demo", "defects", "stabilisation", "part "
  ],

  "path_map": {
    "src/components/offer-tile/**": "PROJ-2940",
    "src/labels/**": "PROJ-2864",
    "ios/**": "PROJ-2971"
  }
}
```

## Bootstrapping on first run

Do this once per repo, then confirm the result with the developer before
relying on it — a wrong `account_id` or author email silently produces an
empty or someone else's picture, which is worse than no config.

1. **base_url and project_keys** — read them off the ticket keys in recent
   commit subjects, and off any Jira URL already open in the browser.
2. **author.emails** — `git config user.email`, plus any other address that
   appears as an author in `git log --format='%ae' | sort -u` with a plausible
   number of commits. Ask before adding a second address.
3. **account_id** — from any Jira REST response where the developer is the
   author or assignee, or `/rest/api/3/myself`.
4. **tempo_timesheet_url** — ask the developer to open their Tempo timesheet
   once and copy the URL; replace the date value with `{date}`. The servlet
   path differs between Tempo versions, so deriving it is unreliable.
5. **fixed_daily** — look at the last two weeks of the timesheet for an entry
   that recurs every working day at the same length. Propose it; do not add it
   silently, because a recurring entry that the developer has stopped logging
   would then quietly reappear in every plan.
6. **day.target_hours / min_hours** — read the timesheet header (`7h of 8h`)
   across a couple of weeks. If the actual daily totals cluster below the
   stated norm, mention the discrepancy rather than encoding it as the target.
7. **path_map** — leave empty. It earns its entries over time (below).

## Rotating tickets

Planning and release tickets are commonly recreated each period — `Planning
June 2026`, `Planning July 2026`. Pinning a key freezes the plan to a ticket
that quietly stopped being the right one, and the mistake is easy to miss
because the entry still logs successfully.

So resolve these by summary at run time. Substitute `{month}` and `{year}` for
the period being planned — in the project's language, matching how the summary
is actually written — and search:

```
/rest/api/3/search/jql?jql=project=PROJ AND summary~"Planning July 2026"&fields=summary,status
```

If nothing matches, say so and ask rather than falling back to last period's
ticket. A missing planning ticket usually means it has not been created yet,
and logging into the previous month's is exactly the misattribution this skill
is supposed to prevent.

## Maintaining the path map

The path map is what stops the same question recurring every week. When a
commit's paths do not match the ticket in its message and the developer says
which ticket it really belongs to, offer to record the mapping.

Keep entries at the directory level that actually corresponds to a ticket's
scope. `src/labels/**` is useful; `src/labels/components/sale-label.tsx` is
too narrow to match anything next time, and `src/**` is too broad to mean
anything.

Treat the map as a hint, not a verdict. It reflects which ticket owned an area
at the time it was written, and areas change hands. When the map and the
developer disagree, the developer is right — and that is a signal to update the
entry.

**Always check the mapped ticket's status before proposing it.** Entries go
stale the moment a ticket closes, and a closed ticket is the single most likely
thing a stale map will hand you. When the map points at a Done or Closed
ticket, do not propose it — say which ticket used to cover that area and ask
which one covers it now, then update the entry with the answer. That turns the
staleness into a one-line question instead of a wrong row in the timesheet.

## Multiple repos

One config per repo. When a day spans several repos, run the collection script
in each and merge the results before proposing hours — the day's target applies
to the developer, not to any one repository.
