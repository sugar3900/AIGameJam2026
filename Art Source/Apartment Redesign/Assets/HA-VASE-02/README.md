# HA-VASE-02 — sage gallery-end vase

Status: modeled Blender candidate for art-lead review; not imported into Unreal. This distinct muted-sage, open-mouthed vase is intended for the west-end hallway cabinet and can hold `HA-FLOWERS-01`. `concepts/vase-multiview-v1.png` is the generated five-view design; `textures/sage-botanical.png` is an independently generated painterly base-color texture. Brushwork is color, not physical paint thickness. `previews/vase-three-quarter.png`, `vase-front.png` and `vase-with-flowers.png` show Blender studio renders, not in-game results. The flowers are a separate asset and are not in the vase FBX.

## Geometry and placement

`model/HA-VASE-02.blend` is editable source; `model/HA_VASE_02.fbx` contains one static hollow ceramic mesh with a modeled inner floor and rolled lip. Blender uses metres, +Z up; vase front is −Y and its origin is tabletop-level centre. Mesh bounds are **0.220 × 0.180 × 0.268 m**; lip top is at z=0.270 m, foot bottom at z=0.002 m. The inner mouth at the lip is approximately 0.142 × 0.116 m. Place the base on the cabinet, rotate its front toward the intended view and confirm mounting, collision and UE axis/unit conversion. Blender FBX export uses **−Z forward, +Y up**.

To reproduce `previews/vase-with-flowers.png`, place the common origin of `HA-FLOWERS-01` at `(0,0,+0.270)` metres relative to this vase's tabletop origin; its stems descend inside the mouth. `model/validate_flower_fit.py` reimports both FBXs and found **no triangle intersections** between the vase and the five transformed flower groups. This is a geometric fit check, not an Unreal material, collision or final-lighting check. Flower petals/leaves require the separate asset's two-sided material guidance.

## Materials and validation

Reconnect `textures/sage-botanical.png` as sRGB base color, non-metallic, roughness ~0.48 as a starting point. This generated image is not proven seamless: inspect the rear cylindrical UV seam, color variation and botanical motif under final room lighting. Blender material graphs and lighting do not transfer automatically to Unreal. Use a simple proxy or no decorative collision rather than automatically colliding the hollow interior.

Rebuild with `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_vase.py`; the final flower-fit render additionally reads `HA-FLOWERS-01/model/HA-FLOWERS-01.blend` without modifying it. Validate FBX with `-b --python-exit-code 1 --python model/validate_fbx.py`, and the separately exported flower assembly with `model/validate_flower_fit.py`. Latest reimport: **3,648 vertices, 7,292 triangles, UVs present, zero nonfinite vertices or degenerate geometry/UV triangles**, expected bounds. A central ray through the mouth reaches the inner base at z≈0.027 m. Unreal material, appearance, floor contact and placement remain untested.
