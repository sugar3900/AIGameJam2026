# FIX-007 bathroom handoff

The reviewed bathroom revision is published in the current `kitchen-dining-study/approved-plan.json` and `elevations/elevation-schedule.json`. The corresponding floor-plan SVG and all four bathroom elevations are regenerated. Historical layouts are unchanged. The draft directory preserves the reviewed proposal and the previous current JSON for comparison.

Source geometry checks pass. Engine placement, collision, real clicks, lighting and encounter acceptance remain pending. Nothing in Content, Tools, Source, Config or the maps was changed by this source pass.

## Placement contract

All positions below are metres in the approved plan coordinates (+X east, +Y south, +Z up). The exact contract, source-to-plan formulas and tile panel extents are in [placement-contract.json](placement-contract.json). Never derive pivots from illustration bounds.

| Instance | Placement / retained behaviour |
|---|---|
| Basin :002 | East wall, facing west. Assembly floor origin `(7.542,7.925,0)`; body and original tap controls move together. Preserve Basin_Tap. |
| Toilet :003 | North wall west of doorway, facing south. Origin `(5.55,6.03,0)`; preserve lid pivot and travel. |
| Linen :004 | Same southeast floor origin `(7.45,9.05,0)`, now facing north toward the door. Limit both doors to 90°; greater travel intersects the east tile. Create two new ROTATE controls from source pivots; no linen-door actions currently exist. Verify open/close with real clicks. |
| Basket :008 | West floor under retained rail, origin `(5.12,8.18,0)`. |
| Mirror :076 | East wall aligned with basin, floor-height assembly origin `(7.822,7.925,0)` (18 mm west of the plaster face; source rear maximum Y is +0.018 m, placing the back flush at X=7.84). Move mirror, both sconces and globes together; retain light labels. Actual overall globe width is 1.014 m. |
| Shelf :077 | East toiletries shelf centred Y=7.10, top Z=1.25. Ring beneath centre, between corbels. |
| Rail :078 | Intentional removal of duplicate rail and its extra towel. Stable record retained with `active:false`; do not place. |
| Switch :079 | North wall right/east of door, centre `(7.60,5.66,1.24)`, facing south. Plan footprint .10 m along X × .035 m along Y. Existing plate/toggle are decorative only; relocate together. No new switch action in this placement fix. |
| Shelf :080 | East second toiletries shelf centred Y=6.35, top Z=1.25; existing jars and soap follow. |
| North art :081 | Retain current placement this pass; unique artwork/frame assignment is separate FIX-006 work. |
| Hook identity :082 | Replace hook/old cloth with BA-HAND-TOWEL-RING-02 hardware and folded towel, shared plate-centre origin `(7.84,7.10,1.15)`, facing west. |
| Paper :083 | West wall beside toilet. Holder origin `(4.878,6.13,.72)`, facing east; load the separate paper mesh as well. |
| Rail :084 | Single full-size 1.13 m rail, west wall, bar origin `(4.86,7.925,1.25)`. Retain ivory towel at its original source offset; remove rose towel. Ends Y=7.36..8.49. |
| Shelf :085 | West folded-towel/tin shelf centred Y=6.95, top Z=1.25. |
| Tile damage :086 | Tyler overlay and repair identity stay unchanged. |

Shelves use source top as their Z datum: body bounds Z=1.105..1.25. Do not use the schedule's schematic `z+h` as a new geometry origin. The mirror begins Z=1.176, the basin reaches .939, and the ordinary tile cap ends 1.05 between them.

## New source exports

`Art Source/Apartment Redesign/Assets/BA-HAND-TOWEL-RING-02/` contains two static FBXs, original blend, reproducible builder, packed colour textures, concept and two source previews. The ring crosses the tile-cap height but remains 17 mm in front of its 36 mm projection. Cloth starts below the cap. Plate stays wall mounted.

`Art Source/Apartment Redesign/Assets/BA-TUB-FIXTURES-02/` contains separate plumbing, curtain-rod and drain FBXs. Move plumbing to the west end at tub centre Y=9.07. Keep the rod at the old combined fixture transform. The old source combined plumbing and rod, so do not simply rotate the old mesh. See the kit README and assembly.json for exact tap pivots, source conversion and fill-effect endpoints. The separate drain uses the exact original tub/combined-fixture transform and stays seated in the basin; do not transform it with wall plumbing. The initial split release omitted it, now corrected additively. Original tub, taps, curtain and bath-water sources are untouched. Re-pose the existing Shower_Curtain SLIDE to gather at the east end, clear of the new west riser; validate both endpoints/full travel against the rod and linen doors.

