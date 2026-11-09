# LV-RUG-01 — living room rug

A 2.50 × 1.80 m bound-edge floral rug, 0.022 m maximum height, +Z up with origin at floor center. The top is a lightly irregular mesh with a single full-range UV; four narrow rounded bound-edge pieces are joined into the export. The rug is a stationary decorative asset; no animation is implied.

## Art direction and candidates

The source concept is `concepts/rug-v1.png`, guided by `painterly-fixer-upper.png`. Two independent image-generated flat albedo candidates are retained as `textures/rug-candidate-a.png` and `rug-candidate-b.png`. Candidate A was selected (`rug-albedo.png`) for its softer, aged palette, smaller central floral cluster and closer visual balance to the concept; candidate B is cleaner and more saturated. Both are complete, flat overhead images with no baked surrounding floor or text. The coloration conveys painterly weave without sculpted paint thickness. The modeled edge is deliberately understated; the scene lighting should decide whether it needs a more textile-like material.

## Files and rebuild

- `model/build_rug.py` creates the mesh, UVs, material slots, `.blend`, FBX, and actual Blender model previews. Run with `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_rug.py` from any directory.
- `model/LV-RUG-01.blend` includes the packed albedo, and `model/LV_RUG_01.fbx` is the game export. Use `textures/rug-albedo.png` with the `Rug_PaintedFloral` material; `Rug_BoundEdge` is a separate rough material slot.
- `previews/rug-three-quarter.png` and `previews/rug-top.png` are rendered from the model, not the concept.
- `model/validate_fbx.py` reimports the FBX and checks finite vertices and UVs, nonzero triangle area, and reports dimensions. Blender 5.2.3 round-trip: 1,209 vertices, 2,288 triangles, 2.50 × 1.80 × 0.022 m; passed.

Unreal texture/material reconstruction, collision (use no blocking collision), floor placement to avoid z-fighting, and appearance under final room lighting remain untested. The top image should use non-tiling UVs and an appropriate high-resolution mip/sampler setting; do not use the concept sheet as a texture.
