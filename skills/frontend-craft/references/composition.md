# Composition: compound components and functional style

This is the house style. When a component has more than one moving part, this is the default shape and deviating from it needs a reason.

The payoff is concrete: the call site becomes a readable description of the UI, adding a part doesn't touch existing parts, and when something breaks you can see from the JSX which brick is responsible.

**Read this as a shape, not as a filesystem.** What matters is the separation — who owns state, who owns structure, where pure logic lives, where data crosses a boundary. The folder names, layer taxonomy, and framework APIs below are one concrete rendering of that shape; a project with a different architecture expresses the same separation with its own names. **Adopt the project's existing structure and idiom every time.** Introducing a foreign taxonomy into a codebase that already has one is a worse outcome than any benefit this file describes.

Examples here are React DOM with a Next-style server/client split, because that's where the idiom was worked out. In React Native, in a plain SPA, or with a different data layer, translate: the same root/parts/context split applies, `Suspense` and async boundaries are whatever the project uses for loading, and there are no server components.

## Contents
- [The ladder](#the-ladder)
- [Rung 1: plain props](#rung-1-plain-props)
- [Rung 2: compound components](#rung-2-compound-components)
- [Anatomy](#anatomy)
- [Slots](#slots)
- [Rung 3: composer and providers](#rung-3-composer-and-providers)
- [Rung 4: lifted state behind a contract](#rung-4-lifted-state-behind-a-contract)
- [When not to climb](#when-not-to-climb)
- [Functional style](#functional-style)
- [Selectors: derive, never store](#selectors-derive-never-store)
- [Boundaries: parse once, at the edge](#boundaries-parse-once-at-the-edge)
- [File and naming conventions](#file-and-naming-conventions)

## The ladder

Composition is a ladder, not a style choice. Each rung answers a specific kind of friction, and each one buys flexibility with indirection — a reader now has to look in one more place to understand what renders.

| Rung | Shape | Climb when |
|---|---|---|
| **1** | Plain props | Default. Start here always |
| **2** | Compound components | The component grows a prop per layout shape, or callers keep wanting an arrangement the props didn't anticipate |
| **3** | Composer + providers | The same UI must render data from swappable, deferred, or fake sources |
| **4** | Lifted state behind a contract | State or actions have to cross a component boundary, and intermediate layers are just forwarding callbacks |

**Climb on demonstrated friction, never on principle.** "This should be a compound component for consistency" is not a reason. Neither is "we might need another data source later". The cost is asymmetric: climbing is easy on paper and tedious to undo once callers depend on the shape, so the cheapest position is always the one you're already on.

The corollary matters as much: **when the friction is real, climb properly rather than patching.** A fifth boolean prop, a `renderX` callback, or one more callback threaded through three layers are all the same mistake — paying the cost of the higher rung without getting its benefit.

## Rung 1: plain props

Reusable UI as a function of its props. A badge, an avatar, a price label, a button. Most components live here permanently and that is a good outcome, not a missing refactor.

Signals you are still fine here: the prop list is short, every prop is data rather than a layout switch, and no caller has asked for an arrangement you can't express.

**One concept, one prop.** When a shared component already owns a concept — how it validates, how it formats, how it sorts — and one caller needs a variation, **widen the existing prop instead of adding a sibling next to it.** `pattern` plus a new `normalizeValue` means two props that only mean something in combination, and every future reader has to learn how they interact; `validate?: RegExp | ((value: string) => boolean)` is the same capability as one idea, and existing call sites migrate by renaming. A union that keeps the common form declarative (`validate={DIAL_FORMAT}`) and admits the uncommon one (`validate={looksLikeEmail}`) costs one `instanceof` at the point of use and nothing at the ten call sites that never needed the escape hatch.

The tell that you are adding a sibling rather than widening: the new prop is useless on its own, and its doc comment has to explain the other prop.

## Rung 2: compound components

The problem they solve: a component that grows props to control its internals — `showHeader`, `headerTitle`, `modalContent`, `isLoading`, `renderFooter` — becomes a configuration language nobody can read. Every new requirement adds a prop, every prop adds a branch, and the component ends up owning decisions its callers should own.

Compound components invert that. The root owns *state*; the caller owns *structure*.

```tsx
// The call site describes the UI. Nothing is configured through flags.
<SizeGuide>
  <SizeOption headerSlot={<SizeGuide.Button />} />
  <ColorOption />
  <SizeGuide.Modal>
    <Suspense fallback={<SizeGuide.Loading />}>
      <SizeGuide.Content gridId={product.gridId} />
    </Suspense>
  </SizeGuide.Modal>
</SizeGuide>
```

Compare with the props-driven version — `<SizeGuide showButton modalContent={...} isLoading={...} />` — which cannot express "put the button inside the size option's header" at all.

**Reach for this when:** parts must be arranged flexibly, several parts share state, some parts are optional, or parts need to sit at different depths in the tree. In practice that is most non-trivial UI: modals, menus, headers, selects, filters, cards with variable sections, anything with a loading/empty/error part.

## Anatomy

Four rules make it work. Break any one and it degrades into props-drilling with extra steps.

**1. The root owns state and provides context. Nothing else holds it.**

```tsx
"use client" // only where the framework has a server/client split

import { createContext, use, useState } from "react"

type ContextType = {
  isOpened: boolean
  setIsOpened: (isOpened: boolean) => void
}

const SizeGuideContext = createContext<ContextType>(undefined!)

export const SizeGuide: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [isOpened, setIsOpened] = useState(false)

  return (
    <SizeGuideContext value={{ isOpened, setIsOpened }}>
      <Dialog.Root open={isOpened} onOpenChange={setIsOpened}>
        {children}
      </Dialog.Root>
    </SizeGuideContext>
  )
}
```

`createContext<ContextType>(undefined!)` is deliberate: there is no sensible default, and a part rendered outside its root is a programming error that should crash loudly during development rather than silently render a fallback. Don't add a `useX must be used within X` guard hook unless the component is published for outside consumers.

React 19: `<Context value={}>` directly (no `.Provider`), and `use(Context)` to read. On React 18, use `<Context.Provider value={}>` and `useContext` — check the project's React version before writing either.

**2. Parts take no props for anything the root already knows — and the root only "knows" what it owns.**

The rule is about *shared* state, not about routing data through the root. Context carries what the root holds: its state, and values two or more parts read. **A value exactly one part consumes is that part's prop.** A root that accepts a bag of presentational data purely to redistribute it through context is props-drilling with extra steps and a longer path: the caller still passes every field, the part still reads every field, and now neither end can see the other.

The check before you write the context type, field by field: *how many parts read this?* Zero — delete it. One — it belongs to that part's props. Two or more, or it changes over the component's life — context.

If **every** field fails that check, the honest conclusion is that you are on rung 1 with a namespace, not rung 2. That is a fine place to be: `Object.assign` a root that renders only the shell (press handling, layout, a style override) onto parts that each take their own data. You get the arrangement freedom that motivated the climb without inventing state nobody owns. Keep a context only when a part genuinely cannot be handed the value — it sits at an arbitrary depth, or the value is state the root mutates.

```tsx
export const SizeGuideButton: React.FC = () => {
  const { setIsOpened } = use(SizeGuideContext)

  return (
    <Dialog.Trigger asChild>
      <Button variant="link" onClick={() => setIsOpened(true)}>
        <Trans>View Size Guide</Trans>
      </Button>
    </Dialog.Trigger>
  )
}
```

A part with `React.FC` and no props type is the healthy signal. If a part needs a prop, it should be data the root genuinely can't know — an id, a piece of content.

**3. One part per file, assembled in the barrel.** Not "one file with all the parts and an `Object.assign` at the bottom" — that file grows with every part, and the reader who wants `X.Price` has to scroll past eight siblings to find it. The folder is the component; the barrel is its API.

```
size-guide/
├── index.ts                  ← the only place the compound is assembled
├── size-guide.tsx            ← root + context
├── size-guide-modal.tsx
├── size-guide-content.tsx
└── size-guide-loading.tsx
```

```ts
// index.ts
import { SizeGuideContent } from "./size-guide-content"
import { SizeGuideLoading } from "./size-guide-loading"
import { SizeGuideModal } from "./size-guide-modal"
import { SizeGuide as SizeGuideRoot, SizeGuideButton } from "./size-guide"

export const SizeGuide = Object.assign(SizeGuideRoot, {
  Button: SizeGuideButton,
  Modal: SizeGuideModal,
  Content: SizeGuideContent,
  Loading: SizeGuideLoading,
})
```

The barrel is the component's public API. Everything else in the folder is internal — a deep import from outside is a coupling bug. (If the project doesn't use barrels, keep the assembly in one designated file and the principle holds.)

**4. Every async part ships with its own `Loading` part.** Pairing `<X.Content>` with `<X.Loading>` keeps the loading state next to the thing that loads, instead of in a distant boolean — whether that pairing is a `Suspense` boundary, a query hook's `isLoading`, or the project's own async primitive.

Part names are structural, not descriptive: `Root`, `Button`, `Trigger`, `Modal`, `Panel`, `Content`, `Item`, `Loading`, `Empty`. `X.Content` reads better than `X.SizeGuideContentBlock`.

## Slots

When a part must render somewhere that isn't a descendant of the compound root — inside a third-party component, inside a sibling's header — pass it as a node prop rather than restructuring the tree:

```tsx
<SizeOption headerSlot={<SizeGuide.Button />} />
```

Name them `*Slot`. This keeps the "who owns structure" answer with the caller, which is the whole point. Where a framework splits rendering environments (server/client components), a slot is also how already-rendered content crosses that boundary without dragging the receiving component across it.

Slots are not an escape hatch for arbitrary configuration — a component with four slots and three booleans should have been a compound component.

## Rung 3: composer and providers

Climb here when the same UI has to render data from more than one source: a live query and an archived one, data that loads eagerly and data that's deferred, real data and a fixture in tests. Rung 2 doesn't help — the parts are fine, it's the *supply* that varies.

Split the piece in two along a contract:

```ts
type QuotesContextValue = {
  state: { quotes: readonly QuoteSummary[] }
  meta: { emptyLabel: string; showStatusBadge: boolean }
}
```

`state` is the data to render. `meta` is presentation that legitimately depends on which source it came from — an archived list wants a different empty label and no status badge. Keeping `meta` in the contract is what stops the composer from growing `isArchived` branches.

**The composer** reads the contract and builds the markup out of rung-2 primitives. It knows nothing about where the data came from:

```tsx
export const QuotesListComposer: React.FC = () => {
  const { state, meta } = use(QuotesContext)

  if (!state.quotes.length) return <EmptyState label={meta.emptyLabel} />

  return (
    <Item.List>
      {state.quotes.map((quote) => (
        <Item.Root key={quote.id}>
          <Item.Content>{quote.name}</Item.Content>
          {meta.showStatusBadge && <Item.Badge status={quote.status} />}
        </Item.Root>
      ))}
    </Item.List>
  )
}
```

**Providers** are interchangeable implementations of that contract — `ActiveQuotesProvider` runs a live query, `ArchivedQuotesProvider` loads deferred, `FixtureQuotesProvider` takes quotes as a prop. Swapping the source is swapping the wrapper:

```tsx
<Tabs.Panel value="active">
  <ActiveQuotesProvider>
    <QuotesListComposer />
  </ActiveQuotesProvider>
</Tabs.Panel>
```

The fixture provider is the payoff people underrate: it makes the composer testable with zero network mocking — render it inside a fixture provider and assert on output. See `testing.md`.

## Rung 4: lifted state behind a contract

Climb here when state or actions must cross a component boundary and the layers in between exist only to forward callbacks. The symptom is an `onUpdateNote` threaded through three components that never call it.

Same contract shape as rung 3, plus actions:

```ts
type NotesContextValue = {
  state: { notes: Note[] }
  actions: {
    addNote: (content: string) => void
    updateNote: (noteId: string, content: string) => void
    deleteNote: (note: Note) => void
  }
}
```

One provider owns the state and the data layer; every intermediate layer drops a prop, and any component under the provider can act — including ones that aren't in the original subtree, like a toolbar button in a header.

The rule that keeps this from degenerating: **layout stays a pure function of its props.** The provider holds state and actions; the components under it render what the contract gives them. Once a "layout" component starts doing its own fetching or holding its own copy of the state, you have two sources of truth again.

## When not to climb

Reasons that are **not** sufficient to move up a rung:

- **Uniformity.** "The other components in this folder are compound" is a stylistic argument, not friction.
- **A source you might need later.** One data source with no concrete alternative in sight stays plain. Speculative providers are the most common wasted climb.
- **State that never leaves the component.** Local stays local.
- **A leaf with one job** — a badge, an avatar, a price label. Never manufacture a context for it.
- **One valid arrangement, no optional parts.** `children` is simpler than a namespace of parts nobody rearranges.

And two signals you climbed to the wrong place rather than too far:

- **The root's state is also needed by siblings outside the compound** — it isn't the root's state. That's rung 4, not rung 2.
- **More than ~7 parts** — the component is probably two components.

## Functional style

The style throughout: pure functions, immutable data, computation over storage, and early returns instead of nesting.

```ts
export const selectProductSizes = (sizeGrid: SizeGrid) => {
  const visibleTypes = new Set(sizeGrid.visibleSizeTypes)
  const globalSizes = new Set<string>()

  const sizesByType = sizeGrid.sizes.reduce<Record<string, SizeEntry[]>>(
    (acc, entry) => {
      globalSizes.add(entry.sizeGlobal)

      if (visibleTypes.has(entry.sizeType)) {
        acc[entry.sizeType] ??= []
        acc[entry.sizeType].push(entry)
      }

      return acc
    },
    {}
  )

  return { globalSizes: Array.from(globalSizes), sizesByType }
}
```

What this demonstrates, and what to reproduce:

- **Pure and named.** Takes data, returns data. No hooks, no I/O, no React. Testable with a single `expect`.
- **`Set`/`Map` for membership and lookup.** `array.includes()` inside a loop is O(n²) and reads worse.
- **`reduce` with an explicit accumulator generic**, so the return type is inferred correctly rather than asserted.
- **Local mutation inside a pure function is fine** — the accumulator never escapes. Purity is about the function's observable behavior, not about banning `push`. Mutating an *argument*, props, or state is the thing that's forbidden.
- **`ReturnType<typeof fn>`** exported as the type, instead of maintaining a hand-written duplicate that will drift.

Also standard here:

- **Early return over nesting.** `if (!data) return <Empty />` at the top, then the main path unindented.
- **Type guards** (`function isX(value: unknown): value is X`) rather than `as`.
- **Exhaustive unions** — a `switch` with a `never` fallthrough so a new variant is a compile error, not a blank screen.
- **A blank line before `return`.** Small thing, consistent throughout the codebase.

Skip the FP ceremony: no `fp-ts`, no `pipe`/`compose` utilities, no Either/Task monads, no point-free style. The value is in purity and immutability, not in the vocabulary.

### FP toolbox: what we take, what we skip

The usual "FP in JavaScript" curriculum lists a dozen techniques. They are not equally worth it in a
TS/React codebase read by a team under deadline. Take the ones that make code testable and
predictable; skip the ones that only change notation.

**Take:**

- **No hidden inputs.** A pure function's result depends only on its arguments. `Date.now()`,
  `Math.random()`, a mutable module variable, the current locale, a feature flag read inside —
  each is a hidden input that makes the function untestable without mocks. Pass them in:
  `isSlotExpired(slot, now)` instead of reading the clock inside. The caller at the edge (hook,
  handler) reads the world; the function stays pure.
- **Declarative collection work.** `filter`/`map`/`reduce`/`some`/`find` over hand-written index
  loops when the intent is a transformation. Keep a `for…of` when the loop needs `break`, `await` in
  sequence, or is genuinely clearer — declarative is the default, not a ban.
- **Compose by naming, not by piping.** Build a transformation from small named functions and bind
  each intermediate result to a named `const`. That is composition that still debugs: every step
  has a name in the stack trace and a value you can inspect with a breakpoint or one log line.
  A `pipe(a, b, c)` chain hides exactly the values you need when it is wrong.

  ```ts
  const visibleLines = lines.filter(isRefundable);
  const byOrder = groupByOrderId(visibleLines);
  const summary = summarizeRefund(byOrder, now);
  ```

- **Immutability the type system can check.** `const` only stops rebinding — the object is still
  mutable. Mark what must not change with `readonly` / `ReadonlyArray<T>` in types and `as const`
  for literal tables. Copy before in-place methods (`[...items].sort(fn)`); the ES2023 non-mutating
  versions (`toSorted`, `toReversed`, `with`) are cleaner, but check the target runtime (Hermes
  version / web browserslist) supports them before using them. `Object.freeze` is not a substitute
  — it is shallow and silent in non-strict code.
- **Functions as values** — strategies, variant maps, callbacks, factories returning configured
  functions. This is where higher-order functions earn their keep; see the `design-patterns` skill.
- **Recursion where the data is recursive** — trees (categories, menus, comment threads). Not as a
  loop replacement over flat data.

**Skip (or justify explicitly in the PR):**

- **Recursion instead of loops over flat or long data.** JS engines do not reliably eliminate tail
  calls, so deep recursion is a stack overflow waiting for a large input, and it reads worse than
  `reduce`/`for…of`.
- **Currying and manual partial application as a style.** `multiply(2)(3)` style APIs make call
  sites and TS inference harder and add nothing a closure or a named wrapper does not. A function
  returning a configured function (`createFormatter(locale)`) is fine — that is a factory, not
  currying for its own sake.
- **`pipe`/`compose` helpers, point-free style, algebraic-structure libraries** (Ramda-style
  toolkits, Fantasy Land / Sanctuary, `fp-ts`). New vocabulary for the whole team, worse stack
  traces and TS inference, no defect class removed that plain named functions do not already
  remove. Use only if the project already does.
- **Chains that walk a large list many times** (`filter().map().filter().reduce()` over thousands of
  items in a hot path). Readability first; fold into one `reduce` only with a measurement
  (`performance.md`).

The test for any FP technique: does it remove a class of bugs (hidden state, shared mutation,
unhandled case) or only change how the code looks? Keep the first kind.

## Selectors: derive, never store

Raw data comes in; components need shaped data. Do the shaping in a pure selector — a plain function, living wherever the project keeps non-React logic — never in `useState` + `useEffect`.

Storing derived data creates two sources of truth that drift — the class of bug that reproduces only after a specific sequence of actions and is very expensive to find. A selector cannot drift; it is recomputed from the source every time.

Within a selector, keep each derived value single-assignment: compose selectors or pure helpers and bind intermediate results with named `const`s. When branches produce different values, use early returns or a small named selector rather than reassigning derived `let`s or compressing the branches into nested ternaries. Local mutation remains appropriate for a clear accumulator; this is not a ban on imperative control flow.

If a selector is genuinely expensive, that is a memoization question (see `performance.md`), not a reason to store it in state.

## Boundaries: parse once, at the edge

Server responses are validated and mapped once, at the data boundary, into app-owned types. A schema library with a transform step (Zod and friends) does parsing and shaping together. Past that boundary nothing should ever see a raw DTO field name.

Data-fetching functions wrap in try/catch, log with context, and return a **safe fallback shape** rather than throwing into the render tree:

```ts
export const verifyProduct = async (cardId: string): Promise<Result> => {
  try {
    return await client.fetch<Result>(`/verify/${cardId}`, { method: "GET" })
  } catch (error) {
    logger.warn("Error validating card id", { cardId, error })

    return { verified: false, item: null, images: [] }
  }
}
```

The fallback must be a shape the UI can render as a real state (not-found, empty), not a half-object that produces `undefined` on screen. Wrap in whatever caching/deduping primitive the project uses, if any.

## File and naming conventions

**Follow the project.** If it has an established structure, naming scheme, or component-typing convention, use it — consistency with the surrounding code beats every preference below. These are the defaults for greenfield code, or for a codebase with no convention of its own.

**Structure — the principle:**

Whatever the taxonomy is called, three kinds of code stay separated, and dependencies point one way only:

- **components** — layout and interaction
- **pure logic** — selectors, helpers, constants, types. No React, no I/O, trivially testable
- **data access** — clients, fetchers, mutations

A feature's public surface is one designated entry point; reaching past it into another feature's internals is a coupling bug. Whether that's expressed as FSD layers (`shared` → `entities` → `features` → `widgets`) with `ui`/`model`/`api` folders, as `features/x/{components,lib,api}`, or as something else entirely, is the project's call — do not import a taxonomy the project doesn't already use.

**Naming and typing — the defaults:**

- **kebab-case filenames**, matching the component: `size-guide-modal.tsx`
- **One component per file**; the assembly point does the composing
- **The name signals the rung**, so a reader knows what they're looking at before opening it:
  - plain name (`NavigationList`, `SizeGuide`) — takes props, rungs 1–2
  - `*Composer` — reads a contract, source-agnostic, rungs 3–4
  - `*Provider` — fills a contract; interchangeable with its siblings
  - `*Slot` props — structure injected by the caller
- **Local type aliases**: `PropsType`, `ContextType`, `ResponseType`, `<Name>ReturnType`. `type`, not `interface`
- **`React.FC<PropsType>`** for typing components; `React.FC` bare when there are no props; `React.FC<React.PropsWithChildren>` for a root
- **Constants extracted**, including translatable message descriptors — not inline in JSX
