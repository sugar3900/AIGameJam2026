# LV-ARMCHAIR-02 — tailored rust reading chair

Replacement source for **LV-CHAIR-01**, addressing FIX-013. The new ID is deliberately descriptive; `assembly.json` records the original ID it replaces. The original export is unchanged. Keep the existing actor transform and surrounding furniture placement.

**Source appearance approved for engine review.** FBX roundtrip, original-envelope preservation and lace-contact checks pass; Unreal material/collision and in-room review remain separate integration steps.

## Construction

A shaped sloping back and rising side frame support a compressed seat and tapered upholstered back pad. The arm caps are true swept oval rolls with shallow domed front ends, small overhangs and a tapered rise into the rear. They use unrolled surface UVs rather than stretched sphere mapping. The seat has a broad crown and weight depression, with continuous deformation through its sides. Fine piping is fitted to the actual upholstery surfaces.

The antimacassar is opaque geometric openwork: bundled rounded flower petals, fine mesh strands, bound sides and scalloped hems. Every stitch follows the visible front, crown and rear of the actual chair back. No floating card, alpha mask or cloth simulation is used. Four textured walnut feet support the frame and reach the floor.

| Path | Purpose |
|---|---|
| `model/LV-ARMCHAIR-02.fbx` | One `LV_Armchair02` render assembly plus 15 simple UCX hulls |
| `model/LV-ARMCHAIR-02.blend` | Editable source collection, packed textures and separate preview context |
| `model/build_armchair.py` | Deterministic headless build/export |
| `model/render_views.py` | Context, front/back/side and closeup renders |
| `model/validate.py` / `validation.json` | Fresh import, original bounds comparison and lace/back intersections |
| `assembly.json` | Exact bounds, source identity, materials/tints and fitted-seam records |
| `release-manifest.json` | Final file sizes and SHA-256 hashes, including the validated FBX/blend |
| `concepts/armchair-tailored-rust.png` | Approved shape/material direction |
| `concepts/generation-prompts.md` | Exact generated-art prompts and provenance |
| `previews/armchair-context.png` | Latest source appearance |

Only `LV-ARMCHAIR-02_SOURCE` members are exported. `PREVIEW_ONLY` walls/floor, cameras and lights are excluded. Earlier iterations live under `previews/archive/`.

## Placement and envelope

Metres, +Z up, **front −Y**, original floor-center origin `(0,0,0)`. Preserve the existing LV-CHAIR-01 actor location, rotation and scale. The established Unreal import conversion keeps X and flips Y, so the imported front is +Y; do not add a blanket rotation correction.

Current bounds are X −0.37000…+0.37000, Y −0.33600…+0.34245, Z 0…0.91427 m: **0.74000 × 0.67845 × 0.91427 m**.

The full new render mesh fits inside the measured original FBX bounds: X −0.374605…+0.374605, Y −0.343700…+0.344586, Z approximately 0…0.935278. Existing radiator/window/fuse encounter clearances are preserved at the source-envelope level; final imported placement still requires in-engine review.

## Material contract — apply the actual textiles

All four slots are opaque and nonmetallic. The texture color is multiplied by the listed **linear RGB multiplier**. These multipliers are part of the approved source appearance; the Blender node graph is not guaranteed to transfer automatically via FBX.

| Slot | Albedo | Linear multiplier / constant | Roughness |
|---|---|---|---|
| `Armchair02_RustJacquard` | `textures/rust-jacquard.png` | Multiply by 0.83 / 0.73 / 0.65 | 0.85 |
| `Armchair02_RustWelt` | None | Constant 0.23 / 0.075 / 0.026 | 0.85 |
| `Armchair02_PaintedWalnut` | `textures/walnut-painted.png` | Multiply by 0.36 / 0.28 / 0.20 | 0.66 |
| `Armchair02_IvoryCrochet` | `textures/ivory-thread.png` | Multiply by 0.78 / 0.72 / 0.61 | 0.85 |

Upholstery panels use a 0.48 m repeat, and the oval arm rolls have longitudinal/circumferential UVs at matching scale. The source adds restrained texture-driven fabric bump (strength 0.12, distance 0.6 mm). Albedo and roughness are the essential import contract; reproduce bump gently if useful under final lighting.

The rust jacquard is newly generated painterly textile. Ivory thread reuses the generated sofa wool swatch; wood reuses the approved LV-BOOK-01 painted walnut. All images are copied locally and packed in the blend.

## Collision and checks

Use **legacy FBX import** because this project's UE 5.8 Interchange path drops UCX. Keep authored collision, disable automatic generation, and retain the 15 convex member hulls. They cover base, back frame, seat, arm panels, segmented rising arm rolls and feet. Lace and piping have no tiny blocking hulls.

Current export: **133,098 vertices / 259,064 triangles**. Fresh import confirms one render mesh, 15 manifold box UCX members, finite vertices/UVs, no zero-area triangles, floor origin preserved and bounds inside the original. The actual lace mesh has **zero BVH surface intersections** against both the shaped back frame and stuffed back pad.

The crochet is actual open geometry and accounts for much of the detail count. These source checks do not claim executed Unreal traversal, engine collision recognition or final material appearance checks.

## Rebuild

Run sequentially, with at most two Blender threads:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/build_armchair.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/validate.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/render_views.py
```

The builder accepts `-- --no-render`; the view script accepts individual view names after `--`: `context front back left right lace-detail seat-detail`. Only this asset folder is written. Validation reads the original LV-CHAIR-01 FBX without changing it.
