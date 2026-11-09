# Social rooms: asset and surface inventory

Working inventory for the A+ living room, kitchen/dining room and hall. Cross-check against `01-living-elevations.svg`, `02-kitchen-elevations.svg`, `03-hall-elevations.svg` and the current A+ plan. **Dimensions are preliminary metres, width × depth × height**; verify actual placement, floor clearance and 3D camera framing before modeling. `W` follows the relevant wall; depth projects into the room. Doors and windows use nominal openings, with detailed trim thickness to be resolved. `×` in quantity means repeated placements, not necessarily distinct models.

IDs below are stable design IDs. A single elevation label can represent an assembly: its child IDs identify separate model/texture/interaction candidates. Repeated paintings, books, jars and plants can share geometry while changing artwork, color or arrangement. `Static` means no planned gameplay motion; it does not preclude physics or dressing. Potential interactions are design opportunities, not a commitment that game code already supports them. Room-facing wall drawings follow N west→east, E north→south, S east→west, W south→north; the same door has only one physical asset.

## Architecture and room surfaces

| ID | Qty | W × D × H | Placement / visual specification | State |
|---|---:|---|---|---|
| ARC-WALL-LV-N | 1 | 5.50 × 0.12 × 2.75 | LV-N; aged warm plaster, LV-WIN-01 opening | Static |
| ARC-WALL-LV-E | 1 | 3.80 × 0.12 × 2.75 | LV-E / KI-W shared partition, living face warm plaster | Static |
| ARC-WALL-LV-S | 1 | 5.50 × 0.12 × 2.75 | LV-S / HA-N, doorway and fuse damage | Static; local damage restored |
| ARC-WALL-LV-W | 1 | 3.80 × 0.12 × 2.75 | LV-W; warm plaster, sofa wall | Static |
| ARC-WALL-KI-N | 1 | 6.50 × 0.12 × 2.75 | KI-N; window, backsplash and worn plaster | Static |
| ARC-WALL-KI-E | 1 | 3.80 × 0.12 × 2.75 | KI-E; pantry return and coat-closet side volume | Static |
| ARC-WALL-KI-S | 1 | 6.50 × 0.12 × 2.75 | KI-S / HA-N; door and coat-closet rear surface | Static |
| ARC-WALL-HA-S | 1 | 12.00 × 0.12 × 2.75 | HA-S / bedroom, bath and office north walls; three doors | Static |
| ARC-WALL-HA-E | 1 | 1.80 × 0.12 × 2.75 | HA-E exterior entry wall; entrance opening | Static |
| ARC-WALL-HA-W | 1 | 1.80 × 0.12 × 2.75 | HA-W gallery focal end | Static |
| ARC-CLOSET-HA-SHELL | 1 | 1.30 × 0.80 × 2.75 | Coat closet within kitchen footprint; HA-N front, KI-E return, KI-S back | Static |
| ARC-FLOOR-LV | 1 set | 5.50 × 3.80 × 0.03 | Living room; honey-brown aged plank floor | Static |
| ARC-FLOOR-KI | 1 set | 6.50 × 3.80 × 0.03 | Kitchen; warm cream/terracotta checker linoleum, locally worn | Static |
| ARC-FLOOR-HA | 1 set | 12.00 × 1.80 × 0.03 | Hall; continuous wood planks, aged finish | Static |
| ARC-CEILING-SOC | 3 surfaces | Room footprint × 0.03 | LV, KI, HA; cream plaster and subtle seams | Static |
| ARC-BASEBOARD | 1 reusable kit | sections 0.30–3.00 × 0.025 × 0.13 | All social walls; painted period wood, breaks at doors | Static |
| ARC-CROWN | 1 reusable kit | sections 0.30–3.00 × 0.035 × 0.10 | Social walls; warm painted wood crown | Static |
| ARC-DOOR-TRIM | 1 reusable kit × 6 openings | 1.04 × 0.035 × 2.18 | All room, entry and closet casings; coordinate actual openings | Static |
| ARC-WINDOW-TRIM | 1 reusable kit × 2 | LV 1.70 / KI 1.20 × 0.06 × 1.48 | LV-N / KI-N, painted wood and projecting sill | Static |
| LV-WIN-01 | 1 | 1.60 × 0.12 × 1.40 | LV-N, double-hung divided sash; sill 0.90 m, head 2.30 m | Potential sash slide; static initially |
| KI-WIN-01 | 1 | 1.10 × 0.12 × 1.40 | KI-N above sink, divided sash; sill 0.90 m | Potential sash slide; static initially |
| ARC-GLASS-SOC | 2 panesets | Fit windows × 0.01 | LV-WIN-01, KI-WIN-01; muted warm daylight/city view | Static, brightness follows time |
| LV-DR-01 | 1 | 0.90 × 0.045 × 2.10 | LV-S / HA-N; old paneled painted wood door | Rotate into living room |
| KI-DR-01 | 1 | 0.90 × 0.045 × 2.10 | KI-S / HA-N; matching paneled wood | Rotate into kitchen |
| BR-DR-01 | 1 | 0.90 × 0.045 × 2.10 | HA-S / bedroom; visible hall face; coordinated with private-room inventory | Rotate into bedroom |
| BA-DR-01 | 1 | 0.90 × 0.045 × 2.10 | HA-S / bathroom; coordinated with private-room inventory | Rotate into bathroom |
| OF-DR-01 | 1 | 0.90 × 0.045 × 2.10 | HA-S / office; coordinated with private-room inventory | Rotate into office |
| HA-ENTRY-01 | 1 | 0.90 × 0.05 × 2.10 | HA-E; solid old paneled door, brass lock and handle; outside landing unresolved | Rotate outward if exterior permits |
| HA-CLOSET-01 | 1 assembly | 0.90 opening × 0.08 × 2.16 | HA-N coat closet sliding fronts, track and casing; back visible KI-S | Slide left/right |
| ARC-DOOR-HARDWARE | 1 reusable set × 6 | 0.12 × 0.08 × 0.08 | Knobs, hinges, escutcheons; antique brass/aged metal | Rotate with each door |
| ARC-WALL-WEAR | 3 reusable decal/texture families | variable, typically 0.2–1.0 × 0.005 | Fine scuffs, cracks and repaired plaster around room corners; restrained localized age | Static; possible patch/restored variants |
| KI-BACKSPLASH-01 | 1 tiled run | 6.50 × 0.02 × 0.56 | KI-N behind cabinetry; muted warm checker/aged grout, trim at ends | Static |
| KI-TILE-01 | 1 material set | Tiles ~0.25 × 0.25 | Kitchen checker floor; separately reusable from backsplash | Static |
| ARC-PLUMB-CHASE | 1 service zone | Coordinate in section | Concealed crossing below HA between kitchen and bath; requires feasibility and fall check | Static |

