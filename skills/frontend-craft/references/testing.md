# Testing — Jest + Testing Library

A test's job is to fail when behavior breaks and stay silent when implementation changes. A suite that fails on every refactor gets muted, and a muted suite protects nothing.

Match the project's existing setup and conventions before importing anything from here.

## Contents
- [What to test at which level](#what-to-test-at-which-level)
- [The core rule](#the-core-rule)
- [Queries](#queries)
- [Async](#async)
- [What to assert for each state](#what-to-assert-for-each-state)
- [Mocking](#mocking)
- [Snapshots](#snapshots)
- [React Native specifics](#react-native-specifics)
- [Test smells](#test-smells)

## What to test at which level

| Level | Test here | Don't |
|---|---|---|
| **Pure functions** (mappers, formatters, validators, reducers) | Everything, including edge cases. Cheapest and most valuable tests in the codebase | — |
| **Hooks** | Only if they hold non-trivial logic, via a component or `renderHook` | Test a hook that just wraps a query call |
| **Components** | Behavior a user can observe: what renders in each state, what happens on interaction | Internal state, function call counts, prop plumbing |
| **Screens/integration** | The flow through several components with the network mocked. Highest confidence per test | — |
| **E2E** | A handful of critical paths only — they're slow and flaky at scale | Recreate unit coverage |

Prefer fewer, higher-level tests. One integration test covering a screen's load → error → retry → success catches more real regressions than twenty shallow component tests.

## The core rule

Test what the user experiences, not how the component is built. Concretely: query by what's on screen, assert on what's on screen.

```tsx
// brittle — breaks on any refactor, proves nothing about behavior
expect(wrapper.find('PriceLabel').props().discounted).toBe(true);

// resilient — this is the actual requirement
expect(screen.getByText('$8.00')).toBeVisible();
expect(screen.getByText('$10.00')).toHaveStyle({ textDecorationLine: 'line-through' });
```

If you can't write the assertion without reaching into internals, the requirement probably isn't visible to a user — which is itself worth questioning.

## Queries

Priority order — the higher you query, the more the test proves:

1. `getByRole` (web) / `getByRole` + accessible name (RN) — also verifies accessibility
2. `getByLabelText`, `getByPlaceholderText`
3. `getByText`
4. `getByTestId` — last resort, for things with no accessible representation

A `testID` added purely to make a test pass is a hint that the element isn't accessible. Fixing the label often fixes both.

`getBy` throws when absent, `queryBy` returns null (use it for absence assertions), `findBy` awaits appearance.

## Async

```tsx
// wait for the thing you care about
expect(await screen.findByText('Order confirmed')).toBeTruthy();

// or for a state change on existing content
await waitFor(() => expect(screen.queryByTestId('spinner')).toBeNull());
```

Never `await new Promise(r => setTimeout(r, 500))` — it's slow when it works and flaky when it doesn't. Always wrap state-changing interactions so React can flush; use `userEvent` where the project has it.

## What to assert for each state

Mirror the state matrix from `states-and-platform.md` — the states that go untested are the ones that ship broken:

- **Loading**: indicator present; content absent
- **Success**: the actual values rendered, including formatting (currency, dates) — formatting bugs are common and invisible in snapshots
- **Empty**: empty message shown, list not rendered
- **Error**: message shown, retry present; pressing retry re-issues the request
- **Interaction**: pressing the primary action calls the right thing with the right payload, and the button is disabled while pending (this catches the double-submit bug)

When the project lets you add tests without asking, add a regression test for every bug fixed; otherwise list it as proposed in the report. It should fail against the old code. If it passes without the fix, it isn't testing the bug.

## Mocking

- **Best case: no mock at all.** If the UI is split into a composer and providers (`composition.md`, rung 3), render the composer inside a fixture provider and hand it data directly. No network, no timing, no mock to keep in sync — and the thing under test is exactly the thing that ships.
- **Otherwise mock at the network boundary** (MSW or the fetch/client layer), not at the module boundary. Mocking your own modules means the test passes while the real wiring is broken.
- Mock time (`jest.useFakeTimers`) rather than waiting on it; reset in `afterEach`.
- Every mock resets between tests. Shared mutable state between tests produces order-dependent failures that appear as "flaky CI".
- Navigation, analytics, and native SDKs: mock through the project's existing facade rather than inventing a new mock per test file.

## Snapshots

Useful narrowly, harmful broadly. A full-screen snapshot fails on every change and gets `-u`'d without reading, which is worse than no test.

- Small, focused snapshots for components whose whole point is markup/style output.
- Never snapshot a screen or anything containing dates, ids, or random values.
- If updating a snapshot, read the diff. A snapshot updated without reading is a regression waved through.
- **Watch the file size as you write, not at review.** A `.snap` in the tens of thousands of lines — a block rendered across theme × language × state — is unreviewable by construction, dominates the PR's diff, and will conflict on every unrelated style change. Two or three cases of a *part*, with everything else asserted by query, buys the same confidence.
- A snapshot cannot prove the absence of something you never rendered. A control hidden behind a new condition needs an explicit `queryByText(...)` → `toBeNull()` case; the snapshot of the screen without it looks identical to the snapshot of a screen where the feature is broken.

## React Native specifics

- `@testing-library/react-native` with the RN Jest preset; check `jest.config` for the project's setup (some repos have a separate native config).
- Assert on text and accessibility labels, not on style objects, except where the style *is* the requirement.
- `fireEvent.press` rather than click.
- Native modules need mocks in the jest setup file — add there, not per-test.
- Platform-specific branches: test both with `jest.mock('react-native/Libraries/Utilities/Platform')` or by testing the extracted pure logic separately, which is usually cleaner.

## Read the harness before you believe it

A test result is evidence about the code *and* the environment, and the environment is the half nobody reads. Two failure modes, both of which cost an afternoon if you take the result at face value:

**A red suite that isn't about the code.** Generated artifacts — compiled i18n catalogs, generated schemas, generated icon components — are usually gitignored, so they are whatever your last command left behind. A snapshot diff showing the wrong *language*, a type error in a generated file, a mismatch in a fixture nobody edited: regenerate first (the project has a script), then look again. Never `-u` a snapshot to make that go away — you would be committing your stale environment into the repo. And never report it as the author's failing test until you've regenerated.

**A green test that never ran your code.** Setup files can neutralize the primitive you're testing. A repo that does `jest.spyOn(React, 'useEffect').mockImplementation(() => {})` globally — a real and not-rare choice in snapshot-heavy native suites — means no passive effect runs in any test: your effect assertion doesn't fail, it never executes, and `waitFor` just times out on zero calls while the "does nothing" test passes for the wrong reason. Same for a hook the project disables under a QA/test env flag. Before writing a test that depends on an effect, timer, or focus event, grep the setup files for the primitive; when the repo stubs one, it almost always ships the escape hatch too (`globalThis.useEffectSpy?.mockRestore()`), and other test files already show where to call it.

Corollary for mock factories: `jest.mock(path, () => { const { useEffect } = require('react'); ... })` captures whatever is installed **when the factory is evaluated** — including a global stub — so a later `mockRestore()` never reaches your copy. Hold the namespace and call through it (`ReactActual.useEffect(...)`) so the restore applies.

The general rule: when a result surprises you, the next step is to make the harness prove it ran your code — one log line inside the callback under test — not to start editing the code.

**A regression test that never failed proves nothing.** For a bug fix, run the new test against the pre-fix code — undo only your fix lines, or run it in a temporary worktree at `HEAD`; never `git stash`, which also hides the developer's other uncommitted work — and watch it fail for the reason you claim. When you force the red by editing code or a fixture instead, diff against the untouched copy to prove the edit is what made it fail. A test written after the fix, from the same mental model as the fix, agrees with it by construction; the red run is the only evidence that it pins the defect rather than the implementation.

**When the harness disables the mechanism your fix depends on, the fix is untested by construction.** If the project's test env short-circuits the loading hook, the effect, the timer or the request layer, then a fix keyed to `isLoading` is inert in every test: the suite stays green whether the fix is there or not.

**Correctness picks the production signal; the harness only picks where you assert it.** The tempting move — swap to whatever value the test store can set, so the suite stays green and the snapshots don't churn — is how a weaker rule ships: you end up asserting an entity's identity because the harness can model that, when the property you actually needed was that *this request* completed. Decide the signal from the invariant first. Then, if the harness cannot exercise it, extract the decision into a pure function and test it there, seed the component so the harness's own state stays representative, and say plainly in the PR that the lifecycle is not covered by tests. A mock of the disabled primitive is the last resort: it tests the mock's shape more than the behaviour.

Untestable-by-harness is a fact to disclose, not a constraint to design around.

## Test smells

- Test name says "works correctly" → the test doesn't state a requirement. Name it "shows retry when the request fails".
- Test needs a comment to explain what it's testing → restructure it.
- Heavy `beforeEach` setup shared by tests that need different things → each test should be readable on its own.
- Asserting on `toHaveBeenCalledTimes` for internal functions → implementation coupling.
- Test passes when the feature is deleted → it's asserting nothing.
- Tautological assertion — the expected value is computed by the code under test or copied from its implementation (`expect(format(x)).toBe(format(x))`, a mock asserted to return what it was told to return) → it agrees by construction. Write the expected value as a literal from the requirement.
- More lines of mock than of test → the unit under test has too many dependencies; that's a design signal, not a testing problem.
