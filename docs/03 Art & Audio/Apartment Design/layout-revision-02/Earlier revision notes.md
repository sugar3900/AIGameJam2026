> Historical version: superseded by the approved compact kitchen/dining layout on 2026-11-09. See [current handoff](README.md).

# Revision 02 — entrance living room and hall-end closet

**Status: design approved for revised elevations, with living-room option A selected.** This revision supersedes A+ for design work. Unreal maps, gameplay transforms and art exports are unchanged. The integration team's editor/Content/Tools reservation remains in force.

Open [the review page](review.html), [the approved SVG](approved-plan.svg), or [the approved coordinates](approved-plan.json). The review page can toggle the previous **documented** A+ plan; that baseline is not a survey of every current engine placement.

The user selected **living-room option A**, now incorporated into the plan, JSON and walking routes. The [three-option comparison](living-options/review.html) and [design notes](living-options/README.md) remain as decision history.

## Recommended arrangement

- Exchange the north rooms: kitchen/dining goes west, living goes east beside the apartment entrance.
- Remove the living/hall partition between x=5.50 and x=12.00, keeping a full-width cased opening and overhead header. The coat closet moves to the south side of the entrance. Shared wood flooring should eventually join the entry and living room visually. The combined gross zone is 6.50 × 5.60 m, with the former living-side coat enclosure removed. Keep circulation along the southern edge of the seating group.
- Put the entry coat closet in the old office closet corner: `[10.75, 5.60, 1.25, 0.80]` m, opening north into the entry. Place a shallower guest wardrobe immediately behind it at `[10.75, 6.40, 1.25, 0.75]`, opening south into the office. They share a back partition at y=6.40. Use sliding fronts so neither needs a door-swing zone. The guest wardrobe targets 0.60 m usable hanging depth; it is reach-in storage. Move the entry bench to the east wall north of the front door.
- Give the kitchen a doorless 1.20 m nominal cased doorway into the living room at x=5.50, y=2.35–3.55. Close its former hall doorway. Retain its separate checker floor and intimate dining character. A closed swinging kitchen door would consume useful approach space; it is not recommended in this draft.
- Move the bedroom closet entirely out of the bedroom into the former western hall end: x=0–2.20, y=3.80–5.60. Its entrance faces south into the bedroom, while the bedroom's main hall entrance remains independent to the east. Remove the old bedroom closet body and its associated obstructing partition when implementation is approved.
- The new closet has approximately 2.08 × 1.68 m inside before trim, a 1.10 m rough opening targeting 1.00 m finished clear, paired outward doors, high side shelving, one hanging bulb and mold on the north interior back wall. Its shell/doors will need a deliberate rebuild; this is not just a move of the smaller existing assembly.
- Retain the southern bedroom, bathroom and office boundaries. The bedroom bed has clear circulation on both sides and a separate approach to the closet. Move the white wainscoting and its associated lead-paint condition to the office/guestroom. The bedroom uses painterly aged plaster with baseboard and crown; closet mold stays in the bedroom closet.

## Furniture and views

The selected living-room option A has a floating sofa facing **east**, the TV on the east wall facing **west**, and the armchair facing **south** at the north end of the rug. The coffee table runs north–south with a 0.46 m gap to the sofa; the existing 2.50 × 1.80 m rug rotates with the group. The bookcase sits against the kitchen partition, and the lamp table sits beside the sofa’s south end. The kitchen route passes west of the sofa; the TV approach passes east of the coffee table. These placements use the source asset dimensions, with approximately 2.90 m from the nominal seat position to the screen. The fusebox and Wyatt repair move to the east wall immediately north of the front door: nominal footprint `[11.82, 3.40, 0.12, 0.45]` m, facing west. The bench shifts north to `[11.60, 2.70, 0.25, 0.65]` so it ends before the fusebox. Keep the repair approach clear and resolve casing/damage-layer extents in elevations. Preserve the existing living/Wyatt gameplay identity when integrating this entry-side position. From the entry, the view opens toward the seating/window; turning west reveals the kitchen doorway and the shorter private hall.

The kitchen uses the narrow sink on the west wall with prep space above and below it. The range occupies the northwest end of that run; the fridge and full-size pantry occupy the northeast. The north window/radiator remains clear of the sink worktop. The vintage table seats two at its short ends. Per the user’s swap, the prep counter finishes the west run. The existing 1.00 m upper cupboard spans y=2.525–3.525 above the adjacent 0.60 and 0.65 m west counter sections. The full-size 1.00 × 0.678 m pantry moves to `[3.25, 0.15, 1.00, 0.678]`, facing south beside the fridge.

The bedroom bed is drawn at its source footprint (about 1.50 × 1.90 m), with its head toward the south wall. The dresser is on the east wall, leaving a 1.15 m nominal aisle. The main bedroom door hinges on the **east jamb** so an open leaf does not block the turn toward the closet. The closet opening faces open floor instead of the bed.

Per the user’s follow-up, white wainscoting now belongs in the office/guestroom. Place the separate lead-paint condition on the north wall between the storage cabinet and room door (x=8.65–9.20 m), with its approach kept clear. Move the office bookcase to the bedroom west wall at `[0.15, 6.45, 0.30, 1.10]` m, beside the closet approach. This fills the bedroom’s open wall and frees space in front of the new guest wardrobe. Keep the office desk, daybed, storage cabinet and lamp. Shift the office doorway 0.15 m west to leave 0.25 m nominal between its east jamb and the coat closet side; verify frame/casing widths later. Panel, window-apron and closet trim fitting will be resolved in the revised elevations.

