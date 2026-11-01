# Examples — house style

Bad / good / over-applied pairs for the house-style rules in `SKILL.md`. Read before writing or
reviewing component code. Each entry ends with one yes/no check; answer it for every component in
the diff before staging.

The over-applied example matters as much as the bad one: a rule applied where its threshold is not
met is a defect too, and reviewers will ask you to undo it.

## Contents

- Nested ternaries
- Conditional rendering — inline
- Conditional rendering — extract
- Conditional rendering — guard states
- JSX through a mutable `let`
- Function signatures
- Comments

## Nested ternaries

Rule: no nested ternary anywhere in JS/TS (`SKILL.md` → Nested ternaries: prohibited).
Applies when: a ternary sits inside another ternary's branch — in JSX, an assignment, a return, a template literal.
Does not apply when: a single ternary picks between two values.

Bad:

```tsx
const label = isLoading ? t`Loading` : items.length ? t`Found ${items.length}` : t`Nothing found`;
```

Good — a pure helper with early returns:

```tsx
const selectResultsLabel = (isLoading: boolean, count: number, t: TFunction) => {
  if (isLoading) return t`Loading`;
  if (count === 0) return t`Nothing found`;

  return t`Found ${count}`;
};
```

Over-applied — a single two-way ternary rewritten into a helper:

```tsx
// Wrong: one ternary is allowed; the helper adds a name and a jump for nothing.
const selectButtonLabel = (isSaved: boolean) => {
  if (isSaved) return t`Saved`;

  return t`Save`;
};

// Right:
const buttonLabel = isSaved ? t`Saved` : t`Save`;
```

Check: does any `?` expression contain another `?` expression?

## Conditional rendering — inline

Rule: a simple condition stays in the JSX (`SKILL.md` → Conditional rendering).
Applies when: one condition with `&&`, or one two-way ternary, and the JSX in the branch is a few lines.
Does not apply when: the branch has nested conditions, three or more states, a `switch`, or JSX long enough to hide the layout around it — see the next entry.

Good:

```tsx
return (
  <Card>
    <Title>{store.name}</Title>
    {store.isOpenNow && (
      <Chip>
        <Trans>Open now</Trans>
      </Chip>
    )}
    {isFavourite ? <FilledHeartIcon /> : <HeartIcon />}
  </Card>
);
```

Over-applied — a render helper per condition:

```tsx
// Wrong: each helper wraps one `&&`. The reader jumps three times to learn nothing.
const renderOpenChip = () => {
  if (!store.isOpenNow) return null;

  return <Chip><Trans>Open now</Trans></Chip>;
};
const renderHeart = () => (isFavourite ? <FilledHeartIcon /> : <HeartIcon />);

return (
  <Card>
    <Title>{store.name}</Title>
    {renderOpenChip()}
    {renderHeart()}
  </Card>
);
```

Check: is there a `render…()` helper or subcomponent whose whole body is one `&&` or one two-way ternary? If yes, inline it.

## Conditional rendering — extract

Rule: a branch that stops being readable in place gets a name (`SKILL.md` → Conditional rendering).
Applies when: nested conditions, three or more states, a `switch` over a union, or long JSX.
Does not apply when: the condition is simple — previous entry.

Choosing the form:

| The branch… | Use |
|---|---|
| reads mostly the component's own locals and props | a local `render…()` helper, called where the UI belongs |
| has its own data, its own hook, or could be reused | a subcomponent with props |

Bad — states piled into the JSX:

```tsx
<View>
  {isQuoteLoading ? (
    <DeliverySkeleton />
  ) : !quote ? (
    <Text><Trans>Delivery unavailable</Trans></Text>
  ) : quote.fee === 0 ? (
    <Text><Trans>Free delivery</Trans></Text>
  ) : (
    <Text><Trans>Delivery {formatMoney(quote.fee)}</Trans></Text>
  )}
</View>
```

Good — one helper, early returns inside it:

```tsx
const renderDelivery = () => {
  if (isQuoteLoading) return <DeliverySkeleton />;
  if (!quote) return <Text><Trans>Delivery unavailable</Trans></Text>;
  if (quote.fee === 0) return <Text><Trans>Free delivery</Trans></Text>;

  return <Text><Trans>Delivery {formatMoney(quote.fee)}</Trans></Text>;
};

return (
  <Section>
    <Address value={order.address} />
    {renderDelivery()}
  </Section>
);
```

