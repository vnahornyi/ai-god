# Lottie format and optimisation

The subset of Lottie (Bodymovin 5.x JSON) that `scripts/lottie_kit.py` writes, and the rules that keep
a file small and drawn the same by every renderer.

## Contents

- Document shape
- Coordinates and draw order
- Keyframes, easing and holds
- Path morphs
- Masks
- Reusing content: precomps
- Renderer support
- Theming hooks
- Optimisation checklist
- Parity page
- Size budget

## Document shape

```text
root      v, fr (fps), ip 0, op (frames), w, h, assets[], layers[]
layer     ty 4 shape | ty 0 precomp (refId) · ip/op · ks (layer transform) · shapes[] · masksProperties[]
group     ty "gr" · it: [paths…, stroke, fill, transform "tr" last]
property  {a: 0, k: value}  or  {a: 1, k: [keyframe…]}
keyframe  {t, s: [value], o: {x, y}, i: {x, y}}  — the last keyframe carries only t and s
```

`lottie_kit` builds each piece: `shape_layer`, `group`, `path_item`, `fill`, `stroke`, `transform`,
`keyframes`, `path_keyframes`, `precomp`, `precomp_layer`, `animation`, `dump`.

## Coordinates and draw order

- Keep Figma's coordinates in the paths and move the whole drawing with each layer's position, the
  offset from the Figma frame origin to the composition origin. Paths stay comparable with the
  design and the model.
- `layers[0]` is drawn on top. Inside a group the first item is on top: list the stroke before the
  fill or the fill covers half the stroke.
- Colours are `[r, g, b, a]` in 0..1 (`hex_color`). Opacity is 0..100.
- A layer is alive from `ip` to `op`, exclusive; the composition plays frames `0 … op`. A layer that
  should be on the last frame needs `op = composition op + 1`, or progress 1 draws nothing.

## Keyframes, easing and holds

- The easing of a keyframe shapes the move **from** it to the next: `o` is the out-handle of this
  keyframe, `i` the in-handle of the next, both cubic-bezier points in 0..1.
- Write handles as scalars (`{"x": 0.455, "y": 0.03}`): every renderer reads them for one- and
  multi-dimensional values.
- `lottie_kit.EASE` holds named curves: `linear`, `in-out-quad` (soft default for key poses),
  `in-out-cubic`, `out-strong`, `in-out-strong`. A per-frame override is the third item of a frame
  tuple.
- A hold (`"h": 1`) keeps the value until the next keyframe: colour flips, visibility steps.
- Times may be fractional (`t: 8.727`) — segment boundaries rarely land on whole frames.
- Position on a group transform is one two-dimensional property; no spatial tangents means straight
  lines between keyframes.

## Path morphs

- Every keyframe of one path property has the same vertex count and closedness;
  `path_keyframes` raises otherwise, and `lottie_check.py` fails on it.
- A closed SVG path whose last point repeats the first is stored without the duplicate.
- Arcs (`A`) are not converted; export them as curves from Figma (outline stroke or flatten) or
  convert before baking.
- A topology change is two layers split by in/out points at a frame where both shapes are identical.

## Masks

- A mask lives in the layer's space and moves with the layer transform. To slide content under a
  fixed clip, animate a group inside the layer; keep the layer transform static.
- Use additive masks (`mode: "a"`) only. Track mattes are supported but cost more on every renderer;
  use one only when a mask cannot express the clip.

## Reusing content: precomps

Content that must appear at two depths (behind something, then in front) is one asset in `assets`
placed by two precomp layers with split in/out points (`precomp`, `precomp_layer`). The keyframes are
stored once; the file does not double.

## Renderer support

Safe on the web, iOS and Android renderers: shape layers, groups, paths with morphs, fills, strokes
(width, cap, join), group and layer transforms, opacity, additive masks, precomps, linear, bezier
and hold keyframes, solid colours, linear and radial gradients.

Avoid: expressions (ignored by native renderers), layer effects, text layers, merge paths (off by
default on Android), repeaters, 3D layers, time remapping, image layers for vector art. Check the
LottieFiles supported-features table for the exact player version when a design needs anything
outside the safe list, and say so in the report.

## Theming hooks

Native players recolour by key path (layer name / group name / item name). Give every layer and group
a stable, meaningful `nm` (`body`, `flap-open`, `letter/sheet`) so a dark theme can be applied by the
player instead of a second file. Do not rename them later without updating the colour filters.

## Optimisation checklist

1. Native keyframes for everything a transform or a same-topology morph expresses; bake only
   modelled geometry.
2. `simplify(frames, 0.05)` on baked tracks: drops samples linear interpolation reproduces.
3. `keyframes()` collapses a track whose values never change into a static value and drops a frame
   equal to both neighbours.
4. `window(frames, ip, op)` keeps only the keyframes a short-lived layer can show.
5. Precision two decimals (`PRECISION = 2`): a hundredth of a unit is invisible at illustration sizes.
6. One precomp instead of duplicated content.
7. Minified JSON (`dump` writes no whitespace). A repository formatter may pretty-print it; the app
   bundler minifies it again, so measure the budget on the minified output.

## Parity page

`scripts/parity-template.html` renders the Lottie with lottie-web and the reference model as SVG,
rasterises both to the same canvas for every frame, and counts pixels that differ by more than 48 in
any channel, as a share of the pixels either drawing inks. Fill its two placeholders:

- `/*LOTTIE_JSON*/` — the baked file.
- `/*REFERENCE_SVG*/` — a function `referenceSvg(frame, width, height)` that returns the model's
  drawing at that frame as an SVG string with the design's viewBox.

Open it in a browser the runtime can read; it shows a chart per frame, the worst frame, a keyframe
strip of diff images and `window.parity` with the numbers.

## Size budget

A small illustration (one object, a dozen particles, under two seconds) fits in 60 KB minified;
`lottie_check.py --max-kb` raises it for a larger scene when the developer agrees. Over budget, walk
the checklist before raising it.
