# Structural patterns — how things are assembled

Seven patterns about composing objects into bigger structures. Four of them (Adapter, Decorator,
Proxy, Facade) are all "a wrapper" — the difference is *what the wrapper does to the interface*,
and it is the most common mix-up in reviews. See the table at the end.

## Contents

- [Adapter](#adapter--адаптер)
- [Bridge](#bridge--міст)
- [Composite](#composite--компонувальник)
- [Decorator](#decorator--декоратор)
- [Facade](#facade--фасад)
- [Flyweight](#flyweight--легковаговик)
- [Proxy](#proxy--замісник)
- [Telling the wrappers apart](#telling-the-wrappers-apart)

---

## Adapter · Адаптер

**Idea.** A translator between an interface you have and the interface your code expects. Neither
side changes; the adapter converts.

**Smell.** API DTO field names (`snake_case`, nested `data.attributes`, numbers as strings) leaking
into components; a third-party SDK's callback style mixed into promise-based code; two libraries
with the same job and different shapes.

**TS/JS.** A pure mapper at the boundary. Parse once, at the edge, into the domain type.

```ts
const toOrder = (dto: OrderDtoType): OrderType => ({
  id: dto.order_id,
  total: Number(dto.total_amount),
  createdAt: new Date(dto.created_at),
  lines: dto.items.map(toOrderLine),
});
```

Callback → promise is also an adapter:

```ts
const getLocation = () =>
  new Promise<GeoType>((resolve, reject) => Geolocation.getCurrentPosition(resolve, reject));
```

**React.** A hook that adapts a library's API to the project's hook contract
(`useExternalValue` over a `subscribe/getSnapshot` pair); a component that maps domain props onto a
third-party component's props so the rest of the app never imports it directly.

**Don't.** Adapt inside a component on every render; spread the conversion across call sites;
write an adapter for one caller of an interface that already fits.

**Confused with.** Facade (simplifies a whole subsystem; Adapter converts one interface);
Proxy/Decorator (keep the interface; Adapter changes it).

---

## Bridge · Міст

**Idea.** Split one class hierarchy that varies along two independent axes into two hierarchies
joined by composition, so N × M implementations become N + M.

**Smell.** Files multiplying as a grid — `CardIos`, `CardAndroid`, `ListIos`, `ListAndroid`; or
`OrderScreenRest`, `OrderScreenMock`, `ProfileScreenRest`… — where each new item on one axis
means one new file per item on the other.

**TS/JS.** The "abstraction" receives the "implementation" as a dependency.

```ts
type StorageType = { get: (k: string) => Promise<string | null>; set: (k: string, v: string) => Promise<void> };

const createDraftRepository = (storage: StorageType) => ({
  load: async (id: string) => parseDraft(await storage.get(`draft:${id}`)),
  save: (id: string, draft: DraftType) => storage.set(`draft:${id}`, JSON.stringify(draft)),
});

createDraftRepository(asyncStorage);   // mobile
createDraftRepository(localStorageAdapter); // web
```

**React.** Shared UI/logic in a cross-platform layer, platform specifics injected: `.ios.tsx` /
`.android.tsx` / `.web.tsx` resolution behind one import, a shared hook taking a platform service,
render-agnostic headless logic (`useCombobox`) + per-platform views.

**Don't.** Design a bridge up front when only one axis varies today; it costs a second interface
forever.

**Confused with.** Adapter (retrofitted onto incompatible things; Bridge is designed in advance);
Strategy (swaps one algorithm; Bridge separates two whole dimensions).

---

## Composite · Компонувальник

**Idea.** Leaves and groups share one interface, so code works on a tree without caring whether a
node is a single item or a container of items.

**Smell.** Nested data of unknown depth (category trees, menus, comment threads, form sections,
bundles of products inside sets) with code that special-cases each level or hard-codes depth.

**TS/JS.** A recursive discriminated union plus recursive functions.

```ts
type MenuNodeType =
  | { kind: 'item'; id: string; price: number }
  | { kind: 'group'; id: string; children: MenuNodeType[] };

const totalPrice = (node: MenuNodeType): number =>
  node.kind === 'item' ? node.price : node.children.reduce((sum, child) => sum + totalPrice(child), 0);
```

**React.** React *is* a composite: `children` is the uniform interface, and a component renders
itself or a group of itself recursively.

```tsx
const MenuTree = ({ node }: { node: MenuNodeType }) =>
  node.kind === 'item' ? (
    <MenuItem id={node.id} />
  ) : (
    <MenuGroup id={node.id}>
      {node.children.map((child) => (
        <MenuTree key={child.id} node={child} />
      ))}
    </MenuGroup>
  );
```

**Don't.** Force list data into a tree shape; render very deep/large trees without flattening
for virtualization (`FlatList`/`SectionList` need a flat array — flatten with depth info).

**Confused with.** Decorator (also recursive, but wraps exactly one child and adds behavior).

---

## Decorator · Декоратор

**Idea.** Wrap something in an object with the *same* interface that adds behavior before or after
delegating. Wrappers stack in any combination.

**Smell.** Cross-cutting concerns copy-pasted into many functions (logging, timing, retry, error
reporting, auth headers), or subclass/prop combinations exploding (`withRetryAndLogging`…).

**TS/JS.** Higher-order functions — same signature in, same signature out.

```ts
const withRetry =
  <A extends unknown[], R>(fn: (...args: A) => Promise<R>, attempts = 3) =>
  async (...args: A): Promise<R> => {
    for (let i = 1; ; i++) {
      try {
        return await fn(...args);
      } catch (error) {
        if (i >= attempts) throw error;
      }
    }
  };

const fetchOrders = withLogging(withRetry(fetchOrdersRaw));
```

Order matters: the outermost wrapper runs first. TS `@decorator` syntax is the same idea for
classes — use only where the project already does.

**React.** Wrapper components (`<ErrorBoundary>`, `<Suspense>`, `<AnalyticsScreen name>`), custom
hooks composing another hook and adding behavior (`useOrdersWithPolling` over `useOrders`),
HOCs in legacy code. Prefer wrapper components and hooks over HOCs in new code: HOCs hide props,
collide on names and break refs/typing. React 19: `ref` is a regular prop, so no `forwardRef`
plumbing in wrappers.

**Don't.** Stack so many wrappers that stack traces and devtools become unreadable; hide a changed
interface under a decorator name (that is an Adapter).

**Confused with.** Proxy (same interface, but *controls access/lifecycle* rather than adding
features, and usually owns the wrapped object); Chain of Responsibility (links may stop the
request; decorators always delegate); Strategy (changes the inside; Decorator changes the outside).

---

## Facade · Фасад

**Idea.** One simple entry point that hides a complicated subsystem. Clients call the facade; the
facade orchestrates the parts.

**Smell.** Every caller repeats the same multi-step dance with a subsystem — init SDK, check
consent, set user, map event name, send; or components import five modules to do one domain thing.

**TS/JS.** A module exporting a small, domain-named API.

```ts
export const analytics = {
  trackPurchase: (order: OrderType) => {
    if (!consent.hasAnalytics()) return;
    firebase.logEvent('purchase', toFirebasePurchase(order));
    appsflyer.logEvent('af_purchase', toAppsflyerPurchase(order));
  },
};
```

**React.** A custom hook exposing a domain API over several stores/services (`useCheckout()`
returning `{ lines, total, submit }`), a provider module wrapping an SDK so the app never imports
the SDK, the provider-method layer in front of the transport.

**Don't.** Let it become a God object — one facade per subsystem/domain, not "services.ts" for
everything; do not block access to capabilities callers genuinely need (expose them, or add a
second focused facade).

**Confused with.** Adapter (converts one interface to match an expected one; Facade defines a new,
simpler one over many); Mediator (coordinates components that talk to *each other*; a facade's
subsystem does not know the facade exists).

---

## Flyweight · Легковаговик

**Idea.** When there are huge numbers of similar objects, share the immutable common part
(intrinsic state) and pass the varying part (extrinsic state) in from outside.

**Smell.** Measurable memory/render cost from many near-identical objects: thousands of list rows
each holding the same style objects, formatters or config; repeated identical objects causing
re-renders because they are new references every time.

**TS/JS.** A cache of shared immutable instances keyed by their intrinsic state.

```ts
const formatters = new Map<string, Intl.NumberFormat>();

export const getPriceFormatter = (locale: string, currency: string) => {
  const key = `${locale}:${currency}`;
  let formatter = formatters.get(key);
  if (!formatter) formatters.set(key, (formatter = new Intl.NumberFormat(locale, { style: 'currency', currency })));
  return formatter;
};
```

**React.** `StyleSheet.create` and module-level constant objects, `memo`ized row components
receiving only per-row data, list virtualization (`FlatList`, `FlashList`) recycling a small pool
of row views for thousands of items, image caches.

**Don't.** Apply without a measurement — it trades memory for lookups and complexity; share
mutable objects (the flyweight must be immutable).

**Confused with.** Singleton (one instance, may be mutable); memoization (caches results of calls,
closely related but not about object identity sharing).

---

## Proxy · Замісник

**Idea.** A stand-in with the *same* interface as the real object that controls access to it:
lazy creation, caching, permission checks, remote access, logging, reference counting.

**Smell.** Expensive or remote things that should load only when used; repeated identical requests;
access checks duplicated at every call site.

**TS/JS.** A wrapper with the same type, or a native `Proxy` for generic interception.

```ts
const withCache = <K, V>(load: (key: K) => Promise<V>) => {
  const cache = new Map<K, Promise<V>>();
  return (key: K) => {
    if (!cache.has(key)) cache.set(key, load(key).catch((e) => (cache.delete(key), Promise.reject(e))));
    return cache.get(key)!;
  };
};

export const getProduct = withCache(fetchProduct);
```

The rejection handler removes failed entries so an error is not cached forever.

**React.** `React.lazy(() => import('./Heavy'))` is a virtual proxy; a query cache in front of the
API is a caching proxy; a route guard component rendering the screen only for authorized users is
a protection proxy; MobX/Valtio/Immer use `Proxy` to observe access.

**Don't.** Cache without an invalidation rule tied to the domain (who makes the cached value stale?);
use a native `Proxy` where a typed wrapper is enough — it defeats type inference and debugging.

**Confused with.** Decorator (adds features, client composes it; Proxy controls access and often
manages the real object's lifecycle itself); Adapter (changes the interface); Facade (new simpler
interface).

---

## Telling the wrappers apart

| Wrapper | Interface after wrapping | Purpose | Wraps |
| --- | --- | --- | --- |
| Adapter | **different** — matches what the caller expects | make incompatible things fit | one object |
| Decorator | **same** (or extended) | add behavior, stackable | one object |
| Proxy | **same** | control access / lifecycle / caching | one object, often created by the proxy |
| Facade | **new, simpler** | hide a subsystem | many objects |
| Bridge | own abstraction + injected implementation | separate two axes of variation | an implementation |
