# BR-CLOSET-STORAGE-03 — fitted walk-in shelves and hooked hangers

FIX-002 source replacement for the old BR-CLOSET-02 shelf/rail/hanger assembly. Two full-length side-wall shelves sit just above eye level, with thin worn ivory boards, metal supports, supported rails and eight separate-looking wooden hangers. The hangers have open curved steel hooks resting over the rails, and their triangular bodies face across the rails instead of running along them. There is no deep front apron.

**Source reviewed; FBX validation passed. Engine import, placement and PIE verification remain separate integration work.** Original BR-CLOSET-02 exports are unchanged. The mold in contextual renders belongs to BR-MOLD-02 and is not included in these exports.

## Files and placement

| File | Purpose |
|---|---|
| `model/BR_ClosetStorage03_West.fbx` | West shelf, supports, rail and four hangers; 14 UCX hulls |
| `model/BR_ClosetStorage03_East.fbx` | East shelf, supports, rail and four hangers; 14 UCX hulls |
| `model/BR-CLOSET-STORAGE-03.blend` | Editable source plus read-only closet context for preview |
| `assembly.json` | Machine-readable dimensions, assembly origin, bounds and export inventory |
| `model/validation.json` | Fresh-FBX reimport, mesh, collision and source door-sweep results |
| `previews/closet-inside-combined.png` | Final inside view with the latest FIX-001 upper-corner mold |
| `previews/hook-closeup.png` | Open metal hook resting over the rail |

Both exports use the same closet floor-center origin. **Place both at approved-plan `(1.10, 4.70, 0)` m**, with source +X right, +Y toward the back wall and +Z up. Mapping is `planX = 1.10 + sourceX`, `planY = 4.70 − sourceY`, `planZ = sourceZ`. FBX axes are −Y forward / +Z up. The established Unreal import conversion keeps X and flips Y; use the existing closet assembly transform without additional centering or rotation. Source meshes retain their assembly coordinates, not a shelf-local origin.

Remove the old shelf/rail/hanger assembly actor (existing BR-CLOSET-02 shelf export, currently `Art_BR_Closet02_Shelf`) when placing these two pieces. Keep the closet architecture, doors, light bulb and encounter actors. Do not import the Blender preview walls, original doors, mold or lights. None are in the FBXs.

## Fit and appearance

- Interior reference: 2.08 m wide × 1.68 m deep × 2.75 m tall.
- Each board: 1.67 m long × 0.40 m deep × 0.035 m thick, top at **1.88 m**. Each end has a 5 mm installation allowance against the finished front/back wall; visually wall-to-wall.
- West board X −1.04…−0.64; east board X +0.64…+1.04. Both Y −0.835…+0.835.
- Rails: Z 1.73 m, 28 mm diameter, 0.28 m off the side walls, with end supports and collars.
- Hangers: approximately 0.42 m wide, four per side, slight varied angle and spacing. Real round-wire open hooks wrap over the rod and terminate separately. Wooden shoulders and trouser bars hang below. Supports occupy other rail intervals.
- Lowest hanger point: Z 1.486 m. Most inward hanger extents X ±0.54676 leave **1.0935 m** clear through the center. A centered 76 cm diameter capsule has **16.7 cm margin per side**.
- Single existing dangling bulb remains unchanged, bottom at 2.06 m. The upper-right mold remains visible above and beyond the shelf; its plane/material is delivered separately under BR-MOLD-02.

The Blender source has individual editable members in collection `BR-CLOSET-STORAGE-03_SOURCE`. Each FBX combines its side into one static render mesh. Hangers are decorative, not individually animated, and have no collision hull; the board, wall cleat, brackets, rail and rail supports have individual simple hulls. Do not apply complex collision as simple if preserving the intentional nonblocking hanger treatment.

## Materials

| Slot | Source | Suggested Unreal treatment |
|---|---|---|
| `CS03_PaintedIvory` | `textures/white-wood.png`, reused approved BR-CLOSET-02 painterly ivory wood | Opaque; roughness 0.8; metallic 0 |
| `CS03_HangerWood` | `textures/hanger-wood.png`, reused approved LV-BOOK-01 painted walnut | Opaque; roughness 0.8; metallic 0 |
| `CS03_AgedSteel` | Base color linear RGB 0.31 / 0.29 / 0.25 | Opaque; roughness 0.48; metallic 0.72 |

Textures are copied into this asset and packed into the source blend. Preview lighting is illustrative; it does not alter the export material values.

## Collision and verification

Import via **legacy FBX**, as this project's UE 5.8 Interchange path drops UCX. Use authored collision, one convex hull per UCX member, and disable automatic collision generation. Each export has **14 named convex UCX members**, avoiding a single solid bounding box across the assembly.

`validate.py` imports the actual exported FBXs into a fresh Blender scene and checks: one render mesh per side, 14 manifold box hulls per side, finite coordinates, nondegenerate triangles, UV presence, zero assembly origins, and aisle bounds. Each render mesh has 4,988 vertices.

It also imports the actual BR-CLOSET-02 door leaves, positions their hinge-local geometry at source X ±0.50 / Y −0.978, and checks source geometry overlap at every degree from closed through 95° outward. Both 96-sample sweeps have zero overlaps; minimum storage-front/door Y separation is 32 mm. This is source geometry validation, not a claim of executed Unreal capsule or encounter tests. Confirm imported simple collision, player traversal, Malcolm's visibility and the open doors in PIE after placement.

## Rebuild

From this folder, run sequentially (do not overlap renders on the shared machine):

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/build_storage.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/validate.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/render_combined.py
```

The builder reads BR-CLOSET-02 for context and BR-MOLD-02 for the combined preview; it writes only this asset folder. `render_combined.py` refreshes the latest mold context, creates the source collection and saves the final inside camera without changing FBX exports. Older doorway/context previews show the original preview door hardware near the lower foreground; those context objects are excluded from exports.
