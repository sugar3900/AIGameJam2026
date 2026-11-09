# LV-SIDE-TABLE-01 — living-room end table

A petite 0.37 × 0.351 × 0.54 m vintage wood table for the living room's table lamp. The top measures 0.37 × 0.35 m; the companion `LV-TABLE-LAMP-01` shade is approximately 0.287 m wide. Verify the lamp's base, placement and the drawer's approach clearance in the actual room. The modeled front apron has a gently shaped profile, with tapered square legs, a shelf, and a separate drawer.

## References and materials

`concepts/side-table-multiview-v1.png` is the original generated open/closed multiview design, and the warm muted painterly wood texture in `textures/walnut-muted-b.png` is reused from the reviewed living chest/nightstand to maintain a cohesive material palette. The source material desaturates this texture to 0.68 and raises its value to 1.35; replicate or bake that correction in Unreal. Thin edge-rub geometry and a muted brass knob are separate material slots. The drawer interior mixes the texture with a lighter wood color; Blender shader nodes do not automatically transfer through FBX.

## Exports and motion

`model/LV-SIDE-TABLE-01.blend` is the editable source. `model/LV_SIDE_TABLE_BODY.fbx` and `model/LV_SIDE_TABLE_DRAWER.fbx` share a floor-center origin in the closed pose. The drawer can translate 0.18 m towards local −Y; `previews/side-table-open.png` shows this test pose, while `side-table-closed.png` shows its fitted resting position. Test axis conversion, collision, door/drawer clearance, and animation in Unreal; no interaction or engine import is implemented here.

Rebuild with `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_side_table.py`; reimport-check with `-b --python model/validate_fbx.py`. The two FBXs passed finite position and UV checks, UV presence, nonzero triangle area and origin checks. The body reimported at 0.370 × 0.3506 × 0.540 m including small edge marks. The model is provisionally ready for room-level art review; materials, lighting, collision and Unreal behavior remain untested.
