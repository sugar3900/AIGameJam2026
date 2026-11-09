# KI-PLANT-01 — kitchen windowsill geranium

Provisional Blender asset for visual review and Unreal evaluation, not yet imported or tested in the game. `concepts/geranium-multiview.png` is the independently generated five-direction/three-quarter concept; it is artistic guidance, not measured geometry. `previews/geranium-perspective.png` shows the actual model after an iteration to increase flower density and give the petals depth. The shallow flower heads and simplified rounded foliage should be judged under the game camera and lighting.

The pot has worn terracotta and soil; the foliage has individually modeled scalloped geranium leaves with a dark zonal ring. Four stemmed clusters have muted rose blossoms. `textures/geranium-leaf.png` is an original AI-generated painterly leaf texture; `textures/terracotta.png` is copied from the previously generated `LV-PLANT-01` pot texture. Petals and stems currently use solid material colors. Texture brushwork is color only, not physical impasto.

## Files and dimensions

- `model/KI-PLANT-01.blend`: editable source. `model/build_geranium.py`: reproducible headless Blender generator. `model/KI_Geranium.fbx`: static assembly, seven material-group meshes with their scene transforms. Import as a combined mesh while preserving transforms, or preserve each FBX object's transform; do not zero individual pieces independently.
- Source uses metres, +Z up, floor/tabletop-centred placement; FBX export specifies **−Y forward / +Z up**, with unit scale. In a fresh Blender FBX import the visible bounds are **0.173 × 0.176 × 0.378 m**, with pot base at z=0; the original inventory target was approximately 0.22 × 0.18 × 0.50 m. Actual height is shorter and must be checked on the kitchen sill under the game camera. Pot maximum diameter is approximately 0.136 m; leaves are slightly wider.
- Recreate the painted clay, leaf, stem and petal material slots in Unreal. The leaves are one-sided modeled surfaces: use a **Two Sided** leaf material and check backface normals/lighting. No alpha masking is needed. Keep collision on the pot only; check windowsill width, window sash/curtain clearance and foliage overlap. The seven material slots and **17,032 triangles** require an in-engine performance check; LODs have not been authored.
- Blender nodes do not transfer through FBX as a complete Unreal material. The generated leaf texture is mapped to individual leaf polygons and is not a seamless surface tile. Reconnect `geranium-leaf.png` and `terracotta.png` and tune roughness/color under the actual room lighting.

## Checks

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python "Art Source/Apartment Redesign/Assets/KI-PLANT-01/model/build_geranium.py"` from the repository root. Validate with the adjacent `validate_fbx.py`; the last Blender 5.2.3 reimport reported seven meshes, 9,739 vertices, 17,032 triangles, finite vertices and UVs, UV layers on every mesh, and zero degenerate geometry triangles (`model/validation.txt`). This is not a test of Unreal scale, orientation, materials, collision, or performance. 
