# ARC-ENTRY-DOOR-01 — hall entry door

Solid vintage four-panel walnut door with cream period casing and aged brass hardware. The [concept sheet](concepts/entry-door-multiview.png) shows front/back/profile and open position; the model is a stylized interpretation, with real slab thickness and applied mouldings on both faces. Walnut texture is reused from `OF-DAYBED-01` for continuity; the ivory casing texture comes from `ARC-DOOR-01`.

## Contents and dimensions

- Editable Blender scene and reproducible script in `model/`, with closed/open and front/back/side renders in `previews/`.
- `ARC_Entry_Door_Frame.fbx`: fixed jamb, paired casings and hinge plates; overall 1.12 × 0.182 × 2.219 m, including crown. Nominal opening between jambs is 0.90 m.
- `ARC_Entry_Door_Leaf.fbx`: solid 0.886 × 0.050 × 2.094 m leaf before mouldings, projecting knobs and hinge barrels; full FBX bounds 0.900 × 0.188 × 2.094 m including hardware. Hinge origin is on the left at floor level. FBXs export each mesh at its own origin; put the leaf origin at the frame's left hinge at x = −0.45 m in Blender-space assembly, converting axes as needed in Unreal. Model local front is negative Y.
- A peephole, deadbolt, knobs and escutcheons are on both faces. They are static with the leaf; no independently animated lock mechanism is supplied.

## Engine assembly

The A+ plan places the entry on the east wall, and the leaf should open **outward toward the landing**. The landing is not designed yet: validate the hinge side, swing direction, full swing clearance, structural opening, exterior collision, player capsule and camera with the actual level before enabling the door. Do not assume the preview's camera orientation defines world orientation. Set up the moving door actor with the leaf's hinge as pivot and select rotation sign based on the placed orientation.

FBX does not reliably transfer Blender node graphs. Recreate the material using `textures/walnut-aged.png` for the leaf, `textures/paint-selected.png` blended toward warm ivory for the frame, and a muted brass material for hardware. See `build_entry.py` for values. Assign collision separately to fixed frame and moving leaf; check UV grain direction and material appearance under game lighting. Door exterior/landing materials and hardware interaction remain untested.

## Validation

Blender 5.2.3 LTS FBX reimport: both meshes have UVs, finite coordinates/normals/UVs, no degenerate triangles. The frame has 1,512 triangles and the leaf 6,352; `validate_pivot.py` confirms the leaf FBX origin is at the hinge and its hinge-relative x bounds are −0.007 to 0.893 m. Preview demonstrates an 80° rotation. That original source-validation pass did not test Unreal import, material fidelity, collision or in-engine swing. See the dated integration findings below for subsequent engine feedback.

## Integration feedback — 2026-11-08

The integration team reports jamb linings coincided with the wall cut and caused z-fighting. For the current unscaled frame, allow **rough-opening width = clear width + 6 cm** (3 cm per side), with the rough header at **214 cm above floor**. For the 90 cm clear-width kit this is a 96 cm wall cut. The casings cover the allowance. The team corrected the walls; no source geometry change is requested. New-width layout proposals must reconcile the frame/leaf dimensions separately rather than assuming this existing kit matches them.

The existing FBX has no authored simple collision. The integration team applied complex-as-simple collision to the current imports; re-run `Tools/Editor/build_redesign_collision.py` after re-import. Future moving leaves/panels should include separately named convex `UCX_<render mesh name>_<index>` collision hulls, following the moving part and its pivot. These hulls have not been added by this documentation update.
