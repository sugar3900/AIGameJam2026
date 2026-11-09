# ARC-SLIDING-CLOSET-01 — bypass closet front

Reusable coat/office closet front for the A+ plan. This is **not** the bedroom's hinged mold closet. The generated concept sheet includes closed, open and perspective reference views. The construction follows the plan rather than any inconsistent dimensions in concept art.

## Dimensions and motion

- Nominal opening: **0.90 m wide × 2.15 m high** between jambs. Overall cap width 1.08 m, height ~2.26 m, casing depth ~0.18 m. Fit a cutout and casing to actual wall thickness; the office elevation also shows a 1.05 m wide alternate and must be reconciled in the room.
- Left and right panels each span 0.46 m × 2.105 m. They overlap 0.02 m when closed. Panel body thickness 0.024 m; face mouldings project 0.006 m.
- Parallel front/back panel track centres are at y = -0.028/+0.028 m; they are separate and do not rotate. To open the left side, slide the left/front panel **+0.44 m in local X** in front of the right panel. Or slide the right/back panel **-0.44 m in local X** behind the left panel. This reveals approximately **0.44 m**, not the full 0.90 m clear frame width. This is a bypass wardrobe opening, not a person-sized doorway. Verify collision and reach for its intended storage use in game.
- Each panel has a recessed-looking pull with separate brass and dark inset details. The recess is a visual assembly on the face, not a boolean cavity.

## Contents and export

- `concepts/closet-multiview-open-closed.png` — generated design/reference sheet.
- `model/ARC-SLIDING-CLOSET-01.blend` — editable source, closed state.
- `model/ARC_Sliding_Frame.fbx`, `ARC_Sliding_LeftPanel.fbx`, `ARC_Sliding_RightPanel.fbx` — separate parts. Blender source has floor-centred frame origin `(0,0,0)`, and panel origins `(-0.22,-0.028,0)` and `(0.22,0.028,0)` metres relative to the frame. Each exported FBX was zeroed at its own origin; reassemble using these relative offsets, checking FBX axis conversion and scale in Unreal before animating local X. One Blender metre = 100 cm.
- `textures/ivory-paint-reused.png` — approved room-door candidate reused for a consistent architectural family. Blender mixes the image 65% with a warm ivory color 35%, with rough paint; FBX does not transfer the Blender node graph, so recreate it in Unreal. Separate muted brass, inset dark and track materials require equivalents.
- `previews/` contains front/back and open/closed studio renders; the solid panel faces use applied field mouldings rather than intersecting raised rails. Black background is transparency, not a closet interior. Add the room's actual interior, casing, wall opening and lights during assembly.
- `model/build.py` regenerates source, FBXs and previews; `validate.py` checks reimported meshes, UVs, finite vertices and non-zero faces.

## Integration checks

Verify open/closed travel in Unreal after importing parts and assigning materials; use a frame-root actor and children at the offsets above, preserving panel track depth. Set reasonable panel collision, avoid frame-wall collision in the aperture, validate that the slide cannot extend beyond the jamb, and test both the hall and office placements with their adjacent walls and trim. Rendered studio lights and transparent background are not included in the exports. The original source-validation pass did not test in-engine appearance, collision, track motion or the narrower-than-person opening. See the dated integration findings below for subsequent engine feedback.

## Integration feedback — 2026-11-08

The integration team reports jamb linings coincided with the wall cut and caused z-fighting. For the current unscaled frame, allow **rough-opening width = clear width + 6 cm** (3 cm per side), with the rough header at **218 cm above floor**. For the 90 cm clear-width kit this is a 96 cm wall cut. The casings cover the allowance. The team corrected the walls; no source geometry change is requested. New-width layout proposals must reconcile the frame/leaf dimensions separately rather than assuming this existing kit matches them.

The existing FBX has no authored simple collision. The integration team applied complex-as-simple collision to the current imports; re-run `Tools/Editor/build_redesign_collision.py` after re-import. Future moving leaves/panels should include separately named convex `UCX_<render mesh name>_<index>` collision hulls, following the moving part and its pivot. These hulls have not been added by this documentation update.
