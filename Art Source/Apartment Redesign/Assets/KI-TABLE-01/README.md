# KI-TABLE-01 — kitchen dining table

One vintage rounded-top table with a four-sided sage apron, four splayed tapered timber legs and separate underside corner blocks. Built against `concepts/table-v1.png` (which already contains front, back, sides, top and perspective), and `references/multiview-selected.png` retains that selected model sheet. Painted albedos were generated from the selected concept and are saved in `textures/` and packed into the Blender source.

- **Footprint / height:** 1.500 × 0.850 × approximately 0.730 m, floor origin; top is at 0.740 m. Z up, X along long side.
- **Materials:** `Table_Wood_Painted` and `Table_Sage_Painted`, image textures in sRGB, rough finish. The apron has no solid infill; the underside is modeled.
- **Interaction:** static table. The assembly has no animated elements. Chairs are separate assets.
- **Files:** `model/KI-TABLE-01.blend`, reproducible `model/build_table.py`, `model/KI_TABLE_01.fbx`, `model/validate_fbx.py`, and six `previews/`.
- **Validation:** FBX imported back in Blender: 778 vertices, 712 polygons, finite positions/normals/UVs, no degenerate polygons or triangulated faces, two materials, expected bounds. This does not test Unreal import, collision, appearance in scene lighting or walkability.

Build: `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_table.py`; validate with `-b --python model/validate_fbx.py`. The top is built as layered rounded rings with explicit triangle fans to avoid the degenerate bevel issue found in the prior dining-table asset. The rim is separately unwrapped along its perimeter; its UV seam and flush scuff material should be inspected in Unreal; tabletop albedo is image-based rather than physically raised paint.
