# ROUND3-BATH-NORMALS-01

Source winding repair for the bathroom's three basket towels and toilet paper. The original generators wound the towel bodies and the paper annulus inward. With backface culling, their front skins disappeared and the far surfaces showed through. This additive kit preserves the original source assets and supplies four replacement FBXs.

## Import contract

All exports are single static mesh objects, authored in metres with the original FBX settings: forward **−Y**, up **Z**, `apply_unit_scale=True`, `bake_space_transform=False`. Reimport each into its existing static mesh using the existing import transform/pivot options. `combine_meshes=True` remains safe (there is only one object per file). Preserve existing Unreal material bindings and actors; import materials/textures can be disabled. Do not apply negative scale or change actor transforms to compensate for this repair.

| Replacement file in `model/` | Existing Unreal asset | Material slots in order | Source origin |
| --- | --- | --- | --- |
| `BA_Towel_0.fbx` | `/Game/ICanFixHim/Environment/Redesign/BA_Basket/BA_Towel_0` | 0 `Towel ivory` | Basket floor centre `(0,0,0)` |
| `BA_Towel_1.fbx` | `/Game/ICanFixHim/Environment/Redesign/BA_Basket/BA_Towel_1` | 0 `Towel ivory` | Basket floor centre `(0,0,0)` |
| `BA_Towel_2.fbx` | `/Game/ICanFixHim/Environment/Redesign/BA_Basket/BA_Towel_2` | 0 `Towel rose` | Basket floor centre `(0,0,0)` |
| `BA_Roll_Paper.fbx` | `/Game/ICanFixHim/Environment/Redesign/BA_ROLL/BA_Roll_Paper` | 0 `Ivory paper`; 1 `Cardboard core`; 2 `Paper layer edges` | Roll axis `(0,−0.071,−0.014)` m relative to holder wall-plane centre |

The exact destination paths should be checked against the live actors before reimport: `Art_BA_Basket_BA_Towel_0/1/2` and `Art_BA_Roll_BA_Roll_Paper`. The small-prop import helper historically derives the paper folder as `BA_ROLL`; preserve whichever case/path the installed asset uses. Each towel retains its assembly-space vertices and original basket offset. The paper retains its local-axis vertices and FBX object translation. Fresh original/patched FBX imports have exactly matching matrices, local bounds, vertex/polygon/triangle counts, material slot names, and UV-per-corner assignments.

Only winding changes: 242 towel-body faces per towel; 256 paper-annulus faces; 216 paper-tail sheet faces. Towel embroidery/hem geometry and paper-layer rings are untouched. The paper's inner bore now faces into the hole, while outer skin and annular end faces face outward. The zero-thickness tail faces the fixture front (−Y); it may continue to use the existing two-sided paper material. No new collision, materials, UV unwrap, sizing, mounting or interaction is supplied. The holder and basket meshes are unchanged.

## Evidence and rebuild

`model/build_patch.py` reads the original `BA-BASKET-01.blend` and `BA-ROLL-01.blend`, verifies the known body topology and inward normals, reverses only the identified faces, checks that every vertex and UV/material corner is retained, and exports replacement FBXs and patched editable masters. Texture references in those masters remain relative to the original source kits. Source input hashes and signed/radial checks are in `model/source-validation.json`.

`model/validate_fbx.py` starts a fresh scene for each original and replacement FBX, finds the closed towel/annulus island independently by connectivity, and tests volume, outward radial normals, inward bore normals, cap direction and paper-tail direction. It also compares original/patched geometry, UVs, material slots, transforms and bounds. Results in `model/fbx-validation.json`: **4/4 PASS**. Each towel remains 2,620 triangles; paper remains 5,552.

| Closed body | Original signed volume (m³) | Corrected signed volume (m³) |
| --- | --- | --- |
| Each towel | −0.0026505 | +0.0026505 |
| Paper annulus | −0.000665450 | +0.000665450 |

Corrected towel side radial dot products are +0.28779 to +0.99999 (rounded shoulders included). Paper outer radial dot products are +1, bore −1, and both annular caps point outward. Before/after single-sided Workbench renders in `previews/*-backface-culling.png` reproduce the hollow-looking source defect and show the corrected opaque surfaces. These are source-normal diagnostic renders; Unreal appearance still requires the integrator's in-room check.

Run each script using Blender 5.2 in background mode, with `--threads 2 --python-exit-code 1 --python <script>`. Acquire `/tmp/apartment_blender.lock` around the Blender process when sharing this workspace. Run the build first, then the validator in a separate Blender process.

## Narrow reuse audit

The exact towel-cylinder construction is duplicated only in `BA-BASKET-01/model/build_basket_lod1.py`. That script builds the same inward-wound towels for its preview master but explicitly leaves the towel FBX exports untouched. The installed towels all use the three FBXs repaired here. The LOD1 basket body is not implicated. Other nearby bathroom lathe builders (`BA-JAR-01`, `BA-BIN-01`, `BA-TOILET-01`) use the standard Z-axis ring ordering, which gives outward normals on rising exterior profiles; they do not share this Y-axis sign error. The paper holder uses Blender cylinder/torus primitives and beveled curves rather than the faulty annulus construction. No additional asset edits are included.
