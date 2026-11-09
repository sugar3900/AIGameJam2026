---
tags: [environment, level-design]
status: draft
---
# Apartment room build guide

This is the handoff for building the selected **A+ gallery plan** in engine while environment art is still arriving. The layout is a design target and blockout, not a verified construction drawing or a finished game level. The room-by-room elevations define the intended density and look; use temporary stand-ins where assets are not ready and replace them as the art worktree supplies reviewed exports. Do not wait for all small props before validating the shell.

## Source of truth and where to start

- [Selected floor plan](A-plus-candidate.svg) and [machine-readable coordinates](A-plus-candidate.json): use the JSON rectangles and opening coordinates for the initial blockout. `rect` is `[x, y, width, depth]` in metres. Room and object rectangles in JSON are nominal; walls use centre-lines, not finished faces.
- Elevations: [living](elevations/01-living-elevations.svg), [kitchen](elevations/02-kitchen-elevations.svg), [hall](elevations/03-hall-elevations.svg), [bedroom](elevations/bedroom.svg), [closet interior](elevations/bedroom-closet-interior.svg), [bathroom](elevations/bathroom.svg), and [office](elevations/office.svg). The room-facing order is north west→east, east north→south, south east→west, west south→north. Check handedness before placing openings and fixtures.
- [Visual brief](Design%20brief.md), [asset status](Asset%20production.md), [FBX handoff snapshot](FBX%20handoff%20snapshot.md), [inventory coverage](Inventory%20coverage.md), [social inventory](elevations/social-room-asset-notes.md), [private inventory](elevations/private-room-asset-notes.md), and [game integration handoff](Integration%20handoff.md). The selected [painterly fixer-upper reference](../../../Art%20Source/Environment%20Concepts/painterly-fixer-upper.png) controls the overall art direction.
- Art is being produced in the separate worktree `/Users/davidwallin/Developer/AIGameJam2026-environment`, branch `environment/apartment-redesign`. Sources and FBXs are under `Art Source/Apartment Redesign/Assets/<ID>/`; each item contains a README, previews and material/animation caveats. **The redesign files are currently uncommitted**; another checkout will not automatically contain them. Coordinate asset handoff across branches/worktrees instead of editing the art worktree or assuming it is in main.

## Coordinates and shell

For blockout, treat `(0,0)` as the **intersection of the north and west exterior wall centre-lines**, +x east/right and +y south/down. The JSON also calls this the exterior corner; that wording is ambiguous. With 0.12 m walls centred on these lines, the outer face is 0.06 m beyond each perimeter centre-line and the physical outer bounds become 12.12 × 9.67 m. Keep the room/opening coordinates unchanged under this convention; resolve and update the plan if the engine blockout instead anchors exterior faces. A convenient independent Unreal mapping is `UE X = 100 × plan x`, `UE Y = 100 × plan y`, `UE Z = 100 × height` in centimetres, plus any single consistent world offset. This is a proposed mapping, not an assertion about the current level's axes; if the existing level uses another orientation, transform the entire plan consistently. Ceiling target is 2.75 m. Overall nominal envelope: **12.00 × 9.55 m**.

| Space | Plan rectangle `[x, y, width, depth]` m | Intent |
|---|---|---|
| Living | `[0, 0, 5.50, 3.80]` | Sofa and TV conversation, window, fuse repair |
| Kitchen / dining | `[5.50, 0, 6.50, 3.80]` | North-wall appliance/counter run and central dining |
| Hall | `[0, 3.80, 12.00, 1.80]` | Main spine, entry at east, gallery view at west |
| Bedroom | `[0, 5.60, 4.80, 3.95]` | Bed, dresser, white wainscot and walk-in closet |
| Bathroom | `[4.80, 5.60, 3.10, 3.95]` | Pink tile, tub, pedestal basin and toilet |
| Office / guest | `[7.90, 5.60, 4.10, 3.95]` | Desk, daybed and fitted closet |

