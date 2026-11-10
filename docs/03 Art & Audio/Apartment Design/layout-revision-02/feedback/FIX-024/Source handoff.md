# FIX-024 outside trim source handoff

**Source released for parent review/integration.** All Blender processes exited; source files settled. No git or engine writes.

Additive kit: `Art Source/Apartment Redesign/Assets/ARC-TRIM-02/`. Original ARC-TRIM-01 remains unchanged. This supplies the missing Baseboard and Crown Outside_Start/Outside_End pairs only; existing straight/inside/casing pieces remain in use.

## Exact files

- `model/Baseboard_Outside_End.fbx`
- `model/Baseboard_Outside_Start.fbx`
- `model/Crown_Outside_End.fbx`
- `model/Crown_Outside_Start.fbx`
- Matching existing engine material `Trim_Cream` on sole slot `AgedIvoryPaint`; copied `textures/paint-selected.png` is byte-identical to ARC-TRIM-01.

The asset manifest contains 15 files with asset-relative paths. SHA256 of `file-manifest.json`: `dc97e59fe9ebadb6ce2038fca2a3cfc26d10af2f38a5d12b23364eb0987edc56`. Source script/blend, source profile evidence, assembly contract, independent FBX validation and three small previews are included.

## Placement and fit

Nominal wall length is1m; outside extensions are30mm baseboard and35mm crown. Source profiles/UV/material naming are identical to ARC-TRIM-01. Use End at source(0,0,Z), Start at(1,0,Z) rotated+90deg. Under the established sourceY→−UEY conversion, hall corner(486,386)cm uses End(386,386,Z)yaw0 and Start(486,386,Z)yaw−90. Baseboard bottom Z=0; crown bottom must match the actual adjacent installed run (10cm below its ceiling/header), not an assumed room ceiling.

Trim distant square ends to fit; do not X-scale the diagonal corner or bounds-centre these asymmetric variants. Baseboard extends to UE X489/Y389 at the convex corner. Exact origin/expected bounds are in `assembly.json` and README. No UCX for decorative trim; retain shell collision.

Explicitly assign existing matching `Trim_Cream`: original source MixRGB graph does not reliably transfer through FBX. Do not use a flat imported Phong fallback.

## Evidence and remaining acceptance

Independent FBX reimport passed all four: baseboard28 triangles each, crown40 each; finite UVs/coordinates, nondegenerate triangles, closed consistently outward normals and positive volume. Both original profiles are unchanged. Maximum paired-profile discrepancy after reimport is0.000152mm baseboard and0.000192mm crown. Opposite separating half-spaces prove no volumetric overlap apart from submicron import tolerance. Source preview review passed: assembled corner and closeups show connected profile faces with no exposed end/gap.

Engine owns the corner shell filler, continuous hall crown, existing inside-mitre swaps, portal casing/lining and base terminations. Verify imported axis/bounds before placement, use matching material, then inspect both directions under apartment lighting and rerun applicable route checks. Source evidence is not in-game acceptance.
