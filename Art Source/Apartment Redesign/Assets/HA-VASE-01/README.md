# HA-VASE-01 — hall console vase

Status: modeled Blender candidate for art-lead review; not imported into Unreal. This is the small glazed vase intended for the hall console. The [multiview design](concepts/vase-multiview-v1.png) establishes its bulbous, short-necked silhouette and hand-painted rose; generated views are visual guidance, not a dimensional blueprint.

## Contents and dimensions

- `model/HA-VASE-01.blend`: editable Blender source. `model/HA_VASE_01.fbx`: one static mesh including the continuous outer and inner ceramic shell and solid foot.
- `textures/vase-ivory-floral.png`: independently generated painterly ivory glaze with a single rose motif; this is a full cylindrical albedo, not a seamless repeating material. `previews/vase-three-quarter.png` and `vase-front.png` are neutral studio renders, not in-game screenshots.
- Overall bounds are **0.240 × 0.180 × 0.258 m**. Coordinates in Blender are metres with **+Z up**, the vase's front toward **−Y** and the origin at its tabletop-level centre. The vertically elongated rose is baked into the texture; rotate the vase as a whole to face the hall camera.
- The open mouth has modeled inner walls and an inner bottom approximately 0.028 m above the base. The model contains no flowers or stems. The vase is static, with no authored animation.

## Unreal handoff

Import the FBX as a static mesh, confirm axis conversion and 100 cm per metre, and place its base on the console surface. Reconnect the albedo as an sRGB base-color texture, metallic 0 and approximately 0.48 roughness as a starting point; Blender's Principled nodes and lighting do not transfer automatically. The generated glaze is subtle and can appear too white under bright lighting, so tune in the assembled hall. Inspect the rear UV seam and contact shadows; the seam is not proven mathematically seamless. Use a simple collision proxy or no decorative collision, rather than relying on generated collision inside the narrow open mouth. Test in-room scale, placement and texture against the finished console and lighting.

## Rebuild and validation

Run `Blender -b --python model/build_vase.py` to regenerate the model, FBX and studio previews, or `Blender -b --python model/validate_fbx.py` for a fresh FBX reimport check. `model/validation.txt` records finite vertices, UVs, nondegenerate triangles and UV triangles, expected dimensions, and a downward ray reaching the inner base through the open mouth. These checks do not validate Unreal import, materials, collision or room lighting.
