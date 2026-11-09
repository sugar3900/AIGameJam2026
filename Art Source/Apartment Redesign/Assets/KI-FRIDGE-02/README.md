# KI-FRIDGE-02 — opposite-hinge vintage refrigerator

**Not selected for Rev02. Retained as an opposite-hinge variant only.** Imported-vertex measurements confirmed on 2026-11-09 that KI-FRIDGE-01 keeps source X and flips Y: its −X hinge is already west at the approved north-wall placement. The earlier east-hinge report came from an incorrect gameplay pivot on the handle edge, not an FBX conversion issue. Integration uses KI-FRIDGE-01 with a corrected click-action pivot.

This variant reflects source geometry across world X and therefore has an east/+X hinge in that placement. Its generated texture, interior, sparse wear, chrome handle and unlettered badge remain consistent with the original. Original exports are unchanged.

The reflection is baked into vertex coordinates and polygon winding is reversed to restore outward normals. **No negative scale or negative-determinant object transform is exported.** The body and door remain independent. Source textures are copied unchanged and packed in the new blend; UVs follow their vertices through reflection.

## Files

- `models/KI_FRIDGE_02_BODY.fbx`
- `models/KI_FRIDGE_02_DOOR.fbx`
- `models/KI-FRIDGE-02.blend`
- `models/manifest.json`: exact bounds, origins, collision counts, axes and motion values.
- `models/validation.json`: FBX reimport validation.
- `textures/ivory-enamel-v2.png`: same generated paint as the original.
- `previews/fridge-closed.png`, `fridge-open.png`: matching studio camera.
- `build_fridge.py`, `validate_fbx.py`: reproducible headless source conversion and checks.

## Axes, origins and motion

Metres, Z up, front **−Y** in Blender. Exports explicitly use **−Z forward / +Y up**, matching the original FBX export defaults. Body origin remains `(0,0,0)` at the assembly floor. The door origin is now **`(+0.38, −0.335, 0)` m** relative to the body, reflected from the old −X hinge. The handle and hinges are both moved to the opposite sides; this is not just a pivot edit.

At the north-wall placement facing south, source **+X remains Unreal +X**, making this the east-hinged variant. Do not use it beside the approved prep counter. The original KI-FRIDGE-01 has the required west hinge; fix its interaction pivot rather than mirroring the artwork.

Source door motion is **0° → +105° about local Z**, the opposite sign from the original −105°. Body remains fixed. Closed body/door bounds and hinge transform are recorded separately in the manifest; preserve the door's hinge offset when assembling imported meshes rather than centering the door on the body origin. FBX pivot baking options can change how Unreal exposes that offset: verify the imported pivot and use the manifest if an explicit hinge scene component is required.

Nominal dimensions remain approximately 0.77 m wide ×0.70 m deep ×1.68 m high, with the handle projecting farther at the front. Place by measured body bounds and preserve the approved hinge-side wall gap. No Unreal scene or animation is changed by this source task.

## Collision and material notes

Body FBX contains per-part convex `UCX_KI_FRIDGE_02_BODY_NN` boxes for side walls, back, top/bottom, plinth, fixed shelves/bins and hinge barrels. It deliberately has no single hull spanning the cavity. Door FBX contains `UCX_KI_FRIDGE_02_DOOR_NN` boxes for the door slab, inner panel, individual shelf bottoms/lips/ends and handle. Every collision object shares its render mesh's origin; door hulls must move with the hinged door. Rounded exterior corners are approximated by boxes; check clearance against the room in Unreal.

Import custom collision with auto-generation disabled and verify hull recognition. Keep materials from the original fridge: painted ivory, porcelain interior, gasket, aged chrome and edge patina. FBX is not a complete Blender material graph transfer.

## Verification

`validate_fbx.py` reimports the two exports and asserts finite positions, UVs and normals; UV presence; no zero-area triangles; positive determinant and scale for render/collision objects; expected reflected bounds; exact body/hinge origins; correct UCX names/counts and convex-box topology. Closed/open renders are checked for matching handedness and interior readability. This is **not an Unreal acceptance claim**: hinge direction, motion sign, material mapping, collision recognition and final wall clearance remain integration checks.

**Source review completed:** closed and +105° open studio images were inspected; body and door handedness match, interior remains readable, and the original painted finish is preserved. FBX reimport validation passes for both exports: body 15,012 triangles / 13 UCX hulls; door 8,808 triangles / 15 UCX hulls. All imported transform determinants are +1 with scale (1,1,1).
