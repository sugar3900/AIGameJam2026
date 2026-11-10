# LV-SOFA-02 — structured vintage floral sofa

FIX-005 rebuild of the sofa frame, cushions, trim, upholstery UVs, decorative pillows and throw. This source keeps the existing floor-center origin, −Y front and placement envelope. LV-SOFA-01 is unchanged. The rug adjustment belongs to engine placement and is not part of this export.

**Source appearance approved for engine review. Final source validation passed.** Unreal material/collision checks and in-room review remain pending integration.

## Design and files

A firm vintage upholstered frame replaces the inflated arm bolsters. Compact arm caps sit on upholstered side panels. Three fitted box seats and three back cushions have broad uneven fill, modest sag and small corner creases. Piping is snapped to the actual upholstery surfaces with a sub-millimetre center offset, so the welt sits partly within its seam.

The teal square cushion uses a newly generated needlepoint bouquet; the coral lumbar cushion uses embroidered floral vines. Their depth tapers toward sewn edges rather than retaining a uniformly thick rectangular side band. The cream throw has a modeled contact-supported upper surface, unequal folds and an outside gravity drop, with hem and individual fringe strands. This is carefully modeled cloth, not a claimed cloth simulation.

| Path | Purpose |
|---|---|
| `model/LV-SOFA-02.fbx` | One `LV_Sofa02` render mesh plus 13 named simple UCX hulls |
| `model/LV-SOFA-02.blend` | Editable individual source members, packed images and separate preview context |
| `model/build_sofa.py` | Deterministic headless rebuild and contextual render |
| `model/render_views.py` | Front, back, left, right and two closeup renders |
| `model/validate.py` / `validation.json` | Fresh FBX import checks and comparison against original bounds |
| `assembly.json` | Dimensions, origin, material slots, seam-contact records and collision inventory |
| `concepts/sofa-structured-vintage.png` | Approved construction and textile direction |
| `concepts/generation-prompts.md` | Exact prompts and built-in image generation provenance |
| `previews/sofa-context.png` | Latest contextual source render |

The source collection is `LV-SOFA-02_SOURCE`. The collection `PREVIEW_ONLY`, cameras and lights are excluded from the FBX. `previews/archive/sofa-context-pass01.png` and `previews/archive/sofa-context-pass02.png` are archived earlier review images, not the final appearance.

## Review history

The approved concept was followed by three visible geometry passes: a structured first pass; a second pass correcting cloth contact and pillow edge thickness; and a third pass adding uneven back/seat fill, pinched cushion edges, continuous fitted piping and gathered throw folds. Parent review accepted the third appearance for engine review. A final geometry-only cleanup increased cloth sampling around the arm cap and eliminated all tested cloth/support surface intersections. The latest context, turnaround and detail views use that validated export geometry.

## Placement and size

Source units are metres; +Z up, **front −Y**. Preserve the existing sofa actor's location, rotation and scale. Source origin remains `(0,0,0)` at the floor center. Do not recenter to the asymmetric throw bounding box.

The established Unreal FBX conversion retains source X and flips Y, so the imported front is **+Y**. An old integration used yaw −90° for its placement; that was a placement-specific angle, not a new axis correction to apply blindly.

Current exported bounds:

- X -0.99250…+1.03984 m, width **2.03234 m**, including the right-side throw.
- Y -0.42358…+0.39000 m, depth **0.81358 m**.
- Z 0…0.96826 m.

The complete new mesh stays inside the measured LV-SOFA-01 FBX bounds (X −0.99640…1.04340, Y −0.44100…0.39000, Z 0…0.99000). No sofa movement or plan expansion is needed.

## Materials and UVs

| Slot | Albedo / source | Roughness |
|---|---|---|
| `Sofa02_PaintedFloral` | `textures/sofa-floral.png`, approved original floral texture | 0.85 |
| `Sofa02_OliveWelt` | Linear RGB 0.18 / 0.155 / 0.085 | 0.85 |
| `Sofa02_WornWalnut` | Linear RGB 0.18 / 0.075 / 0.025 | 0.62 |
| `Sofa02_TealNeedlepoint` | `textures/pillow-teal-needlepoint.png` | 0.85 |
| `Sofa02_AgedGoldCord` | Linear RGB 0.43 / 0.31 / 0.13 | 0.85 |
| `Sofa02_CoralEmbroidery` | `textures/pillow-coral-embroidery.png` | 0.85 |
| `Sofa02_WovenThrow` | `textures/throw-wool.png` | 0.85 |

All are opaque, nonmetallic surfaces. The source uses a subtle texture-driven bump (0.6 mm distance, strength 0.12); the FBX does not guarantee transfer of the Blender node graph. Preserve the supplied albedos and use restrained fabric roughness in Unreal.

Floral panel UVs use a common 0.72 m texture repeat across the frame, arms and cushions. Individual upholstery panels have deliberate seam boundaries; the arm sides are not stretched sphere UVs. Decorative pillows map their artwork once to the front panel; woven throw UVs follow the surface grid. All referenced images are copied into `textures/` and packed into the Blender file.

## Collision and validation

Import with the **legacy FBX** importer because the current UE 5.8 Interchange path drops UCX. Keep the authored hulls and disable automatic collision generation. There are 13 convex box members for the frame, back, arms/caps, seats and feet. Piping, pillows and cloth do not add tiny blocking colliders.

Fresh roundtrip validation: one render mesh, **95,024 vertices / 187,376 triangles**, 13 UCX hulls; finite vertices and UVs; no zero-area triangles; origin at zero; floor at Z 0; full bounds inside the original export. `assembly.json` also records every seam's fit-to-surface offset. The final throw surface has zero BVH surface intersections with the right arm panel, rounded arm cap and seat cushion. Its contact wrap uses dense surface samples and an 11 mm nearest-surface clearance before thickness.

These are source checks. Unreal import-axis confirmation, final material appearance, simple-collision recognition and in-room traversal still require integration review. Do not run complex-as-simple over this mesh if the intended authored simple collision is to be retained.

## Rebuild

Run sequentially from this folder, with at most two Blender threads:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/build_sofa.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/validate.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/render_views.py
```

The builder accepts `-- --no-render` to export/save without rendering. The view script accepts individual names after `--`: `context front back left right cushion-detail arm-throw-detail`. It writes only this asset folder and reads the previous FBX only during validation.
