# Creational patterns — how things get made

Five patterns about *who decides what gets created*. In TS/React the answer is usually "a function"
or "a map", and the class hierarchy in the textbook version is optional.

## Contents

- [Factory Method](#factory-method)
- [Abstract Factory](#abstract-factory)
- [Builder](#builder)
- [Prototype](#prototype)
- [Singleton](#singleton)

---

## Factory Method

**Idea.** Callers ask for "a thing of this kind" through one creation point; which concrete thing
comes back is decided in that point (or by whoever overrides it), not at every call site.

**Smell that justifies it.** The same `switch (kind)` → `new X()` / `<X />` is repeated in two or
more places, and adding a kind means touching all of them.

**TS/JS.** A function returning a common type; the variants live in one map.

```ts
type PaymentMethodType = 'card' | 'cod' | 'applePay';

type PaymentProcessorType = { pay: (amount: number) => Promise<PaymentResultType> };

const processors: Record<PaymentMethodType, () => PaymentProcessorType> = {
  card: createCardProcessor,
  cod: createCodProcessor,
  applePay: createApplePayProcessor,
};

export const createPaymentProcessor = (method: PaymentMethodType) => processors[method]();
```

`Record<Union, …>` makes the compiler fail when a new union member has no creator — that is the
Open/Closed benefit without a class hierarchy.

**React.** A variant → component map instead of JSX `switch` scattered over screens.

```tsx
const blockByType: Record<BlockType['type'], ComponentType<{ block: BlockType }>> = {
  banner: BannerBlock,
  products: ProductsBlock,
  text: TextBlock,
};

const Block = ({ block }: { block: BlockType }) => {
  const Component = blockByType[block.type];
  return <Component block={block} />;
};
```

**Don't.** Build a `Creator` base class with subclasses per product; do not add a factory for a
single variant; do not create components inside render (`const C = makeComponent()` in the body
remounts every render) — keep the map at module scope.

**Confused with.** Abstract Factory (a *family* of matching products, not one); Strategy (swaps
behavior of an existing object, not which object is created).

---

## Abstract Factory

**Idea.** One object produces a whole *family* of related things that are guaranteed to match
each other; switch the factory and every member switches together.

**Smell.** Several parallel choices keyed by the same variant — `brand === 'x' ? iconX : iconY`,
`brand === 'x' ? colorsX : colorsY`, `brand === 'x' ? <HeaderX/> : <HeaderY/>` — and a mismatch
(icon from one brand, colors from another) is a real bug.

**TS/JS.** A typed "kit" per variant; callers depend only on the kit type.

```ts
type UiKitType = {
  colors: ColorTokensType;
  Icon: ComponentType<IconPropsType>;
  Header: ComponentType<HeaderPropsType>;
};

const kits: Record<BrandType, UiKitType> = { main: mainKit, outlet: outletKit };
export const getUiKit = (brand: BrandType): UiKitType => kits[brand];
```

**React.** A context provider that hands the kit down: theme providers, platform component sets
(`Platform.select({ ios: iosKit, android: androidKit })`), design-system variants.

```tsx
const UiKitContext = createContext<UiKitType>(mainKit);
export const useUiKit = () => use(UiKitContext);
```

**Don't.** Introduce it for one brand/platform "in case"; every new product type must be added to
every kit, which is the price — pay it only when mismatches have actually happened or the variants
are real today.

**Confused with.** Factory Method (one product); Builder (assembles one complex product
step by step); a theme object that holds only values is just configuration, not a factory.

---

## Builder

**Idea.** Construct a complex thing in explicit steps instead of one call with a long parameter
list; the same steps can yield different results.

**Smell.** Telescoping parameters (`fn(a, b, undefined, undefined, true)`), a component with a dozen
optional props that only make sense in certain combinations, or a request/query assembled across
many conditional branches.

**TS/JS.** Usually just an options object with defaults. Use a fluent builder only when the order
of steps or the validity of combinations matters.

```ts
const buildOrderQuery = () => {
  const params = new URLSearchParams();
  const builder = {
    status: (s: OrderStatusType) => (params.set('status', s), builder),
    page: (n: number) => (params.set('page', String(n)), builder),
    since: (d: Date) => (params.set('since', d.toISOString()), builder),
    build: () => params.toString(),
  };
  return builder;
};

buildOrderQuery().status('delivered').page(2).build();
```

Immutable variant: each step returns a new object — safe to branch a half-built config.

**React.** Compound components are the builder for UI: the tree of `<Card.Root><Card.Header/>…`
replaces a `<Card title subtitle icon footer actions …/>` prop explosion. Form/schema builders
(zod, yup) and query builders are the same pattern in libraries.

**Don't.** Wrap a 3-field object in a builder; do not keep a mutable builder in component state.

**Confused with.** Abstract Factory (returns finished products immediately); Composite (the tree a
builder often produces).

---

## Prototype

**Idea.** Make new objects by copying a configured existing one, without the copier knowing its
concrete type.

**Smell.** Code that manually re-creates an object field by field to get "the same, but slightly
different", or needs to duplicate items whose shape it does not own.

**TS/JS.** The language has it: objects already inherit via prototypes, and copying is
`structuredClone(value)` (deep, handles Dates/Maps, not functions/class instances) or spread (shallow).

```ts
const duplicateCartLine = (line: CartLineType): CartLineType => ({
  ...structuredClone(line),
  id: createId(),
  quantity: 1,
});
```

For class instances that own their copying, give them a `clone()` — the only case the textbook
shape is needed.

**React.** Immutable updates are prototype-style copying: `{ ...state, field }`, `[...items, item]`.
"Duplicate this item/filter preset" features.

**Don't.** `JSON.parse(JSON.stringify(x))` (drops Dates, undefined, Maps); deep-clone large state
on every render; clone objects holding live resources (sockets, native handles).

**Confused with.** Memento (a copy kept to restore later, not to create new siblings).

---

## Singleton

**Idea.** Exactly one instance, reachable from anywhere.

**Smell.** A resource that must not be duplicated: SDK client, analytics instance, logger, a cache
shared by the whole app, a native module wrapper.

**TS/JS.** An ES module is evaluated once, so a top-level value *is* a singleton. Lazy when the
creation is expensive or needs runtime config.

```ts
let client: AnalyticsClientType | undefined;

export const getAnalytics = () => (client ??= createAnalyticsClient(config));
```

**React.** A module-level store read through `useSyncExternalStore`, a context provided once at the
root, a `QueryClient` created once. Anything created inside a component body is *not* a singleton —
it is per-render; use module scope or a ref if identity must persist.

**Don't.** Use it as a hidden global to dodge passing data (it is untestable and leaks between
tests — export a reset for tests or inject it); keep entity-keyed data in a single global slot
(two screens for two entities will overwrite each other — see `frontend-craft` →
`architecture.md` → Singleton stores keyed by one entity); assume one instance across
multiple JS bundles, iframes, or Hot Reload.

**Confused with.** Flyweight (many shared immutable instances, not one mutable); Facade (often
exported as a singleton, but the pattern is the simplified interface, not the single instance).
