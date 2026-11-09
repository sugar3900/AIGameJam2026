# ARC-WALL-SHELF-01 — period wall shelf

A reusable empty wooden display shelf, intended for the A+ hall, bedroom or office. `concepts/shelf-multiview-v1.png` is the selected generated front/back/left/right/perspective reference. The concept is illustrative; the dimensions and construction below govern the model. No books, plants or other decorative items are baked into the mesh.

## Model and placement

`model/ARC-WALL-SHELF-01.blend` is the editable Blender source, and `model/ARC_WALL_SHELF_01.fbx` is the assembled static shelf (plank, front bead, two shaped corbels, wall plates and four small brass fastener heads). Bounds are **0.650 m wide × 0.150 m deep × 0.145 m high**. The top of the plank is at local Z=0, the back mounting plane at Y=0, and the room-facing direction is local −Y. The common origin is the center of that wall plane at shelf-top height. Mount with its back against the finished wall face; objects placed on it should rest at local Z=0. The preview wall, camera and lights are not exported. The shelf is static; no object interaction is authored.

This is a single joined FBX mesh, so nonuniformly scaling it stretches the brackets, fasteners and wood grain. For a different width, preferably edit the Blender source or rebuild a variant by changing the plank length and bracket separation while retaining their cross sections; recheck the resulting wall clearance. It is not a modular straight-run or automatically adjustable kit. Check the desired shelf elevation, installed collision, decorative-object bounds, wall attachment and camera in Unreal.

## Materials and workflow

The selected `textures/walnut-muted-b.png` is the previously independently generated walnut candidate from `LV-CHEST-01`, copied here for a self-contained asset and to match adjacent furniture. In the Blender preview a Hue/Saturation/Value node sets saturation to 0.68 and value to 1.35, roughness 0.86; recreate or bake that color adjustment in Unreal, as the FBX does not transfer the full Blender node network. The fasteners use a separate muted brass material. Blender UVs project the wood according to face orientation. The painterly character is a color treatment rather than bump or displacement.

Build with `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_shelf.py`; validate with `Blender -b --python model/validate_fbx.py`. The current FBX reimport passed dimension, finite position/normal/UV, UV presence and nonzero-face/triangle checks: **560 vertices, 1,080 triangles**, bounds as above. `previews/shelf-perspective.png` and `previews/shelf-front.png` show the shelf mounted against a preview wall. Unreal material appearance, collision, wall mounting and in-room lighting are untested.
