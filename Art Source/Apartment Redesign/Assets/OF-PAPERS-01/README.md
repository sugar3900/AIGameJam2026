# OF-PAPERS-01 — loose office papers

**Status:** Blender candidate for art review; not imported or tested in Unreal. This static dressing assembly for the office desk consists of five modeled, thin, slightly irregular sheets: two plain backing pages, a written page, a smaller letter and a sepia-toned postcard. Marks are abstract and not intended to convey legible story text. The postcard is a sepia paper treatment rather than the separately illustrated landscape in the concept; no folding or pickup animation is authored.

## Contents and art direction

- `concepts/papers-multiview-v1.png`: generated concept with top, side, front, back and three-quarter views. Its generated labels are not part of the actual asset.
- `textures/paper-candidate-a.png` and `paper-candidate-b.png`: two independently generated painterly paper/ink images. A was warmer and more mottled, so it is used only on the postcard; B is the lighter ivory selected for the written sheets. The two backing papers use a plain cream material. Color images are sRGB; brushwork is color, not displaced paint.
- `model/OF-PAPERS-01.blend`: editable source with packed images; `model/OF_PAPERS_01.fbx`: five meshes in one FBX. `model/build_papers.py` rebuilds source, export and previews; `model/validate_fbx.py` reimports the FBX. `previews/papers-perspective.png` and `papers-top.png` are Blender studio renders with a **preview-only desk**, not game lighting.

## Dimensions, axes and placement

Blender metres, +Z up; sheet layout lies in local X/Y with Z=0 at the tabletop plane and the common origin near its centre. Reimported total bounds are **0.26846 × 0.27808 × 0.00705 m**. The bottom sheet begins about 0.00065 m above the tabletop. Combine imported meshes while preserving assembly geometry, or retain their common transform; do not reset parts to individual corners. FBX uses `-Y` forward and `Z` up; verify axis conversion and scale on Unreal import, place the shared origin on the desk top (OF-DESK-01 desktop is about 0.757 m above floor), and avoid z-fighting.

The model contains `Paper_painterly_written`, `Postcard_painterly_sepia` and `Paper_clean_reverse` slots. Reconnect the two supplied texture files to the first two slots as color maps; Blender nodes do not automatically become Unreal materials. The third slot is muted cream, roughness 0.92. Check color and ink strength at actual camera distance and exposure. The paper is thin solid geometry with both faces; decorative collision can normally be disabled. Sheets share some texture imagery, and their tiny height separations should be checked for intersections and z-fighting in engine.

## Validation

Run from the repository root:

```sh
'/Applications/Blender.app/Contents/MacOS/Blender' --background --python 'Art Source/Apartment Redesign/Assets/OF-PAPERS-01/model/build_papers.py'
'/Applications/Blender.app/Contents/MacOS/Blender' --background --python 'Art Source/Apartment Redesign/Assets/OF-PAPERS-01/model/validate_fbx.py'
```

The latest clean Blender FBX round trip (see `model/validation.txt`) reported **5 meshes, 1,950 vertices, 3,880 triangles, zero degenerate geometry triangles, zero degenerate UV triangles, and no nonfinite coordinates or UVs**. This does not establish Unreal materials, desk contact, camera readability, collision, or performance.

Generated-image prompts: a multiview loose-paper sheet with painterly warm ivory and illegible marks based on `Art Source/Environment Concepts/painterly-fixer-upper.png`; candidate A requested warm aged cream fibers and abstract ink; independent candidate B requested lighter ivory paper with sparse abstract lines and a small botanical sketch. The apartment image was a style reference.
