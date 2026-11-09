# HA-FLOWERS-01 — dried floral stems

Provisional model for art-lead review, not imported into Unreal. `concepts/flowers-multiview-v1.png` is an independently generated painterly multi-view design reference. `textures/petals-painterly.png` is a separately generated rose-petal base-color texture; all brushwork is color, not physical paint relief. `previews/flowers-in-vase.png` shows the bunch against the existing `HA-VASE-01` solely for placement; the vase is not exported with the flowers. The inventory also mentions HA-VASE-02, which needs its own fit check.

## Geometry and placement

`model/HA-FLOWERS-01.blend` is editable Blender source, and `model/HA_FLOWERS_01.fbx` exports five material-grouped mesh objects: stems, sage leaves, pink petals, ivory petals, and flower centres. Stems branch from five main stalks and converge below the flower heads. The blossoms and leaves use thin polygonal surfaces; they are not alpha cards and use no transparent texture.

Blender uses metres, +Z up. **The bunch origin is the vase mouth centre**, not floor/tabletop level: with the HA-VASE-01 base at Z=0, put the flower origin at approximately `(0, 0, +0.260 m)` in its space. Stems descend 0.130 m into the vase and all cross its mouth inside the model's approximately 0.063 × 0.047 m inner elliptical radius; verify fit after Unreal coordinate conversion. The FBX bounds are approximately **0.263 × 0.104 × 0.412 m**, including inserted stems; above-mouth height is about 0.281 m. This is shallower in depth than the 0.18 m design target; judge fullness from the actual hall camera before scaling. Its preview includes a render-only vase and studio setup in the `.blend`; export only the five `Flowers_*` objects.

## Unreal material and validation

Import as static geometry, preserving the five material groups. In Unreal reconnect `petals-painterly.png` as an sRGB base color for `Dusty_Rose_Painterly`; the cream petals, sage leaves, brown stems, and warm centres use solid muted Blender colors. Use high roughness and make the **leaf and petal materials two-sided**, since the meshes are intentionally thin; no cutout/opacity mask is required. Blender nodes do not transfer as finished Unreal materials. Use no decorative collision or a simple proxy. Check lighting, texture scale, backside visibility, vase intersection and hall-camera readability in engine. There is no authored wind animation.

Rebuild using `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_flowers.py` and validate with `-b --python-exit-code 1 --python model/validate_fbx.py`. FBX round-trip validation reports five meshes, **5,510 vertices and 5,880 triangles**, UV layers present, no nonfinite positions/UVs and no zero-area geometry triangles. This check does not establish UV triangle area, Unreal import, material appearance, collision or camera readability.
