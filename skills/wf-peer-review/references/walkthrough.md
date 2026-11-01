# Route through a PR

Fill this for the PR at hand: every step lists **this PR's actual files** (grouped by layer, with
`+/-` line counts) and one or two sentences on what to look at in *these* files. Skip a step only when
the PR has no files for it, and say so in one line.

The order: first the idea of the solution and how its parts interact, then the implementation and how tests cover
the risks. Formal rules belong to linters, typing and automated tests — review time goes to decisions
and risks those checks do not cover. A team PR guide in the local overlay (`company/pr-guide.md`),
when present, wins where it differs.

## 1. Description and ticket (≈5 min)

Read the description, then the ticket. Write down the acceptance criteria as your own checklist —
you tick them off in step 10. Note what the description claims was tested.

## 2. Module and protocol

Before any file: how the module works as a whole. What goes in and what comes out, which artifacts
it produces, where data is stored, whether there is monitoring, which libraries are new, whether the
protocol is documented in OpenAPI and under which operation. Then the interaction: which components
take part and what each is responsible for; who calls whom, with which arguments, and what comes
back. Does that interaction match the requirements and the project's architecture? A wrong idea here
makes every later step moot — say so first.

## 3. Map of changes

The file list grouped by layer, biggest first. Mark noise explicitly ("skim"): lock files, generated
catalogs, snapshots, moved files with no content change. The centre of gravity is where review time
goes.

## 4. Contract

Types, API clients / provider methods, schemas, props of shared components. What changed in the
shape of data, and **who else consumes it** — the agent lists the importers of each changed symbol.
A changed field with an unhandled consumer is the classic miss.

## 5. Logic — core / shared

Pure functions, selectors, hooks, stores. Read each changed function whole, not just the hunk.
Check the edges: empty list, `null`/missing field, error response, double call.

## 6. UI

Components and screens: every state (loading, empty, error, disabled, offline), navigation in and
out, back behaviour, accessibility labels. Compare with the sibling platform when one exists.

## 7. i18n

New strings → present in every catalog that extracts that path; no hardcoded user-facing text;
count-dependent grammar handled the project's way.

## 8. Tests

For each test: would it fail on the old code? Are the acceptance criteria from step 1 covered? Are
mocks hiding the very behaviour that changed? Do the tests cover the risks named in step 2?

## 9. Config, dependencies, deletions

New packages and why · changed scripts or build config · deleted code and who used it (search for it).

## 10. Back to the acceptance criteria

For each criterion from step 1: where in the diff it is implemented, or that it is not.
