# KI-CABINET-01 — vintage kitchen base cabinet

A single 0.65 × 0.65 m base cabinet with a 0.90 m counter height and 0.955 m overall upstand height. Built to accompany the approved `concepts/cabinet-v1.png`, which already contains front, back, sides, perspective, open-door and open-drawer views. The dimensions in the plan govern this model, not measurements inferred from the AI concept.

`model/KI-CABINET-01.blend` is the source; `model/build_cabinet.py` regenerates the source, exports and renders in headless Blender. Front is −Y; Z is up; units are metres. The FBX files are separate moving parts:

- `KI_Cabinet_body.fbx`: floor-centre origin; cabinet carcass, shelves and counter.
- `KI_Cabinet_door.fbx`: hinge origin at (−0.283, −0.326, 0) m, vertical Z axis; the preview opens −100° around Z.
- `KI_Cabinet_drawer.fbx`: assembly floor-centre origin; slides toward −Y, 0.30 m in the open preview.

`previews/cabinet-closed.png` and `previews/cabinet-open.png` show the same assembly and motion. The door opens on its left hinge, and the drawer is a separate hollow box.

## Finish and references

Four independently generated sage albedo candidates are retained as `textures/sage-A.png` through `sage-D.png`. A and B were the initial restrained approaches; C introduces stronger irregular marks, and D uses broad olive/moss and warm ochre strokes closest to the chosen concept. D is used with HSV value 0.75 in the Blender shader; recreate that value adjustment or author an equivalent tint in Unreal. The counter and handles use their own materials. A narrow sage divider behind the drawer masks the dark gap without intersecting its movement. Counter and toe-kick albedos are copies of the previously developed kitchen-sink palette so these adjacent items can share a coherent finish. All color variation belongs to the art treatment; the wear does not use a displacement map.

## Verification

`/Applications/Blender.app/Contents/MacOS/Blender -b --python model/validate_fbx.py` from this asset directory imports each FBX afresh and checks vertices, polygon normals, UVs and zero-area triangles. All three exports passed. FBX round-trip dimensions: body 0.650 × 0.650 × 0.955 m; door 0.569 × 0.088 × 0.515 m including handle; drawer 0.550 × 0.644 × 0.180 m including handle. Origins were checked on reimport.

Unreal materials, collision, hinges and drawer travel, repeated module seams and interaction clearance are not yet verified. The final front finish should be assessed in the final kitchen lighting; the rendered material color may require tuning beside the existing sink.
