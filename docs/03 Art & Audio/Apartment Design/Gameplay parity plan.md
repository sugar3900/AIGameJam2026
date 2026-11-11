# Redesign gameplay parity plan

Goal: make `L_Apartment_Redesign_Blockout` play the full game exactly as `L_Apartment` does today (four hunk encounters, interactables, bed/day cycle, front door, floor-plan travel, saves), using the redesign art, so it can later replace `L_Apartment` as `GameDefaultMap`. Switching the default map is a separate decision for the user.

Status key: ☐ todo · ◐ in progress · ☑ done. Owner: Unreal integration thread (`4ce772b5…`), user-approved 2026-11-08.

## 0. Branch and editor setup
- ☐ Pause the art thread's writes, then commit the redesign work on `environment/apartment-redesign` (art source and docs, then Unreal content and tools). Rebase onto `origin/main`. No path overlaps were found: main touched no redesign files and has not changed `L_Apartment.umap` since `a7ca996`.
- ☐ Close the environment editor, rebuild `ICanFixHimEditor` (main adds `AFixHimDoor`, audio/voice/debug subsystems and `Build.cs` changes), relaunch it on MCP port 8002 and re-validate that the map loads with no missing meshes.
- Editor practice that avoids known crashes: run editor scripts through `Tools/run_editor_script.py`, which uses an isolated namespace plus `gc.collect()`. If a relaunch hangs at frame 0 after a crash, move `Saved/Autosaves/PackageRestoreData.json` aside.
- Review captures: use `Tools/capture_redesign_viewport.py` (real viewport, Lumen). `SceneCapture2D` does **not** render Lumen in this project.

## 1. Map structure: avoid binary conflicts
Put gameplay actors in a separate streamed sublevel, `L_Apartment_Redesign_Gameplay.umap`, always loaded under the persistent redesign map. Environment dressing stays in the persistent map. Two agents can then work without merging a single binary `.umap`. Repair-damage meshes that must attach to a malady move into the gameplay sublevel with it, because attachment cannot cross levels.

## 2. Small C++ changes (shared gameplay code; keep minimal and reviewed)
| Change | Why | Where on main |
|---|---|---|
| `PlacePlayerAtDoor` uses the placed `AFixHimDoor` (or a `PlayerStart` tagged `DoorStart`) instead of the hard-coded `(190,120,·)`/yaw 75 | The redesign entry is on the east hall wall (x=12 m), not the old living-room south wall | `FixHimPlayerController.cpp` ~l.618 |
| `AFixHimDoor::EnsureInWorld` fallback stays as is; the redesign places its own door, so the fallback never fires | — | `FixHimDoor.cpp` l.41 |
| Title-camera fallback transform only if no `TitleCamera`-tagged camera exists; the redesign provides one | — | controller ~l.104 |
| Optional: a `UFixHimSettings` scale for `WindowBrightness` (12→0.35 range), or set the redesign `MI_WindowView` so 12 reads correctly | Cards were tuned at 0.9; the game drives 12 at dawn | controller `UpdateDaylight` |
| Optional: floor-plan orientation. The widget maps world Y→screen X; check that the redesign reads naturally, since the plan's +x is east | Cosmetic | `FixHimFloorPlanWidget.cpp` l.77 |
Every change must keep `L_Apartment` behaving identically.

## 3. Rooms (`AFixHimRoom`)
Room IDs and save compatibility: keep `living`, `kitchen`, `bedroom`, `bathroom`; add `hall` and `office`. Bounds come from the plan rectangles in `A-plus-candidate.json`, in centimetres, with the closets inside their parent room. Each room needs an `entry_point` just inside its door, facing in, plus a `display_name` and `map_color`. The bedroom entry point is also the wake-up spot after sleeping.

| room_id | rect (cm) | entry point |
|---|---|---|
| living | 0,0 → 550,380 | (450, 320) facing north |
| kitchen | 550,0 → 1200,380 | (665, 320) facing north |
| hall | 0,380 → 1200,560 | (1120, 442) facing west |
| bedroom | 0,560 → 480,955 | (360, 620) facing south |
| bathroom | 480,560 → 790,955 | (680, 620) facing south |
| office | 790,560 → 1200,955 | (1010, 620) facing south |

