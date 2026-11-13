---
name: figma-to-lottie
description: Use when an illustration, celebration or other non-UI animation drawn in Figma as a row of keyframes (frames or variants, one pose each) must become a Lottie file, or when an existing Lottie animation must be smoothed, fixed or made smaller.
---

# Figma to Lottie

Without this skill the agent fills the gaps between Figma poses by blending points or cross-fading:
a hinged part slides instead of turning, one part reads as two elements at the switch, particles pop
out of nowhere, a two-sided surface fades its colour. Then it hand-writes or exports a Lottie file
that a native renderer draws differently, or that weighs hundreds of kilobytes.

Motion is visual work: it belongs to the developer until they assign it for the task
(`figma-inspect` → Visual work). Once it is assigned, this skill owns the path from poses to a
verified Lottie file. A project skill for Lottie (where files live, the player, theming, tests) wins on
placement and playback.

## Rules that hold on every path

- **The poses are evidence; the motion is a model.** Every Figma keyframe is reproduced exactly at its
  time. What happens between two poses comes from the physical action that connects them (a hinge
  turning, an object rising, particles thrown), never from interpolating the two drawings.
- **One reference model, one bake.** Write the motion as a pure function `progress → frame` (paths,
  colours, opacity, z-order). The preview, the Lottie file and the parity check all read that model.
  Corrections go into the model and the file is baked again; never edit the Lottie JSON by hand.
- **Cheapest Lottie primitive that reproduces the model:** transform keyframes for rigid movement,
  path keyframes for a morph with one topology, baked path samples only for non-linear geometry,
  hold keyframes and layer in/out points for discrete switches. Details: [Lottie format and
  optimisation](references/lottie-format.md).
- **Only what every native renderer draws:** shape layers, groups, paths, fills, strokes, transforms,
  masks, precomps, linear/bezier/hold keyframes. No expressions, effects, text, merge paths or 3D.
- **The developer judges the motion before it is encoded**, on a preview that plays at the target
  frame rate. Numbers prove parity, not that the motion feels right.

## Pipeline

Each step ends on its criterion; do not start the next one before it holds.

1. **Inventory the poses.** Read the component with `figma-inspect`: every keyframe frame in order,
   every layer in every frame, exported as SVG in one shared coordinate space (same frame size, same
   origin). Record per pose and layer: path, fill, stroke, opacity, stacking position, and whether the
   layer exists. Read timing from the design when it has any (prototype transitions, durations,
   easings, a motion spec); otherwise the duration and easing are defaults you label as such.
   *Done:* a pose × layer table with no guessed cell. A layer absent from a pose is written as absent.

2. **Classify every layer's motion.** One class per layer, with the evidence from the table:

   | What the poses show | Class | Lottie primitive |
   |---|---|---|
   | Same shape, moved, turned or scaled in the picture plane | rigid | group transform keyframes |
   | Same command structure, points moved | morph | path keyframes |
   | A part turning out of the plane, folding, rolling, swinging along an arc | modelled | baked path samples |
   | A part that appears or disappears | emitted | emerges from a source in the scene |
   | A colour, side or stacking order that flips | discrete | hold keyframe, or two layers split by in/out points |

   *Done:* every layer of the table has a class; every "modelled" and "emitted" layer names its
   physical action (hinge line, pivot, source).

3. **Build the in-betweens.** Follow [In-betweening](references/inbetweening.md): solve the hidden
   parameter of each modelled part from the poses (an angle from an apex height, a pivot from two
   positions), pick the spacing per segment, add the contact reactions and depth switches.
   *Done:* a script prints, for every keyframe time, the largest distance between the model's output
   and the Figma path of every layer, and every value is ≤ 0.05 units.

4. **Preview and get the developer's approval.** A page that draws the model with play at the target
   frame rate (60 fps), a frame scrubber and a keyframe strip. Show it to the developer; turn each
   remark into a model change and show it again.
   *Done:* the developer says the motion is right. Each remark that changed the model is noted for the
   report.

5. **Encode.** Bake with `scripts/lottie_kit.py` (import it from a one-off bake script that reads the
   model's output): the primitives from step 2, the optimisations from the format reference.
   *Done:* `python3 scripts/lottie_check.py <file>` exits 0 within the budget.

6. **Prove parity.** Fill `scripts/parity-template.html` with the Lottie JSON and the model's SVG
   renderer and open it: it rasterises both for every frame and charts the share of differing pixels.
   *Done:* mean under 1 % of the drawn area, every frame over 2 % looked at and explained (anti-aliased
   edges under a pixel are fine; a missing or misplaced part is not), and the last frame
   (progress 1) still draws every layer.

7. **Hand off.** The Lottie file goes where the project skill says; the bake script and preview stay
   outside the repository unless the project keeps generators. The report lists: the pose table
   source (node ids), the class of each layer, every timing value with its provenance (`design <node>`
   | `developer <date>` | `default`), the check output (size, layers, keyframes) and the parity
   numbers, and what still needs a release build on a device.

## Red flags — stop and go back to step 3

The developer's words in the left column are the ones heard when the in-betweens were built by
blending poses; each maps to a cause in [In-betweening](references/inbetweening.md):

| Heard or seen | Cause |
|---|---|
| "looks like two separate elements", "it slides" | points interpolated across a turn instead of a rotation about a fixed hinge |
| "broken at the fold", a kink at 90° | topology switched while the two shapes were not identical |
| "closes from behind after 90°" | the far side of the turn reuses the near-side shape, mirrored |
| "the width changes while it turns" | the turn scaled the axis it turns around |
| "a border sticks out at the sides" | vertices of the rising part crossed the hinge line |
| "the colour fades", "a stripe of the wrong colour" | a two-sided surface faded instead of flipping at edge-on |
| "the corner looks wrong where they meet" | the neighbour did not react to the contact (radius, overlap) |
| "confetti appear from nowhere" | an emitted layer with no source or no depth switch |
| "creepy", "unnatural" with no detail | uniform spacing, or one ease across poses that are key holds |

## Never

| Never | Instead |
|---|---|
| Interpolate two drawings of a part that turns, folds or rolls | solve its angle and draw it from the model |
| Fade a colour that belongs to the other side of a surface | hold keyframe at the edge-on frame |
| Animate the transform of a masked layer | animate a group inside it; the mask stays in layer space |
| Bake every frame of something a transform expresses | transform keyframes |
| Duplicate content to put it at two depths | one precomp asset, two precomp layers split by in/out points |
| Edit the encoded JSON by hand | change the model, bake again |
| Ship on a lottie-web preview alone | parity numbers plus a release build on the slowest supported device |
