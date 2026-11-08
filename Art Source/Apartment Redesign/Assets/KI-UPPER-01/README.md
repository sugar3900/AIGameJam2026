# KI-UPPER-01 — vintage upper cupboard

Small wall-mounted two-door cupboard with recessed panels, ivory knobs, aged brass hinges, one middle shelf and a warm wood interior. Added edge rubs and side-panel/crown beading echo the revised pantry. The [open/closed and multiview concept](concepts/upper-open-closed-multiview.png) guides the appearance; plan dimensions control construction. Shelf contents are separate dressing assets.

## Placement and movement

The **body** bounds are 1.000 m wide × 0.3235 m deep × 0.5455 m high. The door-front trim and knobs project roughly 0.04 m beyond the body front. Local +X is across the width, **−Y is the front**, and +Z is up; body origin is its bottom centre. The A+ kitchen elevation places the cupboard on the north wall beside the window. Check the final wall opening, adjacent cabinet and door swing in the engine layout before fixing its exact elevation.

Left and right leaf origins relative to the body are `(−0.470, −0.165, 0.265)` m and `(0.470, −0.165, 0.265)` m. Open left by −100° and right by +100° around local Z for the illustrated pose. Each door has its own hinge-axis origin and includes its knobs and hinge detail. No animation, collision, mounting logic or interaction is encoded in the FBX; recheck origin conversion, rotation signs, wall clearance and movement in Unreal.

## Files and materials

`model/KI-UPPER-01.blend` is the editable closed assembly. `model/build_upper.py` recreates the source, `KI_Upper_Body.fbx`, `KI_Upper_LeftDoor.fbx`, `KI_Upper_RightDoor.fbx`, and open/closed previews. Materials reuse the existing pantry's independently generated candidates for continuity: `textures/sage-B.png` mixed with 28% `sage-A.png`; `interior-wood.png` mixed 48% toward linear RGB `(0.36, 0.26, 0.18)`. Brass, ivory and localized rubbed wood have separate material slots. These are base-color textures; recreate the blend, roughness and metalness in Unreal. Blender shader nodes do not transfer automatically.

Blender 5.2.3 FBX reimport with `model/validate_fbx.py` passed: body 2,700 triangles and 1.000 × 0.3235 × 0.5455 m, left and right leaf 2,520 triangles each, finite geometry/normals/UVs, no degenerate triangles and expected hinge origins. **Unreal materials, collision, wall placement, door animation and in-room appearance are untested.**
