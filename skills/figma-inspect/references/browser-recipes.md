# Browser recipes

Everything below runs in the **signed-in browser**, as JS injected into the Figma tab, or as clicks
at canvas coordinates. The runtime adapter's *Browser* section says which capability is which and
lists the runtime's own quirks (notably: injected JS may not await promises — park the result on
`window` and read it in a second call; output truncates after a few thousand characters).

Figma's DOM has no stable hooks: class names are hashed and `data-testid` attributes did not survive
between sessions. Every recipe here therefore matches on **text shape**, not on selectors.

## 0. Open and confirm the session

Fallback only — prefer TemPad Dev MCP (see `SKILL.md`). Navigate to the link as given, including
`node-id`. A **viewer in Design mode** has both the layers panel and a read-only properties panel
(verified 2026-10-13), so view-only is not a reason to stop. If the URL switches to `m=dev` and an
upsell dialog appears, click "Back to Design Mode".

## 1. Select the deepest layer

Click on the canvas at the element's coordinates **with the platform modifier held** (⌘ on macOS,
Ctrl elsewhere). One click, deepest layer, no drilling.

Pitfalls that cost time:

- **Escape does not select the parent** — it deselects. To go up a level, ⌘-click something in the
  parent's padding area instead.
- **Layers-panel rows lag.** Clicking a row in the tree registers late and often lands on the wrong
  row after the tree scrolls. Use the canvas.
- A point in the gap between two children selects their container — which is exactly how you read a
  container's padding and gap.

## 2. Scrape the properties panel

```js
window.__panel = () => {
  const cands = [...document.querySelectorAll('div')].filter(d => {
    const t = d.innerText || '';
    return /\bExport\b/.test(t) && /Layout|Typography|Content|Colors/.test(t) && t.length < 4000;
  });
  if (!cands.length) return 'NOPANEL';
  const el = cands.sort((a, b) => a.innerText.length - b.innerText.length)[0];
  return el.innerText.replace(/Color format\nHex\n/g, '').replace(/\n{2,}/g, '\n');
};
__panel()
```

Why it is written this way:

- `Export` plus one of the section headers identifies the right-hand panel without selectors.
- `length < 4000` is the safety cap: pick a container that is too high in the tree and you dump the
  document. It is a budget, not a measurement — raise it deliberately if a genuinely large panel is
  truncated.
- **Smallest match wins.** The panel is nested inside several wrappers that all contain the same
  text; the innermost one is the panel itself.
- The replacements strip the colour-format chrome and blank runs so the text stays compact.

The text comes back as labelled lines — position and size, layout (padding, gap, alignment),
typography (family, weight, size, line height), fills, strokes, effects. Read the numbers off it
verbatim. Do **not** round, convert or "correct" anything; keep only the values the implementation
needs.

## 3. Zoom and pan

Only needed to bring something into view for a click, or to confirm what you selected.

```js
const c = document.querySelector('canvas');
window.__zoom = (x, y, d, n = 1) => {
  for (let i = 0; i < n; i++)
    c.dispatchEvent(new WheelEvent('wheel',
      { clientX: x, clientY: y, deltaY: d, ctrlKey: true, bubbles: true, cancelable: true }));
};
window.__pan = (dx, dy, n = 1) => {
  for (let i = 0; i < n; i++)
    c.dispatchEvent(new WheelEvent('wheel',
      { clientX: 700, clientY: 400, deltaX: dx, deltaY: dy, bubbles: true, cancelable: true }));
};
'ready'
```

- `ctrlKey: true` makes a wheel event a zoom; without it, it pans.
- **Zoom is exponential.** `deltaY: -10` is roughly ×1.15 per step — the unit to use. `deltaY: -100`
  overshoots catastrophically (25600% and 4096% both happened in one session). Step in small `n`
  and read the zoom level back before stepping again.
- Read the level back with `[...document.querySelectorAll('button,span')].map(b => b.textContent).filter(t => /^\d+%$/.test(t))[0]`.
- Give the canvas ~300–1500 ms to settle before reading anything after a zoom.
- `Shift+1` (zoom to fit) via a synthetic `keydown` on `document` is the cheap way back to a known
  state after you lose yourself.

## 4. Layer inventory from the layers panel

Rows carry their node id: `[data-testid="<nodeId>-layers-panel-row"]`; the nearest `[aria-level]`
ancestor gives the depth and `aria-expanded`; an icon's `data-tooltip` gives the type (Auto layout,
Instance, Text…); the caret is `[data-testid=layers-panel-expand-caret]`.

1. ⌘-click the frame on the canvas — the panel reveals its path.
2. **Expand the whole subtree with one real Alt-click on the frame's caret.** Synthetic JS events are
   ignored (`isTrusted`). If the row is already expanded, the first Alt-click collapses it
   recursively; wait, re-read the caret position, then Alt-click again. The panel scrolls by itself —
   compute the caret position immediately before clicking.
3. Scrape while scrolling, with an **overlap check**: each batch of rendered rows must contain a row
   already seen; if not, scroll back and retry. The list is virtualized — a plain scroll silently
   skips rows, which is exactly how layers get lost.

```js
window.__rows = () => [...document.querySelectorAll('[data-testid$="-layers-panel-row"]')].map(r => {
  const a = r.closest('[aria-level]');
  return { id: r.dataset.testid.replace('-layers-panel-row', ''), name: r.innerText.trim(),
           level: a?.getAttribute('aria-level'), exp: a?.getAttribute('aria-expanded') };
});
```

4. Accept the inventory only when: no gaps, no level jump greater than one between consecutive rows,
   and `aria-expanded=false` remains only on rows you deliberately left closed. Any failure → repeat;
   two failures → stop and tell the developer.

## 5. What not to do

| Temptation | Why it fails |
|---|---|
| Read numbers off a zoomed screenshot | Measured, not stated — and every screenshot costs more than the panel text it replaces |
| Accept an inventory scraped without the overlap check | The virtualized list drops rows silently |
| Re-select a layer to "double-check" | The value is already in your notes; re-reading is a wasted round-trip |
| Retry a failed scrape unchanged | `NOPANEL` means nothing is selected — fix the cause |
