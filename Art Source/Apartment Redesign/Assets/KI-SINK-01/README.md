# KI-SINK-01 — vintage kitchen sink assembly

**Status: revised modeled candidate for art review**, not an approved final asset or Unreal import. The approved design concept is `concepts/sink-states-v1.png`; `references/multiview-v1.png` is an AI-generated modeling aid, reconciled against that concept rather than treated as measured geometry.

## Geometry

Blender source is `models/KI_SINK_assembly.blend`. The cabinet/sink body, two doors, two drawers, two cross taps and repair-damage overlay are exported as individual FBXs under `models/`. The center section is a deep, open apron basin; the exposed drain, back panel and bucket sit below it. Cabinet doors reveal modeled interiors and drawers have modeled sides and bottoms. The plant, towel, backsplash and any loose counter props in the concept are separate scene assets and are not included.

Dimensions in metres: body bounds 2.37 wide × 0.66 deep × 1.343 high, including faucet. The two side cabinets are 0.66 m wide each, the sink itself 1.05 m wide, and the worktop is at 0.91 m. The model uses Z-up, front toward negative Y. Closed body and leak overlay have floor-centre origin (0,0,0); each door is pivoted at its outer front edge; drawers use their front-centre origins and slide toward -Y; tap pivots are at their handles. These parts require assembly, collision and animation setup in Unreal; the FBXs are not an assembled Blueprint.

`KI_SINK_damage.fbx` holds the leak drops and puddle. Hide it to depict repaired state; the bucket stays as part of the body in both states. The isolated before/after concept art shows the intended story and the previews show model versions. The damage overlay uses opaque preview materials; actual water shading/transparency still needs Unreal testing.

## Materials and provenance

`Sink_SageReference.png` and `Sink_EnamelPainterly-v3.png` were generated for this asset from the chosen concept. `Sink_WoodReference.png` is copied from the earlier environment texture library. The derived `Sink_SageTint-v2.png` and `Sink_ToeTint-v2.png` have their tints baked into the pixels for consistent import. All are UV image colour maps. Chrome and leak materials are separate slots. Textures are packed in the blend and also available under `textures/`.

The revised version rounds the porcelain apron and basin, adds warmer painterly enamel, deepens the sage, mutes the toe-kick, and adds tap collars. The result is still more restrained and cleaner than the highly rendered concept and needs visual review in its final Unreal lighting.

## Validation

Run `Blender -b --python build_sink.py` from any directory to rebuild, and `Blender -b --python validate_fbx.py` to import each FBX in a fresh scene. On this build all eight FBXs had finite vertex positions and UVs, no zero-area polygons, and a UV layer. `previews/open-controls.png` shows both doors rotated and a drawer translated without crashing through the carcass. `previews/leaking-three-quarter.png` and `previews/repaired-three-quarter.png` show the two damage states. These checks do not establish Unreal reimport correctness, render-bounds health, collision, repair persistence or in-game camera clearance.
