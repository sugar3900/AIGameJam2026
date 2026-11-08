# KI-POTTERY-01 — hand-thrown kitchen vessel

A 0.160 m diameter × 0.239 m high honey-cream glazed ceramic vessel for the A+ kitchen display shelf. Its rolled terracotta rim, modest botanical motif and restrained age follow the selected concept. It is a decorative static prop; the mouth and interior cavity are actual continuous geometry, not a painted-on opening.

## Files and placement

- `concepts/vessel-multiview.png`: selected front/back/left/right/perspective concept.
- `textures/botanical-glaze.png`: original generated painterly base-color wrap. `previews/vessel-perspective.png`: studio Blender render on transparent background.
- `model/KI-POTTERY-01.blend`: editable source. `model/KI_Pottery_01.fbx`: the single static mesh. `model/build_pottery.py` and `model/validate_fbx.py` reproduce it and its checks.
- Blender coordinate convention: metres, +Z up; front with botanical sprig faces local −Y. The common origin is at tabletop centre; geometry extends from Z=0 to 0.239 m. The FBX is exported with Blender `axis_forward=-Z`, `axis_up=Y` and unit-scale enabled; verify Unreal axis conversion and scale on import rather than assuming its local yaw.
- Use the base color texture in sRGB, with rough warm glaze. Interior and rim are separate warm ceramic and terracotta material slots. Blender shader settings do not automatically create the finished Unreal material. The generated wrap is not mathematically seamless; its UV seam is at the back (+Y), so inspect it from all accessible views in Unreal. No bump/displacement is required for the painterly strokes.
- Place on the kitchen south display shelf with its base on the shelf surface. Confirm actual placement, collision, lighting and UE texture appearance in-room; these have not been tested in Unreal.

## Validation

Blender 5.2.3 clean FBX reimport: 1 mesh, 2,720 vertices, 5,436 triangles, measured 0.160 × 0.160 × 0.239 m; zero nonfinite coordinates/UVs, zero degenerate geometry or UV triangles. A ray down the centre passes through the open mouth and reaches the cavity floor at z=0.015 m. Validation output is `model/validation.txt`. Initial UV check caught horizontal-rim UV degeneracies; the rebuilt export fixes them.

## Image generation provenance

Both images were created with the built-in image-generation tool with `Art Source/Environment Concepts/painterly-fixer-upper.png` as the style reference.

Concept prompt: "Use case: stylized-concept. Create a clear five-view concept sheet for ONE vintage handmade ceramic kitchen vessel, for the attached painterly fixer-upper apartment game style. A charming useful small hand-thrown jug-vase, 16cm diameter and 24cm tall, warm honey-cream glaze with subdued terracotta rim and a small hand-painted sage botanical sprig on its belly. Rounded foot, gently pear-shaped body tapering to an open neck and rolled rim, real open mouth, no handles. Restrained localized age, good bones. Show consistent front, back, left, right and three-quarter views of the same vessel; no text, no extra objects, neutral backdrop. The painterly quality is rendering and texture, not thick smeared paint."

Texture prompt: "Texture asset for a stylized 3D hand-thrown ceramic vase. Flat unlit rectangular UV wrap color texture, NO photographed vase, NO perspective, NO lighting, NO shadows, NO text. Warm honey-cream ceramic glaze with subtle painterly brush variations and very restrained edge flecks. In the center place one modest hand-painted muted sage botanical sprig with small ochre berries; leave sides mostly plain so cylindrical back seam is unobtrusive. No geometric borders. Match the attached painterly apartment reference. This is an albedo map, not physical paint buildup."
