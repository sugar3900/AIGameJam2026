---
tags: [environment, asset-pipeline]
status: draft
---
# Apartment inventory coverage

Working reconciliation of the [social inventory](elevations/social-room-asset-notes.md), [private inventory](elevations/private-room-asset-notes.md), [asset production log](Asset%20production.md), and asset-folder READMEs. Snapshot: **2026-11-08**. The art is in `/Users/davidwallin/Developer/AIGameJam2026-environment/Art Source/Apartment Redesign/Assets/`; consult each asset's README before use. These are **Blender/source-production states**, not in-game acceptance; the other agent's Unreal work may advance independently.

At this snapshot, 67 asset folders contain both a `.blend` and at least one `.fbx` plus a README. This is a **folder count**, not 67 completed unique inventory entries: the narrow/full sink are alternatives, window variants share a design, assemblies contain multiple inventory entries, and some work is undergoing correction. Counts will move during parallel production. Folder presence alone does not establish a reviewed export, all required states, correct placement or Unreal readiness.

At snapshot time no asset folder was found with only concepts and no FBX. `OF-CABINET-01` nevertheless has an FBX while a drawer-fit correction is underway; this is **in progress**, not an approved finished item. The missing/partial groups below may still have artwork embedded in other concept sheets, but that is not evidence that a separate model exists or that a per-item concept has been selected.

The tables consolidate repeated placements and parts into practical coverage groups. **Export** means a corresponding model/FBX exists; **Partial** means some named parts, appearances, placements or reuse need a decision or additional work; **Missing** means no matching dedicated source/export was found in this art worktree, not necessarily that the project has no older placeholder. This is a navigation and planning aid, not a weighted completion percentage: a floor kit and a jar do not take the same effort, and group boundaries may change.

## Changes since this snapshot

`KI-BOWL-01` now has a reviewed bowl and five separate fruit exports; `BR-ART-FLORAL-01` supplies one bedroom-specific botanical print. `HA-BENCH-01`, `ARC-WALL-SHELF-01`, `HA-HOOKS-01`, `BA-TOWEL-RAIL-01`, `KI-PAN-01` and `KI-PAN-RAIL-01` also have reviewed provisional exports. `HA-SHOES-01`, `HA-COAT-01`, `KI-MUG-01`, `KI-JAR-01`, `KI-POTTERY-01`, `BA-ROLL-01`, `BA-MAT-01`, `BA-BIN-01`, `BA-SOAP-01`, `BA-CUP-01`, `BA-SWITCH-01`, `BA-HOOK-01`, `BA-HAND-TOWEL-01`, `BA-JAR-01`, `BR-CLOSET-BOX-01`, `LV-PLANT-STAND-01` and `HA-FLOWERS-01` also have provisional exports. The other named kitchen and bedroom artwork variants remain to be covered. See [asset production](Asset%20production.md) for live statuses. The tables below retain the snapshot classifications until the next full reconciliation.

## Architecture and reusable kits

