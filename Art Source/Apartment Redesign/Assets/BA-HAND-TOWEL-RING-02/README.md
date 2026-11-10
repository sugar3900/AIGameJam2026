# BA-HAND-TOWEL-RING-02

Reviewed source replacement for the old bathroom hook and hanging hand towel, retaining schedule instance `BA-HOOK-01:082`. This is an actual circular brass ring supporting a folded ivory terry towel with faded rose borders. Hardware and cloth are separate static meshes.

## Files and placement

- `model/BA_Ring02_Hardware.fbx`: wall plate, stem, ring and fixings.
- `model/BA_Ring02_Towel.fbx`: continuous folded, pleated towel with real 2 mm thickness.
- `model/BA-HAND-TOWEL-RING-02.blend`: source and preview scene. Export only the named kit meshes, never the preview wall/lights.
- `model/build_ring.py`: reproducible Blender builder; run headlessly with two threads.
- `assembly.json`: exact exported bounds, transforms and material values.
- `validation.json`: independent FBX import, UV/bounds and tile-cap clearance checks.

Metres; +Z up; front −Y; wall plane Y=0. Both exports have origin `(0,0,0)` at the wall plate centre. Rev02 wall mounting point is plan `(7.84,7.10,1.15)`, facing west. Source-to-plan mapping is `(7.84+sourceY, 7.10+sourceX, 1.15+sourceZ)`. Existing import conversion keeps X and flips Y: UE yaw +90°, actor location `(784,710,115)` cm for both parts, with no additional baked offset.

The 21 cm ring's back surface clears the 36 mm tile cap by **17 mm** throughout world Z=1.00–1.05; this was checked against all re-imported triangles crossing that band. The towel starts below the cap. Keep the plate flush with plaster; no outward actor translation is needed. It hangs below the centre of shelf :077, between its corbels. Ring and towel are decorative, with no blocking collision or new click action.

## Materials and previews

Use `assembly.json` texture paths and tint multipliers explicitly; FBX material colour alone does not carry the complete Blender node graph. Colour textures use sRGB. Brass: metallic 0.68, roughness 0.48. Terry/border: metallic 0, roughness 0.94. Cloth has thickness and outward normals; two-sided rendering is optional, not a substitute for geometry. Textures are reused from the established bathroom rail kit and packed in the blend.

`previews/front.png` and `previews/three-quarter.png` are final source views. `concepts/ring-concept.png` is the generated design reference. Source FBX roundtrip passes; actual game lighting, shelf assembly and interaction acceptance belong to the engine integration review.