## 4. Maladies (`AFixHimMalady`): hunk ids unchanged
| hunk | style | art (already placed) | malady actor | attached `RepairDamage` |
|---|---|---|---|---|
| wyatt | WIRING | `LV-FUSE-01` on the living south wall, x≈312, z 120–180 | at the fusebox face, yaw facing into the room | `Art_LV_Fuse_Wire_Damaged`; the repaired wire becomes visible on repair (needs either a small code hook or a `RepairFixed` tag convention). Missing art: plaster damage |
| lukey | LEAK | `KI-SINK-01` centred x=855 on the north wall | at the sink front | `Art_KI_SINK_damage` |
| tyler | TILE | `BA-TILE-01` damage above the tub, south wall | at the crack | `Damage_BA_CrackedTile` |
| malcolm | MOLD | `BR-CLOSET-01` mold, closet back wall | inside the closet facing the mold | `Art_BR_Closet_Mold` tagged `AuthoredMoldDamage` (suppresses the generated mold FX) |

For each one: set `hunk_spawn` and `talk_spot` so the hunk and player stand in clear floor space with a good dialogue frame in first person (eye height about 1.6 m). Malcolm must fit in the 1.64 × 1.29 m closet with the leaves open. Check that FX offsets land on the art.

## 5. Interactables (`AFixHimInteractable`): mirror the current set and reuse the art meshes as bodies
Each body is a single static mesh, so the moving part (door leaf, drawer, lid) becomes the body and the stationary art stays as dressing. Set `bUseAuthoredBodyMaterials=true`. Pivots come from each README; toggle offsets and rotations need checking in play.

| current | toggle | redesign body mesh | notes |
|---|---|---|---|
| FloorLamp | LIGHT | `LV_TableLampShade` (LV-TABLE-LAMP-01) | light at the bulb |
| TV | LIGHT | `LV_TV_screen_on`/`off`, or the screen as body | screen emissive |
| Fridge_Door | ROTATE | `KI_FRIDGE_DOOR` | hinge pivot check |
| Stove_Burner | LIGHT | **missing art**: burner/flame part | interim: small ring proxy |
| Kitchen_Drawer | SLIDE | `KI_Cabinet_drawer` or a sink drawer | slide 30 cm toward −Y (into the room) |
| Tub_Faucet | REVEAL | `BA_TapLeft` | **missing art**: bath-water reveal mesh; interim: flattened proxy with the reveal colour |
| Toilet_Lid | ROTATE | `BA_ToiletLid` | |
| Bed (`AFixHimBed`) | — | `BR-BED-01` | wake-up at the bedroom entry |
| BedLamp | LIGHT | `BR_LampShade` (one nightstand) | |
| Wardrobe_Door | ROTATE | `BR_Closet_Door_L`/`R` (two interactables) | they gate Malcolm; opening must reveal the mold |
| Dresser_Drawer | SLIDE | `BR_Dresser_drawer1` | |
| FrontDoor (`AFixHimDoor`) | — | `ARC_Entry_Door_Leaf` at the east entry, hidden-body pattern as in `build_apartment.py` | "Leave the apartment" |

Optional extras once parity is reached: office, hall and pantry interactables (sliding closet panels, pantry doors, desk lamp, sconces).

## 6. Scene hooks
- ☐ A `PlayerStart` just inside the entry (≈1120,442, facing west) for the first session.
- ☐ A `CameraActor` tagged `TitleCamera` with an attractive establishing view (for example the living room from the hall door).
- ☐ Window-view cards tagged `WindowView`, with a static `StaticMeshActor` and material parameter `WindowBrightness`; then retune as in section 2.
- ☐ The sun stays the only `DirectionalLight`; the controller animates it from its base rotation. Check the dawn-to-dusk range in play.
- ☐ Integrate `ENV-SKY-01` (sky sphere and specified-cubemap sky light) to match the day cycle.

## 7. Art requests (send to the art thread)
Fusebox plaster damage (Wyatt, `RepairDamage`), range burner/flame part, bath-water reveal mesh, optional sink-wall water stain. Separately, the user still has to decide the sink upstand vs kitchen window sill conflict.

## 8. Tests (each in PIE, viewport screenshots as evidence)
1. New game: title camera → name entry → spawn at the door, facing in.
2. Walk every room in first person, including doors, the 1.68 m hall, closet access and furniture clearance. Floor-plan travel to all six rooms.
3. Every interactable toggles and resets, with prompts correct.
4. Each malady: inspect → hunk spawns → dialogue framing → repair hides attached damage → state persists after save and reload.
5. Bed: day advance, wake-up spot, daylight/window cycle. Front door: the leave-and-end-day prompt.
6. Save compatibility: an old save made in `L_Apartment` loads without the player landing inside geometry. Add a fallback to the room entry point if the saved location is invalid. Relationship and repair progress must be kept.
7. `L_Apartment` regression: the same checks still pass after the C++ changes.
8. Automation: `-FixHimScript="cmd;wait 2;…"` runs console commands; the debug panel (Insert) offers auto-play and day skip.

