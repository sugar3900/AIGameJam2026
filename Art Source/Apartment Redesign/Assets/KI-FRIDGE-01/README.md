# KI-FRIDGE-01 · vintage refrigerator

Refrigerator designed for the selected painterly fixer-upper apartment. The source concept had contradictory hinge sides; `references/left-hinge-multiview-v1.png` fixes the design to a left hinge when viewed from the front. The closed and open images depict the same assembly.

## Contents

- `concepts/fridge-v1.png`: initial approved appearance reference.
- `references/left-hinge-multiview-v1.png`: left-hinged front, rear, both sides, open and perspective study. AI views are interpretive; the dimensions below control geometry.
- `textures/ivory-enamel-v2.png`: generated albedo with painted value variation, not a displacement map. Packed in the `.blend`; import explicitly into Unreal.
- `models/KI-FRIDGE-01.blend`: Blender source with material, lights, camera and independently movable door.
- `models/KI_FRIDGE_BODY.fbx` and `models/KI_FRIDGE_DOOR.fbx`: separate meshes.
- `previews/fridge-closed.png`, `previews/fridge-open.png`: render previews at the same camera.
- `build_fridge.py`, `validate_fbx.py`: reproducible headless generation and geometry checks.

## Scale and motion

Coordinates are metres with Z up, front toward negative Y. Body is at floor origin; at rest the door origin is the left hinge axis `(-0.38, -0.335, 0)` relative to the body. Rotate around local Z from 0° to approximately -105° to open. The closed body including hinge measures approximately **0.77 × 0.70 × 1.68 m**, with the handle protruding slightly beyond the cabinet footprint. Allow additional clearance on the hinge side/front for the door swing. The inner door shelves are attached to the door mesh; three wire racks, freezer and crisper are fixed to the body.

Material slots distinguish painted enamel, interior porcelain, dark gasket, aged chrome and darker toe grille. Painted color comes from the albedo texture; no simulated physical impasto is required.

## Validation and integration

Run:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/KI-FRIDGE-01/build_fridge.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/KI-FRIDGE-01/validate_fbx.py'
```

Both FBXs passed a Blender reimport with finite vertex/UV data, UV layers present and zero zero-area triangles. The body reimported with 7,656 vertices and the door with 4,536. Blender preview verifies closed and open poses, but **Unreal import, pivots, material mapping, collision, lighting, and the door sweep against the final kitchen layout remain untested**. Import as separate meshes and confirm units and origin handling before wiring an interaction.

**Second review pass:** the cabinet is now a rounded hollow shell, the hinges have barrels and screw heads, the plinth is shallower and lighter, and a higher-contrast painted albedo and small flush edge marks add age. Internal lining shares the painterly color treatment. The final in-game finish and animation still need contextual review.
