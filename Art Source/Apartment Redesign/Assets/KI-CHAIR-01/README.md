# KI-CHAIR-01 — vintage dining chair

A warm walnut ladder-back chair with a rust-red padded seat, designed against `concepts/chair-v1.png`. The concept already includes front, rear, both sides and perspective, so no redundant modeling sheet was generated. `textures/wood-selected-v2.png` and `textures/vinyl.png` are independently generated base-color textures, with painted color variation rather than displacement.

- Source: `model/KI-CHAIR-01.blend`; reproducible script: `model/build_chair.py` (Blender background mode).
- Export: `model/KI_CHAIR_01.fbx`, one static mesh with walnut, vinyl and dark seam material slots. Origin at floor center; Z up; forward is -Y. Approximate bounds are 0.460 × 0.513 × 0.898 m, seat top 0.50 m.
- `previews/` contains the three-quarter and four orthographic views. The cushion and curved wood are smooth shaded; texture variation is color-only.
- Validation: `Blender -b --python model/validate_fbx.py` reimported the FBX and reported 4,868 vertices, 9,516 triangles, finite vertex positions, normals and UVs, and zero degenerate triangles.

Unreal import, material reconstruction, collision, scale and final lighting remain untested. Custom wood UVs align grain with each rail/post; texture seams should still be inspected in context. The seat piping is static trim, not an animation.

## Texture review

Two fresh wood directions, `wood-candidate-a.png` and `wood-candidate-b.png`, were generated independently. A was selected for its broad clean directional grain and scattered color accents; B has an artificial painted border that would repeat along the chair. V2 aligns wood texture along the length of the slats and posts and adds rounded caps and small joint pegs. `wood.png` remains the first-pass reference.
