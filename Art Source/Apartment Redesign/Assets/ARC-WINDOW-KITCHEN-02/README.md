# ARC-WINDOW-KITCHEN-02 — fitted north kitchen window

Fitted derivative of `ARC-WINDOW-01` for the user-approved compact kitchen plan (2026-11-09). Reuses that kit's generated ivory paint texture, six-pane sash language, brass latch and source-sized moldings. The paint is stylized in its texture, with no modeled impasto. Original exports are unchanged.

## Placement and fit

**All five FBXs share the opening-sill origin `(0, 0, 0)`**, unlike the old floor-origin window. Units are metres; Z is up, X runs along the window width, and the room-facing front is **−Y**. Align the origin to the wall centre-line at the horizontal centre of the opening and **world Z = 1.25 m**. In the approved plan the north-wall centre is `(2.15, 0, 1.25)` m. The room lies toward plan +Y, so rotate the source front into that direction after checking import-axis conversion; do not copy an old floor-origin placement.

- Wall aperture: **1.60 m wide × 1.15 m high**, X = 1.35–2.95 m, sill 1.25 m, head 2.40 m. Jambs line this aperture; do not use the complete casing bounds as the cutout.
- Model-local opening X = −0.80…+0.80, Z = 0…1.15. Jambs are 44 mm wide/deep in their opening direction; casing is 95 mm wide. The visible sash aperture is smaller than the wall cutout.
- Apron bottom is local Z = −0.07, therefore **world Z = 1.18 m**. Its top is −0.025. The sill is 45 mm thick, with its top at local Z = +0.020.
- The wall front is local Y = −0.06. The sill's foremost point is Y = −0.17, giving **0.11 m projection** from the finished wall face. Casing is shallower. North-facing room placement puts the sill front at plan Y = 0.17 m.
- Sink upstand ends at Z = 1.135 m, leaving 45 mm below the apron. Faucet top is Z = 1.343 m, above the opening sill. The faucet must sit room-side of the glazing and sash track; exact faucet/handle depths still need a paired 3D/engine check.
- Overall frame/casing bounds are recorded in `model/dimensions.json`. Top cap reaches local Z = 1.268, world Z = 2.518 m, below the 2.75 m ceiling.

## Pieces and motion

- `model/ARC_Window_Kitchen_frame.fbx`: jambs, stops, casing, short apron and shallow sill. Individual box collision hulls surround the opening, rather than one convex hull sealing it.
- `model/ARC_Window_Kitchen_upper_sash.fbx`, `...lower_sash.fbx`: wood grids and latch parts. Each has named `UCX_<render mesh>_NN` convex box hulls for its individual members.
- `model/ARC_Window_Kitchen_upper_glass.fbx`, `...lower_glass.fbx`: separate glazing. No glass collision hull is authored; configure window blocking deliberately in engine.

Sashes and glass remain at their common sill origin in the exports. Parent each glass pane to the corresponding sash and translate the lower sash/pane together along local +Z by **up to 0.48 m**. Exported pose is closed. Separate tracks have a nominal 23 mm wood gap in Y; the open preview confirms the lower sash clears the upper track. No Unreal animation is authored. Update collision with the moving sash; do not leave hull actors at the closed location.

Use FBX simple-collision import (`auto_generate_collision = false`, import custom collision) for these parts and verify Unreal recognizes the hulls. Do not replace hollow frame collision with a single auto-convex box that closes the window. Set glass collision intentionally for game needs.

## Materials and reproducibility

`textures/ivory-window-a.png` is copied unchanged from `ARC-WINDOW-01` and packed in the blend. Use it as the painted-wood base color with roughness around 0.8. Brass is a separate material slot; glass is a preview placeholder requiring the established Unreal glass treatment. FBX does not reproduce Blender's material graph automatically.

`model/build_window.py` rebuilds the blend, five FBXs, dimension manifest and closed/front/open previews using headless Blender. `model/validate_fbx.py` reimports every FBX and checks finite geometry/UVs, origin, bounds, nonzero triangle area, collision hull names/counts and convex-box topology. See `model/validation.json` for results.

`previews/window-front.png`, `window-perspective.png` and `window-open.png` are studio renders. Warm plaster, exterior color card and a sink-upstand clearance proxy are preview-only and excluded from exports. The source `.blend` includes these labeled preview objects. Hidden wire collision objects are also preserved in the blend.

Status: Blender build and FBX reimport checks passed; studio closed/open views reviewed and casing seams corrected. Lead/in-engine review remains. Unreal material appearance, coordinate conversion, collision recognition, sink/faucet fit, sash interaction and in-room lighting remain integration checks.

## Paired sink clearance check

`model/check_sink_fit.py` imports the existing narrow-sink body and all five window exports without modifying the sink. Aligning the sink rear bound to plan Y = 0.15 places its source origin at plan Y = 0.4605001 m (its actual bounds are slightly offset from its origin). Window origin is at the wall centre-line, Z = 1.25. In that assembly, the faucet above apron height remains approximately **25.76 mm in front of the sill's foremost point**. Mesh-surface intersection checks found no sink/window contacts at lower-sash offsets 0, 0.12, 0.24, 0.36 and 0.48 m. Results are in `model/sink-fit-validation.json`. This excludes individual tap controls, shell, player and engine collision inflation; preserve the exact back-bound alignment and confirm the assembled game view.
