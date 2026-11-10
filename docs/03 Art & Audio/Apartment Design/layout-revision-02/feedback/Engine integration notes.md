# Feedback batch engine handoff

Reviewed source kits BR-MOLD-02, BR-CLOSET-STORAGE-03 and KI-LEAK-02 are settled for import. [Exact file list and hashes](source-release-001-003.json). Coordinator must grant editor reservation before engine writes. All source kits and layout-revision-02 docs are now **files settled**; all three art subagents and Blender jobs have finished. Git remains coordinated with the engine owner; this handoff does not authorize a commit, push or merge. The editor is paused pending a coordinated memory-safe time slot; released source does not imply integrated validation.

## FIX-001 — mold

Import `BR-MOLD-02/model/BR_Mold02_Back.fbx` and `BR_Mold02_Return.fbx`; both use common plan origin `(1.10,4.70,0)` metres. Replace old central overlay; preserve repair labels/tags, attach both to Malcolm malady. No collision on the art.

Use `textures/mold-colonies-rgba.png`, sRGB off, vertex colors Replace. Constant linear base color `(0.022,0.021,0.020)`; metallic/specular 0, roughness 1; two-sided masked material with DitherTemporalAA. Coverage is `VertexColor.A * Texture.A * pow(saturate((0.56-dot(Texture.RGB,(0.2126,0.7152,0.0722)))/0.38),1.35)`. Do not inherit old green tint.

Move only invisible inspect proxy to visible growth near `(1.82,3.89,2.16)`; root/spawn/talk/camera world transforms stay fixed. Glow about 0.50 m out from wall. Analytic doorway ray clears; confirm actual eye traces and FixHimClick against installed shelves/leaves. No oversized invisible target.

## FIX-002 — closet storage

Import both `BR-CLOSET-STORAGE-03/model/BR_ClosetStorage03_West.fbx` and `BR_ClosetStorage03_East.fbx` at common `(1.10,4.70,0)` origin. Retire `Art_BR_Closet02_Shelf`; retain shell/doors/bulb. Source front −Y, Z up; established import keeps X and flips Y. Legacy FBX with authored UCX, not Interchange. Fourteen hulls per side, 4,988 render vertices each. Hangers intentionally have no collision; do not apply blanket complex collision.

Shelf tops 1.88 m; boards 1.67 × 0.40 × 0.035 m. Actual central aisle 1.0935 m, centered 76 cm capsule margin 16.7 cm each side. Source 0–95° door sweeps passed; actual character/capsule/path checks remain required. Material slots and copied texture names are in README.

## FIX-003 — sink leak

From `KI-LEAK-02/models/`, use `KI_LEAK_02_sink_body.fbx` on current sink body transform/materials, plus `KI_LEAK_02_bucket.fbx` and optional `KI_LEAK_02_bucket_water.fbx` on the same assembly transform. Origins remain the original floor origin; bucket coordinates are baked in—do not add offsets twice. New body preserves all non-bucket geometry, UVs, materials, tap pivots, faucet and upstand. Use original tap meshes. Bucket has 13 hollow UCX hulls; use legacy FBX. Reuse existing body collision policy; water has no collision.

Retire `KI_SINK_NARROW_damage` entirely. Suppress old runtime cylinder puddle and sphere drop with the approved opt-in `AuthoredLeakDamage` path; original map fallback remains unchanged without tag. Reuse `Art_KI_SINK_damage` identity on authored decal, attach to Malady_Sink with RepairDamage/lukey/AuthoredLeakDamage. Normal Sink_Tap stream stays separate.

Source-space leak point `(-0.10,0,0.243)` m, landing/ripple `(-0.10,0,0.115)` m; UE local before actor transform `(-10,0,24.3)` and `(-10,0,11.5)` cm. Transform through sink assembly, then convert to malady local for properties. Drop is only 12.8 cm (gravity fall ~0.162 s), not earlier 30 cm estimate. Form briefly at pipe, use small non-emissive translucent drop and restrained ripple inside bucket. Bucket catches current drops; residual floor spill escaped earlier.

Preferred DBuffer decal uses `textures/T_Leak_Puddle_Mask.png`, alpha coverage only, not white albedo. Padded extent 68.2221 × 86.1652 cm; center source `(-0.0829865,-0.298254,0.004)` m = UE local `(-8.29865,29.8254,0.4)` cm. Image right source +X, up source +Y (UE −Y). Feathered border and three satellites; retain tile visibility, modest darkening and reflective wetness. Optional `KI_LEAK_02_puddle.fbx` is an alternative, never an additional duplicate.

Zinc materials and three texture maps are specified in KI-LEAK-02 README. Do not tint the bucket brown. Keep bucket after repair; hide/stop malady water effects. Bucket's still-water surface may remain; do not conflate it with active leak drops/ripples.

## FIX-004 and rug move

Use latest approved-plan and elevation-schedule records. Fuse center X11.05 on north wall, body bottom Z1.40; planning rect `[10.825,0.06,0.45,0.14]`. Face south with existing left/source−X hinge retained: this becomes the west hinge and opens into the room, away from the east corner. Source hinge X−0.229/Y−0.14; source −105° sweep becomes reflected-Y engine sign (confirm current action). Closed east edge X11.275 is 0.665 m from east finished wall11.94; source westmost open-leaf estimate X10.70. Actual collision sweep remains required. Measure north plaster face for flush placement and 2–3 mm damage offset. Move complete body/door/action/malady/overlays consistently. Re-derive Wyatt spawn/talk/camera with actual capsule, furniture and line-of-sight tests.

