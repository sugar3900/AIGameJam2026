# ARC-SLIDING-CLOSET-02 — fitted coat/guest bypass front

Fitted successor to ARC-SLIDING-CLOSET-01 for the approved revision 02 coat and guest storage. Reuses the original ivory painted wood, field molding and recessed-looking brass pulls at their original sizes. **Source complete; Blender visual and FBX validation passed. Unreal import/motion/collision review remains pending.** No existing exports were changed.

This is a front kit only: no duplicate room walls, storage shell, shelves, rail, floor, or ceiling. Use it twice on the back-to-back storage volumes. It is not the hinged bedroom mold-closet door.

## Opening and dimensions

- Rough wall opening **0.96 m wide × 2.18 m high**. Two jamb linings are **0.03 m** thick at x=±0.465, so outer lining faces are x=±0.480 and inner faces are x=±0.450. The head lining is 0.03 m high, z=2.15–2.18.
- Nominal clear jamb opening **0.90 × 2.15 m**. This corrects the older 0.07 m jamb linings whose overall 1.04 m width did not fit the specified 0.96 m rough cut. Moldings/hardware are not nonuniformly scaled.
- Overall casing/cap width **1.08 m**; cap top **2.2575 m**. Casing fits within the 1.25 m coat/guest bay. Lining depth is 0.14 m; the head cap reaches y=−0.099 and rear casing y=+0.0905 m. At a 0.12 m wall, it projects beyond each wall face; align the frame center to the actual wall centerline.
- Two panels each **0.46 × 2.105 m**, slab depth 0.024 m, lower edge z=0.020 and top z=2.125. Front/back tracks are y=−0.028/+0.028, retaining the **0.056 m** separation. Molding/pulls have approximately 5 mm nominal depth clearance when the panels overlap; test actual collision and rendered fit in engine.
- Closed panels overlap 0.02 m at center. Open the left/front panel **+0.44 m local X**, or the right/back panel **−0.44 m local X**. This reveals about **0.44 m accessible width**, not 0.90 m. It is reach-in storage, not a person-sized doorway. Opening one side closes the other; use one panel-open state at a time.

## Files and placement

- `model/ARC-SLIDING-CLOSET-02.blend`: editable closed-pose source with packed texture.
- `model/build.py`: headless builder adapted from the original kit.
- `model/validate.py`, `model/validation.json`: FBX round-trip/motion-bound checks.
- `model/ARC_Sliding02_Frame.fbx`: frame and tracks, with **three separate** UCX boxes for the two jambs and header. No collision box seals the opening.
- `model/ARC_Sliding02_LeftPanel.fbx`, `ARC_Sliding02_RightPanel.fbx`: independent panels, each with one convex slab UCX hull.
- `assembly.json`: source offsets, export conventions and movement values.
- `previews/`: front/back and perspective views, open and closed. The transparent background is not a modeled storage interior.

Source units are metres, **+Z up, −Y front, +X across the opening**. FBX uses explicit forward −Y/up Z. Every exported object origin is zero. Assemble frame at `(0,0,0)`, left/front panel at **(−0.22, −0.028, 0)** and right/back panel at **(+0.22, +0.028, 0)**, then animate along local X. Check handedness through the existing Unreal importer before mapping the two opposite-facing closet placements; do not just place both normalized panel files at frame origin.

## Materials and collision

`textures/ivory-paint-reused.png` is unchanged from the original kit. The Blender material mixes the generated ivory image at 65% with warm ivory `(0.85,0.79,0.68)` at 35%, roughness 0.78. Brass, inset shadows and track have separate material slots. Reuse the matching existing Unreal materials or reproduce these nodes; FBX does not automatically preserve the graph. Pulls look recessed through bezel/dark inset geometry rather than a boolean hole.

Enable imported UCX collision. Moving panels should use their convex slab hulls and travel with the component; don't replace the frame with a single convex hull. Top/bottom guide rails are visual and excluded from UCX so a floor-level rail doesn't snag the player. Nominal closed panel side edges meet the jamb faces; resolve any desired animation tolerance with the integration team.

## Validation

`Blender -b --python-exit-code 1 --python model/build.py` rebuilds. `Blender -b --python-exit-code 1 --python model/validate.py` independently reimports each FBX and checks finite vertices/UVs, UV presence, nondegenerate triangles, normalized object origins, UCX hull counts, the corrected rough/clear lining bounds, full 0.44 m travel within jambs and more than 4 mm nominal hardware clearance between overlapping panels. Front/open/back renders were inspected. Actual engine axis conversion, click traces, capsule collision and both placement clearances remain integration work.