## Done when
All of section 8 passes in the redesign map, the parity table has no unexplained gaps, and the work is committed. Merging to main and switching `GameDefaultMap` are user decisions.

## Progress log
**2026-11-08 (integration thread):**
- Sections 0–6 implemented. The gameplay sublevel `L_Apartment_Redesign_Gameplay` holds 6 rooms, 4 maladies, 12 interactables + bed, the front door (`AFixHimDoor`), `PlayerStart` tagged `DoorStart` and a `TitleCamera`, built by `Tools/Editor/build_redesign_gameplay.py` (re-runnable). Window cards are tagged `WindowView`; `M_Redesign_WindowView` scales the game's brightness drive.
- Parity art integrated: `LV-FUSE-DAMAGE-01` and `KI-WALL-STAIN-01` are attached `RepairDamage`; `KI-RANGE-FLAME-01` is the stove's lit part; `BA-TUB-WATER-01` is the bath reveal.
- C++ (minimal, `L_Apartment` behaviour unchanged):
  - `PlacePlayerAtDoor` uses a `DoorStart` PlayerStart if present.
  - `AFixHimMalady::SummonHunk` re-frames the dialogue camera, so a closet opened since BeginPlay doesn't jam it.
  - Light toggles show an optional `RevealPart` while on (the stove flame).
- Verified in PIE (`Tools/test_redesign_pie.py`):
  - A new game starts at the door; all four encounters run to the end of the conversation with good framing.
  - Sleep hides all repair damage and the new day starts at the door.
  - `FixHimGoto` works for all six rooms; the front door opens `DoorPrompt`.
  - All interactables toggle, with stove flame and bath water visible.
  - Hunk availability is timing-gated by design (podcast/day rules); skip the podcast before scripted talks.
- Open items:
  - The repaired fuse wire (`RepairFixed`) needs a code hook to appear on repair.
  - A shine overlay shows as a rectangle on invisible malady proxies (same as `L_Apartment`).
  - Old-save location fallback (test 6) and an `L_Apartment` regression pass (test 7) are not yet run.
  - Floor-plan orientation is not reviewed.
  - Small dressing props and `ENV-SKY-01` remain to integrate.
- Build note: with other UnrealEditor instances open, UBT writes a new numbered `libUnrealEditor-ICanFixHim-000N.dylib` without updating `Binaries/Mac/UnrealEditor.modules`. Point the manifest at the new dylib, or the editor loads stale code.

**2026-11-09: PR #3 review fixes (all verified in PIE):**
- **Saves:** non-default maps get their own save file (`ICanFixHim_Save_<Map>.json`); the default map keeps `ICanFixHim_Save.json`. Continue restores a saved position only if it lies inside one of the map's rooms, otherwise it starts at the front door (progress is kept). Verified: the redesign writes its own file; an old-layout position (1300,300) falls back to the door; a valid one (300,200) restores.
- **`L_Apartment` regression (test 7) passed:**
  - New game starts at (190,120), yaw 75, and writes `ICanFixHim_Save.json`.
  - All four encounters run with unchanged framing.
  - Sleep hides all seven damage overlays.
  - Room travel works.
  - Continue restores (1100,300).
- **Scripts are safe to re-run:**
  - Finish materials are updated in place, never deleted.
  - Repair-damage overlays are never duplicated once they exist.
  - The kitchen and furniture imports update existing actors by label, and paths derive from `__file__`.
  - The capture tool quotes everything with `repr` and validates `--size`.
  - The gameplay builder calls `modify()` before hiding body sources, so the hide is saved.
  - Verified by snapshot: re-running ten scripts left the map identical (789 actors, no duplicate labels, no blank material slots, same damage attachments).
- **Debug command:** `FixHimContinue`, the same as the title Continue button, for scripted tests.
- **Rebuild order (environment, then gameplay):**
  1. `build_redesign_finish_materials`
  2. `build_redesign_wall_finishes`
  3. `place_redesign_windows`
  4. `import_/place_redesign_floors_doors`
  5. kitchen, furniture and dressing placement scripts
  6. `place_redesign_closets_lights`
  7. `build_redesign_masked_decals`
  8. `build_redesign_lighting`
  9. `import_redesign_parity_art`
  10. `prepare_redesign_gameplay_level`
  11. `build_redesign_gameplay`
  12. `build_redesign_collision` (also after any art re-import)

  Always finish with the gameplay builder and then the collision pass.

