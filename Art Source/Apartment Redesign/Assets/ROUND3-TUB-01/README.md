# ROUND3-TUB-01 — developed painterly clawfoot tub

Additive replacement for the **body only** at `Art_BA_Tub_BA_Tub`. The original BA-TUB-01 files are unchanged. `model/build_tub03.py` builds the editable blend, one combined FBX and the studio preview; `model/validate_tub03.py` independently imports the FBX and verifies the geometry contract.

## Placement and retained gameplay

- Export `model/BA_Tub03_Body.fbx`, combined mesh, Blender metres, FBX **forward -Z / up Y**, matching BA-TUB-01. Floor origin `(0,0,0)` and identity transform. Keep the installed actor at `(580,907,0)` cm, yaw 180, scale 1.
- Bounds remain local `(-.835,-.340,.010)` to `(.835,.340,.583)` m, exactly the original 1.67 × .68 m footprint and rim height.
- Keep the existing tub collision, repair overlay, interaction identity, water plane, wall plumbing, independent tap handles and both curtains. No new blocking collision or UCX is supplied. Do not auto-convex the hollow bowl.
- The old body and all its old ivory feet/overflow are replaced. This FBX has a new seated overflow escutcheon but **no baked drain**. Retain the separately installed `BA_TubFixture02_Drain` at the original tub transform, local x `-.542…-.458`, y `±.042`, z `.184… .192` m. Its enamel seat remains z `.180` m.
- The existing water surface at z `.430` m, local x `±.718` and y `±.229` m, still fits the preserved inner bowl. The original inner slope sections above z .22 remain unchanged; new sections subdivide those original planes rather than narrowing the basin.

## Model development

The continuous hollow bowl now has a shaped shoulder and a smooth rolled lip with a small lower casting bead. Four scrolled cast-metal ankles support ball-and-claw feet, with tapered curled talons, separate balls, raised leaf-pattern mounting shields and small rivets. Mounting shields and the in-bowl overflow plate follow the actual curved enamel surface. This avoids putting a flat decorative plate across a curved bowl with floating edges.

## Authored material contract

Blender nodes are the source appearance reference. Recreate the texture blend and tints in Unreal; imported FBX Phong materials are insufficient. UV0 is explicit on every part and is the only UV layer.

| Slot (exact order) | Albedo / tint | Metallic | Roughness |
| --- | --- | --- | --- |
| `Tub03_Exterior_Enamel` | `lerp(enamel-albedo.png, enamel-brush.png, .60)`, tint `(1,1,1)` | 0 | .36 |
| `Tub03_Interior_Enamel` | same blend at .30, tint `(1.08,1.08,1.06)` | 0 | .23 |
| `Tub03_Rolled_Rim` | same blend at .45, tint `(1.05,1.04,1.01)` | 0 | .26 |
| `Tub03_Aged_CastMetal` | `aged-metal.png` × `(.38,.42,.42)` | .68 | .48 |
| `Tub03_Raised_Metal` | `aged-metal.png` × `(.67,.64,.56)` | .72 | .39 |
| `Tub03_Overflow_Dark` | flat `(.035,.027,.018)` | 0 | .50 |

All albedo maps use sRGB. Enamel maps are existing BA-TUB-01 painterly sources; aged-metal is the existing HA-SCONCE-01 aged brass image. Copies in this kit make the release self-contained. Preserve medium-scale strokes; do not multiply the enamel by the old orange/ivory FBX diffuse tint. There is no displacement or new emissive surface. Materials remain single-sided.

## Validation

`validation.json` records a fresh FBX import, 70 closed components with individually positive signed volume, zero degenerate triangles/nonmanifold edges/nonfinite coordinates, the exact unchanged bounds, outward exterior and inward cavity face directions, nonzero finite UV0 coverage in all six slots, the clear retained drain seat and the fitting water outline. The preview is a neutral studio view with all source materials using backface culling; installed daytime and close grazing views remain required for acceptance.
