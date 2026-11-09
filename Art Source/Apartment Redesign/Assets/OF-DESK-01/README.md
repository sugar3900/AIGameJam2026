# OF-DESK-01 — vintage writing desk

A 1.75 m × 0.60 m desk with a 0.757 m top, turned legs, aged brass pulls and three independently sliding drawers. Z is up, front is −Y, and the body and each drawer have their origins at the same floor-level assembly origin. A drawer slides along local −Y; the open review shows 0.26 m travel. The AI concept already contains front, back, sides, perspective and open-state views and is copied into `references/`.

The original wood map read too streaked in renders, so two independent fresh candidates were generated. `desk-walnut-v2-expressive.png` was selected for its broader painted color variation; the first and subtler third maps remain alongside it for comparison. The desktop has an explicit physically scaled planar UV projection to keep strokes from stretching. This remains a preliminary art pass and should be judged in final Unreal lighting.

- `model/build_desk.py` builds and renders the asset in headless Blender.
- `model/OF-DESK-01.blend` is the editable source with packed texture.
- `model/OF_DESK_BODY.fbx` and `OF_DESK_DRAWER_1–3.fbx` are separate static mesh exports.
- `previews/desk-closed.png` and `desk-open.png` show the assembly and center drawer.
- `model/validate_fbx.py` reimports each FBX and tests finite vertices, normals and UVs plus zero-area polygons and triangles. All four passed.

Unreal materials, drawer transform, lighting, collision and passage with drawers open have not been verified. The texture candidates are generated albedo images; the color variation is not modeled raised paint.
