# KI-MUG-01 — vintage floral ceramic mug

Provisional Blender asset for kitchen shelves. The generated multiview concept is `concepts/mug-multiview-v1.png`; the original independently generated plain glaze and floral glaze textures are in `textures/`. The selected exterior uses `floral-ceramic.png`, with `ivory-ceramic.png` on the interior and handle, and a separate dusty-rose stripe material. The sprigs are color texture, not sculpted paint. The FBX is a single static assembled mug with a true hollow interior and handle; it can be instanced for two shelf mugs. There is no pickup animation or content in the cup.

## Dimensions and assembly

`model/KI_Mug_01.fbx` reimports at **0.11168 × 0.088 × 0.108 m**, Blender metres, Z up, origin at floor/tabletop centre, front toward −Y; handle projects +X. The FBX uses the default Blender export axis conversion and unit scale; check orientation and centimetres in Unreal. Set the origin on the shelf surface. Use simple nonblocking collision unless interaction design requires otherwise; avoid a collision hull that obstructs adjacent shelf placement.

The mesh has three material slots: `Ivory_Painted_Ceramic` (sRGB `textures/ivory-ceramic.png`), `Floral_Ceramic` (sRGB `textures/floral-ceramic.png`), and `Dusty_Rose` (base color from Blender). Set ceramic roughness near 0.43 and metallic 0; recreate and tune Unreal materials because FBX does not transfer Blender shader networks. Inspect the body UV seam and the stripe from all directions under game lighting. Floral placement is baked in mesh UVs; no shader projection is needed.

`model/KI-MUG-01.blend` is editable source; `model/build_mug.py` regenerates the asset and `previews/mug-perspective.png`. Run Blender background on `model/validate_fbx.py` to reimport and verify geometry, UV presence, finite coordinates and bounds; `model/validation.txt` captures a passing round trip (1 mesh, 2,620 vertices, 5,084 triangles; no degenerate geometry or nonfinite UVs). Unreal materials, collision and shelf placement remain untested. The studio render is not an in-game result.
