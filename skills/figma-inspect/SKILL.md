---
name: figma-inspect
description: Use when a task has a Figma link or UI that must match a design, in planning or implementation, to inventory every layer, state and interaction before the skeleton is built; also for styles and animations the developer assigns.
---

# Figma Inspect

**Default: styles belong to the developer** (`decisions/0003-styles-are-the-developers.md`). The
agent reads Figma to build the skeleton the business logic needs — hierarchy, content, states,
interactions — and writes no style values. Styles, assets and motion are the agent's only after the
developer assigns them for the task ("Visual work" below). Business logic is never this skill's: it
comes from the implementing stage (`wf-implement`, `frontend-craft`).

Three failure modes this skill prevents: a layer, state or interaction that never made it into the
code because nobody listed it; a style value nobody can trace (rounded to a token, copied from a
neighbour, guessed from a screenshot); and parallel runs that drift because each read the design its
own way.

## Sources, in order

1. **Figma's Dev Mode MCP server** — default; needs a Dev or Full seat. Read tools only:
   - work from a node-specific link (`node-id`); no node id → ask; never guess an id;
   - `get_metadata` — the subtree of a frame: ids, names, types, geometry. The inventory source;
   - `get_design_context` — reference code plus a screenshot: real text (a layer's name is not its
     text), component variants, values. A response flagged sparse or too large → `get_metadata` for
     the children, then `get_design_context` on the visible children in one batch;
   - `get_variable_defs` — the variables (tokens) a node uses;
   - `get_motion_context` — keyframes and easing, recursive for a subtree;
   - `get_screenshot` — the visual target; never an asset or a value source.
   On an access or seat error go to the next source, no retries.
2. **The local overlay's `figma-source.md`**, when it exists, names this developer's design source.
   Read it before the first Figma call; it replaces item 1, and everything else here stays.
3. **The signed-in browser** — `references/browser-recipes.md`: panel text and the layers tree with
   overlap checks. Fragile; any failed check means stop and repeat, not "good enough".
4. Nothing works → **stop** and tell the developer. Never build UI from memory or screenshots.

## The skeleton procedure

1. **Scope.** The developer gives a link with `node-id` per frame. Load the domain skills the router
   names for the files in scope first; a question never waits on them. Then ask, in one message:
   - which frames and states are in scope: default, pressed, disabled, loading, empty, error, dark,
     screen sizes;
   - who writes the styles and animations for each block you see — the developer (default) or agents
     from Figma ("agents do the cards, I do the header"). **Agents** → "Visual work" runs for those
     blocks, this task only; **developer** or no answer → skeleton only. A plan whose `Styles:` line
     says the work is assigned already answers this.
2. **Inventory.** The structure of every frame in scope, one read per frame; keep every visible node.
3. **States.** For the frame or its main parts: each component's variant axes
   (`Card[Message=on][Button=off]`) and the real text. Layers hidden in this instance show up as
   variant values — each value is a state the logic must support. A state needed by the logic and
   visible nowhere is a question for the developer.
4. **Coverage table** — `references/coverage-table.md`. Every inventory node gets a row and a status.
   Before reporting, the row count equals the inventory count; an interactive element or state that
   is not `mapped` means the skeleton is not ready.
5. **Report** the table, the questions, and — unless visual work is assigned — the places where the
   developer adds styles (component → node id).

Allowed in the skeleton: markup hierarchy and order (from auto-layout direction), existing
design-system components (a Code Connect mapping names the one to reuse), text through i18n, states,
handlers, navigation, data flow, accessibility attributes. A component's variant/size prop only when
the Figma instance names that variant; otherwise the component's default, noted in the report.

Forbidden without visual work: spacing, sizes, colours, fonts, radii, shadows, animations, inline
styles, new style files, values copied from neighbouring components or the sibling platform, "like
the developer did there", library defaults chosen as styling, placeholder values.

## Visual work — only on the developer's assignment

Scope: layout values (auto-layout → the platform's layout, gaps, padding, sizes, constraints),
colour, typography, radii, borders, shadows and effects, static assets, the visual difference between
states, and motion. A visual change that needs a logic change is a question, not a line you write.

1. **Envelope, before the first value.** Read only what decides representation: the styling method,
   theme or token files, existing primitives, the asset folder and unit conventions; for React or
   React Native, `frontend-craft` → `references/house-style.md`. Design code from the source (often
   React + Tailwind) is a reference prototype: translate it into the project's styling system, and
   absolute positioning into native layout unless the design only works fixed. No new dependency
   without the developer's approval.
2. **Values table, read once by the orchestrating session.** One row per element and property:
   `block → element (node id) → property → value → source (node id | token | approved <date>)`.
   A token only when its value is **exactly** equal; otherwise the literal value, marked "no token".
   Never round: Figma `15` against a `space-4 = 16` token stays `15`. States: only those Figma shows
   as variants. Motion rows add trigger, property, from → to, duration and easing or spring; for
   React Native run the `react-native-animations` gate first, and motion the developer asked for that
   Figma does not specify takes that skill's defaults, each marked "default react-native-animations".
3. **Assets.** Download each as the source says; no temporary Figma URL stays in code. Never redraw,
   inline, crop or substitute an asset; add no icon package.
4. **Blocks.** Split the work into blocks: a component or region with its own files, no file in two
   blocks. Shared changes (a token, a theme entry, an asset several blocks use) are made by the
   orchestrating session first. One block, or a developer who wants to watch → inline. Otherwise each
   block is one background subagent, run mode `background` (the runtime adapter → Run modes gives the
   model and how it starts), all in one worktree from the `worktree` skill — never the developer's
   working tree. Each brief comes from `references/block-brief.md` and carries only that block's rows,
   files, screenshot and checks; the subagent does not open Figma.
5. **Integrate and verify.** Every changed style line in a block's diff has a row in the table; a
   value without a row is reverted, whatever it is. Run the project's checks for the touched files.
   Render the screen where the project has a way (simulator, Storybook, a dev server) and compare it
   with the Figma screenshot at the same size; fix a delta only when a table row explains it, no
   tuning by eye. No render path → report it as visually unverified. Pixel parity is confirmed by the
   developer or QA, not by AI review.
6. **Report** per block: files changed, the provenance table, "no token" values, defaults used, what
   was not verified, open questions.

Staging and the commit go through the Git rules in the global agent instructions.

## Token discipline

Text over screenshots. One structure read per frame, not per element. Read each node once; record
it in the table instead of re-reading.
