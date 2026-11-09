# OF-DAYBED-01 — vintage daybed

A walnut spindle daybed with ivory mattress, floral draped quilt and two cushions. The concept sheet supplies front, back, end and perspective references. The modeled assembly measures 1.85 × 0.77 × 0.83 m in Blender, consistent with the approximately 1.9 × 0.8 m footprint. Front is −Y and the pillow end is +X.

`model/OF_DAYBED_Source.blend` is the editable scene; `build_daybed.py` rebuilds it. FBX exports include a complete assembly and separate frame and bedding. Use either the assembly or the two parts together. The quilt is modeled with fixed draping; there are no interaction animations. Textures are in `textures/`; the floral quilt is generated for this asset, and the aged walnut is a new generated texture; an independent unused alternative is retained as walnut-alternate.png. Ivory linen and rose knit are shared copies from BR-BED-01. The preview is a neutral studio render, not an Unreal screenshot.

`model/validation.txt` records an independent Blender reimport of each FBX, checking finite vertex positions and UV values, UV layer presence, zero-area triangles and dimensions. Unreal import, material assignment, collision and in-game lighting have not been checked.