| Inventory group and IDs | Coverage | Evidence / outstanding work |
|---|---|---|
| Living wall faces `ARC-WALL-LV-*`, kitchen wall faces `ARC-WALL-KI-*` | Partial | `ARC-LIVING-WALL-01`, `ARC-KITCHEN-PLASTER-01` export modules/materials, not the entire built A+ shell. Adapt to actual door/window cuts and shared wall faces. |
| Hall faces `ARC-WALL-HA-*`, private `P-ARC-PLASTER` and return walls `P-ARC-RETURN` | Partial | `ARC-LIVING-WALL-01` and `ARC-BEDROOM-PLASTER-01` supply candidate surfaces; hall/office/bath wall geometry and finishes still need shell-specific placement. `BR-CLOSET-01` already contains its own interior. |
| Hall coat-closet shell `ARC-CLOSET-HA-SHELL` and office fitted shell `P-ARC-CLOSET` | Partial | `ARC-SLIDING-CLOSET-01` supplies bypass doors/track, not both closets' complete walls and storage; the 0.90 m opening reveals only ~0.44 m. |
| Bedroom closet `P-BR-CLOSET-DOORS`, `P-BR-MOLD`, `P-BR-CLOSET-BULB/SHELF/RAIL/HANGER` | Export | `BR-CLOSET-01` has shell, paired doors, mold, bulb, high shelving and hangers. Exact inventory rail and shelving arrangement/quantities should be checked in scene. Both standing character and reveal interaction remain untested. |
| Bedroom closet loose boxes and low shelf `P-BR-CLOSET-BOX`, `P-BR-CLOSET-LOW-SHELF` | Missing | `BR-CLOSET-01` README describes high shelves and hangers; it does not establish these lower props. |
| Floor surfaces `ARC-FLOOR-LV/KI/HA`, bedroom/office and bathroom | Export | `ARC-FLOOR-WOOD-01`, `KI-TILE-01`, `BA-FLOOR-01` modules and separate optional wear. Exact per-room cuts, collisions, transitions and repeat scale need work. |
| Ceiling surface `ARC-CEILING-SOC` | Export | `ARC-CEILING-PLASTER-01`; room-specific layout and any sparse wear remain unverified. |
| Baseboard/crown/door casing `ARC-BASEBOARD`, `ARC-CROWN`, `ARC-DOOR-TRIM` | Partial | `ARC-TRIM-01` straight and inside-corner kits; outside/casing corners and actual opening fits need assembly. Door kits also contain trim; avoid duplicate pieces. |
| Windows/casing/panes `LV-WIN-01`, `KI-WIN-01`, `ARC-WINDOW-TRIM`, `ARC-GLASS-SOC`, `P-ARC-SASH-BR/BA/OF` | Export | `ARC-WINDOW-01`, `ARC-WINDOW-NARROW-01`, `ARC-WINDOW-BATH-01`, `ARC-WINDOW-OFFICE-01` cover four opening sizes; glazing materials/privacy and sash movement are not implemented by FBX. `ARC-LIVING-WALL-01` also contains an alternative fixed window. |
| Interior doors `LV-DR-01`, `KI-DR-01`, `BR-DR-01`, `BA-DR-01`, `OF-DR-01`, `P-ARC-DOOR`, hardware | Export | `ARC-DOOR-01` is a reusable panel door, frame and hardware; five placements, swing direction, pivots and collision require Unreal checks. |
| Entry door `HA-ENTRY-01` | Export | `ARC-ENTRY-DOOR-01`; outside landing and outward swing are unresolved. |
| Hall/office sliding fronts `HA-CLOSET-01`, `P-ARC-CLOSET` | Partial | `ARC-SLIDING-CLOSET-01` front kit only, with narrow accessible opening; dimensions differ from some earlier elevation dimensions. Not the bedroom's walk-in closet doors. |
| Local wall wear `ARC-WALL-WEAR` | Partial | `ARC-KITCHEN-PLASTER-01` includes optional hairline geometry; all three requested reusable families and placement coverage have not been established. |
| Kitchen backsplash `KI-BACKSPLASH-01` | Export | Same-named kit, caps and repeat. Judge checker against kitchen floor at room scale. |
| Cross-hall service chase `ARC-PLUMB-CHASE` | Missing | Service-routing feasibility remains a design assumption, not an authored asset. |
| Curtain panels/rod `LV-CURTAIN-01`, `LV-CURTAIN-ROD-01`, `KI-CURTAIN-01`, `KI-CURTAIN-ROD-01`, `P-TEX-CURTAIN-BR/OF` | Partial | `ARC-CURTAINS-01` is a 1.60 m-window kit with 2.18 m rod, morph-based panels. Other window sizes/fabric variants need adaptation; Unreal skeletal/morph import and clearance remain untested. |
| Bedroom wainscot/lead `P-BR-WAINSCOT`, `P-BR-LEAD` | Partial | `BR-WAINSCOT-01` exports panels and separate lead-damage overlay. Break the 1.10 m-high rail around the 0.90 m-sill window; separate lead-hunk gameplay/story is not implemented. |

## Living room

