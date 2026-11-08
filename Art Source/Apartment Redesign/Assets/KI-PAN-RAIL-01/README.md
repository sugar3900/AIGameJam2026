# KI-PAN-RAIL-01 — kitchen pan rail

Status: Blender candidate for visual review; Unreal materials, mounting, collision and hanging placement remain untested. `concepts/pan-rail-multiview-v1.png` is the generated five-view target; `previews/rail-perspective.png` and `rail-front.png` show the modeled rail. Blender source and repeatable scripts are in `model/`.

## Dimensions, placement and exports

Blender is in metres, Z up; X runs along the rail, the wall is at Y=0, and the rail projects toward −Y. The shared origin is on the wall at rail centre height. The assembly is approximately 0.592 m wide × 0.067 m maximum projection × 0.105 m high, with four static S-hooks at X = −0.225, −0.075, +0.075 and +0.225 m. Wall mounting plates are at X = ±0.270 m. Rotate and translate the entire assembly to the kitchen wall; check the real wall, cabinetry and countertop positions. The 0.067 m projection exceeds the inventory's schematic 0.04 m depth.

`KI_Pan_Rail_Assembly.fbx` contains the complete rail and hooks. `KI_Pan_Rail_Body.fbx` and `KI_Pan_Rail_Hooks.fbx` are alternatives for separate placement; do not add them on top of the complete assembly. All exports share the wall-centre origin; the hooks are one group and have no authored animation. The preview wall and lights are not exported.

The two outside hooks are 0.45 m apart, so two `KI-PAN-01` bowls of 0.26 m diameter have approximately 0.19 m horizontal separation in an ideal aligned hanging pose. The hook rod is approximately 5.6 mm in diameter and the pan handle's through-hole is 12 mm in diameter; actual installation is not proven by these nominal figures. The pan is 0.483 m long overall; allow at least that much space below its suspension point and check hooks, wall, range, heat, counters, viewing angle and pan orientation with the actual exported meshes in the assembled kitchen. The two centre hooks should not also carry full-size pans at the same height unless overlaps are resolved.

## Materials and validation

`textures/iron.png` is copied from the painterly `KI-PAN-01` iron material; `textures/brass-patina.png` is the reviewed `HA-HOOKS-01` aged-brass candidate. The Blender material mixes iron at 55% and brass at 45%, with metallic 0.32 and roughness 0.70; recreate this material in Unreal because the FBX does not reproduce Blender shader graphs. The finish is muted and retains the pan's shared visual language; inspect it under the actual kitchen lighting.

Rebuild using `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_rail.py`; validate using the same Blender executable with `-b --python model/validate_fbx.py`. The validator reimports each export and checks finite geometry and UV coordinates, present UV layers, nonzero geometry-triangle area and assembly bounds. Consult `model/validation.txt` for the recorded run. This does not establish Unreal UV/material transfer, hook physics, pan collision, visual tangencies or gameplay behavior.
