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

  Always finish with the gameplay builder.