**2026-11-09: click actions for the newer art, collision, doorway and sofa fixes:**
- **41 new interactables wired** in `build_redesign_gameplay.py`:
  - **Kitchen:** pantry, upper-cupboard, cabinet and sink doors; sink drawers; the oven door (drops open on +85° roll); the sink tap (water stream).
  - **Living:** ceiling light and fuse-box door. Wyatt's malady now sits inside the box, behind that door.
  - **Hall:** both ceiling lights, both sconces, the console drawer, the end-cabinet doors and drawer, and the coat-closet sliding panels.
  - **Bedroom:** two dresser drawers, both nightstand drawers, and the east bed lamp.
  - **Bath:** mirror sconces (the light sits out from the wall so it leaves no hotspot in the mirror), the basin tap, and the shower curtain slide.
  - **Office:** the closet panels, three desk drawers, the cabinet doors and drawer, the desk lamp and the floor lamp.
  - Open poses were checked in viewport captures. Sliding-closet panels each slide behind the other, so clicking one opens that half.
- **Collision (new `build_redesign_collision.py`):**
  - **Problem:** the FBX imports had no simple collision. The click trace (Visibility, simple) passed through every art-body interactable, including the older Fridge/Wardrobe/TV/Bed parts, and the player walked through furniture.
  - **Fix:** 226 redesign meshes now use complex collision as simple. Exact shapes keep doorways, cabinets and closets open. Placement scripts that spawn with collision off (floors, ceiling, trim, door frames) are unchanged.
  - **Verified:** a trace sweep shows every interactable and malady is reachable. Wyatt's is reachable only once the fuse door is open, as intended. In PIE, a real click opened the fuse door, and a second click started Wyatt's encounter.
- **Doorways:** the room-door, entry and sliding-closet frames put their jambs exactly on the clear opening, and their head jambs at 211 cm (215 cm for the sliding frames). The walls were cut to the same line, so the plaster z-fought with the jambs and showed under the heads.
  - **Fix:** `build_redesign_wall_finishes.py` cuts door-type openings 3 cm wider per side, with headers at 214 cm (218 cm for the sliding frames). The casings hide the cut.
  - An `EntryBacker` panel outside the east wall stops sky light showing through the gap around the entry leaf, which never opens.
- **Sofa:** turned to yaw −90. Its front is Blender −Y, which imports as +Y; at yaw 90 it faced the west wall.

## Revision 02 integration (2026-11-09)

The approved revision 02 layout ([handoff](layout-revision-02/README.md)) is built as a separate map pair,
`L_Apartment_Rev02` + `L_Apartment_Rev02_Gameplay`, by a re-runnable pipeline in `Tools/Editor/Rev02/`. The
game and editor default maps now point to `L_Apartment_Rev02`; the original `L_Apartment_Redesign_Blockout` remains available.

**Pipeline** (run in order; 01 always starts from a fresh copy of the A+ maps, so the whole chain reproduces):
1. `rev02_01_make_maps` — copy the A+ map pair to Rev02 and re-point the streamed gameplay sublevel.
2. `rev02_02_import_fitted` — import the fitted kits (KI-CABINET-02, KI-SINK-NARROW-01, ARC-WINDOW-KITCHEN-02,
   BR-CLOSET-02, ARC-SLIDING-CLOSET-02, ARC-DOOR-02, ARC-ENTRY-DOOR-02, KI-WALL-TABLE-02, KI-STOOL-02,
   ARC-CLOSET-STORAGE-02, LV-BOOK-01 book parts). Run once per source release, not per rebuild. Uses the legacy FBX
   importer: UE 5.8's Interchange path drops authored UCX hulls.
3. `rev02_03_shell` — walls, rough openings (doors 1.05 × 2.14 m, sliders 0.96 × 2.18, walk-in 1.10 × 2.14, kitchen
   portal 1.20 × 2.30, living/hall 7.20 × 2.45), floors, trim, bath tile, office wainscot with under-sill panels,
   lead paint, windows, the 0.99-clear room/entry doors (open leaves collide, posed at 90°), sliding frames.
