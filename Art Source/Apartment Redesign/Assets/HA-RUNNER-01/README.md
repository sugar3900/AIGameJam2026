# HA-RUNNER-01 — hall runner

A narrow, faded floral flat-woven runner for the A+ hall. The target is 6.00 × 0.80 m, with an olive/sage ground, warm-rose floral binding and softly scattered cream/rose flowers. The sage direction was chosen over a separately generated rose-ground alternative to distinguish it from the living-room rug and contrast with the honey wood floor. Art style is painterly; wear is restrained rather than heavy grime.

## Reference and texture decisions

- `concepts/runner-sage-a.png` and `runner-rose-b.png` are independently generated complete directions. `runner-sage-full-length.png` is a full 7.5:1-proportioned sage design, and `runner-multiview.png` provides top, backing, edge and three-quarter design views; independently generated views are visual references, not measured engineering drawings.
- `textures/runner-albedo.png` is a centered crop of the full-length generated design. The entire runner's top uses it once, with approximately correct design proportions; no tiling or duplicated large floral motifs. Its source is about 2004 × 265 pixels, so inspect close-up texture resolution and compression in the actual game. Backing and binding use simple separate material colors, not woven normal maps.

## Model and export

- `model/HA-RUNNER-01.blend` is the editable model. `model/build_runner.py` rebuilds and exports it using headless Blender. `model/HA_RUNNER_01.fbx` is the complete single static mesh; origin is center at floor level, +Z up, long axis X. Bounds after reimport: **6.000 × 0.800 × 0.015 m**. It has a subtly undulating textile surface, backing and slim physical binding. Designed as a static prop; no interaction animation is planned.
- Reimport validation: `blender -b --python model/validate_fbx.py`. Passed with 1 mesh, 1,463 vertices and 2,700 triangles, finite geometry and UVs, no zero-area triangles, and expected bounds. This is a Blender round trip, not an Unreal import test.
- `previews/runner-perspective.png` and `runner-top.png` show the exported model. Preview floor is a simple proxy using the wood-floor source image, **not** the finished floor module or final lighting.

## Unreal handoff

Import the FBX at centimetre game scale (verify it measures 600 × 80 × 1.5 cm). Recreate three material slots: sRGB albedo on the textile top with UV0 and high roughness (~0.95), muted rose binding, and tan backing. FBX does not carry the complete Blender material graph. Preserve full-length UVs; disable wrapping if using clamp so the border stays intact. Place directly above the visible hall floor and keep clear of the east entry leaf and door swings. Avoid a raised blocking collision slab that can catch the player; use no collision for the textile if the continuous underlying floor supplies character collision. Test z-fighting, camera angle, texture resolution, floor clearance, colors and final lighting in the engine. Nothing here claims in-game validation.
