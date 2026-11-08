# BA-TIN-01 — vintage bathroom toiletries tin

Status: **Blender candidate for lead and Unreal review**, not an integrated game asset. `concepts/tin-multiview-v1.png` is the generated open/closed six-view concept; `textures/tin-floral.png` is a separately generated painterly enamel/floral color texture. `textures/ivory-enamel.png` is the reviewed kettle enamel texture reused to coordinate the room. The floral detail is UV-mapped directly onto the body front and lid top, not an overlaid geometry decal. The generated floral and kettle texture colors differ slightly at the front-to-side edge; assess under room lighting.

## Geometry and assembly

- `model/BA-TIN-01.blend` is the editable master, with `model/build_tin.py` as its reproducible headless builder. The hollow, open-topped body, bottom, sides and fine rolled rim are one export; fitted lid is a separate lift-off export. The lid is not hinged; there is no authored animation.
- `model/BA_Tin_Body.fbx`: 0.121 × 0.091 × 0.1435 m including rim. The body origin is at the tabletop center. `model/BA_Tin_Lid.fbx`: 0.120 × 0.090 × 0.0135 m, with origin at the closed seating datum `(0, 0, 0.145)` m relative to the body. At closed state assemble those origins at the documented relative positions; verify the FBX import transforms rather than zeroing both components indiscriminately.
- Blender uses metres, Z up, front −Y and X across width; exports specify FBX **−Y forward / Z up**. Verify axis, units and relative origins in Unreal. Lid top reaches approximately 0.158 m. The preview's lifted lid is an illustrative pose, not an included animation.

## Material and validation

The body uses a warm enamel texture on side faces, a separate floral image on the large front surface, dark aged rim and a warm interior material. Lid top uses the floral image; underside and edges use enamel. Recreate these material slots from the supplied color maps and the source Blender materials in Unreal; FBX does not transfer Blender's material graph. Use high roughness with restrained metallic response, check edge joins and the floral tint across surfaces, and use appropriate simplified collision if the tin is interactive.

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/BA-TIN-01/model/build_tin.py'` from the worktree root. `model/validate_fbx.py` cleanly reimports each FBX and tests finite geometry and UV coordinates, UV presence and nonzero geometry triangle areas; results are in `model/validation.txt`. The body has 864 vertices / 1,692 triangles and the lid 576 vertices / 1,128 triangles on that check. `previews/tin-closed.png` and `previews/tin-open.png` are studio renders, not Unreal screenshots. Unreal materials, collision, lid movement, shelf placement and in-room appearance remain untested.
