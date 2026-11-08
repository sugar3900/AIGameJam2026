# BA-SWITCH-01 — bathroom wall switch

Status: **ready for parent visual review; Unreal import and interaction untested.** This is a warm ivory ceramic switch plate with aged-brass screws/collar and a separately moving toggle, for `P-BA-SWITCH` in the A+ bathroom. The multiview/on-off concept is `concepts/switch-multiview-on-off-v1.png`; the model has a restrained stylized finish rather than heavy physical paint.

## Geometry, pivots and states

Blender uses metres, +Z up, wall surface Y=0, front facing −Y. Plate dimensions are **0.100 × 0.010 × 0.120 m**, excluding the collar. `model/BA_Switch_Plate.fbx` contains the plate, two slotted brass fasteners, collar and rear housing; its origin is the wall-plane centre `(0,0,0)`. The rear housing projects **6.5 mm behind the wall plane**; allow a recess or hide that back portion in the wall and avoid z-fighting.

`model/BA_Switch_Toggle.fbx` is exported in the **neutral** pose with its origin at `(0,-0.014,0)` m relative to the plate origin, at the center of the collar. Its neutral ivory lever projects toward −Y. In Blender the preview rotates this part about its local X axis: **+28° is down/off and −28° is up/on**. The FBX contains geometry and pivot only, not keyframes, light linkage or gameplay. Place the plate at the wall and assemble the toggle using the documented relative pivot; verify FBX transform/axis conversion, rotation signs, collision and wall placement in Unreal. Connect the switch interaction to the actual bathroom fixture and persisted light state if that is desired; it is not implemented here.

The source `model/BA-SWITCH-01.blend` includes a preview wall, camera and studio lights; they are not in the two selected FBXs. `previews/switch-off.png` and `switch-on.png` show the two geometric poses. Studio renders are not final game lighting.

## Materials and provenance

`textures/ivory-ceramic.png` is copied from `KI-MUG-01`; `textures/enamel-brush.png` is copied from `KI-KETTLE-01` and blended **32%** over ivory in Blender to give restrained painted color variation. `textures/aged-brass.png` is copied from `HA-SCONCE-01`. These are color textures; there is no modeled impasto. The plate and lever are restrained and may read smooth at game distance. Recreate the two-texture ceramic mix and brass metallic/roughness in Unreal; FBX does not automatically reproduce Blender's material nodes. Check seams, patina and roughness in the actual bathroom.

Concept generated using the built-in imagegen tool, with `painterly-fixer-upper.png` as a style reference. Prompt: “Design one vintage 1930s bathroom wall light switch matching the warm painterly fixer-upper apartment style: 10 by 12 cm gently aged warm ivory rectangular ceramic plate, rounded bevel, two small slotted patinated brass screws and one short ivory toggle on a brass collar. Show the same switch in front, side, back and three-quarter views and clear on/off toggle positions; neutral background, no lettering, no people.” The generated sheet includes labels despite the prompt; they are not part of the model or game UI.

## Verification

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/BA-SWITCH-01/model/build_switch.py'` from the worktree root to rebuild. `model/validate_fbx.py` reimports both FBXs in clean Blender scenes and checks finite vertices/UVs, UV presence and nonzero triangle area; `model/validation.txt` records the latest run, including the plate and toggle origins. Both passed. Unreal material, transforms, collision, placement, animation and interaction remain untested.