Nominal partitions are 0.12 m thick. A 1.80 m hall between centrelines gives approximately **1.68 m clear before trim**, not 1.80 m of free walking width. Door leaves are nominally 0.90 m; allow for casing and frame in actual structural openings. Verify the player's collision capsule and camera, not only the diagram. The kitchen and bath lie across the hall; a below-floor or accessible service chase is a design assumption, not modeled plumbing.

## Openings

Coordinates below are opening **starts** and widths along the indicated plan axis. Horizontal openings extend +x; vertical openings extend +y. Plan swing direction indicates intended side, but hinge position and exact frame opening must be resolved against the SVG and the actual moving asset.

| Door | Start `(x, y)` m | Width | Opens |
|---|---|---:|---|
| Living / hall | `(4.05, 3.80)` | 0.90 m | North into living |
| Kitchen / hall | `(6.20, 3.80)` | 0.90 m | North into kitchen |
| Bedroom / hall | `(3.15, 5.60)` | 0.90 m | South into bedroom |
| Bathroom / hall | `(6.35, 5.60)` | 0.90 m | South into bathroom |
| Office / hall | `(9.65, 5.60)` | 0.90 m | South into office |
| East entry | `(12.00, 3.975)` | 0.90 m | East/outward; outside landing is unresolved |

| Window | Start `(x, y)` m | Width | Sill / head above floor |
|---|---|---:|---|
| Living north | `(1.35, 0)` | 1.60 m | 0.90 / 2.30 m |
| Kitchen north | `(8.00, 0)` | 1.10 m | 0.90 / 2.30 m |
| Bedroom south | `(3.55, 9.55)` | 1.10 m | 0.90 / 2.30 m |
| Bathroom south | `(5.25, 9.55)` | 1.15 m | 1.50 / 2.30 m; frosted |
| Office south | `(9.70, 9.55)` | 1.40 m | 0.90 / 2.30 m |

Windows face outside the rectangular envelope. Model actual glazing, casings, sills, wall openings and light; do not leave solid collision behind an opening. Curtain kits may need a skeletal/morph import rather than a static FBX; consult their README.

## Room composition and focal points

- **Living:** warm aged plaster, honey wood floor, original trim. Sofa on west wall faces TV/console east; north window with chair/radiator and bookcase, coffee table and rug in the middle. Fusebox and its damaged plaster on the south wall belong to **Wyatt**. Allow a readable approach to the fusebox and interesting views toward the window, sofa and TV.
- **Kitchen/dining:** worn cream/terracotta checker floor and sage cabinets; on the north wall from west to east are fridge, range, counter, sink under window, and more counter. A narrow pantry is east. The vintage dining table sits centrally with chairs at the short ends. **Lukey** is the leak under the sink; bucket/water and repair state must remain visible and reachable. Check doors and chair paths in 3D.
- **Hall:** entry on the east end; a long gallery sightline ends at a framed focal piece to the west. Shallow console, pedestal, bench and end cabinet should remain at or below their planned 0.25 m depth; actual player and camera clearance takes priority. The coat closet sits on the north side in the kitchen footprint, with sliding doors facing the hall.
- **Bedroom:** vintage bed and floral bedding toward the south wall, narrow dresser on east, shelves and framed art around the room. White wainscoting wraps the walls with a **localized lead-paint condition on the east wall**, distinct from Malcolm. Preserve a nominal 0.90 m bed-to-dresser passage before trim and drawer movement; validate in engine. Lead-paint character/gameplay is not currently implemented.
- **Bathroom:** pink tile wainscot and warmer plaster above; tub along south beneath the frosted window, basin west, toilet and linen cabinet east. **Tyler** is the localized cracked tile above the tub; the intact and broken appearances are separate. Preserve visibility and interaction reach, and avoid placing the shower curtain over the repair.
- **Office/guest:** a window-lit desk on the south, daybed west, low bookcase and floor lamp east, and small fitted closet at the northeast. Keep the desk chair and central turning area usable. This room should feel like a lived-in second bedroom or study, not an empty utility space.

