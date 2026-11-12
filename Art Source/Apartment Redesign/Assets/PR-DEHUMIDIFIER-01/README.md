# PR-DEHUMIDIFIER-01 — portable floor dehumidifier

Painterly ivory-and-sage household **dehumidifier**, developed from concept A. Three concepts were generated and shown before any mesh work. A was chosen as the working direction because it fits the apartment's existing appliances; it is not recorded as an explicit user selection. Concept PNGs and the complete built-in imagegen prompt set are in `concepts/`.

The model has a continuous softened casing, recessed front louvers, top exhaust, rear filter grille, rotary humidity dial, power rocker, full-tank lens and pictogram, carry handle, four casters, rear service fasteners, a stowed power cable and plug. The collection bucket is hollow and removable, with a finger recess, water-level window and collected water. It emits no mist.

## Deliverables and coordinates

- `model/PR-DEHUMIDIFIER-01.blend`: editable individual parts, authored materials and studio setup; saved with the bucket seated.
- `model/DH_Dehumidifier01.fbx`: combined static prop, plus a single simple `UCX_DH_Dehumidifier01_00` collision hull around the main casing.
- `model/DH_Dehumidifier01_Body.fbx` and `model/DH_Dehumidifier01_Tank.fbx`: optional split assembly. These omit collision; use them instead of the combined prop.
- `previews/`: front, rear and bucket-pulled studio renders. The pulled pose illustrates assembly access; no animation or interaction system is included.
- `model/build_dehumidifier.py` and `model/validate_dehumidifier.py`: reproducible headless Blender build and independent fresh-FBX verification. Both serialize against `/tmp/apartment_blender.lock`.
- `materials.json`: exact slot names and material values. Texture copies in `textures/` make the kit self-contained.

Blender metres, Z up, front **−Y**, right +X. All exports share the floor-centred `(0,0,0)` assembly pivot. FBX forward −Z/up Y, unit scale applied; default FBX import preserves centimetre size in Unreal. Main casing is 34 × 29 × 47 cm, from z 5.5 to 52.5 cm. Handle reaches about 58 cm above the floor. The stowed cable projects behind the casing. See `validation.json` for measured complete export bounds.

The optional bucket pulls along Blender −Y, illustrated at −24.5 cm. It shares the assembly pivot rather than having a bucket-centred pivot. The bucket is seated with a nominal 3 mm bay reveal. Combined collision excludes the small projecting details and provides a body blocker. Split assembly collision must be configured by its integrator.

## Material contract

FBX Phong transfer does not reproduce these shader graphs. Recreate the nine slots using `materials.json` and the Blender source as the appearance reference. All images use sRGB and explicit UV0.

| Slot | Base colour | Metallic | Roughness |
| --- | --- | --- | --- |
| `DH_Ivory_Painted` | `lerp(enamel-albedo, enamel-brush, .52) × (1.06,1.04,1)` | 0 | .40 |
| `DH_Sage_Painted` | same blend × `(.37,.47,.32)` | 0 | .52 |
| `DH_Aged_Hardware` | `aged-metal × (.46,.43,.34)` | .70 | .49 |
| `DH_Rubber` | `(.035,.029,.024)` | 0 | .82 |
| `DH_Filter_Shadow` | `(.045,.040,.030)` | 0 | .91 |
| `DH_Control_Print` | `(.83,.79,.64)` | 0 | .62 |
| `DH_Tank_Window` | `(.38,.52,.48)` | 0 | .18 |
| `DH_Collected_Water` | `(.32,.45,.43)` | 0 | .12 |
| `DH_Amber_Lens` | `(.60,.18,.025)` | 0 | .24 |

Window and collected-water slots use Principled transmission .60/.75 in Blender. For Unreal, configure translucent materials appropriate to the project's renderer, without water collision. The amber lens is not emissive: this static prop does not imply an active warning. Other surfaces are opaque and single-sided. Hardware is aged rather than bright chrome. Images are unchanged copies from ROUND3-TUB-01, using the established bathroom enamel and aged-brass sources.

## Build and validation

Run from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --threads 2 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/PR-DEHUMIDIFIER-01/model/build_dehumidifier.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --threads 2 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/PR-DEHUMIDIFIER-01/model/validate_dehumidifier.py'
```

`validation.json` records fresh FBX import checks: bounds/pivot, finite positions and UVs, nonzero UV0 coverage per material, zero degenerate triangles and nonmanifold edges, positive volume for every closed component, combined/split assembly agreement and collision identity. Neutral studio renders are the appearance reference. This source kit does not claim an Unreal import, map placement or gameplay validation.