## Living room: furniture, textiles and decor

| ID | Qty | W × D × H | Placement / material | State |
|---|---:|---|---|---|
| LV-SOFA-01 | 1 | 2.00 × 0.85 × 0.75 | LV-W; upholstered vintage green sofa with worn arms, wooden feet | Static |
| LV-CUSH-01 | 3 | 0.45 × 0.18 × 0.30 each | Sofa; muted green/rose patterned cushions | Static; separable loose pieces |
| LV-THROW-01 | 1 | 0.55 × 0.08 × 0.90 | Sofa arm; floral fabric or knitted throw, not thick paint | Static cloth |
| LV-CHAIR-01 | 1 | 0.75 × 0.70 × 0.85 | LV-N foreground; worn rust upholstered armchair | Static |
| LV-TABLE-01 | 1 | 1.20 × 0.60 × 0.45 | Living center; warm wood coffee table, readable worn edges | Static; optional drawer slide |
| LV-RUG-01 | 1 | 2.20 × 1.45 × 0.015 | Living center; faded floral woven rug | Static |
| LV-BOOK-01 | 1 | 1.25 × 0.40 × 1.85 | LV-N; old wood bookcase with shelf divisions | Static |
| LV-BOOKS-01 | 5 clusters | 0.32 × 0.16 × 0.28 each | LV-BOOK-01 shelves; mixed muted bindings | Static; reusable clusters |
| LV-BOOKS-02 | 1 stack | 0.38 × 0.22 × 0.12 | LV-S chest; 2–3 separate old books | Static; potential pickup |
| LV-TV-01 | 1 | 0.90 × 0.35 × 0.72 | LV-E; rounded retro TV, dark screen and controls | On/off emissive/screen |
| LV-TV-CONSOLE-01 | 1 | 1.10 × 0.50 × 0.55 | LV-E below TV; warm wood stand, paneled doors | Potential doors rotate |
| LV-CHEST-01 | 1 | 0.90 × 0.38 × 0.40 | LV-S; wood chest / storage box | Potential lid rotate |
| LV-BOX-01 | 1 stack | 0.62 × 0.30 × 0.63 | LV-E; boxes, books or record stack | Static; separate loose pieces |
| LV-LAMP-TABLE-01 | 1 | 0.37 × 0.35 × 0.54 | LV-W; small wood end table under lamp | Static |
| LV-LAMP-01 | 1 | 0.28 × 0.28 × 0.52 | LV-W; brass stem, warm fabric shade | On/off light |
| LV-PLANT-STAND-01 | 1 | 0.45 × 0.35 × 0.48 | LV-W; wood stand | Static |
| LV-PLANT-01 | 1 | 0.32 × 0.26 × 0.62 | LV-N; potted trailing/leafy plant | Static |
| LV-PLANT-02 | 1 | 0.32 × 0.26 × 0.62 | LV-E; ceramic pot and foliage | Static |
| LV-PLANT-03 | 1 | 0.32 × 0.26 × 0.62 | LV-W on stand; ceramic pot and foliage | Static |
| LV-RAD-01 | 1 | 0.65 × 0.15 × 0.60 | LV-N, under window; period cast iron, faded ivory | Static; verify chair separation |
| LV-CURTAIN-01 | 1 pair | 2 panels 0.17 × 0.04 × 1.48 | LV-N; gathered faded floral or rust cloth, separate rod/tiebacks | Potential slide; static cloth initially |
| LV-CURTAIN-ROD-01 | 1 | 1.74 × 0.07 × 0.05 | LV-N above window, aged wood or brass | Static |
| LV-ART-01 / 02 | 2 | 0.52 × 0.035 × 0.42; 0.42 × 0.035 × 0.55 | LV-E; old framed landscape/portrait | Static; separate artwork and frame |
| LV-ART-03 | 1 | 0.53 × 0.035 × 0.50 | LV-S; faded framed print | Static |
| LV-ART-04 | 1 | 0.72 × 0.035 × 0.52 | LV-W above sofa; framed landscape | Static |
| LV-FUSE-01 | 1 assembly | 0.45 × 0.12 × 0.65 | LV-S; old metal fusebox, door, handle, wiring and fuses | Door rotate; exposed damaged → repaired interior |
| LV-FUSE-DOOR-01 | 1 | 0.45 × 0.03 × 0.65 | Fusebox hinged front with handle | Rotate separately |
| LV-FUSE-INNER-01 | 1 | 0.37 × 0.08 × 0.57 | Fusebox interior; ceramic fuses, switches, insulated wiring | Damaged → repaired |
| LV-FUSE-DAMAGE-01 | 1 set | ~0.70 × 0.01 × 1.10 | LV-S localized fissures, discolored plaster and exposed wires around fuse | Visible damaged → hidden/repaired |
| LV-CEILING-01 | 1 | 0.35 × 0.35 × 0.28 | Living ceiling; period warm-glass flush or pendant light | On/off potential |