Use object rectangles in the JSON for initial placement. Hall decor and some bath/office dressing were added during elevation review and are provisional. The current `LV-LAMP-01` export is a **1.56 m floor lamp**, suitable for the office floor-lamp position; the similarly named 0.52 m living-room table lamp in the inventory still needs a separate model. Asset dimensions can differ from the drawn footprint; for example, the current radiator includes pipework beyond its nominal depth. Review actual bounds, door and drawer sweeps, and sightlines instead of forcing colliding art into place.

## Known fit conflicts: resolve in the first blockout

These discrepancies were found in a read-only review of the actual exports. Do not assume the 2D plan already resolves them.

- **Kitchen sink/counters:** `KI-SINK-01` is a 2.37 m assembly, including the 1.05 m sink and two 0.66 m side cabinets. If centered on the planned sink at x=8.485, it spans approximately x=7.30–9.67. It already occupies the planned x=7.28–7.93 counter and part of x=9.05–10.20 counter. Either use its built-in side cabinets and omit overlapping `KI-CABINET-01` bodies, or use the reviewed `KI-SINK-NARROW-01` 1.05 m sink-only alternative with separately fitted side cabinets; do not place both sink assemblies. Fit additional non-overlapping cabinets/counter only in remaining space. Verify seams and reconcile the counter run and plan after the actual meshes are placed.
- **Kitchen sink/window vertical fit:** sink worktop is 0.91 m above the floor; the narrow window kit's sill spans approximately 0.872–0.917 m and its apron projects below that. They intersect at the current shared wall. Resolve with a coordinated sill/apron, sink and opening adjustment in 3D (for example, investigate raising the complete opening and checking head trim against the 2.75 m ceiling), then update the plan/window schedule. Also check faucet/upstand and sash motion. Do not silently stretch or clip the model.
- **Bedroom window/east wall:** its opening currently ends at x=4.65, only 0.15 m from the east partition centre-line. The 1.33 m casing around the 1.10 m opening reaches about x=4.765; a 0.12 m centered east partition has a room-facing plane at x=4.74, so the casing overlaps it by roughly 0.025 m. Investigate shifting the window left or adapting trim, preserving access and updating the plan after checking bed/curtains.
- **Bedroom window/wainscoting:** window sill is 0.90 m but wainscot and rail reach 1.10 m. Interrupt or adapt panels, rail and window apron under the window; do not place a continuous wainscot rail through the window assembly.
- **Avoid duplicated shells:** `ARC-LIVING-WALL-01` already includes wall geometry and base/crown; its window-wall kit also includes its own separate fixed sash/casing and glazing. Use either that window assembly or the separately reviewed operable `ARC-WINDOW-01` components, and remove/omit overlapping trim rather than stacking the kits. `BR-CLOSET-01` body includes closet walls, ceiling and floor; do not place duplicate blockout surfaces in the same location. Its mold is a separate masked mesh.
- Wall materials that use mirrored world-space projection need their documented Unreal material graph; ordinary UV import will not reproduce the Blender result. Check rotated walls and corners, as well as any visible mirrored symmetry, in room lighting.

## Closet geometry and reveal

- Bedroom closet occupies `[0, 5.60, 1.80, 1.45]` m, full 2.75 m height. Its front faces south at `y = 7.05`; a 0.90 m opening starts at `x = 0.45` with **two 0.45 m leaves hinged outward into the bedroom**. Mold belongs on the **interior north/back wall**. A single bare bulb dangles from the closet ceiling. The interior must fit Malcolm standing, not merely a flat decal.
- Closed leaves conceal mold and prevent its glow, prompt and interaction from leaking through the door. Open leaves reveal the mold and allow the encounter. Preserve the closet, doors and bulb after repair; remove only repair damage. The lead-paint condition is separate and must not share Malcolm's save ID.
- Existing encounter logic teleports the player to a talk spot and uses a malady camera and hunk spawn. Test the actual character, camera, door leaves, shelves and line traces together in this small volume. Position shelves and the bulb around the standing character rather than blocking him. See the [closet elevation](elevations/bedroom-closet-interior.svg) and [integration handoff](Integration%20handoff.md).
- Office fitted closet is `[10.75, 5.60, 1.25, 1.20]` m with a 0.90 m sliding opening starting x=10.93 on the south-facing front. Hall coat closet is `[10.70, 3.00, 1.30, 0.80]` m with a 0.90 m sliding opening starting x=10.90 on the south/hall-facing front. The reviewed `ARC-SLIDING-CLOSET-01` is a bypass wardrobe front: its 0.90 m opening reveals only about 0.44 m with one panel slid aside; it is for storage, not the walk-in mold closet. Check both against physical wall thickness and adjacent furniture.

