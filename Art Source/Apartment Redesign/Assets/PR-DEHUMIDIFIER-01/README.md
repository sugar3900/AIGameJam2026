# PR-DEHUMIDIFIER-01 — portable floor dehumidifier

Painterly cream-and-blue-gray household **dehumidifier**, developed from the user's selected **concept B**. Three concepts were generated and shown before mesh work. B supersedes the initial working A model. Original concept PNGs and the built-in imagegen prompt set remain in `concepts/`.

The broader workhorse casing has blue-gray vertical intake vanes, a sloping cream control brow, blue-gray side panels, a broad matching blue-gray top exhaust, horizontal rear filter grille, humidity dial, power rocker, full-tank lens, folding carry bail, four casters and service fasteners. The hollow collection bucket is removable. The stowed cable and grounded plug are separate assets so being plugged in can drive the storyline. It emits no mist.

## Deliverables and coordinates

- `model/PR-DEHUMIDIFIER-01.blend`: editable individual parts, authored materials and studio setup; saved with the bucket seated.
- `model/DH_Dehumidifier01.fbx`: combined static prop, plus a single simple `UCX_DH_Dehumidifier01_00` collision hull around the main casing.
- `model/DH_Dehumidifier01_Body.fbx`, `model/DH_Dehumidifier01_Tank.fbx`, `model/DH_Dehumidifier01_CordStowed.fbx`: split assembly, with common floor pivot. Use these instead of the combined prop for gameplay.
- `model/DH_Plug01.fbx`: matching grounded plug, pivot at its seating face. It is authored separately and must use the transform in `interaction-anchors.json` to join the stored assembly.
- `model/DH_CableSegment01.fbx`: a 1 m long, 6 mm diameter cable along +X, with 32 longitudinal subdivisions, for runtime spline deformation.
- `previews/`: front, rear, bucket-pulled and handle-raised studio renders. These are illustrative poses, not animation clips.
- `model/build_dehumidifier.py` and `model/validate_dehumidifier.py`: reproducible headless Blender build and independent fresh-FBX verification. Both serialize against `/tmp/apartment_blender.lock`.
- `materials.json`: exact slot names and material values. Texture copies in `textures/` make the kit self-contained.
- `interaction-anchors.json`: floor/carry placement, cord exit, bail hinge, tank direction, plug insertion axis and stored transform. Named source empties mark the main attachment points.

Blender metres, Z up, front **−Y**, right +X. Body, bucket and stored cord share the floor-centred `(0,0,0)` pivot. The plug uses its own insertion-face pivot; the straight cable uses its first endpoint. FBX forward −Z/up Y, unit scale applied. Main casing is 39 × 31 × 45.5 cm, from z 5.5 to 51 cm. The folding handle and cord project beyond it. See `validation.json` for measured complete bounds.

The bucket pulls along Blender −Y, illustrated at −24.5 cm, with a nominal 3 mm bay reveal. The bail's transverse hinge passes through `(0,.075,.428)` m and is folded back 30° in the delivered mesh. The raised source preview illustrates a +30° rotation from this delivered pose. Combined collision excludes projecting details. Split assembly collision must be configured by its integrator.

## Storyline and gameplay handoff

The selected movement interaction is **choose a destination room**. The user will implement gameplay in a separate thread. These are source assets and attachment contracts; no runtime actions, UI, save schema or story progression were added here.

For the portable state, assemble body + bucket + stored cord, with the separate plug at its stored transform. For a plugged-in state, hide `CordStowed`, keep the outlet fixed to its wall, snap the plug to one of PR-OUTLET-01's socket anchors, and use the straight cable with a spline/cable component from `CordExit` to the plug's cord exit. Do not stretch the coiled mesh between the appliance and wall. The outlet has two compatible socket anchors. Power, occupancy, relocation and persistence remain gameplay state.

## Material contract

Concept-fit revision: the front vanes are now 12 mm deep and recessed 10 mm behind the casing face. Top vents retain their accepted geometry. The cream control brow has a genuinely flat angled area integrated into the casing; the dial ring, switch and indicator mount directly onto this plane. Side, low and overhead control close-ups are included in `previews/controls-*.png`. The separate plug now has a tapered brown bakelite housing and wider blade spacing matched to the revised outlet.

FBX Phong transfer does not reproduce these shader graphs. Recreate the ten slots using `materials.json` and the Blender source as the appearance reference. All images use sRGB and explicit UV0. Front intake and top exhaust vanes share the side panels’ existing `DH_BlueGray_Painted` material and texture blend.

| Slot | Base colour | Metallic | Roughness |
| --- | --- | --- | --- |
| `DH_Ivory_Painted` | `lerp(enamel-albedo, enamel-brush, .52) × (1.06,1.04,1)` | 0 | .40 |
| `DH_BlueGray_Painted` | same blend × `(.26,.38,.49)` | 0 | .56 |
| `DH_Aged_Hardware` | `aged-metal × (.46,.43,.34)` | .70 | .49 |
| `DH_Rubber` | `(.035,.029,.024)` | 0 | .82 |
| `DH_Filter_Shadow` | `(.045,.040,.030)` | 0 | .91 |
| `DH_Control_Print` | `(.83,.79,.64)` | 0 | .62 |
| `DH_Tank_Window` | `(.38,.52,.48)` | 0 | .18 |
| `DH_Collected_Water` | `(.32,.45,.43)` | 0 | .12 |
| `DH_Amber_Lens` | `(.60,.18,.025)` | 0 | .24 |
| `DH_Plug_Bakelite` | `aged-metal × (.22,.15,.09)` | 0 | .58 |

Window and collected-water slots use Principled transmission .60/.75 in Blender. For Unreal, configure translucent materials appropriate to the project's renderer, without water collision. The amber lens is not emissive: this static prop does not imply an active warning. Other surfaces are opaque and single-sided. Hardware is aged rather than bright chrome. Images are unchanged copies from ROUND3-TUB-01, using the established bathroom enamel and aged-brass sources.

## Build and validation

Run from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --threads 2 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/PR-DEHUMIDIFIER-01/model/build_dehumidifier.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --threads 2 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/PR-DEHUMIDIFIER-01/model/validate_dehumidifier.py'
```

`validation.json` records fresh FBX checks for all six exports: bounds/pivots, finite UV0 with coverage per material, zero degenerate triangles and nonmanifold edges, positive volume per closed component, reconstructed split assembly agreement (including the plug transform), cable length/diameter and combined collision. Bucket extraction is checked at 11 positions over 24.5 cm. Neutral studio renders are the appearance reference. This source kit does not claim an Unreal import or gameplay validation.
