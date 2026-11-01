# Reading Jira and Tempo from the browser

## Contents

- The async pattern
- Ticket metadata, several at once
- Worklogs per ticket per day
- Two things that will mislead you
- The Tempo timesheet


The developer is already signed in, so a same-origin `fetch` from any page on
the Jira host carries their session. That is dramatically faster than driving
the UI, and it returns exact numbers instead of numbers read off a screenshot.

You need four browser capabilities: list/open tabs, navigate, run JavaScript in
the page, and read page text. The browser must be the developer's own signed-in
one, not a clean sandbox — a fresh profile has no Jira session. Which tools
provide them, and how to load them, is in your runtime adapter. With no
signed-in browser tool available, say so and ask the developer to paste the
timesheet instead of guessing.

Navigate one tab to the Jira host. Keep a second tab for the Tempo timesheet so
you do not lose it while paging through API calls.

## The async pattern

A JS tool that does not await promises — an `async` IIFE returns `{}`. Park
the result on `window` and read it in a second call:

```js
// call 1
window.__r = 'pending';
(async () => {
  const r = await fetch('/rest/api/3/issue/PROJ-123?fields=summary,status,timetracking',
                        { headers: { Accept: 'application/json' } });
  window.__r = JSON.stringify(await r.json());
})();
'go'
```

```js
// call 2
window.__r
```

Output gets truncated around a few thousand characters. Return compact lines
rather than raw JSON, and slice long lists across several calls:

```js
window.__r.split('\n').slice(0, 20).join('\n')
```

## Ticket metadata, several at once

```js
window.__r = 'pending';
(async () => {
  const keys = ['PROJ-1','PROJ-2','PROJ-3'];
  const out = [];
  for (const k of keys) {
    const r = await fetch(`/rest/api/3/issue/${k}?fields=summary,status,assignee,timetracking,description`,
                          { headers: { Accept: 'application/json' } });
    const j = await r.json();
    const t = j.fields.timetracking || {};
    const e = t.originalEstimateSeconds || 0, s = t.timeSpentSeconds || 0;
    out.push([
      k, j.fields.status.name,
      j.fields.assignee ? j.fields.assignee.displayName : '-',
      'est ' + (e ? (e/3600).toFixed(1) + 'h' : 'NONE'),
      'spent ' + (s/3600).toFixed(2) + 'h',
      e && s > e ? 'OVER +' + ((s-e)/3600).toFixed(2) + 'h' : 'ok',
      j.fields.summary.slice(0, 60)
    ].join(' | '));
  }
  window.__r = out.join('\n');
})();
'go'
```

## Worklogs per ticket per day

```js
window.__r = 'pending';
(async () => {
  const keys = ['PROJ-1','PROJ-2'];
  const from = '2026-07-20', to = '2026-07-26';
  const m = {};
  for (const k of keys) {
    const r = await fetch(`/rest/api/3/issue/${k}/worklog?maxResults=500`,
                          { headers: { Accept: 'application/json' } });
    const j = await r.json();
    (j.worklogs || []).forEach(w => {
      const d = w.started.slice(0, 10);
      if (d >= from && d <= to) {
        const key = d + ' | ' + k;
        m[key] = (m[key] || 0) + w.timeSpentSeconds;
      }
    });
  }
  window.__r = Object.keys(m).sort()
    .map(k => k + ' | ' + (m[k]/3600).toFixed(2) + 'h').join('\n');
})();
'go'
```

Individual worklogs also carry `comment`, `id`, `created` and `updated`, which
are worth pulling when auditing — a cluster of entries all created within a
couple of minutes is a retroactive backfill, and `updated` timestamps show when
something was last touched.

## Two things that will mislead you

**Worklog `author` is often the Tempo app, not the person.** Entries created
through Tempo come back with `"displayName": "Timesheets by Tempo …"` and
`accountType: "app"`. Filtering by `worklogAuthor = currentUser()` in JQL
therefore returns nothing, and filtering the REST response by accountId drops
most of the developer's entries. Do not use author as a filter.

**Shared tickets carry everyone's time.** Release tickets, planning tickets and
similar buckets aggregate the whole team. The REST worklog endpoint gives you
the ticket total, with no reliable way to isolate one person. Whenever a shared
ticket is in play, read that person's figure off the Tempo timesheet instead.

## The Tempo timesheet

Navigate to the configured URL with `{date}` replaced by any date in the target
week, then wait a few seconds and take a screenshot — the app renders in an
iframe, so page-text extraction returns nothing and a screenshot taken too early
catches a blank page.

```
navigate   → .../tempo-app#!/my-work/week?date=2026-07-22&type=LIST
wait       → 3 s
screenshot
```

The view gives you what the API cannot: the developer's own per-day totals, the
day header (`7h of 8h`), the week header (`36h 15m of 40h`), and one card per
entry with ticket key and duration. Page across weeks by changing the date in
the URL rather than clicking the arrows — it is fewer round trips and you keep
the exact week you asked for.

Columns can overflow below the fold when a day has many entries. Cross-check
each column's cards against the day header total; if they do not add up, an
entry is hidden and you need to scroll that column or fall back to the API for
that ticket.