Both kits have independent FBX roundtrip validation, finite vertices, UVs and preserved origin/bounds. They are decorative and have no added blocking collision; retain the existing interactive tap collision.

## Loaded toilet paper

The original BA-ROLL-01 source already includes a separate paper mesh. Reuse `BA_Roll_Holder.fbx` and `BA_Roll_Paper.fbx`; investigate hidden/missing assembly or materials before replacing the source. Source paper pivot `(0,−.071,−.014)` transforms to plan `(4.949,6.13,.706)`. If import baked this offset, do not add it again. The spindle runs parallel to the west wall. Paper source bounds relative to assembly are X ±.0523, Y −.118..−.024, Z −.089..+.033.

Paper is matte, roughness .92, metallic 0, tint `(0.96,.94,.88)`, with two-sided tail. Cardboard tint `(0.54,.44,.32)`, roughness .95. Holder brass tint `(0.80,.75,.56)`, metallic .68, roughness .45. Preserve the source texture connection.

## Tile field and shower corner

Ordinary tiles run floor to 1.00 m with a 50 mm cap to 1.05 m. Existing 100 mm tile pitch stays unchanged: crop/remove one row from the old low module rather than vertically scaling grout. Tile projects 18 mm; cap projects 36 mm.

West and east high tile starts at Y=8.55, with a 50 mm vertical trim at Y=8.50..8.55, and runs to ceiling 2.75 m. The remaining bath rail ends before that trim. South wall is full height, cut around the original window X=5.25..6.40, Z=1.50..2.30. Do not continue horizontal low cap through the shower area or window. Exact panels are in the contract.

At the southwest corner verify structural wall overlap in X=4.74..4.86, Y=9.49..9.61 and clean tile mitres. Diagnose the reported bright slit using geometry/normals and lighting; source drawings do not prove the in-engine gap has been repaired.

## Validation and engine acceptance

[layout-validation.json](layout-validation.json) checks a radius .38 m circular capsule against conservative source bounds, open 90° room door and open 90° linen door. Five routes pass with continuous lower-bound margins: entry 92.5 mm, toilet 106.5 mm, basin 79.5 mm, tub 64.3 mm, cabinet 35 mm. This is analytical supporting evidence, not PIE verification. Cabinet opening at 90° has 29 mm east-tile clearance; 95° and 100° collide and are rejected.

All 102 schedule IDs remain; 101 are active after the intentional duplicate-rail removal. Non-bathroom item records, room extents, openings and ceiling fixtures are unchanged. All generated SVGs parse and active items have elevation coverage.

Engine acceptance must exercise the real pawn routes, toilet lid, both linen doors, basin taps, Tub_Faucet/fill, Shower_Curtain, relocated existing lights, decorative switch placement, loaded paper visibility, Tyler camera/repair, and the southwest light seam. Preserve all existing interaction labels. Source work does not claim those tests passed.

## Rebuild

Run `generate_plan.py --kitchen-dining-study`, then `elevations/generate_elevations.py --kitchen-dining-study`, then `elevations/package_review.py --kitchen-dining-study` from layout-revision-02. They consume `feedback/FIX-007/bathroom_layout.py`. Run `feedback/FIX-007/validate_layout.py` for regression/route checks. Do not run the historic draft builder; its reviewed output is preserved as a snapshot.

## Engine audit reconciliation

Use the published exact positions above rather than earlier approximate suggestions. In particular the basin remains Y7.925 and linen floor origin remains (7.45,9.05), with a 90-degree stop; pushing the linen south flush or moving the basin north would change the reviewed clearances. Actual source bounds and real sweeps decide acceptance. The ring kit now exists. The paper roll exists in source and is mostly occluded by the current incorrect wall offset, so correct the complete mounting transform. Shelf/rail retirements follow stable schedule IDs, not old wall descriptions.

Two new linen-door actions must be counted as additions in parity documentation. The decorative-only switch has no toggle action to preserve. Confirm real cabinet clicks and collision after binding. The southwest light seam still requires live diagnosis; the source pass does not claim it fixed.
