# In-betweening — from Figma poses to natural motion

## Contents

- Poses are evidence, motion is a model
- Rigid parts: solve the parameter, not the points
- Turning out of the plane: hinges, flaps, doors, pages
- Switching topology at the right moment
- Contact reactions
- Things that appear: emit from a source
- Depth: when the stacking order changes
- Spacing and easing
- Frame rate and baking
- Checking the model against the poses
- Worked example: an envelope that opens and throws confetti

## Poses are evidence, motion is a model

A designer's keyframes are key poses: drawings of where things are at a few moments. They are exact
at those moments and silent between them. Blending the drawings (linear interpolation of path points,
cross-fading opacity) produces motion no physical object makes: shapes shear, shrink through their
midpoint, or swap places as if they were two objects.

Before writing any in-between, name the action that carries each part from one pose to the next:
translation, rotation about a pivot, rotation about a hinge line out of the picture plane, a fold, an
emission from a source, a flip. The model is that action with its parameters solved from the poses.
A pose that the action cannot reproduce exactly means the action is wrong or the pose hides a second
action; ask the developer or the designer before inventing one.

## Rigid parts: solve the parameter, not the points

A part whose shape does not change between two poses is rigid. Find its pivot and its parameters:

- **Translation:** the difference of any matching point (use the bounding-box centre when the shape
  is symmetric).
- **Rotation in the plane:** the angle between one matching edge in both poses; the pivot is where the
  perpendicular bisectors of two matching points meet. When the design gives the rotation (a
  transform in the layer), use it instead.
- **Scale:** the ratio of matching edge lengths along each axis.

Encode the result as transform keyframes on a group (anchor = pivot, position = where the pivot
goes). Never bake the points of a rigid part: the file grows and the motion loses the exact easing.

## Turning out of the plane: hinges, flaps, doors, pages

A flat part turning about a hinge line that lies in the picture plane (an envelope flap, a lid, a
door, a page) keeps its length along the hinge and changes only its projected depth across it.

