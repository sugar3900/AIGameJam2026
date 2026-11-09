# ARC-DOOR-01: five-panel room door

Reusable 1930s-style painted interior room door and double-faced casing. The concept is in `concepts/` and a generated multiview study is in `references/`; the mesh is modeled from those and the A+ opening dimensions rather than relying on inconsistent concept-sheet projection. Studio previews show closed, open, front, back and side.

## Source and measurements

- Editable source: `model/ARC-DOOR-01.blend`; reproducible generator: `model/build_door.py` (Blender 5.2.3).
- Opening: 0.90 m clear width × 2.11 m clear height. Leaf slab: 0.886 × 0.042 × 2.094 m. Assembled casing extends approximately 1.12 × 0.182 × 2.219 m. The complete leaf including knobs and hinges measures approximately 0.90 × 0.178 × 2.094 m.
- Frame and leaf exports are separate. `ARC_Door_Frame.fbx` has a floor-center origin. `ARC_Door_Leaf.fbx` has its origin at the hinge axis at floor height; in Blender coordinates place this leaf at (-0.45, 0, 0) relative to the centered frame before applying the opening rotation. Frame and leaf use metres, Z up, with the closed door spanning X. Account for Unreal's axis conversion and FBX import settings rather than assuming the signs transfer unchanged.
- Each face has five raised-frame panels and a brass knob/escutcheon; three hinge barrels are included with the moving leaf. Pivot positioning and a visual 80° swing were verified in Blender. Validate Unreal pivot conversion, swing, hit collision and clearance against the actual wall, player, camera and furniture; mirror/handed placements require special care.

## Materials and texture

`textures/paint-A.png` and `paint-B.png` are two independently generated warm ivory paint candidates. B was selected for its less directional, softly varied brushwork; the selected image is `paint-selected.png`. The Blender material mixes it at 65% with a warm neutral color at 35%, then uses a rough surface. A small number of thin wood-colored edge rubs and a separate muted metallic brass material provide restrained wear. Texture size and lighting in an assembled room may make brushwork less visible; review the final material under Unreal game lighting.

FBX does not preserve the Blender node graph reliably. Recreate the paint color mix, roughness and aged brass material in Unreal; assign the exported material slots, and inspect both faces. The image is UV mapped on the modeled components, not a certified seamless wall material.

## Validation

`model/validate_fbx.py` reimports both FBXs and checks finite vertices, normals and UVs, UV presence and nonzero triangle areas. `model/validate_pivot.py` reimports the leaf and asserts the hinge origin and extent. Both passed in Blender; leaf 8,576 triangles, frame 1,512. That original source-validation pass did not test Unreal import, runtime interaction, animation, collision or assembled-room fit. See the dated integration findings below for subsequent engine feedback.

## Integration feedback — 2026-11-08

The integration team reports jamb linings coincided with the wall cut and caused z-fighting. For the current unscaled frame, allow **rough-opening width = clear width + 6 cm** (3 cm per side), with the rough header at **214 cm above floor**. For the 90 cm clear-width kit this is a 96 cm wall cut. The casings cover the allowance. The team corrected the walls; no source geometry change is requested. New-width layout proposals must reconcile the frame/leaf dimensions separately rather than assuming this existing kit matches them.

The existing FBX has no authored simple collision. The integration team applied complex-as-simple collision to the current imports; re-run `Tools/Editor/build_redesign_collision.py` after re-import. Future moving leaves/panels should include separately named convex `UCX_<render mesh name>_<index>` collision hulls, following the moving part and its pivot. These hulls have not been added by this documentation update.
