# Approved compact kitchen + dining — elevation set

Approved by the user on 2026-11-09. Compact kitchen with north-wall fridge beside prep, sink under the window, west-wall pantry and dining between kitchen and sofa. This is the current design handoff, including the approved FIX-007 bathroom placement revision; engine acceptance remains pending.

## Drawings

[Interactive room/wall viewer](review.html). Each room has north, east, south and west views; individual wall SVGs also have a `-projected` version with floating/opposite-side furniture. Numbered markers refer to one physical assembly, even when it is visible in multiple views.

- [Living / dining + entry: four-wall sheet](lv-elevations.svg)
- [Compact kitchen: four-wall sheet](ki-elevations.svg)
- [Hall: four-wall sheet](ha-elevations.svg)
- [Bedroom: four-wall sheet](br-elevations.svg)
- [Bathroom: four-wall sheet](ba-elevations.svg)
- [Office / guest: four-wall sheet](of-elevations.svg)
- [Mold closet: four-wall sheet](bc-elevations.svg)
- [Entry coat closet: four-wall sheet](ct-elevations.svg)
- [Guest wardrobe: four-wall sheet](wg-elevations.svg)

## Surface and interaction design

- Living, hall and bedroom: warm painterly plaster, original base/crown and honey wood floor. Bedroom has no wainscoting.
- Office/guest: white 1.10 m wainscoting; interrupt panels and rail around window/apron, doors and wardrobe. Reuse BR-WAINSCOT-01 under its stable asset ID. The separate lead-paint condition is on the office north wall.
- Kitchen: muted sage cabinetry, cream enamel, restrained backsplash and warm checker floor. Worktops 0.91 m; sink upstand 1.135 m, faucet 1.343 m. Cabinet frontages need fitted variants, not nonuniform scaling of hardware.
- Bathroom: pink tile with cream grout, localized Tyler damage; preserve the tub, fixtures, water reveal and operable parked curtain.
- Bedroom closet: diffuse BR-MOLD-02 charcoal colonies wrap the upper-right north/east corner; both overlays disappear on repair. BR-CLOSET-STORAGE-03 adds full-length shelves on both sidewalls, 35 mm boards with tops at 1.88 m and hooked hangers under rails at 1.73 m. Clear hanger-to-hanger aisle is 1.094 m; retain single bulb and existing encounter transforms.
- Damaged/repaired study SVGs: [mold closet](bc-n-repaired.svg), [office paint](of-n-repaired.svg), [bath tile](ba-s-repaired.svg). These depict removal of localized damage, not new gameplay implementation.

## Construction and export notes

- Door wall cuts allow 3 cm per side beyond clear frame width, with rough heads 2.14 m; sliders 2.18 m. New room/entry door widths require matching frame/leaf variants. Closet pair uses 1.10 m rough and 1.00 m clear target.
- Wainscoting projects up to 0.072 m; finish/casing/trim clearances must be deducted in engine. Floor-plan figures are planning values.
- Rebuild the larger bedroom closet shell and paired doors; fit the two smaller storage shells around their shared wall, avoiding duplicate geometry.
- Future moving exports should include UCX collision. Re-imports currently need the integration team’s collision script; see the durable integration handoff.
- Source front-axis conversion is not identical across kits. Plan-facing directions control placement; use the verified imported sofa +Y front.
- All static scene items and mounted dressing have physical records in [elevation-schedule.json](elevation-schedule.json). Some child props remain candidates or reuse existing geometry with distinct artwork; inclusion is not a claim of production readiness.

## Review and limits

- SVG parsing, opening extents and coverage of every scheduled assembly were checked. Footprint checks cover primary routes in the matching floor-plan JSON.
- The clean sheets show walls and nearby furniture; the projected sheets also show the floating sofa, table and opposite-wall pieces. An object repeated across views is not an instruction to duplicate it.
- No Unreal editor, source mesh, export, material or map was modified. These drawings require dimensional/collision/lighting validation during integration.
- Do not re-open an obsolete A+ elevation for placement. Use this set together with its matching revision floor plan.

## Feedback placement changes

- FIX-007: revised bathroom fixtures and lower tile cap; toilet north, basin/mirror east, one source-size bath rail west, real hand-towel ring, split west-end tub plumbing and north-facing linen. See [Bathroom handoff](../../feedback/FIX-007/Bathroom%20handoff.md) and its exact placement contract. Original IDs retained; duplicate rail :078 is inactive. Engine interaction/traversal acceptance pending.
- FIX-003: KI-LEAK-02 replaces the sink body and embedded bucket with a separate galvanized pail; original tap controls and Lukey identity remain. New water/puddle are optional transparent effects; retire old static beads/puddle and authored-leak fallback.
- FIX-004: fuse box moves above the corner plant on the north wall, facing south, at lower-edge origin(11.05,0.06,1.40). Move door/wires/damage together; west hinge is retained. Coat rack centers at east-wall y 3.30; bench stays. Engine interaction and encounter checks remain pending.
- FIX-005: rug shifts 0.15 m east toward the coffee table; sofa footprint remains unchanged pending its source replacement.
- FIX-006: preserve all 17 wall-art instance IDs for unique images/frames. Hall :058 target is 1.30x 0.90 m centeredX 5.15, bottomZ 1.12 between bedroom and bathroom casings. Source assignments pending.

## New kitchen/dining fit requirements

- Kitchen width 4.80 m; partition x=4.80, portal y=2.35–3.55. Bookcase follows partition. Living A seating is unchanged.
- North sink centred x=2.15; aperture 1.60 m wide, sill 1.25/head 2.40. Short apron bottom>=1.18 m; sill projection<=0.12 m from finished wall. Check faucet at 1.343 m against glass/sash in depth.
- Fridge faces south beside north prep, at x=0.35 with 0.29 m to west wall face and 0.08 m to prep. Prep frontage is 0.425 m; pantry remains west facing east. Nominal 105-degree fridge sweep needs 3D hardware/shelf validation. The east-return upper remains full-size 1.00 m; check doors at the corner, with no cupboard directly above burners.
- Optional wall table 0.90 ×0.45 m and tucked stool are new pieces; do not squash the vintage dining table to make them.
- Kitchen radiator from the earlier window wall is omitted in this alternative; any needed heating provision belongs to the later service/layout pass.
- Dining chairs pull north/south; keep both side aisles clear. A 0.40 m south-chair pullback leaves 0.40 m to the route centreline, which still needs capsule verification.

