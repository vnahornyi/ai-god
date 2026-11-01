# Contracts and backend surface

Read this when the task touches an API, a schema, storage, a migration, a worker, an integration, or a cache — i.e. whenever the plan cannot be executed purely inside the UI layer.

The rule that orders everything below: **settle the contract before the implementation.** A plan that describes screens in detail and leaves "the API will return the reviews" as a sentence has deferred the only part that can invalidate the whole estimate. Contract first, UI second — in the plan and in the review.

## Reconstruct the intended protocol

Before proposing any change, write down who is who:

- the **producer** and the **consumers** (name every platform: web, mobile, admin);
- the **authoritative owner** of each fact in the payload;
- where **validation** happens, where **persistence** happens;
- the **source of truth for the contract itself** — `openapi.yaml`, a generated client, hand-written types, or docs — and which of those are generated from which;
- what is **current**, what is **intended**, what is a **migration state**, and what is explicitly **not supported**.

If any of these can't be answered from the repo or the docs, that is a dependency on someone else's team. Say so in the plan's risks section — it is the most common reason a frontend estimate doubles.

## Request and response shape

Check, and state the answer in the plan:

- status codes and error shapes, including the ones the UI must distinguish;
- required vs optional vs nullable, per **lifecycle state** — draft, unpublished, imported, legacy and published records do not share a shape. Do not tighten a shared type to the published-only case;
- enum changes: an added value ships to old clients that don't know it. Every client-side `switch` over that enum needs a defined default;
- pagination, sorting, filtering, and whether the client or the server owns each;
- permissions, auth, tenant/role scoping;
- backwards compatibility: is there a deployed client that will keep sending the old shape?

**Overfetching is a design finding.** Fields the consumer doesn't need — internal notes, permissions, operational flags, other users' data, payment or personal fields — end up in the bundle, in devtools, in a crash report, in a log. Ask what each new field is for.

**`''` vs `null` on the way out.** A cleared input yields `''`; servers usually validate one and not the other. Decide the normalisation point once, and verify the server accepts what the client sends.

## Storage and migrations

- ownership, nullability, uniqueness, foreign keys, indexes the new query actually needs;
- does this need a **backfill**, and what does the app show for rows that haven't been backfilled yet;
- is the change **destructive** — dropped column, tightened constraint, changed enum — and what is the rollback;
- transaction boundaries, and what a partial failure leaves behind;
- retention and lifecycle for anything personal.

Only propose a different table or storage shape when the change creates a concrete integrity, performance, privacy or maintainability problem. "Would be cleaner" is not a plan item.

## Generated and documented contracts

Generated types, OpenAPI, fixtures and mocks are **claims to verify, not proof**. They are as stale as the last generation run. Confirm against runtime behaviour, and name in the plan:

- the exact generation command and when in the sequence it runs;
- which generated files must not be hand-edited;
- whether the docs (Outline/Confluence) also have to be updated, and by whom.

## Workers, jobs, integrations

When the task adds or touches one:

- registration, scheduling, queue/routing — is it a timer, a one-off job, or a consumer? The rules differ;
- retry, ack/nack, **idempotency and dedupe** — what happens when the same message arrives twice;
- failure visibility: where does a silent failure show up, and does anyone see it;
- for outbound integrations: timeouts, rate limits, idempotency keys, callback verification, and what a partial failure means for the user;
- **no secrets, tokens, payment or personal data in the logs**, while keeping enough context to debug;
- latency: a synchronous external call in a user-facing path is a product decision, not an implementation detail.

## Cache, search, feeds

- invalidation: what triggers it, and what the user sees in the window before it lands;
- cache keys — do they include everything that varies (locale, role, tenant, feature flag)?
- fan-out and batching cost, and query-in-a-loop patterns;
- reconciliation between the cache/index and the authoritative store.

## What the plan must carry

For a task with a backend surface, the plan's contract section is not done until it names:

1. the endpoint(s), method, request and response shape, with lifecycle-specific nullability;
2. the error cases the UI distinguishes, and what each renders;
3. the migration/backfill, if any, and its rollback;
4. the generation commands and the order they run in;
5. the dependency on another team, with the concrete thing being waited on;
6. what regresses on **every** consuming platform, not just the one in scope.
