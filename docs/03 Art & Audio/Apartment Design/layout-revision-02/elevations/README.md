# Earlier revision 02 / living A — superseded — elevation set

Historical elevation set, superseded by the approved compact kitchen/dining set in kitchen-dining-study/elevations. Do not use these older kitchen coordinates for integration.

## Drawings

[Interactive room/wall viewer](review.html). Each room has north, east, south and west views; individual wall SVGs also have a `-projected` version with floating/opposite-side furniture. Numbered markers refer to one physical assembly, even when it is visible in multiple views.

- [Living + entry: four-wall sheet](lv-elevations.svg)
- [Kitchen / dining: four-wall sheet](ki-elevations.svg)
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
- Bedroom closet: mold stays on north interior back wall, with a single bulb and clear standing space. Doors conceal it. Coat and guest closets are separate, back-to-back reach-in storage.
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