Check: does any JSX expression hold more than one condition? If yes, it needs a name.

## Conditional rendering — guard states

Rule: a guard on the whole output is an early return at the top of the component (`SKILL.md` → Conditional rendering; `composition.md` → Functional style).
Applies when: the component renders nothing, or only a loading / empty / error state, for some input.
Does not apply when: only part of the output depends on the state — that part is a branch inside the JSX.

Good:

```tsx
export const StoreCard: React.FC<PropsType> = ({ store, onPress }) => {
  if (!store) return null;

  return <Pressable onPress={() => onPress(store.id)}>…</Pressable>;
};
```

Over-applied — the guard moved into a render helper that the return calls:

```tsx
// Wrong: the whole-output guard is now one jump away from the component signature.
const renderContent = () => {
  if (!store) return null;

  return <Pressable onPress={() => onPress(store.id)}>…</Pressable>;
};

return renderContent();
```

Check: does the component's `return` call a helper that holds the whole output? If yes, move the guard up and inline the rest.

## JSX through a mutable `let`

Rule: never assemble JSX through a `let` reassigned across branches (`SKILL.md` → Conditional rendering).
Applies when: a `let` holds JSX and an `if`/`switch` reassigns it.
Does not apply when: a `let` holds a non-JSX accumulator inside a pure function (`composition.md` → Functional style).

Bad:

```tsx
let content = <Text><Trans>Delivery {formatMoney(quote.fee)}</Trans></Text>;
if (isQuoteLoading) content = <DeliverySkeleton />;
else if (!quote) content = <Text><Trans>Delivery unavailable</Trans></Text>;
```

Good: the `renderDelivery` helper in "Conditional rendering — extract".

Check: does any `let` in a component hold JSX?

## Function signatures

Rule: three or more parameters or a boolean flag → one object with named fields; one returned value → the value itself (`SKILL.md` → Function signatures).
Applies when: you write or change a function's parameters or its return type.
Does not apply when: the signature is fixed by a library or a callback contract, or the result carries several values the caller uses together.

Bad:

```ts
export function pickLabelInFrame(
  labels: LabelType[],
  frame: FrameType,
  viewSize: ViewSizeType,
  ignoredLabel: string | null,
  isRotated: boolean,
): { text: string | undefined } | undefined { … }

const picked = pickLabelInFrame(found, frame, size, null, isLandscape);
onPicked(picked.text);
```

Good:

```ts
export function pickLabelInFrame({
  labels,
  frame,
  viewSize,
  ignoredLabel,
  isRotated,
}: PickLabelInFrameArgsType): string | undefined { … }

const picked = pickLabelInFrame({
  labels: found,
  frame,
  viewSize: size,
  ignoredLabel: null,
  isRotated: isLandscape,
});
onPicked(picked);
```

Over-applied:

```ts
export const formatMoney = ({ value }: { value: number }) => …; // one obvious parameter
const { width, height } = measure(view); // two values used together stay an object
```

Check: does any call site in the diff pass three or more positional arguments or a bare `true`/`false`/`null`, or read the only field of a returned object?

## Comments

Rule: default zero; a comment carries business or domain knowledge absent from the code (`SKILL.md` → Comments).
Applies when: always.
Does not apply when: never — but a project rule that mandates a comment is satisfied in one line carrying the domain why.

Bad:

```tsx
// Clear the search query when the category changes
useEffect(() => setQuery(''), [categoryId]);

/**
 * Formats money.
 * @param value the amount
 * @returns the formatted amount
 */
export const formatMoney = (value: number) => …;
```

Good — no comment; the names already say it:

```tsx
useEffect(() => setQuery(''), [categoryId]);

export const formatMoney = (value: number) => …;
```

Good — a comment that earns its place:

```tsx
// Courier API reports fee 0 for zones it has not priced yet, so 0 alone is not "free"
if (quote.fee === 0 && !quote.isPriced) return <Text><Trans>Delivery unavailable</Trans></Text>;
```

Check: for each comment in the diff — could a reader who sees the whole file know this without it? If yes, delete it.
