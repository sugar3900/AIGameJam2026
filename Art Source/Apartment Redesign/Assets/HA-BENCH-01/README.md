# HA-BENCH-01 — shallow hall bench

Provisional asset for the A+ hall, not yet reviewed in Unreal. `concepts/bench-multiview.png` is the generated five-view design reference; the model conforms to the inventory's strict 0.25 m depth limit. A muted walnut texture is reused from the previously reviewed `LV-SIDE-TABLE-01`; the selected source candidate was originally generated for the living chest. Reuse gives nearby furniture a coordinated palette, while keeping the bench more restrained than the concept's brighter finish.

## Model and placement

`model/HA-BENCH-01.blend` is the editable source and `model/HA_BENCH_01.fbx` is the complete static bench. It includes a beveled solid seat, four gently splayed tapered legs, apron rails, lower stretchers and minimal worn edges. Z is up, length is X, the long front faces −Y and the origin is centred on the floor. The measured reimported bounds **including wear geometry** are **0.620 × 0.24975 × 0.450 m**. The A+ plan proposes x=11.08–11.70, y=5.29–5.54 against the hall south wall; transform the bench consistently with the chosen plan/Unreal coordinate mapping. It occupies essentially the entire 0.25 m design allowance, so there is little margin for trim, wall intersection or any blocking collision extending beyond the render mesh.

This is a decorative bench, not a sit animation or interaction implementation. Its narrow 0.25 m seat may not comfortably support the player's actual character rig. Verify capsule/camera clearance in the hall, adjacent wall/trim placement and the entry-door swing with the real game character. Use an appropriately bounded collision shape; do not assume mesh dimensions alone prove passability. There is no exterior landing design in the current plan.

## Materials

`textures/walnut-muted-b.png` is a packed generated color texture and a separate copy for Unreal import. In the Blender preview, the texture passes through Hue/Saturation with saturation 0.68 and value 1.35, and roughness is 0.83. Recreate or bake this color adjustment in Unreal; FBX does not transfer the Blender graph. `Localized rubbed edges` is a separate simple material used only by a few thin highlights. Confirm grain orientation, color, appearance and collision under final room lighting; avoid physical bump that makes the painterly style look like thick paint.

## Build and validation

From the repository root, run Blender headlessly with `--background --python 'Art Source/Apartment Redesign/Assets/HA-BENCH-01/model/build_bench.py'`; the script exports, renders and writes the `.blend`. `model/validate_fbx.py` reimports the FBX in a clean scene and checks finite positions/normals/UVs, nonzero triangle area, floor origin and measured dimensions. Latest result is in `model/validation.txt`: 1,728 vertices, 3,384 triangles and **0.24975 m depth**. `previews/bench-perspective.png` and `bench-front.png` are studio views, not Unreal screenshots. Unreal material reconstruction, collision, entry clearance and character suitability are untested.
