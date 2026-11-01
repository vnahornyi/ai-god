# Behavioral patterns — who talks to whom, and who decides

Ten patterns about distributing responsibility and communication. In React most of them already
exist as a hook, a reducer, a union type or a function prop; the entries say which.

## Contents

- [Chain of Responsibility](#chain-of-responsibility--ланцюжок-обовязків)
- [Command](#command--команда)
- [Iterator](#iterator--ітератор)
- [Mediator](#mediator--посередник)
- [Memento](#memento--знімок)
- [Observer](#observer--спостерігач)
- [State](#state--стан)
- [Strategy](#strategy--стратегія)
- [Template Method](#template-method--шаблонний-метод)
- [Visitor](#visitor--відвідувач)
- [Communication patterns compared](#communication-patterns-compared)
- [Look-alikes](#look-alikes)

---

## Chain of Responsibility · Ланцюжок обов'язків

**Idea.** A request passes through an ordered list of handlers; each one either handles it, stops
it, or passes it on. The sender does not know which handler will act.

**Smell.** A long `if … return` sequence of checks (auth → validation → rate limit → feature flag)
that grows with each feature, or the same sequence duplicated in several flows.

**TS/JS.** Middleware: an array of functions with a `next`.

```ts
type HandlerType<C> = (ctx: C, next: () => Promise<void>) => Promise<void>;

const runChain = <C>(handlers: HandlerType<C>[], ctx: C) => {
  const dispatch = (i: number): Promise<void> =>
    i < handlers.length ? handlers[i](ctx, () => dispatch(i + 1)) : Promise.resolve();
  return dispatch(0);
};
```

Request/response interceptors (axios), Express/Koa middleware, Redux middleware, deep-link
resolvers trying routes in order — all this pattern.

**React.** Event bubbling through the component tree (a handler may `stopPropagation`); nested
error boundaries (the nearest one that can handle it does); a deep-link handler list where the
first matcher that recognizes the URL navigates.

**Don't.** Leave the "nobody handled it" case undefined — make the end of the chain explicit
(fallback handler or logged error); rely on order without naming it in one place.

**Confused with.** Decorator (always delegates, never stops); Command (the request as an object,
not the route it travels).

---

## Command · Команда

**Idea.** Turn an action into a value: something you can store, pass around, queue, retry, log,
serialize, or undo — separated from what triggers it.

**Smell.** The same action wired from several places (button, swipe, shortcut, push action);
a need for undo/redo, offline queueing, retries, or an audit log of what the user did.

**TS/JS.** A plain object, often with `undo`.

```ts
type CommandType = { run: () => Promise<void>; undo?: () => Promise<void>; label: string };

const removeCartLine = (lineId: string, snapshot: CartLineType): CommandType => ({
  label: 'remove-line',
  run: () => cartApi.remove(lineId),
  undo: () => cartApi.add(snapshot),
});
```

Serializable commands (`{ type: 'cart/remove', lineId }`) are what an offline queue persists.

**React.** Redux/`useReducer` actions are commands; `useActionState` / form `action` functions;
an "Undo" snackbar holding the last command; an offline mutation queue replayed on reconnect.

**Don't.** Wrap every click handler in a command object; if there is no queueing, undo, logging or
multiple triggers, a function is enough.

**Confused with.** Strategy (varies *how* one operation is done; Command packages *what* to do);
Memento (stores state for undo; Command stores the action and its inverse — they pair well).

---

## Iterator · Ітератор

**Idea.** Walk a collection element by element without knowing how it is stored; several walks can
run independently.

**Smell.** Consumers reaching into a structure's internals (tree children, page cursors) to
traverse it; traversal logic duplicated; loading everything into memory to loop once.

**TS/JS.** The iteration protocol and generators — built in.

```ts
function* walk(node: MenuNodeType): Generator<MenuNodeType> {
  yield node;
  if (node.kind === 'group') for (const child of node.children) yield* walk(child);
}

async function* pages<T>(load: (cursor?: string) => Promise<PageType<T>>) {
  let cursor: string | undefined;
  do {
    const page = await load(cursor);
    yield* page.items;
    cursor = page.nextCursor;
  } while (cursor);
}
```

**React.** Infinite lists consume a cursor-based iterator one page per `onEndReached`; a hook
exposing `{ items, loadMore, hasMore }` is an iterator over a paged API. Render still needs arrays —
materialize what is shown, keep the cursor in state.

**Don't.** Write custom iterator classes for arrays; use generators where `map/filter` is clearer.

**Confused with.** Visitor (performs operations on elements; Iterator only yields them — they are
often combined).

---

## Mediator · Посередник

**Idea.** Components stop talking to each other directly; they report events to one coordinator,
which decides who reacts. Many-to-many links become many-to-one.

**Smell.** Sibling components passing callbacks sideways through parents to poke each other; a form
where changing field A must reset B, reload C and toggle D, with that logic spread across A, B, C, D.

**TS/JS.** A coordinator that receives events and issues instructions.

**React.** The parent that owns state and passes it down is the default mediator; for complex
interaction, a reducer is the mediator:

```tsx
const checkoutReducer = (state: CheckoutStateType, event: CheckoutEventType): CheckoutStateType => {
  switch (event.type) {
    case 'deliveryChanged':
      return { ...state, delivery: event.delivery, slot: null, payment: resetIfUnsupported(state.payment, event.delivery) };
    case 'slotSelected':
      return { ...state, slot: event.slot };
  }
};
```

Children dispatch *what happened*, not *what others should do*. Compound components' shared context
is also a mediator between the parts.

**Don't.** Let one mediator coordinate unrelated features (God reducer / God context) — split by
flow; use a global event bus as a mediator (untraceable; see Observer).

**Confused with.** Facade (one-directional simplification; the subsystem does not know it);
Observer (distributed one-to-many notifications; Mediator centralizes the decision).

---

## Memento · Знімок

**Idea.** Capture an object's state as an opaque snapshot so it can be restored later, without
exposing or depending on the object's internals.

**Smell.** Undo/redo, "discard changes", restoring a draft after the app is killed, rolling back an
optimistic update when the request fails.

**TS/JS.** With immutable state, a snapshot is just the previous value.

```ts
const optimisticToggleFavorite = async (store: FavoritesStoreType, id: string) => {
  const snapshot = store.getState();
  store.setState(toggle(snapshot, id));
  try {
    await favoritesApi.toggle(id);
  } catch {
    store.setState(snapshot);
  }
};
```

**React.** `useOptimistic` (React 19) keeps the confirmed state and reverts automatically;
undo history as `{ past: S[]; present: S; future: S[] }` in a reducer; form drafts persisted to
storage and rehydrated.

**Don't.** Keep unbounded history (cap it); snapshot mutable objects by reference (the "snapshot"
changes with the original); restore a stale snapshot over newer server data without checking.

**Confused with.** Prototype (copy to create a new object, not to restore); Command (they pair:
commands for redo, snapshots for undo).

---

## Observer · Спостерігач

**Idea.** A subject keeps a list of subscribers and notifies them when it changes; subscribers come
and go at runtime; the subject does not know what they do.

**Smell.** One change must reach several unknown consumers (auth state, cart count, network status,
push token), and consumers currently poll or are called by hand.

**TS/JS.** A tiny store; `EventTarget`/`EventEmitter` for events.

```ts
const createStore = <S>(initial: S) => {
  let state = initial;
  const listeners = new Set<() => void>();
  return {
    getState: () => state,
    setState: (next: S) => {
      state = next;
      listeners.forEach((listener) => listener());
    },
    subscribe: (listener: () => void) => (listeners.add(listener), () => listeners.delete(listener)),
  };
};
```

**React.** `useSyncExternalStore(store.subscribe, store.getState)` is the correct bridge from any
observable to React; Zustand/Redux/MobX, `NetInfo.addEventListener`, `AppState`, navigation
listeners. React state + props is itself observation of a single source.

```ts
const useNetworkOnline = () => useSyncExternalStore(networkStore.subscribe, () => networkStore.getState().online);
```

**Don't.** Subscribe in an effect without returning the unsubscribe (leaks, updates on unmounted
screens); use a global event bus to pass data between components that have a common parent — that
is state in the wrong place; depend on notification order.

**Confused with.** Mediator (central decision-maker vs broadcast); Pub/Sub with a broker (a variant
where publisher and subscriber do not even know the subject).

---

## State · Стан

**Idea.** An object's behavior depends on which state it is in, and each state defines what is
allowed and where it can go next — instead of every method checking flags.

**Smell.** Boolean soup — `isLoading`, `isError`, `isSubmitted`, `isRefunding` — with impossible
combinations representable; `if (status === …)` repeated in every handler and render branch;
transitions that are legal from one state and silently broken from another.

**TS/JS.** A discriminated union for states + a transition function (a finite state machine).

```ts
type RefundStateType =
  | { status: 'idle' }
  | { status: 'submitting'; lineIds: string[] }
  | { status: 'pending'; refundId: string }
  | { status: 'failed'; error: RefundErrorType };

type RefundEventType =
  | { type: 'submit'; lineIds: string[] }
  | { type: 'accepted'; refundId: string }
  | { type: 'rejected'; error: RefundErrorType };

const refundTransition = (state: RefundStateType, event: RefundEventType): RefundStateType => {
  switch (state.status) {
    case 'idle':
    case 'failed':
      return event.type === 'submit' ? { status: 'submitting', lineIds: event.lineIds } : state;
    case 'submitting':
      if (event.type === 'accepted') return { status: 'pending', refundId: event.refundId };
      if (event.type === 'rejected') return { status: 'failed', error: event.error };
      return state;
    case 'pending':
      return state;
  }
};
```

Double submit is impossible by construction: `submit` is ignored outside `idle`/`failed`.

**React.** `useReducer(refundTransition, { status: 'idle' })`; render by `switch (state.status)`;
data available only in the state that has it (`refundId` exists only when `pending`). XState for
large, hierarchical machines.

**Don't.** Introduce a machine for a two-state toggle; spread transition rules between the reducer
and handlers (the reducer owns them).

**Confused with.** Strategy (strategies are picked from outside and do not know each other; states
decide the next state themselves).

---

## Strategy · Стратегія

**Idea.** A family of interchangeable algorithms behind one signature; the caller picks one and the
context uses it without knowing which.

**Smell.** A function with a growing `switch` over *how* to do one job (sort by price/rating/new,
delivery cost by method, validation per country), or copies of a component differing only in one
calculation.

**TS/JS.** A function type and a map of functions — the class version is not needed.

```ts
type SortStrategyType = (a: ProductType, b: ProductType) => number;

const sortStrategies: Record<SortKeyType, SortStrategyType> = {
  priceAsc: (a, b) => a.price - b.price,
  priceDesc: (a, b) => b.price - a.price,
  rating: (a, b) => b.rating - a.rating,
};

const sorted = [...products].sort(sortStrategies[sortKey]);
```

**React.** Function props: `renderItem`, `keyExtractor`, `getItemLayout`, `filter`, `validate`,
`renderAmount`; a custom hook passed or selected by the caller (`useProductsSource`) for the same UI
with different data/behavior. Keep strategy maps at module scope so identity is stable.

**Don't.** Create a strategy for one algorithm; add a `strategy`/`mode` flag to a shared function
only to keep old callers unchanged (see `frontend-craft` → `architecture.md` → When NOT to abstract);
make the client understand internal differences to choose — expose domain-named keys.

**Confused with.** State (self-transitioning); Command (what vs how); Template Method (inheritance
instead of composition); Decorator (outside vs inside).

---

## Template Method · Шаблонний метод

**Idea.** A fixed skeleton of an algorithm with some steps left for variants to fill in; the order
of steps stays in one place.

**Smell.** Several flows copy the same sequence (validate → prepare → send → track → navigate) and
differ in one or two steps; fixes to the sequence are applied to one copy and missed in another.

**TS/JS.** Not inheritance — a higher-order function whose varying steps are parameters (which
makes it a Strategy per step).

```ts
type SubmitStepsType<I, R> = {
  validate: (input: I) => ValidationResultType;
  send: (input: I) => Promise<R>;
  onSuccess?: (result: R) => void;
};

const createSubmitFlow =
  <I, R>({ validate, send, onSuccess }: SubmitStepsType<I, R>) =>
  async (input: I) => {
    const validation = validate(input);
    if (!validation.ok) return validation;
    const result = await send(input);
    onSuccess?.(result);
    return { ok: true as const, result };
  };
```

Optional steps (`onSuccess?`) are the template's *hooks*.

**React.** A shared screen/layout component that fixes structure (header → content → sticky footer)
with slots or render props for the varying parts; a generic hook (`useFormSubmit`) taking the
varying steps as arguments; class components' lifecycle methods were a template method.

**Don't.** Use class inheritance for it in React code; add so many optional steps that the skeleton
becomes a configuration language — split into two templates.

**Confused with.** Strategy (swaps a whole algorithm; Template Method fixes the order and swaps
steps); Builder (constructs an object step by step, not a process).

---

## Visitor · Відвідувач

**Idea.** Keep a stable set of node types free of operations; put each operation (render, validate,
serialize, price) in its own place that handles every node type.

**Smell.** A stable family of node types (CMS blocks, AST nodes, order line kinds, form field
kinds) and a growing number of operations over them, each currently a method sprinkled into the
types or an `if (node.type === …)` chain that forgets a type.

**TS/JS.** Classic double dispatch is unnecessary: a discriminated union with an exhaustive switch
per operation, or a typed visitor record.

```ts
type VisitorType<R> = { [K in FieldType['kind']]: (field: Extract<FieldType, { kind: K }>) => R };

const visit = <R>(field: FieldType, visitor: VisitorType<R>): R =>
  (visitor[field.kind] as (f: FieldType) => R)(field);

const validateField: VisitorType<string | null> = {
  text: (f) => (f.required && !f.value ? 'required' : null),
  phone: (f) => (matchesPhoneRule(f.value) ? null : 'invalidPhone'),
  checkbox: (f) => (f.required && !f.checked ? 'required' : null),
};
```

Adding a node kind makes every visitor fail to compile until it handles it — the key benefit.
With a plain `switch`, get the same guarantee from `default: return assertNever(node)`.

**React.** A renderer map per block type (rendering is one visitor), plus separate pure visitors for
analytics payloads, validation, or search indexing over the same data.

**Don't.** Use it when node types change often and operations are few — then methods/components
per type are simpler; reach for `accept(visitor)` classes in TS.

**Confused with.** Iterator (walks, does not operate); Strategy (one algorithm for one context, not
one operation per type); Factory/variant map (chooses *which component to create* — often the same
map shape, different intent).

---

## Communication patterns compared

Four ways to connect a sender to receivers:

| Pattern | Shape | Sender knows receiver? | Use when |
| --- | --- | --- | --- |
| Chain of Responsibility | sequential, one may handle/stop | no | ordered checks, middleware, fallbacks |
| Command | the request as a value | no — whoever runs it | queue, retry, undo, multiple triggers |
| Mediator | many → one coordinator → many | no — only the mediator | tangled peers, cross-field rules |
| Observer | one → many, broadcast | no | unknown/dynamic listeners to a change |

## Look-alikes

- **State vs Strategy** — same composition shape; states pick the next state, strategies are chosen
  from outside.
- **Strategy vs Template Method** — composition per object vs a fixed skeleton with pluggable steps.
- **Command vs Strategy** — *what* to do vs *how* to do it.
- **Mediator vs Observer** — central decision vs distributed notification; a mediator is often
  implemented with observer subscriptions.
- **Chain of Responsibility vs Decorator** — the chain may stop; decorators always pass through.
- **Memento vs Command for undo** — restore the state vs run the inverse action.
