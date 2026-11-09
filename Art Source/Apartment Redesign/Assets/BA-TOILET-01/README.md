# BA-TOILET-01

Vintage floor-mounted porcelain toilet, front faces −Y, Blender metres / Z up. The input concept already contains front, back, side, perspective, and open/closed views. The model includes a hollow bowl, oval fixed seat, cistern, brass flush lever, porcelain base, and separate pivoted lid.

## Files and build

- `model/build_toilet.py` builds `model/BA-TOILET-01.blend`, `BA_ToiletBody.fbx`, `BA_ToiletLid.fbx`, and two preview renders. Run with `/Applications/Blender.app/Contents/MacOS/Blender -b --python <script>`.
- `model/validate_fbx.py` imports both exports and checks finite positions/UVs, UV presence and zero-area triangles.
- `textures/porcelain-candidate-a.png`, `-b.png`, `-c.png` and `-d.png` are independent generated candidates; D was selected for broader warm/cool strokes. The source PNG feeds Blender base color directly, and brass is a separate material slot.
- `previews/toilet-closed.png` and `previews/toilet-open.png` show the modeled states.

## Placement and pivots

The body FBX has its origin on the floor. It measures approximately 0.578 × 0.713 × 0.924 m. The lid FBX pivot is at `(0, 0.125, 0.505)` in the assembled Blender scene; animate it around local X from 0 to **−68°**. That pose clears the cistern in a vertex-bound check and avoids the visibly intersecting 90° pose. The oval seat is fixed; only the cover moves. The floor bolts project slightly beyond the ceramic base.

## Checks and remaining review

Both FBX round trips passed Blender finite-position/UV and degenerate-triangle checks. At −68° no lid vertices were found within the cistern bounding region. The design was revised twice: a rounded cistern and lid, porcelain trap contours and a new independently generated finish were added after the first review; the raised lid clears the cistern in the bounds check. Unreal material setup, import/reload warnings, collision, hinge pivot and scene lighting have not been tested. Its finish still needs an in-room review against the richer painterly concept.
