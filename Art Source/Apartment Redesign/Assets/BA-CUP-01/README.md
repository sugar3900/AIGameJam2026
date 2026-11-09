# BA-CUP-01 — bathroom toothbrush cup

Provisional art asset for the bathroom shelf in the A+ elevations. `concepts/cup-multiview-v1.png` is the generated front/back/side/perspective and empty-cup concept. The finished model includes a genuinely hollow ivory tumbler, rose band, and two separate ivory/sage toothbrushes with modeled bristle tufts. `previews/cup-perspective.png` shows the assembly; `previews/cup-empty.png` shows the interior.

## Export and placement

- `model/BA_Cup.fbx` is the cup; `model/BA_Brush_Ivory.fbx` and `model/BA_Brush_Sage.fbx` are individual brushes. All three use the same tabletop-centred `(0,0,0)` origin and export in the assembled pose. Place the three FBXs at the same transform to reproduce the preview, or move the brushes separately for interaction. Local X spans the cup, Z is up and the floral face / bristles point toward −Y. One Blender metre corresponds to 100 Unreal centimetres; verify the FBX import's orientation and scale in the target level.
- Reimported cup bounds are **0.0778 × 0.0778 × 0.099 m**. Each brush is ~0.177 m long with its assembly tilt baked in; the two brush FBXs include modeled tuft geometry. Use simple nonblocking collision for shelf dressing and do not let an automatic solid collision hull prevent the brushes from occupying the hollow cup. Brush pickup/animation is not implemented.
- The two ceramic textures under `textures/` are copied from `KI-MUG-01` for a coherent bathroom/kitchen palette. `Floral_Ceramic` uses `floral-ceramic.png`, `Ivory_Ceramic` uses `ivory-ceramic.png`; `Rose_Band`, `Sage_Handle`, `Ivory_Handle`, and `Warm_Bristles` are separate simple material slots. The floral detail is in the UV color texture, not physical paint. Recreate the materials in Unreal (sRGB color maps, roughly 0.47 ceramic roughness, muted diffuse handles); FBX does not transfer the complete Blender material graph. Inspect the cup's UV seam, tiny bristles, textures and scale in room lighting.

## Rebuild and checks

`model/BA-CUP-01.blend` is the editable source. Run Blender headless with `model/build_cup.py` to rebuild exports and the perspective preview; `model/render_empty.py` renders the cup without brushes. `model/validate_fbx.py` reimports each FBX and checks mesh presence, finite vertices/UVs, UV layers and nonzero geometric triangle area. Latest reimport results in `model/validation.txt` show 2,940 triangles for the cup and 2,820 per brush, with zero invalid geometry or UV errors. The two texture images are referenced relative to the blend file.

The concept and studio renders are not engine results. Unreal import, material mapping, collision, shelf placement, brush interaction and room-scale appearance remain untested.
