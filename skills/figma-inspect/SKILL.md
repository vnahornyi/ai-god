---
name: figma-inspect
description: Read a Figma frame so that no layer, state or interaction is missed — a full layer inventory and a coverage table for building the UI skeleton, with zero style values unless the developer assigned visual work. Use whenever a task has a Figma link or UI that must follow a design, in planning or implementation. Do not use for pixel QA, design critique or editing the Figma file.
---

# Figma Inspect

**Default: styles belong to the developer.** The agent reads Figma only to build the skeleton the
business logic needs — hierarchy, content, states, interactions. It writes no style values. Visual
work is the agent's only when the developer assigns it for the task (see "Visual mode").

Two failure modes this skill prevents: a layer, state or interaction that never made it into the
code because nobody listed it; and a style value nobody can trace, which is hard to find and fix
later. Every invented or unapproved change lands on the developer.

## Sources, in order

1. **TemPad Dev MCP** — reads the file open in the developer's signed-in browser; works for viewers
   (no edit access, no Dev Mode). Read-only tools only:
   - `list_design_sessions` — which file is open; use its `sessionId` on every call;
   - `get_structure` — the whole subtree of a node in one call: ids (including instance paths),
     names, types, geometry. A node on another page returns `NODE_NOT_VISIBLE`: load the page first
     with `get_structure` + `pageId` (`depth: 0`), then retry;
   - `get_code` — real text content (a layer's name is not its text), component **variant axes**
     (the states the logic needs), tokens;
   - `get_screenshot` — only to locate an element, never as a source.
   Calls to one file run one at a time (`DESIGN_TASK_BUSY` otherwise). Never call canvas-writing or
   task tools (`apply_canvas`, `manage_design_task`, `set_design_anchor`, `upload_asset`).
2. **Figma's own MCP** — only for files where the developer is an editor; on "no edit access" go
   straight to the next source, no retries.
3. **The signed-in browser** — `references/browser-recipes.md`: panel text and the layers tree with
   overlap checks. Fragile; any failed check means stop and repeat, not "good enough".
4. Nothing works → **stop** and tell the developer. Never build UI from memory or screenshots.

## The procedure

1. **Scope.** The developer gives a link with `node-id` per frame. Ask which frames and states are in
   scope: default, pressed, disabled, loading, empty, error, dark, screen sizes.
2. **Inventory.** `get_structure` on every frame in scope; keep every visible node.
3. **States.** `get_code` on the frame (or its main parts): collect each component's variant axes
   (`Card[Message=on][Button=off]`) and the real text. Layers hidden in this instance show up as
   variant values — each value is a state the logic must support. A state needed by the logic and
   visible nowhere is a question for the developer.
4. **Coverage table** — `references/coverage-table.md`. Every inventory node gets a row and a status.
   Before reporting, the row count equals the inventory count; an interactive element or state that
   is not `mapped` means the skeleton is not ready.
5. **Report** the table, the questions, and the list of places where the developer adds styles
   (component → node id).

## What the skeleton may contain

Allowed: markup hierarchy and order (from auto-layout direction), existing design-system components,
text through i18n, states, handlers, navigation, data flow, accessibility attributes. A component's
variant/size prop only when the Figma instance names that variant; otherwise the component's default,
noted in the report.

Forbidden: spacing, sizes, colours, fonts, radii, shadows, animations, inline styles, new style
files, values copied from neighbouring components or the sibling platform, "like the developer did
there", library defaults chosen as styling, placeholder values.

## Visual mode — only on the developer's explicit assignment

Then, additionally: every value comes from the node (`get_code`, the properties panel) or a token
whose value is **exactly** equal, or from the developer's approval in chat. No exact token → the
literal value, flagged "no token". Never round to the nearest token. Report a provenance table
`element → property → value → node id | token | approved <date>`. Pixel comparison stays human QA.

## Token discipline

Text over screenshots. One `get_structure` per frame, not per element. Read each node once; record
it in the table instead of re-reading.
