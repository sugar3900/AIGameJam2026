# FIX-023 — BA-TOILET-02 source handoff

Source rebuilt and reviewed on 2026-11-09. Original BA-TOILET-01 and all engine files remain untouched. This is ready for parent source review and then coordinated engine integration; it is not in-game acceptance.

## Files

Release folder: `Art Source/Apartment Redesign/Assets/BA-TOILET-02/`.

- `model/BA_Toilet02_Body.fbx` — 5,166 vertices / 10,252 triangles; 21 named UCX hulls.
- `model/BA_Toilet02_Lid.fbx` — 1,172 vertices / 2,316 triangles; 1 named UCX hull; new hinge pivot.
- `model/BA_Toilet02_Water.fbx` — 128 vertices / 252 triangles; no collision.
- `assembly.json` — explicit transforms, material recipes and interaction binding contract.
- `README.md` — build/reimport instructions and acceptance limits.
- `model/BA-TOILET-02.blend`, `model/build_toilet.py`, `model/validate_fbx.py` — editable/reproducible source.
- `previews/toilet-closed.png`, `toilet-open.png`, `toilet-side-open.png`, `toilet-top-open.png` — small CPU previews reviewed by the source agent. The top view shows the recessed bowl and still-water pool.
- `validation/build-report.json`, `validation/fbx-roundtrip.json` — successful source checks.
- `file-manifest.json` hashes every delivered asset file except itself.

## What changed

The flattened cover now matches the seat perimeter and connects through brass moving barrels/leaves to fixed hinge cheeks. The hinge is brought forward onto the seat deck. There are underside lid bumpers and an 85° opening pose, with no tank hits through the sampled arc. The rear ceramic support extends under the cistern down to a shared floor base. A front-facing lever replaces the side peg; the top button is removed. The bowl descends into a trap throat and has a separate standing-water surface. An annular pedestal prevents the former hidden top cap from filling the cavity.

The original painted-ivory texture is reused directly and the revised body fits within the old plan footprint. New source floor minimum is zero, eliminating the old 8 mm gap at the same floor origin.

## Placement and interaction

Retain approved FIX-007 body/water assembly transform **UE (555,603,0) cm, yaw 0**; do not recenter using bounds. Source coordinates map to plan as `(5.55+X,6.03-Y,Z)`.

The lid's **new source pivot is (0,0.110,0.516) m**, replacing `(0,0.125,0.505)`. This becomes **UE (555,592,51.6) cm**. Rebind the existing `Toilet_Lid` actor/action to this pivot and new mesh. Source opening is **−85° about local X**. The front must rise toward the tank; determine engine rotation sign by that motion and the endpoint reference in `assembly.json`, not by copying the old 68° action. FBX stores assembled origin/geometry; avoid adding the pivot translation twice.

Body material slots: Painted_Ivory_Enamel, Trap_Interior, Aged_Brass. Lid slots: Painted_Ivory_Enamel, Aged_Brass, Ivory_Rubber_Bumpers. Water slot: Toilet_Standing_Water. Bind exact recipes from assembly.json; cream base colour texture is sRGB and unmultiplied. Use legacy FBX import so UCX is retained.

The water is static at source Z=.275, centred (0,-.075), radii .088/.109 m. Reuse the successful bucket still-water material treatment in Unreal: clear restrained reflection/refraction, low roughness, no emissive or collision. Keep water attached to the static toilet, not the rotating lid; no repair-hide tags, flush animation or new flush action requested.

## Validation and remaining checks

All three fresh FBX imports pass finite vertex/UV, material-slot, collision-count and zero-area triangle checks. The body centreline ray reaches the deep passage at Z=.146 while the water ray hits Z=.275, verifying the bowl is actually open and not capped by pedestal geometry. The lid is sampled at every degree through 0–85° with zero hits in the conservative tank-front region. Source open/closed/side/top views were reviewed.

Engine owner still needs real open/close clicks, full collision sweep against tank/body/nearby room door, approved bathroom routes, wall clearance and lit Lumen appearance of the bowl water. A source preview does not certify the Unreal water material.