| Inventory group and IDs | Coverage | Evidence / outstanding work |
|---|---|---|
| Sofa, cushions and throw `LV-SOFA-01`, `LV-CUSH-01`, `LV-THROW-01` | Export | `LV-SOFA-01` includes sofa, loose-looking cushions and throw; actual counts/placement should be compared with elevation. |
| Armchair `LV-CHAIR-01` | Export | Same-named asset. |
| Coffee table, rug `LV-TABLE-01`, `LV-RUG-01` | Export | `LV-COFFEE-01` is the inventory's coffee table; `LV-RUG-01` is the rug. |
| Bookcase, shelf books `LV-BOOK-01`, `LV-BOOKS-01` | Export | `LV-BOOK-01` includes separate book cluster export and plant/tin dressing. Bookcase model height is 2.056 m, above the inventory's 1.85 m. |
| Loose book stack / boxes `LV-BOOKS-02`, `LV-BOX-01` | Partial | `LV-BOOK-01` books may be reusable; no independent box or explicitly approved chest-top stack was located. |
| Television and console `LV-TV-01`, `LV-TV-CONSOLE-01` | Export | `LV-TV-01` is a combined 1.10 m-wide body plus separately hinged console doors; screen and light behavior need Unreal setup. |
| Storage chest `LV-CHEST-01` | Export | Same-named body and separately hinged lid. |
| Lamp and end table `LV-LAMP-01`, `LV-LAMP-TABLE-01` | Export | Inventory's table lamp maps to `LV-TABLE-LAMP-01` and its stand to `LV-SIDE-TABLE-01`. The folder `LV-LAMP-01` is a 1.56 m **floor lamp**, not this inventory row. |
| Plant stand `LV-PLANT-STAND-01` | Missing | No dedicated matching stand located. |
| Three potted plants `LV-PLANT-01/02/03` | Partial | `LV-PLANT-01` trailing pothos plus `LV-BOOK-01` plant export are reusable candidates; distinct pot/foliage arrangements and final counts are not established. |
| Radiator `LV-RAD-01` | Export | `LV-RADIATOR-01`; 0.254 m overall depth with pipes vs 0.15 m inventory. Check chair/window clearance. |
| Living prints `LV-ART-01/02/03/04` | Partial | `LV-ART-04` garden landscape exists; frame kit may be reusable, but the other named prints/portraits are not established as distinct artworks. |
| Fuse and damage `LV-FUSE-01`, `LV-FUSE-DOOR/INNER/DAMAGE-01` | Export | `LV-FUSE-01` contains door, interior and damaged/repaired wire states; authored wall damage and gameplay linkage still need verification. |
| Living ceiling light `LV-CEILING-01` | Export | `ARC-CEILING-LIGHT-01` is a plausible matching flush fixture; size and light fit require in-room confirmation. |

## Kitchen and dining

| Inventory group and IDs | Coverage | Evidence / outstanding work |
|---|---|---|
| Fridge + doors `KI-FRIDGE-01`, `KI-FRIDGE-DOOR-01` | Export | `KI-FRIDGE-01`; confirm hinges, interior and clearances in engine. |
| Range, door, knobs and burners `KI-RANGE-01`, `KI-RANGE-DOOR/KNOB/BURNER-01` | Partial | `KI-RANGE-01` has door, knobs and burners; knobs are fixed geometry, so optional knob motion is not supplied. |
| Base cabinet/doors/drawers/counter `KI-CAB-01`, `KI-CAB-DRAWER/DOOR-01`, `KI-COUNTER-01` | Partial | `KI-CABINET-01` supplies a module and moving parts. Exact run/counter cut, sink junction and variants need fitting to plan. |
| Sink/faucet/drain/leak/bucket `KI-SINK-01`, `KI-FAUCET-01`, `KI-DRAIN-01`, `KI-LEAK-01`, `KI-BUCKET-01` | Partial | Choose **one** of `KI-SINK-01` (2.37 m with side cabinets) and `KI-SINK-NARROW-01` (1.05 m central sink) to avoid duplicate counters; `KI-BUCKET-01` also exists as a separate candidate. Window sill/upstand conflict and water/repair lifecycle remain unresolved. |
| Upper cabinet and pantry `KI-UPPER-01`, `KI-UPPER-DOOR-01`, `KI-PANTRY-01`, `KI-PANTRY-DOOR-01` | Export | `KI-UPPER-01` and `KI-PANTRY-01` include movable leaves; pantry's north door sweep must be checked against wall. |
| Dining table/chairs `KI-TABLE-01`, `KI-CHAIR-01` | Export | Same-named assets; table and chair/capsule clearance still need in-room verification. |
| Kettle `KI-KETTLE-01` | Export | Same-named asset; spout interior is a visual approximation. |
| Fruit bowl and fruit `KI-BOWL-01`, `KI-FRUIT-01` | Missing | No dedicated bowl or fruit export found. |
| Hanging pans and rail `KI-PAN-01`, `KI-PAN-RAIL-01` | Missing | No dedicated matching exports found. |
| Kitchen plant `KI-PLANT-01` | Partial | `LV-PLANT-01` and `LV-BOOK-01` have foliage candidates, but neither is established as the specified small geranium. |
| Shelves/canisters/mugs/pottery `KI-SHELF-01/02`, `KI-JAR-01`, `KI-MUG-01`, `KI-POTTERY-01` | Missing | No dedicated shelf, jar, mug or pottery assets found; group repeated objects for future reuse without assuming complete coverage. |
| Kitchen sconce/ceiling `KI-SCONCE-01`, `KI-CEILING-01` | Partial | `HA-SCONCE-01` and `ARC-CEILING-LIGHT-01` are plausible reuse candidates, not confirmed as the specific kitchen fixtures. |
| Kitchen framed prints `KI-ART-01/02/03` | Partial | `HA-ART-09` and `LV-ART-04` offer reusable frame/art examples; kitchen artwork and variants have not been authored as named. |

