# ARC-CLOSET-STORAGE-02 — coat/guest shelf, rail and empty hangers

Separate interior storage assembly for both revision 02 reach-in closets. This corrects the earlier schedule reference to a sliding-door kit for shelf/rail geometry. Reuse this same stable asset ID twice, behind the ARC-SLIDING-CLOSET-02 fronts. **Source complete; Blender visual and FBX validation passed. Engine material, collision and placement review remains pending.**

## Dimensions and placement

Source units are metres, **+Z up, −Y toward the closet front**, +X across the shelf width. **Origin is rear-edge center at floor level, with the rear wall mounting plane at local Y=0.** This is not a geometric-center origin. Geometry stays at Y≤0, projecting into the closet rather than through its back wall.

- Ivory shelf: **0.95 m wide × 0.30 m deep**, x=−0.475…+0.475, y=−0.30…0, z=**1.95…1.985**.
- Rear cleat and two restrained brass/wood support brackets fit beneath the shelf.
- Brass rail center: `(0, −0.27, 1.85)`, parallel to local X, 0.87 m long plus end buttons.
- Three empty wood hangers, at local X=−0.30, 0, +0.30. Their triangular planes run along closet depth, hanging normally from the crosswise rail. The complete assembly projects about **0.49 m** from its rear mounting plane because the hangers extend beyond the 0.30 m shelf; do not use shelf depth as the complete asset footprint. Lowest geometry is approximately **1.582 m**. It fits within the minimum 0.63 m usable closet depth.

| Placement | Plan rear-edge origin (m) | Front direction | Plan mapping from source |
|---|---|---|---|
| Entry coat closet | (11.375, 6.34, 0) | north | x=11.375+localX; y=6.34+localY; z=localZ |
| Guest wardrobe | (11.375, 6.46, 0) | south | x=11.375−localX; y=6.46−localY; z=localZ |

The guest placement is the same assembly rotated 180° around Z in plan. Apply the mappings through the project’s existing FBX-axis convention; do not compensate by negatively scaling the mesh. Account for actual rear-wall finish thickness and door tracks in engine. With these rear planes, the hangers remain behind the closet fronts and leave room for the bypass panels. The boxes, doors, walls, clothes and closet lighting are separate assets and are **not included**.

## Files

- `model/ARC_ClosetStorage02.fbx`: one UV-mapped render mesh plus two named UCX collision hulls, normalized object origin `(0,0,0)`.
- `model/ARC-CLOSET-STORAGE-02.blend`: editable source with packed ivory painterly texture and studio setup.
- `assembly.json`: exact coordinate convention, source bounds and repeated placement definitions.
- `model/build_storage.py`: reproducible headless Blender builder.
- `model/validate.py` and `model/validation.json`: independent FBX round-trip checks and measured bounds.
- `previews/perspective.png`, `front.png`, `side.png`: inspected studio renders.
- `textures/closet-white-wood.png`: unchanged painterly ivory wood reused from BR-CLOSET-02 / BR-CLOSET-01.

## Materials and collision

Ivory shelf paint reuses the original closet texture; warm hanger wood and aged brass match the fitted bedroom closet material family. Source-sized bevels, bracket stock and hanger rods preserve the existing stylization. The image texture supplies painted color variation; the geometry does not simulate paint impasto.

FBX export uses explicit forward **−Y**, up **Z**. Reuse matching Unreal materials or reproduce the packed Blender material slots; import does not automatically carry all shader nodes. Import UCX: one shelf box and one narrow rail box. Decorative hangers and brackets have no collision hulls, avoiding unnecessary player snagging. No door-animation component belongs to this static assembly.

Build: `Blender -b --python-exit-code 1 --python model/build_storage.py`.

Validate: `Blender -b --python-exit-code 1 --python model/validate.py`.

Validation checks finite geometry/UVs, UV presence, nonzero triangle areas, zero object origin, the two closed convex UCX boxes, shelf dimensions/heights, overall hanger depth below 0.50 m, and no geometry behind the mounting plane. Engine axes, clearance to sliding fronts, actual materials and interaction traces remain integration checks.