Coat rack center Y3.30, measured length 0.72 m giving Y2.94–3.66; shift hooks and coat together. Bench stays. Rug rect `[8.95,0.90,1.80,2.50]`, +0.15 m east toward coffee table; no sofa movement.

## Validation and later releases

Reconcile schedule identities; test routes/encounters/door sweeps, actual fuse and mold clicks, repaired-state hiding/stopping, and normal tap toggle. Review moving water in a visible environment editor window under actual lighting. Source studio renders are not final engine acceptance.

## Additional source releases

Use each kit's exact manifest and assembly/README, not an older draft or source filename guess. Preserve existing actor/interaction identities unless the handoff explicitly retires them.

| Fix | Released source | Contract / remaining checks |
|---|---|---|
| 005 | LV-SOFA-02 | Preserve old actor origin/transform; 13 UCX; seven materials. Imported, contextual visual check pending. Living rug move remains +0.15 m east. |
| 006 | ART-REV02-001 through 017 | Mapping in FIX-006/wall-art-inventory.json. All 17 unique images/frames imported; materials/placement pending. Priority :058 outer frame 1.30 × 0.90 × 0.055 m, origin (5.15,5.54,1.12), yaw180, rect [4.50,5.485,1.30,0.055]. Direct texture replaces base tint. |
| 007 | BA-HAND-TOWEL-RING-02; BA-TUB-FIXTURES-02 | [Bathroom handoff](FIX-007/Bathroom%20handoff.md), placement-contract.json and file-manifest.json. Current plan/elevations published. 102 stable IDs, 101 active after retiring duplicate rail :078. Additive drain export stays at old tub transform; existing plumbing/rod FBXs unchanged. Curtain gathers east with re-posed SLIDE; linen needs two new ROTATE actions; switch is decorative-only. Actual cabinet open/close, shower gap and traversal pending. |
| 008 | HA-SCONCE-02 | file-manifest.json: 17 files. Separate hardware/shade/bulb, closed opaque opal shade; one hardware UCX. Preserve existing sconce/light action identities; keep one visible shade via interactable Body and test all three instances. |
| 010 | ARC-ENTRY-DOOR-03 | file-manifest.json: 17 files. Original frame/leaf bounds and transforms preserved; stile-mounted hardware and matching strikes. Frame adds slot2/leaf slot3 dark recess. Preserve FrontDoor; closed alignment, sweep and exit action pending. |
| 013 | LV-ARMCHAIR-02 | release-manifest.json: 23 files. Replaces LV-CHAIR-01, same actor origin, within old bounds, 15 UCX. Four materials explicitly use texture multipliers from assembly.json. Contextual review pending. |
| 014 | LV-PLANT-02 | file-manifest.json: 15 files. Five visual groups and one pot UCX, closed outward leaf shells, upward soil and closed pot base. Preserve stand/riser and actor identity; plant origin +0.511 m above stand floor with original riser. Check 43.1 × 41.8 cm foliage against wall/fusebox. |
| 016 | HA-SLIPPERS-01 | file-manifest.json: 13 files. One pair, two meshes/common floor origin, NoCollision. Proposed origin (1170,362,0) cm, yaw90. Retire tray and all four old shoes, retain bench. Verify doorway and bench fit. |
| 018 | KI-CHAIR-02 | release-manifest.json: 21 files. Same seat/frame/legs/materials/UVs/envelope; concave reclined slats. One mesh, 26 UCX. Preserve all actor transforms, including inherited +12.38 mm mesh minimum Z. Verify all shared instances. |
| 019 | OF-WAINSCOT-02 | file-manifest.json: 17 files. [Exact handoff](FIX-019/Source%20handoff.md); six static fitted runs at (796,566,0) cm, yaw0, scale1, no blocking collision. Retire only Wainscot_OF_* modules. Reproject lead visible plane to Y5.668 m. Close documented wardrobe shell quadrant; verify trim/doors/slider. |
| 020 | HA-RUNNER-02 | file-manifest.json: 10 files. Thin 5.00 × 0.80 m body plus fringe, NoCollision. Origin (523.4,470,0.118546) cm, yaw0. Planned fringe X266.802–780.013 cm gives 14.05 cm gap before hall cabinet. Verify actual feet, floor contact and grazing-angle appearance. |

## Placement and interaction fixes without new source

- FIX-009: decorative kitchen switch :086 rect [4.705,3.595,0.035,0.1], same Z and flush mount;4.5cm jamb clearance each side. No bound switch action exists. Test Sconce_Kitchen and CeilingLight_HallEast separately.
- FIX-011: seat bedroom shelf books and tin on actual shelf top, supported within bounds, clear of wall; check side and gameplay views.
- FIX-012: recover exterior painted scenery through bedroom window by diagnosing glass, backdrop, exposure/bloom and lights; compare shared windows and retain warm interior.
- FIX-015: move office plant pot/foliage out of wall, keeping pot base supported by shelf.
- FIX-017: orient office task lamp toward desk work area; clicking base, arm or shade should toggle the same light. Preserve desk drawer actions and check cable/contact.

These items are authorized user feedback, but the engine owner's reservation still governs all engine writes and editor use. The master [fixes list](../Feedback%20fixes.md) records acceptance status; no fix closes on source review alone.
