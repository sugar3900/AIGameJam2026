# OF-CABINET-01 — office storage cabinet

An old shallow wooden cabinet for the office west wall, distinct from the open low bookcase. The generated `concepts/cabinet-open-closed-multiview.png` supplies the open/closed and front/side/back views; the model follows its paneled doors, drop pulls and plinth while adhering to the plan footprint. It adapts the separately authored HA-CABINET-01 construction and the LV-CHEST-01 muted walnut candidate, with a solid plinth and different proportions.

## Dimensions and use

Closed assembled FBXs reimport to **0.750 × 0.300 × 0.7195 m** including hardware. The plan placement is the office west wall approximately x=8.05–8.35, y=5.96–6.71 m; rotate so the front faces into the room. Leave room for trim and actual capsule/camera clearance. Opening doors and the drawer extends substantially beyond the closed 0.30 m footprint; test door sweeps and the 0.16 m drawer travel in engine.

All parts use metres, Z up, front −Y. `model/OF_CABINET_BODY.fbx` and `OF_CABINET_DRAWER.fbx` share the floor-centered origin. The drawer slides 0.16 m in local −Y in the open preview. `OF_CABINET_DOOR_L.fbx` and `OF_CABINET_DOOR_R.fbx` export from the closed pose with hinge origins at respectively **(−0.34191, −0.13095, 0)** and **(+0.34191, −0.13095, 0)** metres relative to the body origin. Preview opens them by −75° and +75° around local Z. Reassemble and verify axis conversion and collisions in Unreal. Doors expose an actual shelf and the drawer is a hollow box.

## Materials and checks

`textures/walnut-muted-b.png` is an independently generated LV-CHEST-01 wood candidate reused for visual consistency. Blender mixes the image through HSV saturation 0.68 and value 1.35, roughness 0.84; hardware is aged brass. Recreate this finish in Unreal; FBX does not transfer Blender's material nodes. Texture variation is painted color, not physical impasto. Studio previews use illustrative lighting, and the artwork, material, collision, movement and fit remain untested in Unreal.

`model/OF-CABINET-01.blend` is the editable source; `model/build_cabinet.py` rebuilds it and the four separate FBXs and open/closed previews. `model/validate_fbx.py` reimports each FBX and checks finite vertex/normals/UV values, UV presence and zero-area faces and triangles; `model/check_assembly.py` checks the door hinge origins and assembled bounds. Both checks passed with Blender 5.2.3; their results are saved in `model/validation.txt` and `model/assembly-validation.txt`. The assembly must still be reviewed in its final room lighting.
