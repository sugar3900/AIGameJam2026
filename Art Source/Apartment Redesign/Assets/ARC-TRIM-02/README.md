# ARC-TRIM-02 — compatible outside-corner mitres

Additive FIX-024 source kit. Four trim meshes complete ARC-TRIM-01's missing convex/outside 90-degree corners; the original kit remains unchanged. No casing, inside-corner or straight replacement is included.

| Mesh | Local X bounds (m) | Projection | Height |
|---|---:|---:|---:|
| Baseboard_Outside_End | 0 … 1.030 | 0.030 m | 0.130 m |
| Baseboard_Outside_Start | −0.030 … 1 | 0.030 m | 0.130 m |
| Crown_Outside_End | 0 … 1.035 | 0.035 m | 0.100 m |
| Crown_Outside_Start | −0.035 … 1 | 0.035 m | 0.100 m |

All exports are metres, source Z-up, nominal one-metre wall length, common bottom/back/start origin. Y=0 is the wall surface; the profile projects into negative source Y. The original profile literals are read directly from ARC-TRIM-01's generator, not approximated. The opposite ends remain square. Mitre extensions exceed nominal length; do not bounds-centre the pieces or scale them back to exactly one metre.

## Placement

In source/Blender coordinates: place **End** at `(0,0,Z)` and **Start** at `(1,0,Z)` rotated **+90° about Z**. End has the mating plane `x+y=1`; Start has local `x−y=0`. After transformation the two faces match exactly and occupy opposite half-spaces. This is an outside corner; the existing Inside pairs rotate −90° and are not interchangeable.

For the established Unreal conversion (source X kept, source Y flipped, metres to cm), the hall outer corner `(486,386)` cm can use End origin **`(386,386,Z)` yaw 0°** and Start origin **`(486,386,Z)` yaw −90°**. Expected baseboard bounds: End X386–489/Y386–389 and Start X486–489/Y286–389 cm. The 3 cm extension wraps the convex corner; it does not consume the wall run. Use Z=0 for baseboard. For crown set Z to the target existing crown bottom (10 cm below its matching ceiling/header datum); do not guess whether this junction follows the 245 cm header or 275 cm ceiling. Confirm importer bounds before placement.

These are nominal one-metre corner pieces. Cut the distant square ends to fit adjacent runs; never scale profile depth/height or X-stretch the mitre angle. Arrange the pair from its corner datum and trim the far square ends, preserving the diagonal face. No collision is exported; treat decorative trim consistently with ARC-TRIM-01 and retain shell collision.

## Material

One slot **`AgedIvoryPaint`**, same as ARC-TRIM-01. The supplied `textures/paint-selected.png` is byte-identical to the original. Source shader mixes sampled sRGB image at 64% with warm linear constant `(0.82,0.76,0.65)` at 36%, roughness0.84, metallic0. UV rule is the original `u=x, v=(z+y)*2.5`.

FBX does not faithfully serialize the MixRGB graph. Explicitly assign the same existing **Trim_Cream** Unreal material used on the matching installed trim, or recreate the documented shader. Do not accept a flat auto-import Phong material as a texture transfer. The original texture is not certified seamless; inspect the junction in apartment lighting.

## Rebuild and verification

Run `model/build_outside.py` with Blender in background; it writes four FBXs, the arranged preview blend and three small CPU previews. Then run `model/validate_outside.py` for independent reimport checks. `profiles.json` records the original generator hash and exact section vertices. `validation.json` records bounds, finite UVs, nondegenerate triangles, closed consistently wound positive-volume solids and matching mitre vertices. Opposite separating half-spaces provide an explicit no-volume-overlap proof for both pairs.

Unreal installation, collision clearance and in-game appearance are engine-owner acceptance, separate from source validation. The blend's plaster/floor/camera/lights are preview-only and never exported.