## Exterior sky

`ENV-SKY-01` is a provisionally reviewed painterly golden-hour 360° sky, with a soft brick-rowhouse/tree horizon. The 2K PNG and LDR-derived RGBE are ready for Unreal import and evaluation; the latter is not a captured HDRI. It is a texture/environment asset rather than an FBX, so it will not appear in the FBX snapshot; see its asset README and [production log](Asset%20production.md) for current status and orientation. Match the visible sun direction to the actual directional light, and avoid counting an LDR image as true HDR illumination.

## First playable assembly and acceptance

1. Block out walls, floors, ceilings, openings and closet volumes; confirm the plan and elevations together. Add the actual player capsule and a temporary camera early. Test entry, room access, navigation, wall/camera clipping and door swings.
2. Place major existing art as it becomes available: `ARC-LIVING-WALL-01` (avoid duplicate casing/trim as described above), `ARC-DOOR-01`, `ARC-ENTRY-DOOR-01`, `BR-CLOSET-01`, `BR-WAINSCOT-01`, `BA-TILE-01`, `LV-SOFA-01`, `LV-FUSE-01`, `KI-FRIDGE-01`, `KI-RANGE-01`, `KI-SINK-01`, `KI-CABINET-01`, `KI-TABLE-01`, `BA-TUB-01`, `BA-BASIN-01`, `BA-TOILET-01`, `BR-BED-01`, `BR-DRESSER-01`, `OF-DESK-01`, `OF-DAYBED-01`. Check each README for export parts, pivot, sizing and material work; no FBX implies an Unreal-ready material. `ARC-FLOOR-WOOD-01`, `KI-TILE-01` and `BA-FLOOR-01` have reviewed preliminary floor modules with optional separate wear layers; in-room evaluation is pending. `ARC-CEILING-PLASTER-01` has a reviewed repeatable ceiling module. `ARC-BEDROOM-PLASTER-01` has a reviewed upper-wall finish for placement above the white wainscoting. `KI-BACKSPLASH-01` has a reviewed module; evaluate its checker pattern alongside the kitchen floor. `ARC-WINDOW-01` has a reviewed 1.60 m living-window kit and `ARC-WINDOW-NARROW-01` fits the 1.10 m kitchen/bedroom openings; `ARC-WINDOW-BATH-01` fits the 1.15 × 0.80 m bathroom opening and `ARC-WINDOW-OFFICE-01` fits the 1.40 m office opening; all still need Unreal glass and motion testing. `ARC-TRIM-01` has reviewed straight strips and 90° inside-corner miter variants; outside and casing corners need fitting in engine.
3. Keep the existing room IDs `living`, `kitchen`, `bathroom`, `bedroom` and hunk IDs `wyatt`, `lukey`, `tyler`, `malcolm` compatible. Deliberately implement hall/office room volumes and map UI. Existing saved player locations are world-space: migrate or validate them with a safe fallback when walls move, without discarding relationship or repair progress.
4. Recreate painterly materials and lighting; check wall tiling at rotated walls, glass/reflection, textile and foliage settings, bulb emission and actual light. Do not rely on a studio render to establish in-game appearance.
5. Test first visit, all four existing encounters, closet closed/open/repaired states, save/load/reset, old saves, floor-plan travel and actual character dialogue framing. Capture representative views of each room and log unresolved differences. Lead paint is a separate future gameplay item and should not be presented as implemented until it has its own content and state.

Treat the chosen plan as a design target: if an in-engine test exposes a collision or layout error, document the specific adjustment and update the plan/elevation together rather than silently changing one representation.
