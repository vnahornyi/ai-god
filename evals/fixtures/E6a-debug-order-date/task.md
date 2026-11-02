# E6a — order history shows the wrong day

Node 24 project in `src/` (no dependencies). The app shows order history grouped by day for customers
in Ukraine; the shop and its customers are in the `Europe/Kyiv` time zone.

**Bug report (from support):** "A customer placed an order at half past midnight on 1 November, but
the history shows it under 31 October. It seems to happen only for orders placed shortly after
midnight." Sample data is in `src/orders.json`; order `o-103` is the customer's order.

Find the cause and fix it. You may add tests (`node --test`). Do not add dependencies.
