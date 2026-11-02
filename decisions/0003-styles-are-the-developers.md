# 0003 — Style values are the developer's unless visual work is assigned

**Context.** Spacing, colour, type, radii and motion copied from neighbouring code or guessed from a
design drift from the design system and are expensive to review: every value looks plausible.

**Decision.** By default a diff adds no style values. Structure, states, handlers, i18n text and
accessibility come from the design inventory (`figma-inspect`); the values stay with the developer.
When the developer assigns visual work, every value traces to a Figma node, an equal token or the
developer's approval and is listed with its source. Motion the developer asks for follows
`react-native-animations`: its defaults, each labelled in a provenance table.

**Consequences.**
- AI review checks states, behaviour and style provenance, never pixel parity — that is human QA.
- A plan carries no style values unless visual work was assigned.
- An implementer that "fills in" a value is a review finding, whatever the value.

**Source.** `frontend-craft` → `mode-build` Gate 2 Styles; `figma-inspect`; `ai-workflow` §5;
`wf-review` → `review-contract` → Design verification boundary.
