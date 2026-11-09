# LV-FUSE-01 — vintage apartment fusebox

Reference: `concepts/fusebox-states-v1.png`. The generated `references/multiview-v1.png` is a guide, not a measured blueprint; front, back, sides and open perspective were reconciled to the shared dimensions below. The latest generated albedos are `textures/T_Fusebox_GrayGreen_Painterly_v2.png` and `textures/T_Fusebox_Ceramic_Painterly_v2.png`. A planar UV pass preserves medium-sized painted strokes across the door and shell. Earlier paint explorations remain in `textures/`.

## Dimensions and placement

Box body is 0.45 m wide, 0.58 m high and 0.14 m deep. The complete assembly including exposed cables is approximately 0.464 × 0.14 × 0.824 m. Source coordinates use metres, Z up, front toward −Y, wall at Y=0. The shell and both repair wires use origin (0, 0, 0) at the wall on the lower box edge. The door's origin is its left hinge axis at (−0.229, −0.14, 0); keep the door at that relative position when assembling. Rotate the door around its local Z axis, approximately −105° for the illustrated open pose. Test axis conversion and pivot on Unreal import before integrating.

## Contents and animation

- `LV_FUSE_01_Shell.fbx`: body, four fuse assemblies, screws, cable clamps, fixed hinge knuckles and fixed red/blue cables.
- `LV_FUSE_01_Door.fbx`: lid, latch and moving hinge knuckles. Closed at zero rotation.
- `LV_FUSE_01_Wire_Damaged.fbx` and `LV_FUSE_01_Wire_Repaired.fbx`: alternate cream-wire repair states sharing the shell origin. Display exactly one. The open damaged preview illustrates the reveal; the repaired preview illustrates the swap.
- `blender/LV-FUSE-01.blend` is the editable assembly. Three `previews/` PNGs show closed, damaged open, and repaired open states.

Regenerate with `/Applications/Blender.app/Contents/MacOS/Blender -b --python blender/build_fusebox.py` from this folder. Regeneration uses the existing generated painterly image, and writes the other two color textures, FBXs and previews. `blender/validate_exports.py` imports each FBX independently and checks finite positions and UVs, nonzero face areas and dimensions. On this build it passes all four files. The FBX includes copied texture references in its `.fbm` folder; assign matching material slots explicitly during Unreal import.

## Review status

Model and texture were iterated three times after the first preview: its regular generated marks were replaced by a richer painterly image, and overly wide bevels were fixed after round-trip validation found degenerate faces. The latest pass adds darker gray-green metal, flat irregular edge wear, an inset gasket, terminal posts and branch leads, and more hinge detail. The result is a stylized interpretation and still needs parent art review, in-engine material/lighting evaluation, collision and animation checks. It has not been imported or validated in Unreal. The image-generated textures were requested tileable; their seams have not been measured. The preview uses warm ambient light and is not a substitute for in-game lighting.
