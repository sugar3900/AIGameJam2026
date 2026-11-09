# KI-JAR-01 — floral ceramic kitchen canister

Provisional Blender asset awaiting parent visual review and Unreal evaluation. The original generated open/closed and multiview concept is `concepts/jar-multiview-v1.png`. `textures/floral-ceramic.png` is an independently generated flat painterly rose pattern; `textures/ivory-ceramic.png` is reused from `KI-MUG-01` to coordinate the lid and interior. The floral artwork is a base-color treatment, not raised physical paint.

## Geometry and assembly

The hollow body is approximately 0.158 m diameter × 0.202 m high; the assembled closed jar is 0.1604 m diameter × 0.245 m high including the finial. Body and lid are independent: `model/KI_Jar_Body.fbx` has a tabletop-centred origin at (0,0,0); `model/KI_Jar_Lid.fbx` has its pivot at the lid seating centre, (0,0,0.196) m relative to the body. Blender reimport retains that offset. +Z is up, the designated front is −Y. Recreate the closed assembly at those relative positions, checking Unreal FBX unit and axis conversion. The lid can lift away, but no animation or interaction is authored.

The model uses distinct floral exterior, ivory interior/lid and dusty-rose glaze material slots. FBX does not transfer Blender's complete shader graph: reconnect `floral-ceramic.png` and `ivory-ceramic.png` as sRGB base color, recreate a muted rough glazed ceramic and rose band, and inspect the back seam and color under game lighting. The generated floral wrap is not certified mathematically seamless. Use simple nonblocking collision where appropriate and verify jar spacing on the kitchen shelf.

## Source and checks

`model/KI-JAR-01.blend` is the closed-pose source and `model/build_jar.py` rebuilds the source, FBXs and open/closed previews using headless Blender. `model/validate_fbx.py` reimports both FBXs and checks finite geometry and UV coordinates, presence of UVs and nonzero geometry triangle area. `model/validation.txt` records the Blender reimport result; Unreal rendering, materials, pivots, collision, shelf placement and lid motion have not been tested.
