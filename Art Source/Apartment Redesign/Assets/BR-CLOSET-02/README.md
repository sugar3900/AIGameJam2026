# BR-CLOSET-02 — fitted hall-end mold closet

Fitted replacement for the smaller BR-CLOSET-01 assembly, following the approved compact-kitchen revision 02 plan. **Source kit complete; Blender visual and round-trip validation performed. Unreal placement, pivot conversion, material appearance, player/character clearance and encounter cameras still require integration review.** The original asset is unchanged.

The room is 2.20 × 1.80 m between wall centerlines, with 0.12 m walls, giving 2.08 × 1.68 m inside before skirting. The main center/east floor stays free. The north interior wall carries the removable mold patch; the west wall carries one high shelf with a hanging rail and three empty hangers. There is one bare dangling bulb, bottom at 2.06 m. Paired ivory paneled doors open outward into the bedroom.

## Files

- `model/BR-CLOSET-02.blend`: editable closed-pose scene, packed existing painterly textures, preview shell, lights and camera.
- `model/build_closet.py`: reproducible headless builder; `model/validate_fbx.py`: independent FBX round-trip checks.
- `assembly.json`: authoritative part placement offsets, door angles and export filenames.
- `model/BR_Closet02_Trim.fbx`: jambs, layered casing, plinth blocks and lintel cap. Three separate UCX hulls follow jambs/header, leaving the portal open.
- `model/BR_Closet02_Door_L.fbx`, `BR_Closet02_Door_R.fbx`: separately pivoted paneled leaves, inner faces, brass knobs/hinges and subtle edge wear. One leaf-sized UCX hull per door.
- `model/BR_Closet02_Shelf.fbx`: west high shelf, cleats/brackets, rail and hangers. One shelf UCX hull; no central room-filling collider.
- `model/BR_Closet02_Bulb.fbx`: rosette, cable, socket and bulb. Add one engine point light; the FBX does not carry a light. No collision needed.
- `model/BR_Closet02_Mold.fbx`: separate UV-mapped plane on the north interior wall. Hide this piece on repair; no collision needed.
- `previews/closet-closed.png`, `closet-open-mold.png`, `closet-open-repaired.png`, `closet-interior.png`: contextual visual review.
- `model/validation.json`: round-trip counts and measured assembled bounds.

**Do not import the preview shell from the blend.** No room walls, floor, ceiling or baseboards are included in the FBXs. The engine's shared apartment shell must form the closet; this avoids duplicate exterior/hall/bedroom walls. Preview room surfaces and floorboards are only visualization aids. Low storage boxes are reused from BR-CLOSET-BOX-01 and are not duplicated into this kit.

## Coordinates, pivots and opening

Source units are metres, +Z up, front toward −Y, +X toward the right when looking at the closed doors. The assembly origin is floor center. In plan coordinates it is **(1.10, 4.70, 0)**. Source north is +Y and plan north is −Y, so the intended mapping is `planX = 1.10 + sourceX`, `planY = 4.70 − sourceY`, `planZ = sourceZ`. Apply this through the existing import/placement convention, not a negative geometry scale. Verify handedness after FBX import.

The FBX exporter explicitly uses `axis_forward='-Y', axis_up='Z'`. Every exported visual mesh has **object origin (0,0,0)**; static groups already contain assembly-space coordinates. Door mesh vertices are local to their floor-level hinge, and each needs the following assembly offset after import:

| Part | Source assembly offset (m) | Opening in source local Z |
|---|---|---|
| Door_L | (−0.500, −0.978, 0) | 0 → −95° |
| Door_R | (+0.500, −0.978, 0) | 0 → +95° |
| Trim, Shelf, Bulb, Mold | (0, 0, 0) | static |

The door pivots are 0.50 m on either side of center, **1.00 m apart**, not 0.50 m apart. Door leaves are each 0.495 m wide, with a 0.010 m center gap; they extend from z=0.015 to 2.100. This yields no threshold collision and room below the head jamb. The jamb inner faces are x=±0.500 and underside of head is z=2.110. **Rough wall cut is 1.100 m wide × 2.140 m high**. In plan the south opening spans x=0.55–1.65 at y=5.60. Nominal jamb clear width is 1.00 m; open leaf thickness and hardware reduce effective passage slightly. The exterior casing runs to |x|=0.675 and cap top z=2.2435; allow that extent on the bedroom wall.

The door plane is source y=−0.978, slightly forward of the south wall's finished bedroom face y=−0.960. This keeps the outward swing ahead of the casing. Check open leaves and knobs with the actual player capsule and bed/closet approach in engine. Do not place both doors at the common assembly origin.

## Interior placements and finishes

- Mold plane: x=−0.45…+0.45, y=+0.837, z=0.75…1.85. It sits 3 mm in front of the north wall's finished face y=+0.840. This matches the approved elevation height; the old kit's higher patch is not copied.
- Shelf: x=−1.04…−0.74, y=−0.37…+0.68; top z=2.25. The rail/hangers stay against the west wall, leaving the center clear.
- Bulb center: x=0.04, y=0.02; lowest point z=2.06. Engine point-light starting location: (0.04, 0.02, 2.04), warm and low intensity; tune against the apartment lighting rather than duplicating a second visible bulb.
- Standing reference: 0.60 × 0.60 × 1.80 m centered at source (0,0.15), floor z=0. Its box is not exported. Static source clearance is checked, but Malcolm's real body/animation/camera need an engine test.
- Low box reuse: BR-CLOSET-BOX-01 is about 0.300 × 0.253 × 0.181 m including its lid, not the 0.035 m wall-depth proxy used in the earlier elevation schedule. Keep boxes in the west strip beneath the shelf, with east edge no farther than source x=−0.74. A suitable single-box floor center is (−0.89, +0.35, 0); validate a second stacked box and any lid animation separately. Do not block the north-wall reveal or door approach.

The painterly plaster, ivory wood and mold image are reused from BR-CLOSET-01; no new visual direction was introduced. Geometry has restrained soft edges and narrow molding profiles, not paint impasto. The mold material preserves the existing mask, thresholds alpha at 0.08–0.60 to suppress the pale fringe, and multiplies RGB by muted dark olive `(0.12,0.15,0.07)` with subtle procedural alpha breakup. Recreate this as a masked/two-sided engine material or reuse the integration team's existing mold material and inspect under actual lighting. FBX does not reproduce Blender nodes. Repair toggles only the mold plane; the doors, shelf and bulb remain.

## Validation

Build: `/Applications/Blender.app/Contents/MacOS/Blender -b --python-exit-code 1 --python model/build_closet.py`.

Validate: `/Applications/Blender.app/Contents/MacOS/Blender -b --python-exit-code 1 --python model/validate_fbx.py`.

Validation reimports every FBX, verifies finite geometry/UVs, UV presence, nondegenerate triangles, zero export object origins, UCX hull counts/closed eight-vertex boxes, mold/bulb heights, west-only shelf extents and the central 1.80 m standing proxy. Round-trip checks do not certify Unreal axis conversion, interaction traces or moving convex collision. Keep UCX enabled on import and inspect the portal with collision visualization; never replace the whole kit with one convex hull.
