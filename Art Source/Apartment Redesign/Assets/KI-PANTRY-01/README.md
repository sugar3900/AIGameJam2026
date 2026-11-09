# KI-PANTRY-01 — tall sage pantry

Vintage pantry with a full-height, two-door front, five shelf levels plus base, a real open interior, narrow panel moulding, ivory knobs and aged-brass hinges. Shelves are intentionally empty; jars and dishes are separate dressing assets. `concepts/pantry-open-closed-v1.png` is the selected design and `references/pantry-multiview.png` provides consistent views. AI reference dimensions are illustrative; the plan and modeled dimensions govern the build.

## Dimensions and placement

Body/crown bounds are **1.000 m wide across the doors × 0.678 m deep (including projecting crown bead) × 1.976 m high**. Front is local **−Y**, width runs local **X**, up is **+Z**. The A+ plan calls for `[11.20, 0.12, 0.67, 1.00]` metres in the northeast kitchen: local width spans the plan's north–south axis; the door front faces west into the kitchen. With plan +x east, +y south, map local +X to plan north (−y) and local +Y to plan east (+x), i.e. rotate −90° around Z under the proposed plan-axis mapping; position the body floor-center at plan (11.535, 0.620). If the engine scene has a different axis mapping, transform consistently. The original concept looks shallower; this assembly intentionally follows the deeper plan footprint.

Each leaf has a hinge-axis origin, relative to the body floor center: left `(−0.472, −0.335, 1.020)` m and right `(+0.472, −0.335, 1.020)` m. Open the local left door −100° and local right door +100° around Z (the `pantry-open.png` preview illustrates both); no animation is embedded. Knobs and hinge barrels move with each door. Confirm imported pivots and rotation signs in Unreal. The northern door is near the north wall: **door swing and wall/adjacent furniture clearance have not been verified** and may require an adjusted final opening angle or placement.

## Files and materials

`model/KI-PANTRY-01.blend` is the editable closed-state source. `model/build_pantry.py` regenerates the Blender source, separate `KI_Pantry_Body.fbx`, `KI_Pantry_LeftDoor.fbx`, `KI_Pantry_RightDoor.fbx` and closed/open studio previews. There is no collision or interaction logic encoded. Preserve each component transform and origin when assembling.

Two independent generated paint candidates are `textures/sage-A.png` (darker olive) and `textures/sage-B.png` (soft warm grey-sage). The Blender material blends B with 28% A for a warm sage finish; recreate that blend in Unreal. `textures/interior-wood.png` is reused from the existing KI-CABINET-01 interior and mixed 48% toward linear RGB (0.36, 0.26, 0.18) to soften the orange; recreate that adjustment in Unreal. Brass, ivory and tiny exposed-wood rubs use separate materials. The texture is base color only. Recreate materials, roughness and metalness in Unreal; Blender shaders and the transparent studio background do not transfer automatically.

Headless Blender 5.2.3 FBX reimport validation with `model/validate_fbx.py` passed: body 2,844 triangles, each door 3,564 triangles, finite positions and normals, UV layers and no zero-area triangles. Reimport recorded the expected three pivot locations above. **Unreal import, material appearance, collision, movement, clearances and in-room lighting remain untested.**
