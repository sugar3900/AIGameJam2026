# CABINET-JOINERY-02 — FIX-033 / FIX-034 / FIX-036

Replaces doors with 22 mm frames and 6 mm recessed panels (14 mm face recess), 40 mm rails/stiles, real edge hinges, latch-stile knobs and a shared 96 mm mounting-centre bow pull on the base doors/drawers. Removes raised wear ticks. All sage casework uses the same textured finish. Linen stays warm ivory.

The original carcasses, tops, shelves, fillers and UVs are retained, apart from deleting decorative wear-tick faces and remapping materials. Base doors extend toward the carcass edges so opened leaves no longer stand across the last few centimetres of the opening. Base drawer shape, front plane and slide travel remain unchanged; only their old pulls and ticks are removed/replaced.

## Import and binding

20 FBXs. Source metres, +Z up, front -Y. Engine conversion flips source Y, then applies the existing assembly yaw. All exported object transforms are identity. Doors have pivot-local vertices; body and drawer exports use the original assembly origin. `assembly.json` gives exact `pivot_source_m`, old-to-new mesh mapping, material slots, bounds and hull counts.

Place each DOOR root at the existing assembly transform applied to `(100*x, -100*y, 100*z)` from its new pivot. Give its Body the same world rotation as the original assembly, at that root, without adding the pivot twice. The new pivot is at/outside the hinge edge on the back plane; visible hinge barrel axes coincide. Keep gameplay identities, prompts, rooms and SFX. Do not reuse the old door pivot offsets.

DRAWERS retain assembly-origin geometry, as before. Keep existing drawer roots, slide axis and 30 cm travel; bind the mesh in the original closed assembly pose using a relative Body offset/rotation. Do not place an assembly-origin drawer mesh directly at the old drawer-centre root with identity transform.

| Door | New source pivot (metres) | Unreal target yaw travel (degrees) |
|---|---|---|
| KI_Cab03_0425_door.fbx | [-0.20249999999999999, -0.253, 0] | 100 |
| KI_Cab03_0775_door_L.fbx | [-0.3775, -0.253, 0] | 100 |
| KI_Cab03_0775_door_R.fbx | [0.33749999999999997, -0.253, 0] | -100 |
| KI_Cab03_0450_door.fbx | [-0.17500000000000002, -0.253, 0] | 100 |
| KI_Upper02_LeftDoor.fbx | [-0.472, -0.167, 0.265] | 100 |
| KI_Upper02_RightDoor.fbx | [0.472, -0.167, 0.265] | -100 |
| KI_Pantry02_LeftDoor.fbx | [-0.47, -0.318, 1.02] | 100 |
| KI_Pantry02_RightDoor.fbx | [0.47, -0.318, 1.02] | -100 |
| BA_Linen02_LowerDoor.fbx | [-0.278, -0.305, 0.565] | 60 |
| BA_Linen02_UpperDoor.fbx | [-0.278, -0.305, 1.295] | 90 |

Linen lower opens 60 degrees to avoid the basin; upper opens 90. Base/upper/pantry open 100. Blender source swing signs are reversed from Unreal, recorded separately. Body placements remain unchanged. Approximate linen world pivots under assembly (745,905,0), yaw180: (772.8,874.5,56.5) lower and (772.8,874.5,129.5) upper. Exact assembly transform wins over rounded audit coordinates.

## Finish

Use explicit material mappings from `assembly.json`, including interactable Bodies. FBX Phong auto-materials do not reproduce intended roughness/metalness. All texture images are sRGB base colour; tint already baked, so use unity engine tint. Sage across base/upper/pantry is `Joinery_Sage` / T_Joinery_Sage.png. Linen `Joinery_Ivory`; cabinet interiors `Joinery_Interior`; knobs `Joinery_KnobIvory` plus `Joinery_AgedBrass` rose/neck/collar. Brass roughness .42, metallic .65. Ivory knob roughness .32, nonmetal. Upper/pantry retain empty legacy wear slots with zero faces; assign a harmless material or strip unused slots on import.

## Validation and limits

`fbx-validation.json`: all 20 fresh imports match authored bounds within 10 micrometres, have UVs and the specified collision hull count, and contain no degenerate faces. Ten door/carcass triangle sweeps, 101 poses each across the full designed travel, have zero intersections. These are source geometry checks, not an Unreal gameplay claim.

One convex slab hull per new door; five original open-box hulls per drawer. Base body hulls 11/14/12 retained. Upper/pantry/linen original bodies had no UCX; preserve existing engine complex collision rather than auto-generating an enclosing box across their interiors.

Review previews include each assembly closed/open. In-engine acceptance: replace/retire old meshes; verify all changed hinge roots, closed/back clearance, hardware, installed neighbour sweeps (especially linen lower/basin), actual click open/close, drawer travel and materials in lit gameplay. Preserve FIX-007 placement and bathroom routes. No git operations.
