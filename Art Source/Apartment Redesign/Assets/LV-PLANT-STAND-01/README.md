# LV-PLANT-STAND-01 — living-room wooden plant stand

Status: **provisional Blender asset for lead review; not yet imported or checked in Unreal.** The generated `concepts/plant-stand-multiview.png` supplies front, back, left, right, top and perspective reference. The 0.45 × 0.35 × 0.48 m measured model, not the illustrative reference, controls placement.

## Files and fit

- `model/LV-PLANT-STAND-01.blend` is the editable Blender source. `model/LV_Plant_Stand.fbx` is the separate static stand: top, tapered legs, shaped apron, lower shelf and sparse edge wear, joined with material slots. Its reimported bounds are approximately **0.45055 × 0.35055 × 0.480 m**, including the fine wear pieces; dimensions are metres, Z up, long axis X, front −Y, origin floor-centre. Trim or adjust placement if the small overhang affects a strict footprint.
- `model/LV_Plant_Stand_Riser.fbx` is an optional **0.156 m diameter × 0.036 m high** wood pedestal, exported separately with its origin on its bottom centre. To match the fit preview, place its bottom at the stand top, Z = 0.480 m in the assembly, then place the `LV-PLANT-01` plant assembly origin at Z = 0.516 m. The original plant's lowest leaves descend roughly 0.030 m below its pot base; the riser leaves about 6 mm of nominal vertical clearance above the tabletop. Inspect actual foliage and collision after Unreal import. The riser is omitted from the stand-alone previews and can be left out if a different plant or placement is used.
- `previews/stand-perspective.png` and `stand-front.png` show the stand alone; `previews/stand-with-plant.png` appends the existing plant **only for scale and fit review**. The plant is not included in the stand FBXs. The pot base diameter is about 0.13 m, supported by the 0.156 m riser.
- `textures/walnut-muted-b.png` is the independently generated, selected walnut candidate reused from `LV-CHEST-01` to match adjacent furniture. Blender uses Hue/Saturation/Value saturation 0.68 and value 1.35, roughness 0.86; recreate or bake this color adjustment in Unreal. Edge-rub geometry has a separate material slot. Do not assume the FBX reproduces the Blender material graph.

## Validation and use

Headless Blender `model/validate_fbx.py` reimports both exports and checks finite positions and UVs, UV presence, nonzero geometry triangles and dimensions. Results are recorded in `model/validation.txt`: stand 1,432 vertices / 2,800 triangles; riser 764 triangles. Build with `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_stand.py` and render the separate plant fit with `model/render_plant_fit.py`. The fit preview requires the adjacent `LV-PLANT-01` source and is not a saved combined asset.

Unreal import, axis conversion, materials, collision, in-room lighting, foliage clipping and player clearance are **untested**. Check the riser and plant share the intended offsets after FBX import; the riser is not an animation. The front/back view is symmetrical; orient the long X dimension to suit the living-room elevation and actual space.
