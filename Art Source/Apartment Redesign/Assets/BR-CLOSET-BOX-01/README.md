# BR-CLOSET-BOX-01 — fabric-covered closet box

Provisional Blender prop for the A+ bedroom closet, awaiting lead review and Unreal assessment. It is a small sage linen-covered storage box with a removable shallow lid, hollow interior, ivory binding, subtle front stitches and a blank label. Reuse it twice if the final placement leaves Malcolm's standing space, closet doorway, mold sightline and dialogue camera unobstructed; no low shelf is included. The box is dressing and does not replace the closet's single dangling bulb or its repair state.

## Contents and construction

- `concepts/box-open-closed-multiview.png`: selected coherent open/closed and front/back/side concept, generated with the built-in image tool from the painterly-fixer-upper reference.
- `textures/sage-linen.png`: original generated painterly sage fabric color texture; it is a color map, not physical paint displacement. Binding, lining, blank paper and brass use Blender material colors. The generated fabric is not proven tileable; its image is mapped per face with no promised seamless wrapping.
- `model/BR-CLOSET-BOX-01.blend` and `model/build_box.py`: editable source and reproducible headless build.
- `model/BR_BOX_BODY.fbx`, `model/BR_BOX_LID.fbx`: separate closed-pose parts with no baked animation. `previews/box-closed.png` and `box-open.png` show the closed and lifted-lid poses; the open lid is a presentation pose, not a hinge.

Body bounds are **0.295 × 0.2457 × 0.1505 m**, lid bounds **0.300 × 0.2527 × 0.029 m**; closed assembly top is about 0.181 m above the floor. The body origin is at the floor centre `(0,0,0)`, the lid origin is `(0,0,0.155)` m relative to the body, with Blender **+Z up, −Y front, +X across the width**. Both exported FBX transforms retain those locations in the Blender round trip; confirm axis conversion and pivot handling in Unreal. The lid is lifted/translated, not rotated as a hinge; if animated, its separate origin is near its underside. Set collision and placement in the engine rather than relying on model geometry.

To rebuild, run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_box.py` from this folder. Run `Blender -b --python-exit-code 1 --python model/validate_fbx.py` to reimport. Both FBXs passed finite vertex/UV, UV-presence, nonzero geometry and UV triangle checks: body **3,976 vertices / 7,668 triangles**, lid **2,128 vertices / 4,104 triangles**. It verifies dimensions and reports origins; Unreal import and in-closet appearance, collision, shelf fit, interaction and motion remain untested.

## Generation prompts

Built-in image generation was used with the painterly-fixer-upper scene as a style reference. Concept prompt: “A modest old rectangular fabric-covered closet storage box with a removable shallow lid, approximately 30 × 25 × 18 cm, muted faded olive-sage cloth, ivory stitched edging and a blank aged paper label holder; same object in open/closed three-quarter and front/back/side views, inviting and gently worn, painterly rendering.” Texture prompt: “Flat square close-up of old olive-sage woven linen, subtle fibers and broad soft painterly variation, gently faded, no seam, object, text or lighting gradient.”