The hallway keeps both existing console pieces. Place `HA-CABINET-01` at the new west terminus, against the east face of the relocated bedroom closet: `[2.28, 4.19, 0.2475, 1.02]` m, facing east. Retain its landscape picture and vase as the end-of-hall focal group. Move `HA-CONSOLE-01` to the hall-facing south wall between the bathroom and office doors: `[7.85, 5.27, 1.05, 0.25]` m, facing north. This leaves 0.55 m nominal to each adjacent doorway and removes the side console from the north wall. Positions use the source assets’ dimensions rather than resizing them. Both pieces have a 0.02 m allowance from the nominal wall face; confirm skirting, hardware and animated doors/drawers later.

## Clearance review

| Location | Proposed allowance | Limitation |
|---|---:|---|
| Living sofa to coffee table | 0.46 m | Seated-access gap, not the main walking route |
| Living seat to screen | About 2.90 m | Nominal seat point, not a viewing standard |
| Living / entry opening | 6.50 m nominal | Header and jambs need later detailing |
| Guest wardrobe | 0.75 m nominal depth; target 0.60 m usable | Allow for walls, sliding tracks and trim |
| Guest wardrobe front approach | 0.90 m reserved | Keep clear of small props and furniture |
| Bedroom bookcase to bed | 1.15 m where their lengths overlap | Does not obstruct closet door swing |
| Kitchen doorway | 1.20 m rough; about 1.10 m finished clear | Depends on frame/casing |
| Private hallway | 1.68 m between wall faces | End cabinet stays at western terminus |
| Side console to adjacent doorways | 0.55 m each side | Before casing; doors open into rooms |
| Side console front to old north-wall face | 1.41 m closed / about 1.28 m drawer open | Living room is open on the north side here; verify hardware |
| Bedroom closet entry | About 1.00 m finished clear | Wider doors than existing asset |
| Beyond fully open closet leaves to bed's north edge | 1.30 m in the north–south direction | Actual swept geometry and interaction camera still need testing |
| Bed to dresser front | 1.15 m | Drawer extension temporarily reduces this |
| Kitchen table to south wall face | 1.04 m | Before skirting/protrusions |
| Kitchen north prep to table | 1.05 m | Appliance doors need separate motion checks |
| Sink front to parked west chair | 1.22 m | Pulling the chair out reduces this aisle |

SVG and JSON parse checks passed. Sampled route centre-lines stay at least 0.40 m from the depicted floor-furniture rectangles; no floor furniture rectangles overlap. This is a 2D planning check, **not** a test of the engine capsule, door collisions, trim or encounter cameras. Routes show primary access, not every interaction stance. Bathroom footprints are carried forward; office closets and doorway are revised, with engine validation still pending.

## Elevation and implementation handoff

1. Rework both north-room elevations, the hall, bedroom/closet and office/guestroom elevations. Preserve the painterly fixer-upper direction and existing major pieces where they fit.
2. Widen the new living window from 1.10 to 1.60 m around its existing centre (x=8.55). Keep the former living window for the kitchen. Shift the bedroom opening 0.25 m west to clear its east-wall casing conflict. Detail ordinary plaster/trim at the bedroom sill. In the office, terminate the relocated wainscoting around the window apron, fitted closet and room doorway.
3. Relocate kitchen water/waste to the west wall. The service route is a design assumption needing a new plan, not proof that an existing plumbing run works. Use KI-SINK-NARROW-01; the full sink-plus-cabinet assembly does not match this footprint.
4. Rebuild the entry coat closet and shallower guest wardrobe with a shared back wall and opposite-facing sliding fronts; do not stack duplicate shell walls. Relocate the office bookcase and entry bench as drawn. Keep the hall-end cabinet at the new terminus and move the narrow side console between the bathroom and office doors. Rebuild the larger bedroom closet shell/doors while preserving the hidden mold, hanging bulb, interaction state and reveal. Test with Malcolm standing, the player, both doors and the dialogue camera.
5. Update room/repair volumes, lighting, floor transitions, nav/collision, save-location fallback and the in-game floor-plan UI through the integration team. Check existing source dimensions and pivots before moving imports.
6. Reassess bathroom and office sightlines from the open living room. Their doors can close for privacy; if the user prefers a screened vestibule, resolve that at this floor-plan stage rather than adding obstructions later.

The approved SVG/JSON are the canonical design files; `proposed-plan.*` remain identical compatibility copies for the study generator. Revised elevations live in `elevations/`. No commit, push, rebase or editor operation was performed.

## Fitted-width pieces identified in elevation review

The user's pantry/prep swap allows the existing 1.00 m pantry and existing 1.00 m upper cupboard to be reused at their proper dimensions. West prep frontages of 0.45, 0.60 and 0.65 m still need coordinated cabinet widths. The range’s source depth including controls is 0.732 m; its plan footprint includes those controls, and the adjacent prep begins y=0.90 to avoid overlap. The entry fusebox now uses its 0.45 m source width; the bench shifts 0.05 m north to preserve separation. These are fit details within the selected arrangement. Room/entry frames must match the selected wider openings; the existing 0.90 m clear kits require width variants.

## Compact kitchen / dining alternative

After selecting living A, the user asked to try the kitchen counter and sink on the north window wall, pantry/fridge on the west, a smaller kitchen, and dining between kitchen and sofa. The [saved alternative SVG](kitchen-dining-study/proposed-plan.svg), [coordinates](kitchen-dining-study/proposed-plan.json) and [matching elevation viewer](kitchen-dining-study/elevations/review.html) preserve that exploration separately. Its kitchen is4.80 m wide; the dining table rotates north–south. The optional wall table is0.90 ×0.45 m with a tucked stool. The sink window is a new counter-height variant, not the original low-sill kit.

The [original selected revision02 elevation set](elevations/README.md) is also complete. All sets include four walls for each main room and each closet/storage interior, plus optional furniture projections and localized repaired-state views. No engine changes have been made.
