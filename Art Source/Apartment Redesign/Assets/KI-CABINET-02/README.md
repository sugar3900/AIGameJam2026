# KI-CABINET-02 — fitted sage base cabinetry

Fitted variants of KI-CABINET-01 for the approved compact kitchen. Existing painterly sage/enamel/interior textures are reused; joinery is rebuilt at fitted widths while hardware and profiles retain physical dimensions. The two cabinets adjoining the range now have recessed 40 mm sage fillers to preserve their full door travel.

| Variant | Module width × depth × height | Carcass width / local X offset | Range-side filler | Approved module centre (plan X,Y) |
|---|---|---|---|---|
| `0425` | 0.425 × 0.650 × 0.910 m | 0.425 m / 0 | None | (1.4125, 0.475) |
| `0775` | 0.775 × 0.650 × 0.910 m | 0.735 m / −0.020 m | 40 mm east | (3.0625, 0.475) |
| `0450` | 0.450 × 0.650 × 0.910 m | 0.410 m / +0.020 m | 40 mm west | (4.425, 0.475) |

All face south in the plan. Worktops retain their full module widths, original origins and 0.91 m top height. The fillers are part of each body FBX; their fronts are recessed to source Y=−0.19 m, behind the hinges, to avoid creating a new swing obstruction. No rear upstand is included. Keep the separate backsplash/window clear. The 0425 variant is unchanged by this fit revision.

## Files and assembly

`model/build_casework.py` generates eleven FBXs, three source blend files, and closed/open renders. Each `KI-CABINET-02-<width>.blend` contains the three native-origin variants, with only its named variant visible. Hidden variants are retained for comparison; do not export them accidentally. Lineup previews show 0425, 0775 and 0450 from left to right, translated only for presentation.

- `KI_CAB_0425_body.fbx`, `_door.fbx`, `_drawer.fbx`
- `KI_CAB_0775_body.fbx`, `_door_L.fbx`, `_door_R.fbx`, `_drawer_L.fbx`, `_drawer_R.fbx`
- `KI_CAB_0450_body.fbx`, `_door.fbx`, `_drawer.fbx`

Source coordinates: metres, Z up, front −Y. FBX exports use −Z forward/+Y up. Bodies and drawers keep the **module-centred floor origin**, including the two narrower, shifted carcasses. Do not recenter them from their visible front geometry. Door origins coincide with the brass barrel axis; panel centres remain at Y=−0.2575 m.

| Door | Native hinge pivot relative to module origin (m) |
|---|---|
| 0425 single | (−0.1705, −0.2705, 0) |
| 0775 left | (−0.3455, −0.2705, 0) |
| 0775 right | (+0.3055, −0.2705, 0) |
| 0450 single | (−0.1430, −0.2705, 0) |

Source motion: single/left door Z=0→−100°; right door Z=0→+100°. Drawers slide along source −Y by 0.30 m. The wider module retains distinct `Sink_Door_L`, `Sink_Door_R`, `Sink_Drawer_L`, `Sink_Drawer_R` identities because the narrow sink has no moving cabinetry. All filenames and identities remain stable.

FBX transforms include hinge offsets. If Unreal preserves local pivots, place doors at those offsets relative to the module; if the importer bakes assembly coordinates, use a separate hinge component at the documented position. Do not apply both methods. Confirm actual imported front axis before choosing map yaw. Reimport **all body, door and drawer meshes for 0775 and 0450** for the range-filler revision; old fronts and new bodies must not be mixed.

Each FBX contains one render mesh and named `UCX_<render mesh>_NN` hulls. Body hulls cover separate structural members and recessed filler, preserving the open cavity. Each drawer has five convex wall/bottom boxes. Door collision is a thin panel slab; decorative profiles and pulls do not add bulky collision. The lower/interior shelf fronts sit 5 mm behind the closed door back after the previous 10 mm shelf setback.

## Finish

The packed/generated textures are `sage-D.png`, `ivory-enamel.png`, `interior-wood.png` and `toe-dark.png`, inherited from KI-CABINET-01. Sage uses HSV value 0.75 and roughness 0.78; brass metallic 0.7/roughness 0.33. Reuse or recreate these material settings in Unreal. The full Blender node graph does not transfer automatically through FBX.

## Validation and previews

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_casework.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python model/validate_fbx.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python model/validate_range_fit.py
```

`model/validation.json` records eleven fresh FBX reimports, finite geometry/normals/UVs, nonzero triangles, render/UCX naming, native pivots, full module bounds, unchanged 0425 bounds and drawer/door independence. Own-cabinet sweeps include full handles, molding and hinge geometry.

`model/range-fit-validation.json` records actual imported range body/controls and oven door, narrow sink, fridge and all cabinet render meshes. Range body is centred at plan X=3.825 with its measured back at Y=0.15, matching x=3.45–4.20. Door sweeps sample every degree through 100°; drawer slides sample every 5 mm to 0.30 m, with oven closed and open 82°. Additional combined poses open all cabinet doors and drawers together. Tests use common right-handed source coordinates; plan positions are `(X, −sourceY, Z)`.

The **range oven door/handle extends farther forward than the body's nominal 0.732 m depth**. The test uses the complete actual door geometry rather than clipping it to the floor-plan rectangle. Exact measured neighbour bounds are in the report.

- `previews/casework-closed.png`, `casework-open.png`: three widths and revised front proportions.
- `previews/range-fit-closed.png`, `range-fit-open.png`: source-style cabinet/range contact and full opening poses.

These are sampled Blender geometry checks, not continuous engine physics acceptance. Confirm Unreal imported UCX, actual pivots, motion easing, player capsule, interaction camera, collision tolerances and final lighting during integration.
