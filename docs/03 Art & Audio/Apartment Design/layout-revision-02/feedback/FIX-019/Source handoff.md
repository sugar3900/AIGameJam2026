# FIX-019 fitted office trim source release

Parent-reviewed source kit: `Art Source/Apartment Redesign/Assets/OF-WAINSCOT-02/`. Read its README, assembly.json, validation.json and file-manifest.json before integration. Original source kits are unchanged. Current office elevation notes and south under-apron panel drawing now reflect this fitted source.

Import **OF_Wainscot02_N, CS, WF, E, S and W** from their individual FBXs under `model/`. Place every mesh at **(796,566,0) cm, yaw 0, scale 1**. Source units metres, Z up; import keeps X and flips Y. All are static finishes with no added blocking collision. Retire only old `Wainscot_OF_*` module actors, keeping crown, wall shell, all casings/frames/leaves, closet travel and gameplay.

The single `OF02_Painterly_Ivory` material uses `textures/painted-ivory.png` directly as sRGB Base Color, roughness .80, metallic 0, opaque. No warm tint multiplier. Texture is the original selected ivory paint, unchanged.

Retain `Damage_BR_LeadPaint`, current mesh/material/tags/identity/scale, X=8.925/Z=.700 centre. Reproject its visible plane to **Y=5.668 m**, 1 mm ahead of the new recessed face. This is a bounds/visible-plane target, not raw actor origin. Expected original patch width .4619 m fits inside the new clear recessed bay. Kit README gives precise intervals.

All new trim is at most 22 mm deep. Casings and sill have 2 mm source clearance; under-apron cap top .778 has 5 mm clearance below actual apron bottom .783. At the wardrobe's 20 mm east-corner sliver, use the included 7 mm plain return and capped east run beginning Y=7.239. Do not stretch the short piece or move the closet frame.

**Shell correction to verify in engine:** current Rev02 shell code leaves the outer closet quadrant **X10.69..10.75 / Y7.15..7.21 / Z0..2.75 m** uncovered. Verify the live map and extend one wall 60 mm or fill that quadrant with matching plaster. Source trim and final previews assume the intended square outer corner `(10.69,7.21)`. The separate preview-only slit from casing-edge stops and overlapping coplanar preview wall faces was corrected; final context uses real rough-opening extents and a clean closed outer corner.

Source validation passes for all six FBXs: finite vertices/UVs, zero degenerate triangles, zero boundary edges, common origins and matching bounds (maximum roundtrip error below .000001 m). All six runs were checked against the actual imported room-door, wardrobe and office-window frame meshes: **zero intersections**. Final previews show north door/lead paint, outer wardrobe corner, under-window fit and tight wardrobe termination. Actual engine traversal, doors/slider, lighting, shell fill and lead-paint interaction remain acceptance work.

Reconciliation now accounts for 153 existing/planned source IDs with no unresolved folders. Entry03, armchair02, plant02, slippers01, runner02, sconce02, sofa02, all17 art kits and this office kit are source-ready/engine-pending. KI-CHAIR-02 is also parent-approved/source-ready following independent verification of all21 release-manifest hashes. Engine acceptance remains pending for these source releases.
