# House style

The house-style rules in `SKILL.md`, each with when it applies and when it does not. Read before
writing or reviewing component code. Bad / good / over-applied code pairs for these rules live in the
local overlay (`style/house-style-examples.md`); read that file too when it exists. Each entry ends
with one yes/no check; answer it for every component in the diff before staging.

Over-applying a rule matters as much as missing it: a rule applied where its threshold is not met is
a defect too, and reviewers will ask you to undo it.

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

Check: does any `?` expression contain another `?` expression?

## Conditional rendering — inline

Rule: a simple condition stays in the JSX (`SKILL.md` → Conditional rendering).
Applies when: one condition with `&&`, or one two-way ternary, and the JSX in the branch is a few lines.
Does not apply when: the branch has nested conditions, three or more states, a `switch`, or JSX long enough to hide the layout around it — see the next entry.

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

Check: does any JSX expression hold more than one condition? If yes, it needs a name.

## Conditional rendering — guard states

Rule: a guard on the whole output is an early return at the top of the component (`SKILL.md` → Conditional rendering; `composition.md` → Functional style).
Applies when: the component renders nothing, or only a loading / empty / error state, for some input.
Does not apply when: only part of the output depends on the state — that part is a branch inside the JSX.

Check: does the component's `return` call a helper that holds the whole output? If yes, move the guard up and inline the rest.

## JSX through a mutable `let`

Rule: never assemble JSX through a `let` reassigned across branches (`SKILL.md` → Conditional rendering).
Applies when: a `let` holds JSX and an `if`/`switch` reassigns it.
Does not apply when: a `let` holds a non-JSX accumulator inside a pure function (`composition.md` → Functional style).


Check: does any `let` in a component hold JSX?

## Function signatures

Rule: three or more parameters or a boolean flag → one object with named fields; one returned value → the value itself (`SKILL.md` → Function signatures).
Applies when: you write or change a function's parameters or its return type.
Does not apply when: the signature is fixed by a library or a callback contract, or the result carries several values the caller uses together.

Check: does any call site in the diff pass three or more positional arguments or a bare `true`/`false`/`null`, or read the only field of a returned object?

## Comments

Rule: default zero; a comment carries business or domain knowledge absent from the code (`SKILL.md` → Comments).
Applies when: always.
Does not apply when: never — but a project rule that mandates a comment is satisfied in one line carrying the domain why.

Check: for each comment in the diff — could a reader who sees the whole file know this without it? If yes, delete it.