1. **Measure each pose.** The projected distance `d` of the part's far edge or apex from the hinge
   line, with sign (towards or away from the viewer's side of the hinge). `L` is the true length,
   from the pose where the part lies flat.
2. **Choose the projection.** Orthographic: `d = L · cos θ`. It collapses the part to a line at 90°,
   which reads as the part vanishing. Add a slight camera tilt so the edge-on part keeps a sliver:
   `f(θ) = cos θ − k · sin θ` with `k` between 0.3 and 0.4, then `d = L · f(θ)`. Pick `k` so every pose
   still solves.
3. **Solve the angle per pose:** `θ = solve(f(θ) = d / L)` on `[0, π]`. The sequence of angles is the
   motion; interpolate the angle, never the points.
4. **Draw from the angle:** every point keeps its coordinate along the hinge and gets
   `hinge + (p − hinge) · f(θ)` across it. Width along the hinge never changes; a turn that changes
   the width reads as the part shrinking.
5. **Two-sided surfaces:** the side facing the viewer flips at edge-on (`f(θ) = 0`). The fill
   switches there in one frame (a hold keyframe), never through a fade: a fade shows a colour that
   neither side has.

## Switching topology at the right moment

The open pose of a part is often drawn with a different path structure from the closed pose (more
corners, a different start point). A morph between them is impossible, and a cut between them shows
as a jump unless both shapes are identical at the cut.

- Cut where both shapes collapse to the same drawing: for a hinged part, edge-on, where both reduce
  to the hinge line.
- Past the cut, grow the new shape out of that line: keep the base fixed on the hinge, move only the
  tip, and scale the rise by the same `f(θ)` so the speed is continuous across the cut.
- Clamp every vertex of the growing shape to its side of the hinge. A vertex that dips below the
  hinge line for even one frame shows as stroke "whiskers" at the sides.
- Check the frames on both sides of the cut at 4× zoom. The part must read as one object turning
  through: the same hinge, the same width, no step.

After the cut the open shape follows the designer's open poses as a normal morph (same topology).

## Contact reactions

Where two parts meet, the one that is not moving still reacts: a corner radius that made sense
while the parts were separate must close when they join, and open again after.

- Tie the reaction to the moving part's parameter, not to time: `openness = smoothstep(1 −
  |f(θ)| / range)` with `range` around 0.6, so the reaction peaks at contact and fades either side.
- Animate the geometry (radius toward 0, overlap), never the width or position of the neighbour.

## Things that appear: emit from a source

A particle, a letter or a sparkle that is absent in one pose and present in the next must come from
somewhere in the scene, not fade in place.

- Give it a start pose inside its source (the envelope, the box, the hand), hidden behind the
  source's front layer, at the source's opening.
- Move it out along the path its later poses imply; keep its opacity at the pose value, not ramped.
- Fade out only at the end, over the last segment, when the design ends with it gone or faint.

## Depth: when the stacking order changes

A part that starts behind another and ends in front of it (a letter rising out of an envelope,
confetti clearing the pocket) needs two copies at two depths. Switch at the moment the part's visible
edge clears the occluder, never at a pose boundary by default.

- In the model: one boolean per part, `isBehind(progress)`.
- In Lottie: two layers at the two depths with in/out points split at the switch frame; for large
  content, one precomp asset placed twice. Never toggle opacity on two always-alive copies.

## Spacing and easing

- **Key poses with holds** (the designer drew a pose to be seen): ease in and out of every pose,
  per segment. Quadratic in-out is the soft default; label it a default.
- **Samples of one continuous motion** (the poses are points on one throw or one turn): one curve over
  the whole span; per-segment easing would stop at every sample and look mechanical.
- **Physical cues:** something thrown decelerates as it rises and accelerates as it falls; a hinged
  part accelerates through edge-on. Spacing that ignores them reads as "unnatural" even when every
  pose is right.
- The total duration comes from the design; without it, a default the developer confirms. A rare
  celebration has room for 1–2 s; UI motion stays under 300 ms and is not this skill's.
- Overlap and follow-through (a part settling after it stops) only when the design or the developer
  asks.

## Frame rate and baking

- The model is continuous; it has no frame rate. The composition runs at the target rate (60 fps).
- Bake modelled layers at every composition frame inside their non-linear span, add the exact
  segment boundaries, then drop the samples linear interpolation reproduces within 0.05 units
  (`lottie_kit.simplify`). Everything else stays native keyframes.
- Keep the last frame drawable: every layer that should be visible at the end lives one frame past
  the composition end.

## Checking the model against the poses

Print, for each keyframe time and each layer, the largest point distance between the model and the
Figma path; every value ≤ 0.05 units. Then look at the preview at 60 fps, at the cut frames zoomed,
and at the keyframe strip next to the Figma frames. The developer approves the motion; only then
encode.

## Worked example: an envelope that opens and throws confetti

Twelve poses: closed, flap rising, flap edge-on, flap open, letter rising, confetti thrown, settled.

| Layer | Class | Model |
|---|---|---|
| Flap | modelled | angle solved per pose from the apex height with `k = 0.35`; closed topology until edge-on, open topology rising from the hinge after; fill flips at edge-on |
| Body | morph | top corner radius 4 → 0 → 4 driven by the flap's `f(θ)` |
| Letter | rigid | vertical offset per pose; behind the body until it clears the flap, then in front; clipped by the envelope frame |
| Front pocket | discrete | fill fades in over the first segment, the outline is always drawn |
| Confetti ×12 | emitted + rigid | start inside the envelope behind the pocket, then the designer's positions and turns; in front once clear; fade over the last segment |

Remarks that changed the model, in order: the flap slid instead of turning (points were lerped);
past 90° it closed from behind (a mirrored copy); the fold broke (topology cut before edge-on); the
width changed (scaled along the hinge); the colour faded (no hold); the sides showed a border (rise
crossed the hinge); confetti appeared from nowhere (no source). Each row of the red-flag table in
`SKILL.md` is one of these.

Result: 8 layers, one precomp, 278 keyframes, 47 KB minified, parity with the model 0.5 % mean.
