# BA-BIN-01 — vintage bathroom pedal bin

Provisional Blender candidate for the A+ bathroom; not yet imported or tested in Unreal. `concepts/bin-multiview-states-v1.png` is the generated open/closed and front/back/side visual reference. The render is cleaner and has less edge wear than the generated concept; judge at scene scale against the bathroom tile and lighting.

The cylindrical bin has an actual hollow interior, a rear-hinged lid, fixed hinge hardware, and a separately pivoted pedal. Approximate closed body is 0.224 m diameter and 0.302 m high; with pedal its footprint is approximately 0.224 × 0.29 m. Blender uses metres, Z up, front toward −Y. The exports are closed pose:

- `model/Bin_body.fbx` has the floor-centred origin `(0, 0, 0)`.
- `model/Bin_lid.fbx` has hinge origin `(0, 0.119, 0.292)` relative to body; rotate around local X (preview uses −105°). Confirm FBX axis and origin conversion in Unreal.
- `model/Bin_pedal.fbx` has pivot `(0, −0.112, 0.028)` relative to body. Pedal and lid are separate meshes; there is no mechanical linkage or authored animation. Coordinate their animation in engine if needed.

`textures/enamel.png` is the earlier selected enamel from `KI-KETTLE-01`, and `textures/brass.png` is the muted brass from `LV-TABLE-LAMP-01`; copies are included for portable source. These are color textures, not physical paint displacement. Images are packed in the `.blend`. Recreate the ivory and brass material graphs in Unreal; verify UV seams, roughness, wear, open-lid clearance and collision in room. The preview ground and lights are not exported. No Unreal integration has been tested.

Build with `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_bin.py`; validate with the adjacent `validate_fbx.py`. The clean FBX round-trip checked finite coordinates, normals and UVs, UV layer presence, and nonzero geometry triangles. `model/validation.txt` records bounds and origins. `previews/bin-closed.png` and `previews/bin-open.png` show the two positions.
