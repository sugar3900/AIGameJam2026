# HA-COAT-01 — hanging hallway coat

Status: **prototype for visual review**, not yet approved or imported to Unreal. `concepts/coat-multiview-v1.png` is the generated multiview garment reference. `previews/coat-three-quarter.png` and `coat-front.png` show the actual modeled object; the background wall is for preview only. The collar and sleeves are simplified modeled surfaces rather than a cloth simulation. A review pass added a lined neck and curved back collar, softened lapels, vertical folds and asymmetric drape. Compare the silhouette with the concept in the assembled hallway.

## Model and placement

`model/HA-COAT-01.blend` is editable source; `model/HA_Coat.fbx` contains 17 mesh parts representing the coat, folded lapels, pockets, buttons, cuffs and a small hanging loop. It is a static prop, with no pickup interaction or cloth simulation. Combine the FBX pieces at import or preserve their transforms; do not import the preview wall, lights or camera. Blender axes: Z up, visible front toward −Y. The authored top-center datum is at (0, 0, 0); the coat hangs downward, and reimported bounds are **0.446 m wide × 0.110 m deep × 0.852 m high**. It is about 2.6 cm wider and 4.8 cm shorter than the schematic 0.42 × 0.12 × 0.90 m inventory target. The loop sits near the top rear at x=0; align it with one hook on `HA-HOOKS-01` rather than simply placing both origins at the same point. The rail's overall projection is 0.067 m and the coat extends toward −Y; check the hook intersection, wall penetration and hall capsule/camera clearance in Unreal.

## Texture and validation

The selected `textures/wool-felt-v2.png` is a separately generated muted rust felt material with painterly color variation. `wool-russet-v1.png` is an independent earlier woven candidate, rejected for overly prominent weave at this scale. The material is a UV color texture, packed in the blend and included alongside the export. FBX does not transfer Blender's full node graph; recreate a high-roughness fabric material in Unreal and verify texture orientation and seams. The coat has thin cloth surfaces with solidified body/sleeves/lapels; the neck lining is a single face and may require a two-sided material if viewed from behind. Validate actual shading from both sides in engine. The gray wall in the render is not an exported coat component.

Rebuild from the worktree root with `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/HA-COAT-01/model/build_coat.py'`; validate with the adjacent `validate_fbx.py`. The latest clean FBX reimport reports **17 meshes, 7,299 vertices, 14,383 triangles, no zero-area geometry, finite vertices/UVs and UV layers present on all meshes**. This is a Blender round-trip only. Unreal import, material, two-sided shading, placement, collision and final in-room appearance remain untested.

## Image generation provenance

Built-in imagegen was used with the apartment's painterly fixer-upper reference for a single empty warm russet vintage coat shown front, rear, both sides and three-quarter; no person, hanger or hook. Two independent built-in generated material directions were compared: textured warm russet woven wool and softer muted rust felt with broad brush variation. The latter was selected because it reads more subtly at prop scale. See `concepts/` and `textures/` for the retained files.
