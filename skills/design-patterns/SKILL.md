---
name: design-patterns
description: The 22 GoF design patterns as they look in modern TypeScript and React/React Native — symptom that justifies each, the idiomatic shape, and when it is overkill. Use when a plan, diff or question names a pattern, or code shows a growing switch, prop explosion, tangled communication, an SDK wrapper, undo/redo, a state machine or a pipeline. Do not load by default for planning or review.
---

# Design patterns — for TS/JS and React

Source of the catalog and its taxonomy: refactoring.guru (22 GoF patterns). Everything below is
rewritten for the stack actually used here — TypeScript, React 19 with the compiler, React Native —
not transcribed from the site.

## What a pattern is, and is not

- A pattern is a **named shape of a solution** to a recurring problem. It is not code to paste and
  not an algorithm: an algorithm fixes the steps, a pattern fixes the *roles and their relationships*
  and leaves the steps to you.
- Levels: **idioms** (language-specific: `?.`, discriminated unions, hooks) → **design patterns**
  (this skill) → **architectural patterns** (layers, provider-method data flow, feature folders).
  Solve at the lowest level that works.
- By intent: **creational** (how things get made), **structural** (how things are assembled),
  **behavioral** (how things talk and who decides).
- The real payoff is **vocabulary**: "this is an adapter over the SDK" replaces a paragraph in a
  review. Use the names in plans and reviews; do not use them as decoration in code identifiers.

## Most GoF patterns are already a language feature here

The classic criticism holds hard in TS/React: many patterns are workarounds for languages without
first-class functions, closures, modules or structural typing. Before building the class-shaped
version, check the column on the right.

| Pattern | Usually just is, in TS / React |
| --- | --- |
| Strategy, Command, Template Method | a function passed as an argument / prop |
| Factory Method, Abstract Factory | a function returning an object; a `Record<Variant, Component>` map |
| Singleton | an ES module's top-level value |
| Iterator | `Symbol.iterator`, generators, `for…of` |
| Observer | `EventTarget`, a store `subscribe`, `useSyncExternalStore` |
| Prototype | `structuredClone`, spread |
| Decorator | a wrapper function, a HOC, a custom hook composing another |
| Flyweight | shared immutable objects, `memo`, list virtualization |
| Visitor | `switch` on a discriminated union with an exhaustive `never` check |
| State | a discriminated-union state + reducer |
| Composite | `children` / the React tree itself |

So the default for any pattern is its **function-and-union form**. Reach for classes only where the
codebase already uses them for that concern (SDK wrappers, native modules, services).

## Choose by symptom, not by name

Start from what hurts. If nothing on this list hurts yet, **no pattern** — see "When not to".

| Symptom in the code | Candidate | Reference |
| --- | --- | --- |
| `switch (type)` choosing *which object/component to create*, repeated in several places | Factory Method / variant map | creational.md |
| Several things that must match each other (theme tokens + icons + components per platform/brand) | Abstract Factory | creational.md |
| A constructor/hook/component with 8+ optional params, or objects built across many steps | Builder | creational.md |
| Need a copy of a configured object without knowing its concrete type | Prototype | creational.md |
| Exactly one instance of a resource (SDK client, logger, cache) | Singleton = module scope | creational.md |
| A third-party/legacy API whose shape does not match ours | Adapter | structural.md |
| Two independent axes of variation multiplying files (UI × platform, feature × transport) | Bridge | structural.md |
| Tree data where leaf and group must be treated alike (menus, categories, form sections) | Composite | structural.md |
| Add behavior around something without touching it (logging, retry, auth, analytics) | Decorator / HOC / wrapper hook | structural.md |
| Callers orchestrate 3+ calls into a subsystem every time | Facade | structural.md |
| Thousands of similar items eating memory or render time | Flyweight | structural.md |
| Control access to something: lazy, cached, guarded, remote | Proxy | structural.md |
| A request passes a sequence of checks/handlers, each may stop it | Chain of Responsibility / middleware | behavioral.md |
| Actions must be queued, retried, logged, undone, or bound to several triggers | Command | behavioral.md |
| Custom traversal of a structure, or lazy/paged sequences | Iterator / generator | behavioral.md |
| Components/fields that all poke each other directly | Mediator | behavioral.md |
| Undo, draft restore, rollback of optimistic updates | Memento | behavioral.md |
| One change, many unknown listeners | Observer / pub-sub | behavioral.md |
| Boolean soup (`isLoading && !isError && data`), impossible states, `if` on status in every handler | State | behavioral.md |
| Same operation, several interchangeable algorithms (sorting, pricing, validation) | Strategy | behavioral.md |
| Several flows share a skeleton but differ in a few steps | Template Method → prefer Strategy / hooks | behavioral.md |
| Many unrelated operations over a stable set of node types (AST, blocks, order lines) | Visitor = exhaustive union switch | behavioral.md |

Read only the reference you need. Each pattern entry has the same fields: **idea**, **smell that
justifies it**, **TS/JS**, **React**, **don't**, **confused with**.

## When not to — this section outranks the tables

1. **Rule of three.** One variant is not a strategy, two is a ternary, three that keep growing is a
   candidate. A pattern for a variant that does not exist yet is speculative generality.
2. **The pattern must delete more complexity than it adds.** Count call sites and branches before
   and after. If the "after" has more files and the same number of branches, revert to the plain
   version.
3. **Follow the project first.** If the repo already solves the concern a certain way (provider
   methods for data, a store for shared state, a navigation layer), that *is* the pattern — do not
   introduce a GoF one next to it. Project skills and `AGENTS.md` outrank this skill; `frontend-craft`
   decides layering and composition, this skill only names and shapes the solution inside that.
4. **Don't textbook it.** Adapt the shape to the case: a Command does not need an interface
   hierarchy if it is a `{ run, undo }` object; a Mediator can be a reducer.
5. **Names in plans and reviews, not in identifiers.** `useCheckoutMediator`, `PriceStrategyFactory`
   are noise. Name the thing by its domain role (`useCheckoutFlow`, `priceByDelivery`) and mention the
   pattern in the PR description if it helps the reviewer.
6. **No God objects by stealth.** Facade and Mediator are the two that most often rot into one — the
   moment either knows about unrelated features, split it.

## In reviews and plans

- If a diff *claims* a pattern, check it is the right one using the "confused with" line of that
  entry (Adapter vs Facade vs Proxy vs Decorator is the most common mix-up).
- If a diff *implements* a pattern nobody asked for, apply "When not to" and propose the plain form.
- If a diff *needs* one (a growing switch, prop explosion, listeners wired by hand), name it with the
  symptom row that triggered it and the smallest shape from the reference.
- In a tech plan, name the pattern next to the step that needs it, with the symptom that justifies
  it. One line — no UML.