## Kitchen / dining: appliances, cabinetry and loose objects

| ID | Qty | W × D × H | Placement / material | State |
|---|---:|---|---|---|
| KI-FRIDGE-01 | 1 body | 0.75 × 0.70 × 1.72 | KI-N; rounded ivory aged enamel, cavity/shelves | Static body |
| KI-FRIDGE-DOOR-01 | 2 | 0.75 × 0.06 × 0.82 / 0.85 | Fridge upper and lower doors, vintage handles and seal | Rotate; independent hinges |
| KI-RANGE-01 | 1 | 0.75 × 0.70 × 0.88 | KI-N; vintage enamel range, burner plates, knobs and backguard | Oven door rotate; controls potential on/off |
| KI-RANGE-DOOR-01 | 1 | 0.67 × 0.06 × 0.45 | Range front, inset dark glass and handle | Rotate down |
| KI-RANGE-KNOB-01 | 4 | 0.05 × 0.035 × 0.05 | Range front, aged enamel/metal | Rotate potential |
| KI-RANGE-BURNER-01 | 4 | 0.17 × 0.17 × 0.02 | Cooktop, dark cast iron | Static |
| KI-CAB-01 | 1 set | 0.65 + 1.05 + 1.15 run × 0.65 × 0.86 | KI-N; three sage cabinet modules, worn edges, cream top | Base static; drawers slide / doors rotate |
| KI-CAB-DRAWER-01 | 2 | ~0.45 × 0.45 × 0.15 | Cabinet fronts and separate drawer boxes | Slide |
| KI-CAB-DOOR-01 | 4 | ~0.48 × 0.03 × 0.55 | Paneled sage fronts, ivory knobs | Rotate |
| KI-COUNTER-01 | 1 set | 2.92 × 0.65 × 0.06 | KI-N; warm ivory countertop with sink cutout | Static |
| KI-SINK-01 | 1 assembly | 1.05 × 0.65 × 0.22 basin; counter top at 0.86 | KI-N under window; old enamel sink, wall-mounted faucet, exposed plumbing | Leak damaged → repaired |
| KI-FAUCET-01 | 1 | 0.24 × 0.18 × 0.25 | Sink; worn metal spout and handles | Handle rotate; drip on/off |
| KI-DRAIN-01 | 1 | 0.20 × 0.15 × 0.45 | Under sink; curved aged metal drain pipe | Damaged drip → fixed |
| KI-LEAK-01 | 1 set | 0.90 × 0.70 × 0.02 puddle, drip 0.5 high | Beneath KI-SINK-01; water, stain and visible drip | Visible damaged → hidden/repaired |
| KI-BUCKET-01 | 1 | 0.25 × 0.25 × 0.30 | KI-N beneath leak; galvanized bucket and handle | Static; potential handle rotate |
| KI-UPPER-01 | 1 carcass | 1.00 × 0.32 × 0.55 | KI-N; sage upper cupboard beside window | Static body |
| KI-UPPER-DOOR-01 | 2 | 0.50 × 0.025 × 0.55 | KI-UPPER-01 paneled doors and knobs | Rotate |
| KI-PANTRY-01 | 1 body | 0.67 × 1.00 × 1.98 | KI-E north end; tall sage pantry, align plan footprint | Static body |
| KI-PANTRY-DOOR-01 | 2 | 0.50 × 0.025 × 1.90 | KI-PANTRY-01 KI-E face, knobs | Rotate; verify usable swing |
| KI-TABLE-01 | 1 | 1.50 × 0.85 × 0.75 | Kitchen center; aged wood or chrome-edged vintage dining table | Static |
| KI-CHAIR-01 | 2 | 0.40 × 0.60 × 0.85 | Table ends x=7.65 and 9.85, y=2.05 per corrected plan | Static; potential move |
| KI-BOWL-01 | 1 | 0.30 × 0.25 × 0.13 | Table; shallow ceramic fruit bowl | Static; potential pickup |
| KI-FRUIT-01 | 4–6 | ~0.08 × 0.08 × 0.08 each | KI-BOWL-01; separate lemons/fruit | Static; potential pickup |
| KI-KETTLE-01 | 1 | 0.24 × 0.20 × 0.20 | Range top; warm ivory or red enamel, handle and lid | Static; potential lid rotate |
| KI-PAN-01 | 2 | ~0.26 × 0.06 × 0.35 | KI-N hanging pans, dark metal with separate handles | Static; potential sway |
| KI-PAN-RAIL-01 | 1 | 0.60 × 0.04 × 0.05 | KI-N above range/counter, hooks | Static |
| KI-PLANT-01 | 1 | 0.22 × 0.18 × 0.50 | KI-N window ledge, small geranium in clay pot | Static |
| KI-SHELF-01 | 1 | 0.90 × 0.18 × 0.05 | KI-E, wood shelf and brackets | Static |
| KI-JAR-01 | 3 | ~0.16 × 0.16 × 0.24 each | KI-SHELF-01; patterned ceramic/aged glass canisters | Static; lid optional |
| KI-SHELF-02 | 1 | 1.00 × 0.18 × 0.05 | KI-S, wall shelf and brackets | Static |
| KI-MUG-01 | 2 | ~0.12 × 0.10 × 0.12 each | KI-SHELF-02, cream/rose pottery | Static; potential pickup |
| KI-POTTERY-01 | 1 | 0.16 × 0.16 × 0.24 | KI-SHELF-02, small handmade vessel | Static |
| KI-SCONCE-01 | 1 | 0.14 × 0.14 × 0.24 | KI-E; brass wall fitting, warm glass | On/off potential |
| KI-ART-01 / 02 / 03 | 3 | 0.60 × 0.035 × 0.45; 0.48 × 0.035 × 0.55; 0.55 × 0.035 × 0.44 | KI-E, KI-S, KI-W; framed print variations | Static |
| KI-CURTAIN-01 | 1 pair | 2 panels 0.17 × 0.04 × 1.48 | KI-N, faded warm check or floral fabric | Potential slide; static cloth initially |
| KI-CURTAIN-ROD-01 | 1 | 1.24 × 0.07 × 0.05 | KI-N over window, aged brass or wood | Static |
| KI-CEILING-01 | 1 | 0.35 × 0.35 × 0.25 | Kitchen ceiling, period enamel/glass fixture | On/off potential |

