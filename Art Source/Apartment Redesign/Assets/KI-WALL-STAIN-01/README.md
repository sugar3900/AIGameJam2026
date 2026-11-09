# KI-WALL-STAIN-01 — optional sink-wall water stain

**Status: provisional Blender asset for parent review; Unreal not tested.** An optional, restrained ochre water tide and hairline damage patch for warm kitchen plaster. It is distinct from the closet's black mold. See `concepts/stain-before-after-v1.png` for the initial kitchen concept and `previews/stain-before.png` / `stain-after.png` for the same preview scene with the separate stain shown and hidden. The displayed sink and wall are preview context, **not part of this export**. The preview is an illustrative arrangement, not a decision about the unresolved sink upstand/window sill conflict.

## Files and placement

- `model/KI_Wall_Stain.fbx`: single zero-thickness quad with UVs, **0.70 m wide × 0.47 m high**, mesh origin at the centre of the stain. Source Blender coordinates are metres, +X right, +Z up, front facing −Y. The quad and its origin are local at zero in the FBX; the Blender source places the object at `(0.48, 0.323, 1.63)` m only to make the arbitrary preview. Do not copy this illustrative transform into the level.
- `model/KI-WALL-STAIN-01.blend` and `model/build_stain.py`: editable scene and reproducible build, including preview-only imported sink, wall, camera and lighting. Building the preview requires the existing `KI-SINK-NARROW-01` body and textures in their original paths; only the stain is selected for FBX export.
- `textures/stain-candidate-a.png` and `stain-candidate-b.png`: two **independently generated** transparent candidates. A had an opaque plaster-shaped halo and was rejected. B supplies the selected irregular water marks, streaks and fine cracks. Both are generated color/alpha images, not an edited plaster image or a physical normal map. The selected image is packed in the `.blend` and available separately for Unreal.
- `model/validate_fbx.py` / `model/validation.txt`: clean Blender FBX reimport and alpha-edge checks. Run from the worktree root with `'/Applications/Blender.app/Contents/MacOS/Blender' -b -t 2 --python 'Art Source/Apartment Redesign/Assets/KI-WALL-STAIN-01/model/validate_fbx.py'`.

Treat placement as flexible: rotate so the FBX's visible face points into the room, then place its centre on a clear plaster face above or beside the sink; offset slightly toward the room to avoid z-fighting (the preview uses a ~2 mm offset). Avoid covering the window, sash, tap, cabinets, backsplash or interaction targets. Confirm FBX conversion, actual wall normal, and viewing angles in Unreal. The placement must be decided against the final sink/window arrangement, which remains unresolved.

## Unreal material and repair state

FBX does not transfer the finished Blender shader. Import `stain-candidate-b.png` with its alpha; reconstruct a two-sided translucent surface material, or use an equivalent correctly configured decal. The preview uses:

1. Texture RGB multiplied by linear tint `(0.58, 0.46, 0.31)` for muted ochre.
2. Opacity `clamp((TextureAlpha - 0.008) * 1.25, 0, 1)` to feather the marks and suppress residual outer-edge alpha. Do not use the raw image as an opaque wall panel. Adjust brightness and opacity for the actual plaster and scene lighting.
3. Rough, non-metallic surface; no collision and no shadow casting. Inspect from shallow angles and at final mip levels for fringing, sorting artifacts or a visible quad. Opacity and shadow behavior have **not** been tested in Unreal.

Show the damage before repair and hide it for the clean wall. If the integration team chooses to tie it to Lukey, use a separate `RepairDamage`-tagged actor attached to the appropriate malady in the same streamed sublevel, and verify repair, save/reload and reset. This file does not implement or promise that gameplay linkage.

## Validation and limits

Latest Blender 5.2.3 FBX round trip: one quad, UVs present and finite, nonzero polygon area, dimensions `(0.70, 0.00, 0.47)` m. Selected source PNG raw outside-edge alpha is at most `0.0078432`; the documented subtract/multiply opacity formula produces a maximum of zero along that edge. This does not establish mip behavior or transparency quality in Unreal. The marks are intentionally small and low-contrast; verify readability against actual kitchen lighting and wall texture rather than globally darkening the room.

The stain concepts were generated with the built-in image tool. Candidate A requested a pale water-stained plaster patch on transparency; B requested only translucent tide lines, drips and cracks with no backing. Candidate B was selected because A retained a pale plaster-shaped halo. The damaged/repaired previews were rendered from the assembled Blender scene, with the same sink and wall and only the stain visibility toggled.