## Hall

| Inventory group and IDs | Coverage | Evidence / outstanding work |
|---|---|---|
| Console and drawer `HA-CONSOLE-01`, `HA-CONSOLE-DRAWER-01` | Export | Same-named assembly; drawer extension and corridor clearance pending. |
| End cabinet and drawer `HA-CABINET-01`, `HA-CABINET-DRAWER-01` | Export | Same-named assembly; closed depth 0.2475 m and moving parts need capsule/door checks. |
| Hall runner `HA-RUNNER-01` | Export | Same-named full-length texture and mesh; verify entry swing and texture resolution in engine. |
| Paired wall lights and ceiling lights `HA-SCONCE-01/02`, `HA-CEILING-01` | Export | `HA-SCONCE-01` and `ARC-CEILING-LIGHT-01` can be instanced; light and material setup pending. |
| Gallery focal print `HA-ART-09` | Export | Same-named landscape and frame. |
| Hall plants and stand `HA-PLANT-STAND-01`, `HA-PLANT-01` | Partial | `LV-PLANT-01` is a reusable plant candidate but the shallow stand and placement are not established. |
| Hall bench `HA-BENCH-01` | Missing | No dedicated bench export found; depth must remain ≤0.25 m. |
| Shoe tray and shoes `HA-SHOES-01`, `HA-SHOE-01` | Missing | No dedicated footwear/tray export found. |
| Vases and flowers `HA-VASE-01/02`, `HA-FLOWERS-01`, `HA-SHELF-VESSEL-01` | Missing | No dedicated matching vase/flower exports found. |
| Coat hooks, coat and shelf `HA-HOOKS-01`, `HA-COAT-01`, `HA-SHELF-01` | Missing | No dedicated matching exports found. |
| Gallery prints `HA-ART-01` through `HA-ART-08` | Partial | `HA-ART-09` and `LV-ART-04` establish frame/art candidates, but the eight other specified print variants are not authored individually. |

## Bedroom, bathroom and office

