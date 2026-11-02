# E6b — a price shows on the wrong product, and the test is flaky

Node 24 project in `src/` (no dependencies). `loadPrice` fetches a product price and caches it; the
product screen reads `cachedPrice` when the customer switches between products.

**Bug report:** "If I switch from shoes to socks quickly, the shoes sometimes show the socks price.
Hard to reproduce." The team also says `src/price-cache.test.js` fails "now and then" in CI and
passes when rerun.

Find the cause and fix it. You may change the test and add tests (`node --test`). Do not add
dependencies.
