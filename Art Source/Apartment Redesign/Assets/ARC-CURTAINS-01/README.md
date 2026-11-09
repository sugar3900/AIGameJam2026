# ARC-CURTAINS-01 — paired floral curtains

Concept-guided curtains for a 1.60 m window. The [concept sheet](concepts/curtains-v1.png) supplies front, back, side, perspective and open/closed views. Blender uses metres, Z up, with a shared floor origin: rod spans 2.18 m, its center is 2.27 m high, and fabric hangs from approximately 2.21 m to 0.18 m above the floor. Adjust assembly height for the actual window.

## Fabric comparison

Both images in `textures/` are independent generations. Candidate A has the compact rose/coral flowers and olive foliage closest to the reference and is used for the model. Candidate B has a more open wildflower motif and is retained as an alternative. They are color albedos rather than height maps. Their edges have not been proven seamless: avoid tiling outside 0–1 and check the center join in-game.

## Files and continuous drawing

- `model/ARC-CURTAINS-01.blend` and `model/build_curtains.py` — editable source and headless rebuild.
- `model/Curtain_Rod.fbx` — static rod, finials and brackets.
- `model/Curtain_Left.fbx` and `model/Curtain_Right.fbx` — individually skinned panels with matching `Basis` and `Closed` blend shapes, each bound to one neutral `CurtainRoot` bone. Seven rings per panel are part of the same topology and move with the fabric.
- `previews/curtains-open.png`, `curtains-halfway.png`, and `curtains-closed.png` — Blender renders at shape-key values 0, 0.5, and 1.

The FBX files share a floor origin. Import the rod as a static mesh and each panel as a **skeletal mesh with Import Morph Targets enabled**. Set the `Closed` morph target continuously from 0 (gathered) to 1 (drawn) on both panels together; the neutral root holds the mesh, and the key moves the rings and fabric. Apply `Curtain_Floral` and `Aged_Brass` materials, and use no decorative collision. This is a prescribed morph, not a cloth simulation: inspect the entire transition in Unreal, particularly panel/window intersections, the center join and ring attachment. The FBX round-trip preserves the key and armature in Blender, but Unreal import, target naming, animation, materials and placement remain **untested**.

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/validate_fbx.py` from this asset directory. Each reimport is checked for finite positions and UVs; panel morph targets and armatures must exist with matching topology, and evaluated mesh normals and triangle areas are checked at values 0, 0.5 and 1. Current checks pass for all three files. Recreate Unreal materials and verify lighting, collisions, draw-call cost and actual transition in the assembled room before approval.
