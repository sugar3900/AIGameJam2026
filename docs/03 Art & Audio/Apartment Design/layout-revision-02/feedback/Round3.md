# Round 3 — completed apartment feedback corrections

All reported corrections in this round are installed and reviewed. The editor was saved and closed before commit. No C++ or gameplay state-machine changes were made. The independently merged matte-character changes on main were incorporated without overwriting them; unrelated UI concept work is outside this change.

## Final changes

| User report | Final correction and evidence |
| --- | --- |
| Baseboard glitching; living-room north uses old profile | Correct outward winding on all five slim stocks. Remove only the embedded low ivory base from derived living-wall meshes, retain plaster/crown/collision, install the 14 mm profile and butt both inside corners. Final hall and north-wall views are in `Round3/evidence/r3f_*`. |
| Pink tile edge pieces glitch | Correct outward quarter-round winding and regenerate fitted cap/bullnose meshes. Closed-positive-volume checks and installed grazing views pass. |
| Towel bar untextured | Bind its authored aged-brass image/PBR finish; cloth remains separate. |
| Rolled towels and toilet paper inverted | Correct towel skins/caps, paper outer skin, bore and tail. Four fresh FBXs preserve positions, pivots, UVs and slots; single-sided previews and installed views confirm the correction. |
| Basin taps unfinished/noninteractive | Left and new independent right tap each have a fitted 12.6 cm authored stream and synchronized splash. Real clicks prove independent on/off states, and aim traces pass through water. Close on/both-on/right-only evidence is archived. |
| Clawfoot tub undeveloped/untextured | Develop continuous hollow bowl, rolled rim, cast ball-and-claw supports and seated overflow; explicit painterly enamel and aged-metal blends. Drain seat, water level and placement remain fitted. Post-restart tub capture verifies the saved material. |
| Window frame top gaps | Close the south-window 22.5 mm and kitchen 5 mm casing/jamb gaps, add the living head return; all five installed headers show wood across the former opening. Exact outer bounds, origins and collision conventions retained. |
| Floating pot dots; faceted vessel | Remove four detached botanical spheres, rebuild a smooth 96-segment hollow pot/lip/saucer and recessed soil; both living and office copies replaced. Existing foliage positions/UVs/materials preserved. |
| Pantry door gap and repeating paint | Narrow 16 mm centre reveal to 4 mm, use distinct full-height paint crops, fix thin-edge/end UVs and supply matching hulls. Source and engine full-travel checks pass. |
| Countertop piecemeal | Replace embedded tops and five 4 cm filler strips with three continuous 5 cm slabs, fitted to walls/fridge/sink/range. One UV frame continues across each top and edge; drawer clearance retained. |
| Backsplash grout/edge tiles | Rebuild square cropped tiles, recessed 2 mm ivory joints, outward top/fridge bullnose and spherical corner. Create previously missing glaze MIs. 197 source tile/grout rays and installed close-ups verify the result. |
| Stove undeveloped; flat controls and handles | Fluted bakelite/ceramic controls, textured steel mounts/pulls, physical oven-window aperture, gasket, recessed subframe and adjustable feet. Concealed hinge relief removes new frame/plate interference. Real oven and burner clicks pass. |
| Black boxes under cabinets/stove | Replace cabinet toe blocks with recessed sage-painted U plinths; range has a recessed frame and defined feet. Original cabinet hulls retained. |
| Kitchen pipes/fittings too new; drain must match faucet | Shared tarnished alloy for faucet/taps/drain, with stronger corrosion/mineral wear on low pipes. Day/evening evidence shows matching fittings and visibly aged plumbing. |
| Picture frames untextured | Explicit wood/paint/gilt PBR finishes; correct grain normalization and world-planar sampling because old bevel UVs were near-constant. Artwork and mounts unchanged; close grain views archived. |
| Coat/office closet trim differs from doors | Match regular-door casing/head/cap sections on both faces, retaining panel tracks and travel. Floor casing stays ±54 cm; cap overhang is excluded from baseboard stop measurements. No duplicate frame was installed. |
| Mold too sparse and mirrored | User rejected both generated concept rounds and chose the original BR-MOLD-02 pattern. Preserve the original texture/formula and ~160 cm scale; enlarge to back plus both side walls, Z55–264 cm, using continuous unfolded coordinates and edge-faded offset samples with no flips. Ceiling overlay retired. |

## Validation

- [32-source export index and hashes](Round3/source-release.json); kit READMEs and fresh-import JSON reports document axes, pivots, material slots, UVs and collision. Closed solids have outward winding/manifold checks; foliage remains deliberately two-sided. Source review corrected the living liner and pantry thin-edge UVs.
- Room-control validator: PASS. Real PIE clicks cover the changed oven, burner, pantry doors, coat/office slides, kitchen tap and both basin taps. [Click log](Round3/engine-logs/r3_clicks.txt), [basin independence/visibility/trace log](Round3/engine-logs/basin_clicks.txt).
- Ten hinged kitchen/linen doors clear at 21 full-travel samples against current neighbours, including new slabs/backsplash. Pantry is clear to ±100°. [Kitchen sweep](Round3/engine-logs/sweep_r3_kitchen.txt).
- Oven: three near-closed hinge hardware/gasket contact samples at 0°, 4.25°, 8.5°; no neighbour contact, and the pressed frame clears throughout. Engine is clear from 12.75° through 85°; denser source sweep is clear from 10°. This improves both prior versions. [Sweep history](Round3/engine-logs/sweep_r3.txt) keeps the failed/pre-neighbour-list attempts; its final line uses all current neighbours.
- Mold repair is state-driven: visible initially and immediately after SetFixed, hidden after the next morning refresh and still hidden on Continue. The log was recorded with four attached surfaces; all three final wall surfaces were included, and the ceiling surface was subsequently removed. [Raw repair/load log](Round3/engine-logs/mold_repair.txt). This log does not claim a new puddle repair test; prior-batch puddle evidence remains separate.
- Reconciliation: 103 schedule instances, zero problems and zero unaccounted actors. [Generated reconciliation](../../Rev02%20engine%20reconciliation.md).
- All 753 referenced mesh/material packages are on disk; no saved new/modified package points to a UEDPIE world. New master materials compile after restart. A missing in-memory-only tub material was caught and fixed; creation now verifies actual package persistence.
- New/modified entry points fail early during PIE and preflight required actors before material/placement mutation. The importer validates returned import paths. Unchanged editor re-save churn was restored before handoff.

## Evidence and limits

[Final captures](Round3/evidence/), [raw logs](Round3/engine-logs/) and [SHA-256 manifest](Round3/evidence-manifest.json) are archived with the source. `r3f_*` are final installed views; selected `r3c_*` close-ups show running taps, grout, frame grain and oven details. `mold_orig_wrap_*` shows the accepted original-pattern implementation. Early `r3_*` and procedural `mold_C*` views are not acceptance evidence.

The broad white patches in some captures are the existing interactable shine wipe, confirmed by a PIE-only overlay A/B test in [diagnostics](Round3/diagnostics/); the production shine/hover behavior remains enabled. Splash planes are intentionally subtle. Tick validators require `Tools/run_in_editor.py` with a persistent namespace. The old environment validator's stale `Wardrobe_Door` label and auto-close harness's office retreat point inside the unchanged daybed remain documented pre-existing harness limits.

[Generated mold studies and prompts](Round3/mold-concepts/README.md) are archived as rejected explorations. They were made with the built-in imagegen tool and are not runtime assets; the original mold texture remains authoritative.
