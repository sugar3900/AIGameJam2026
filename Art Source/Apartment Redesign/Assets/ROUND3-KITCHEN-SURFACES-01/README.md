# Kitchen worktops, backsplash and recessed plinths

Additive source release for feedback round 3. Original kits remain immutable. `build_surfaces.py` creates ten FBXs and `models/KitchenSurfaces03.blend`; `validate_surfaces.py` checks fresh imports. All meshes use identity transforms, source metres with -Y facing the room, FBX forward -Z / up Y matching Joinery02 and Backsplash02. Place at the listed world-centimetre origins with yaw 0 and scale 1. Source review blend objects are already assembled and must not supply a second placement offset.

## Carcasses

| New FBX | Replaces | Existing world origin, cm |
| --- | --- | --- |
| `KI_Cab06_0425_Body` | `Joinery02/KI_Cab03_0425_Body` | (141.25, 47.5, 0) |
| `KI_Cab06_0775_Body` | `Joinery02/KI_Cab03_0775_Body` | (306.25, 47.5, 0) |
| `KI_Cab06_0450_Body` | `Joinery02/KI_Cab03_0450_Body` | (442.5, 47.5, 0) |

The old `Counter_Ivory` worktops and `Toe_Dark` solid black blocks are removed from render geometry. Every other original polygon, coordinate and UV is preserved. Both old slots remain empty in the original slot order `[Joinery_Sage, Joinery_Interior, Toe_Dark, Counter_Ivory]` for binding compatibility.

New 18 mm painted plinth front and side-return panels replace each solid toe block, forming a recessed U support with an open interior and back. Their outer footprint, 11 cm support height and front plane are identical to the old toe: the front remains at world Y74, 6 cm behind the counter front Y80. They use `Joinery_Sage` and its existing painterly image. The old black material is never used by any render polygon. No cabinet fronts, doors, drawers, hinge roots or movement are changed.

Each FBX includes the original body's UCX pieces, renamed for the new mesh but geometrically unchanged. Import those authored hulls and retain the current collision response. They include the previous worktop and toe support volumes. Keeping those hulls preserves collision; their old worktop portion sits inside the new slab, so overlapping collision volumes there are intentional. There is no duplicate visible worktop or black toe geometry.

## Continuous slabs

| FBX | World origin, cm | Full world bounds, cm |
| --- | --- | --- |
| `KI_Counter03_A` | (112.1, 6, 86) | X112.1–162.5, Y6–80, Z86–91 |
| `KI_Counter03_B` | (267.5, 6, 86) | X267.5–345, Y6–80, Z86–91 |
| `KI_Counter03_C` | (420, 6, 86) | X420–474, Y6–80, Z86–91 |

Each is one closed 5 cm slab, with a 2.5 mm edge bevel and one authored box UCX. They replace all embedded counters and all five `KI_CounterFiller02_*` actors. There are no separate rear, fridge-end or east-end strips. UV0 uses one world coordinate frame over the entire kitchen, continuing from the top across the 5 cm edge instead of restarting a texture on each strip. `Counter_Ivory` uses the unchanged `ivory-enamel.png`, metallic 0 and roughness 0.48, with ordinary UV0 sampling. Reuse the installed equivalent only if it uses that image and unmodified UV0. Slab bottom remains Z86; drawer top Z85.5 retains 5 mm clearance.

## Backsplash

| FBX | World origin, cm | Full world bounds, cm |
| --- | --- | --- |
| `KI_Backsplash03_A` | (112.1, 6, 91) | X112.1–162.5, Y6–7.8, Z91–117.5 |
| `KI_Backsplash03_B` | (267.5, 6, 91) | X267.5–345, Y6–7.8, Z91–117.5 |
| `KI_Backsplash03_Range` | (345, 6, 107) | X345–420, Y6–7.8, Z107–117.5 |
| `KI_Backsplash03_C` | (420, 6, 91) | X420–474, Y6–7.8, Z91–117.5 |

These replace all four `KI_Backsplash02_*` bands and their obsolete trims. Use NoCollision. The 10 cm square checker grid is globally aligned in X/Z, with boundary tiles cropped rather than scaled; the smallest cropped dimension is 23 mm, with no hairline slivers. Interior grout joints are 2 mm. The complete closed grout backing reaches world Y7.6, while tile fronts reach Y7.8, so the visible grout sits 2 mm behind the glaze. Tile backs butt the grout backing, with no overlapping interiors. Cropped tiles retain their position within a full square's UV crop, and deterministic swatch offsets/rotations vary the painterly image.

An outward-facing 18 mm quarter-round runs along the top. Only run A has an exposed fridge-end bullnose. A closed spherical octant connects that vertical trim and top trim edge-for-edge, avoiding the previous intersecting/degenerate profile ends. All other ends are square cuts against the sink, range or east wall. Top stays at Z117.5, 5 mm below the window apron at Z118. No bottom trim is added.

Map slot names explicitly; do not retain the flat FBX Phong defaults:

| Slot | Finish |
| --- | --- |
| `Joinery_Sage` | Existing `MI_Joinery_Sage`, unchanged `T_Joinery_Sage.png`, roughness .78 |
| `Joinery_Interior` | Existing `MI_Joinery_Interior`, unchanged `T_Joinery_Interior.png`, roughness .80 |
| `Counter_Ivory` | `ivory-enamel.png`, roughness .48, metallic 0, plain UV0 |
| `Warm_ivory_ceramic` | Existing `MI_Backsplash02_Ivory`, `glaze-ivory.png` |
| `Soft_sage_ceramic` | Existing `MI_Backsplash02_Sage`, `glaze-sage.png` |
| `Cream_glazed_cap` | Existing `MI_Backsplash02_Cap`, `glaze-ivory.png` |
| `Warm_cream_grout` | Opaque warm ivory, linear base (.76,.70,.59), roughness .90, metallic 0 |

Closed solids must remain single-sided. Winding repairs belong in source geometry, not in a two-sided material workaround.

## Validation

`validation.json` records ten fresh FBX imports with identity transforms, finite UVs, correct bounds, positive volume for every closed component, zero nonmanifold edges and zero degenerate faces. It proves all retained carcass polygons/UVs and original UCX geometry are unchanged, with both replaced old material groups empty. Each slab is one closed component with matching UCX and the common world UV frame. Backsplash components have no overlapping AABB interiors. Outward radial normals are checked on the top, vertical and spherical bullnose surfaces. 197 rays through tile centres and actual grout joints verify the expected material, outward face and 2 mm depth difference.

Source previews show the complete runs, close grout/slab detail and the fridge corner. They omit appliances so the manufactured boundaries are visible. Unreal integration still must confirm actual finish binding, no old fillers or embedded counters remain, preserved cabinet clicks/sweeps and appliance interfaces. Do not move or scale appliances to accommodate the new surfaces.