## Hall: furnishings, art and lighting

| ID | Qty | W × D × H | Placement / material | State |
|---|---:|---|---|---|
| HA-CONSOLE-01 | 1 | 1.05 × **≤0.25** × 0.72 | HA-N, global x2.00–3.05, y3.86–4.11; shallow wood console | Potential drawer slide |
| HA-CONSOLE-DRAWER-01 | 1 | 0.95 × 0.18 × 0.24 | HA-CONSOLE-01, separate box and handle | Slide |
| HA-PLANT-STAND-01 | 1 | 0.45 × **≤0.25** × 0.48 | HA-S, x2.05–2.50, y5.29–5.54; shallow pedestal | Static |
| HA-PLANT-01 | 1 | 0.30 × 0.22 × 0.60 | HA-S stand; foliage and clay pot | Static |
| HA-BENCH-01 | 1 | 0.62 × **≤0.25** × 0.45 | HA-S x11.08–11.70, y5.29–5.54; worn wood | Static |
| HA-CABINET-01 | 1 | 1.02 along wall × **≤0.25** × 0.72 | HA-W x0.06–0.31, y4.18–5.20; gallery-end cabinet | Potential drawer slide |
| HA-CABINET-DRAWER-01 | 1 | 0.88 × 0.18 × 0.20 | Gallery-end cabinet, separate drawer and knob | Slide |
| HA-SHOES-01 | 1 set | 0.38 × 0.25 × 0.42 | HA-E next to entry; shoe tray and 2 pairs of shoes | Static; split tray/shoe pieces |
| HA-SHOE-01 | 4 | ~0.11 × 0.24 × 0.11 each | Individual shoes on HA-SHOES-01 tray | Static; potential pickup |
| HA-VASE-01 | 1 | 0.24 × 0.18 × 0.26 | HA-N console, glazed ceramic | Static |
| HA-VASE-02 | 1 | 0.22 × 0.18 × 0.27 | HA-W cabinet, glazed ceramic | Static |
| HA-FLOWERS-01 | 1 bunch | 0.28 × 0.18 × 0.28 | HA-VASE-02; dried or fresh stems | Static |
| HA-HOOKS-01 | 1 rail, 4 hooks | 0.72 × 0.07 × 0.12 | HA-N by coat closet; wood rail and aged brass hooks | Static |
| HA-COAT-01 | 1 | 0.42 × 0.12 × 0.90 | On hooks or inside closet, warm woven cloth | Static; potential pickup |
| HA-SHELF-01 | 1 | 0.65 × 0.15 × 0.05 | HA-S; small wood shelf | Static |
| HA-SHELF-VESSEL-01 | 2 | ~0.18 × 0.14 × 0.25 each | HA-S shelf, aged ceramic | Static |
| HA-SCONCE-01 / 02 | 2 | 0.14 × 0.14 × 0.24 each | HA-N flanking gallery entries; aged brass and warm glass | On/off potential |
| HA-CEILING-01 | 2 | 0.32 × 0.32 × 0.22 each | Hall ceiling; matching warm-glass lights | On/off potential |
| HA-RUNNER-01 | 1 | ~6.00 × 0.80 × 0.015 | Hall floor; worn floral runner, keep away from entry leaf | Static |
| HA-ART-01 / 02 | 2 | 0.55 × 0.035 × 0.48; 0.38 × 0.035 × 0.42 | HA-N; framed old prints | Static |
| HA-ART-03 / 04 | 2 | 0.65 × 0.035 × 0.52; 0.45 × 0.035 × 0.43 | HA-N; framed landscapes/portrait | Static |
| HA-ART-05 / 06 | 2 | 0.48 × 0.035 × 0.52; 0.40 × 0.035 × 0.42 | HA-S; framed prints | Static |
| HA-ART-07 / 08 | 2 | 0.55 × 0.035 × 0.52; 0.50 × 0.035 × 0.52 | HA-S; framed prints | Static |
| HA-ART-09 | 1 | 0.90 × 0.035 × 0.65 | HA-W; focal framed landscape at hall end | Static |

## Reconciliation and acceptance notes

- Kitchen sideboards from an earlier elevation draft were removed: the east unit intersected the coat-closet footprint and the south unit narrowed the table passage. Kitchen chairs now occupy table ends, per the revised plan.
- Hall console, pedestal, bench and end cabinet are proposed additions and are **not yet in the shared plan**. At 0.25 m maximum depth each, the opposite console/pedestal pair leaves 1.18 m between surfaces before trim; a single bench leaves 1.43 m. These estimates assume 1.68 m between wall faces and do not prove capsule sweep, camera or interactive door clearances.
- Radiator, loose decor, all specified ceiling fixtures, range detail, upper cupboard, shelves and wall art also need placement in the selected plan and/or 3D layout. Asset dimensions are not construction dimensions.
- The painterly target is a stylized rendering and finish. Damage should be localized and legible; the majority of furnishings retain the attractive, usable structure in the approved concept.
- Validate pivot origins, exact materials, collision, open-door paths, repaired-state attachments, UVs and finite geometry with clean Blender export and fresh Unreal load. No concept-sheet coverage is implied by this inventory.