4. `rev02_04_furnish` — rigid moves of every A+ assembly with its dressing and click actions to the plan, plus the
   fitted kitchen, walk-in, sliding panels, storage, wall table and stool.
5. `rev02_04b_dressing` — wall-mounted dressing and children from the elevation schedule (shelves, switches, rails,
   sconces, books from LV-BOOK-01 parts), and schedule height corrections.
6. `rev02_05_gameplay` — re-bind changed click actions (kitchen cabinet fronts from the KI-CABINET-02 manifest
   pivots, narrow-sink tap, west-hinged fridge, walk-in doors, sliding panels), rooms + travel points, the walk-in as
   a `bedroom` sub-volume, front door, door start, title camera, re-derived talk spots, Malcolm's glow light.
7. `rev02_06_lighting` — fills, window-view cards and sun spot follow the new rooms/windows.
8. `rev02_08_reconcile` — verification: writes [Rev02 engine reconciliation](Rev02%20engine%20reconciliation.md)
   (every elevation-schedule instance and child → actors or an intentional omission; every other placed actor classified).

**Current feedback stages (screenshot batch 2):** the eight-stage list above is the original integration history, not the complete current rebuild recipe. Before rebuilding maps, compile the current C++ editor target and import all current kits with `rev02_02_import_fitted`, then build `rev02_02b_feedback_materials`. The importer uses legacy FBX for authored UCX. Never recreate the maps merely to import a source release.

For a fresh map build, run 01, 03, 04, 04b and 04c (wall art), then 05 (gameplay, which invokes 09 controls), followed by the feedback stages in this order:

1. 05b bathroom, 05c bath tile, 05d feedback placement, 05e fuse box, 05f closet light, 05g TV, 05h materials, 05i joinery.
2. 05j second-batch materials/placements, 05k baseboard stops, 05l kitchen fronts/backsplash/fillers/range and box cloth, 05m room-source replacements.
3. Reapply 05c after 05m so pink curved bullnose replaces the temporary plum caps; reapply 05h for tile glaze and 05k for casing stops. This late pass is required because earlier feedback stages may reconstruct those actors.
4. 06 lighting (including `WindowSun` tags), 09 controls, then 05n authored tap water and synchronized splash, followed by 05o dielectric puddle film (retiring the ineffective wet-only decal).
5. 08 reconciliation, followed by the applicable PIE controls, clicks, capsule routes, neighbour sweeps, encounter/repair-state checks and final lit room captures. Scripts completing is not gameplay acceptance.

For an incremental source update, import the changed kit, rebuild affected material graphs, and run its matching feedback stage plus any dependent late stages. Preserve existing gameplay identities, pivots, repair bindings and saved states. Source kit READMEs document the axes, origins, material mappings and collision exceptions. Do not use auto-convex collision across door or closet openings.

**C++:** `AFixHimRoom::bSubVolume` — an extra area of a room (the walk-in closet of the bedroom). Standing in it counts
as being in that room; crossing between it and the main volume neither changes the room nor dismisses the room's
hunk (`NotifyLeftRoom` returns before dismissing); the floor plan draws it without status or a travel button and
`FixHimGoto` skips it.

**Collision:** fitted kits keep their authored UCX hulls; sources without UCX (narrow sink, closet bulb/mold) use
complex-as-simple. `build_redesign_collision.py` now counts convex hulls as existing collision.

**Click actions and repair identities:** the A+ map has 54 interactable actors (13 from the original parity pass,
41 added 2026-11-08; FrontDoor and Bed included). Rev02 keeps all 54 by label and adds 3: `Cabinet_Door_2` and
`Kitchen_Drawer_2` (the 0450 cabinet's fronts) and `Sconce_Kitchen` (breakfast sconce) = 57. The four maladies keep
their hunk ids: `Malady_FuseBox` (wyatt, living), `Malady_Sink` (lukey, kitchen), `Malady_PinkTile` (tyler,
bathroom), `Malady_Mold` (malcolm, bedroom via the walk-in sub-volume). Changed bodies: Sink_Door_L/R and
Sink_Drawer_L/R on the KI-CABINET-02 0775 fronts, Cabinet_Door/Kitchen_Drawer on 0425, Sink_Tap on the narrow
sink's tap, Wardrobe_Door_L/R on BR-CLOSET-02, the four closet panels on ARC-SLIDING-CLOSET-02. The A+ fridge
action pivoted on the handle edge; it now pivots on KI-FRIDGE-01's measured west hinge (105° in Rev02; the A+
builder is fixed too, applied on its next run — the A+ map itself was not rebuilt).

