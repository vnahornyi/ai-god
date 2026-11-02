# E6c — the catalogue got slow after 2.4.0

Node 24 project in `src/` (no dependencies). `visibleProducts` merges the catalogue pages and removes
duplicates; `src/make-pages.js` builds pages shaped like the API's (about 20,000 products).
`CHANGELOG.md` lists the last two releases.

**Bug report:** "Since 2.4.0 opening the full catalogue freezes for about two seconds on mid-range
phones. In 2.3.0 it was instant." Product ids must stay unique and in the order they first appear.

Find the cause and fix it. You may add tests and scripts (`node --test`, `node <file>`). Do not add
dependencies.
