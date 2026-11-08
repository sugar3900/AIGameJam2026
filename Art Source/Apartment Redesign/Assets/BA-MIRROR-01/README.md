# BA-MIRROR-01: bathroom mirror and sconces

Arched brass mirror with two globe sconces, based on `concepts/mirror-sconces-v1.png`. The source scene is `model/BA-MIRROR-01.blend` and can be regenerated with `model/build_mirror.py` using Blender 5.2. The revised brass material uses the painterly `textures/brass-candidate-b.png` (packed in the blend); the independent candidate A and earlier selection are retained for comparison.

The mirror is approximately 0.525 m wide and 0.85 m high; its bottom is 1.185 m above the wall datum. The two sconces are centered 0.86 m apart. Coordinates are in metres, Z up, with the wall at Y=0 and the visible face toward negative Y. All three FBX exports retain the shared wall datum:

- `model/BA_Mirror_mirror.fbx`: arched glass, backing, trim and side mounts.
- `model/BA_Mirror_sconce.fbx`: both brass fixtures and fittings.
- `model/BA_Mirror_globe.fbx`: both opal globes, separately controllable.

`previews/mirror-sconces-off.png` and `previews/mirror-sconces-on.png` show the proposed light states. The on-state preview uses globe emission and separate warm point lights; these lights are preview-only and should be recreated in the game, with independently controlled globe emissive material. The exports contain no preview wall, camera or lights. The mirror uses a low-roughness metallic surface without a baked reflection. Preview-only reflection geometry demonstrates the material; it is not exported. In Unreal, recreate a mirror material (metallic 1, low roughness) and configure suitable scene reflection support, such as a planar reflection or another tested scene-reflection method, to reflect off-screen content. Recreate the brass material with the candidate-B base color, metallic around 0.82 and roughness around 0.4, then tune to lighting. Set up the two emissive globes and warm local lights as separately controllable runtime elements; validate material and texture import in the actual level.

Validation: reimported each FBX into a clean Blender scene with `model/validate_fbx.py`; all meshes had UVs and finite vertices, and no degenerate triangles were found. The mirror, sconces and globes contain 10,002, 5,584 and 1,920 triangles respectively.

The revised model adds a rear keyhole plate and slotted screw details. The brass has been warmed and darkened using the existing broader-stroke texture candidate; the small studio preview still reads smoother than the illustrative concept. Visual review in the level remains necessary, especially the reflection, roughness and aged surface response. The pair exports as combined groups rather than two individually positioned sconce assets; the globes are separate from the fittings but grouped together.