**Validation (2026-11-09, final build):**

| Check | Method | Result |
|---|---|---|
| Schedule coverage | `rev02_08_reconcile` vs. elevation schedule (97 instances) | 0 problems, 0 unaccounted actors; 11 intentional omissions recorded |
| Routes | capsule traces (r 38, hh 90) along every approved circulation path, room leaves colliding at 90°, closet leaves closed and open | all clear; the only hit is the segment that starts inside the closed entry leaf |
| Bedroom route | real PIE pawn, both closet leaves open, actual bed | y 6.55 blocked by the right leaf (hinge at 5.678, tip 6.181); y 6.62/6.65/6.68 pass — plan updated to 6.65 |
| Walk-in entry | real PIE pawn through the open leaves | passes on the centreline and ±2/±4 cm |
| Encounter spots | capsule overlap at every hunk spawn / talk spot (closet leaves open and closed), room containment, sight line | all clear; Wyatt's and Lukey's talk spots re-derived (sofa 30 cm, wall table) |
| Door/drawer sweeps | body collision overlaps through full travel (5°/3 cm steps); sensitivity check (forced 10 cm overlap registers) | 33 clear; pantry/upper doors and shower curtain have no simple collision (bounds-checked) |
| Range-side doors | traces on KI-RANGE-01 sides, then sweeps after the 40 mm filler revision | full 100° restored, clear |
| Clicks | real `FixHimClick` from the pawn on 17 actions (new/re-bound/reveal) | all toggle; reveals visible: sink tap water, stove flame, tub water |
| Encounters | conversations run to the end (`met=1`) | Wyatt by real clicks (fuse door, then malady), Lukey, Tyler, Malcolm via `FixHimTalk` |
| Repairs | **state-driven repair test** (not the repair minigames): all met, `FixHimSetFixed` ×4, `FixHimSleep` → new day (pawn back at door start) | the six hunk-attached overlays hide (flags + before/after scene captures); lead paint stays (not tied to a hunk) |
| Walk-in sub-volume | PIE walk bedroom ↔ closet, travel | room id stays `bedroom`; `hall` on leaving; `FixHimGoto bedroom` lands in the bedroom. Non-dismissal while crossing is code-backed: Malcolm auto-dismisses 0.35 s after a talk (`HandleConversationEnded`), so "present and idle while crossing" was not reachable |

Captures: `Saved/ApartmentProgress/rev02/` (room views and `pie_*` scene captures); the reviewed set is archived by
the art thread under `layout-revision-02/engine-review/`.

**Hook-up audit (2026-11-09, after the merge):** code, config and dialogue data hold no references to old-layout
labels or positions except the title camera. `FixHimPlayerController` replaced every map's title camera with a view
tuned for the original `L_Apartment`; in Rev02 that framed a wall edge beside the kitchen portal. A camera tagged
`TitleCameraAsPlaced` is now used as placed (Rev02's sits on the hall centreline so the ±60 cm title drift stays clear
of walls); untagged cameras keep the old override. `CeilingLight_HallEast` now hangs in the kitchen and has
`room_id` `kitchen` (non-malady room ids are not read by gameplay). Room-id audit: 0 mismatches of 61. In PIE, the
front door and the bed open the end-of-day prompt by real clicks, and the title screen shows the living room.


## Current round-3 rebuild order (2026-11-11)

This supersedes the batch-2 recipe above. Asset/script changes only; no new C++ build is required for this pass. Stop PIE before every entry point. For incremental work import only the affected kit/parts; do not regenerate maps just to update a source mesh.

Imports: `rev02_02_import_fitted` → `rev02_02c_reimport_round3` → `rev02_02b_feedback_materials`. The full map pipeline then runs 01, 03, 04, 04b, 04c, 05, 05b, 05c, 05d, 05e, 05f, 05g, 05h, 05i, 05j, 05l, 05m, 05n, 05o, 05p, 05q, 05r, 05s, 05v, 05t, 05u, 05k, 06, 08. Numeric suffixes here refer to `Tools/Editor/Rev02/rev02_*` scripts. The late 05k uses floor-level casing footprints so header caps cannot shorten baseboards.

Round-3 acceptance and known test limits: [completed feedback record](layout-revision-02/feedback/Round3.md). The new `Basin_Tap_R` follows the existing taps' authored-off new-game/load behavior; it operates independently and has its own authored water reveal/splash.