| Inventory group and IDs | Coverage | Evidence / outstanding work |
|---|---|---|
| Bed, quilt and pillows `P-BR-BED`, `P-BR-QUILT`, `P-BR-PILLOW` | Export | `BR-BED-01` includes frame, mattress, quilt and pillows. |
| Nightstands and lamps `P-BR-NIGHTSTAND`, `P-BR-LAMP` | Export | `BR-NIGHTSTAND-01` and `BR-LAMP-01`; both need instancing/placement and drawer/light setup. |
| Dresser and mirror `P-BR-DRESSER`, `P-BR-MIRROR` | Export | `BR-DRESSER-01` assembly; inspect actual drawer/mirror export and east-side clearance in room. |
| Bedroom keepsakes `P-BR-TRAY/PERFUME/KEEPSAKE/BOOK/VASE` | Partial | Book assets exist in `LV-BOOK-01` as candidates; no dedicated tray, perfume, keepsake or vase coverage established. |
| Bedroom prints and shelves `P-ART-BR-*`, `P-SHELF-BR-*` | Partial | Existing framed landscapes provide candidates, but bedroom-specific artwork and display shelves are not established. |
| Bathroom tile/crack `P-BA-TILE`, `P-BA-CRACK` | Export | `BA-TILE-01` has modular field, surround and removable damage overlay. Material mapping and repair state remain untested in Unreal. |
| Tub, shower and curtain `P-BA-TUB`, `P-BA-SHOWER`, `P-BA-SHOWER-CURTAIN` | Export | `BA-TUB-01` includes tub, fixtures and a rigid sliding curtain; no cloth simulation. |
| Basin, mirror and sconces `P-BA-SINK`, `P-BA-MIRROR`, `P-BA-SCONCE` | Export | `BA-BASIN-01`, `BA-MIRROR-01` including sconces; UE reflection and lighting pending. |
| Toilet and linen cabinet `P-BA-TOILET`, `P-BA-LINEN` | Export | `BA-TOILET-01`, `BA-LINEN-01`; hinges/material/clearance pending. |
| Basket and rolled towels `P-BA-BASKET`, `P-BA-TOWEL-ROLL` | Export | `BA-BASKET-01` contains three rolled towels versus two specified; optional basket LOD is available. |
| Toilet roll/holder `P-BA-ROLL` | Missing | No dedicated matching export found. |
| Hooks, towel rails and hanging towels `P-BA-HOOK`, `P-BA-HOOK-TOWEL`, `P-BA-RAIL-E/W`, `P-BA-TOWEL-E/W` | Missing | No dedicated matching rail/hook/hanging-towel exports found. Rolled basket towels do not establish hanging towel coverage. |
| Bath mat, pedal bin and switch `P-BA-MAT`, `P-BA-BIN`, `P-BA-SWITCH` | Missing | No dedicated matching exports found. |
| Bathroom shelves and toiletries `P-SHELF-BA-*`, `P-BA-JAR-N`, `P-BA-SOAP-N/W`, `P-BA-FOLD-E`, `P-BA-TIN-E`, `P-BA-BOTTLE-W`, `P-BA-CUP-W` | Missing | No dedicated matching individual exports found. |
| Bathroom framed print `P-ART-BA-PRINT` | Partial | Other framed artwork exists, but this print is not established. |
| Office desk, chair, lamp `P-OF-DESK`, `P-OF-CHAIR`, `P-OF-DESK-LAMP` | Export | `OF-DESK-01`, `OF-CHAIR-01`, `OF-DESK-LAMP-01`; chair fit/desk movement pending. |
| Daybed, pillows, throw `P-OF-DAYBED`, `P-OF-PILLOW`, `P-OF-THROW` | Export | `OF-DAYBED-01` includes mattress, floral quilt and two cushions; confirm intended folded throw placement. |
| Office low bookcase and cabinet `P-OF-BOOKCASE`, `P-OF-CABINET` | Export | `OF-BOOKCASE-01`, `OF-CABINET-01`; cabinet drawer fit is being corrected at this snapshot. |
| Office floor lamp `P-OF-FLOOR-LAMP` | Export | `LV-LAMP-01` is a 1.56 m floor lamp and plausible office fit; confirm actual shade extent in planned footprint. |
| Office papers and books `P-OF-PAPERS`, `P-OF-DESK-BOOK`, `P-OF-BOOKS`, `P-OF-N-BOOK`, `P-OF-W-BOOK` | Partial | `LV-BOOK-01` has detachable books/cluster; desk papers and office arrangements/quantities remain unestablished. |
| Office box, plants and pots `P-OF-STORAGE`, `P-OF-PLANT`, `P-OF-N-POT`, `P-OF-W-PLANT` | Partial | Existing bookcase and pothos plant/tin assets are candidates; desired office-specific containers, plant scale and storage box are not established. |
| Office shelves and prints `P-SHELF-OF-N/W`, `P-ART-OF-N/E/W` | Partial | Frame/art candidates exist, but office-specific shelves and named artworks are not established. |
| Closet character `P-BR-CLOSET-HUNK` | Partial | Existing Malcolm is a game character, not a new static art asset. Closet stand location, camera, door gating and repair/save lifecycle are not verified. |

## Cross-cutting constraints

- Check [Room build guide](Room%20build%20guide.md) for source-of-truth coordinates and documented fit conflicts: sink/counter overlap, kitchen sill vs worktop, bedroom window casing vs east wall and sill vs wainscot, duplicated wall/closet shells and wall-centreline datum.
- Blender round-trip validation does not prove Unreal pivot/orientation, materials, opacity, collision, performance, movement or save/repair behavior. Keep individual asset README caveats attached to handoff.
- Concepts and before/after views exist for many modeled assemblies, but a complete concept audit for every distinct missing object, frame-art variant and repair/interactive state has not been performed. Do not treat the folder count as concept coverage.
- The selected plan and elevations remain design intent; verify all clearances against actual player/character/camera in the engine build and update both representations after any adjustment.
