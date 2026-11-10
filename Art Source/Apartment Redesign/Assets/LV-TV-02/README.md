# LV-TV-02 — FIX-031 / FIX-032

Separate tabletop television and exact original stand. Cabinet has firm small-bevel joinery, visible walnut grain, a tapered recessed Bakelite CRT bezel, one convex glass screen, inset speaker louvres/cloth and defined controls. It is deliberately a tabletop unit, without extra floor legs.

## Placement / identities

All three FBXs in models/ use **the original assembly floor-centre origin**, source metres, front -Y. Import as current LV-TV-01 at world **(1165.1,205,0)cm yaw90**; source mapping world offset=(100*y,100*x,100*z). Geometry is already assembly-height, so do not add stand height a second time.

- LV_TV02_Stand.fbx: exact original stand face geometry/UVs/material names, no TV geometry. MaxZ64.75cm. Replace the combined Art_LV_TV body with this and the new housing; retain original left/right cabinet door meshes and their pivots. A separate stand identity is requested; :089 was suggested subject to engine checking it is free.
- LV_TV02_Housing.fbx: stationary wood case, inset bezel/gasket, control panel/knobs, speaker and rear vents. BaseZ64.75cm sits directly on stand. X±51.75cm, sourceY within±23cm; top131.4cm, over20cm below Art04's bottom152. Use complex static collision consistent with current TV cabinet. Keep stand's useful hollow collision/interior; do not turn the whole assembly into a solid blocking box that prevents access to the cabinet.
- LV_TV02_Screen.fbx: **one** closed convex CRT glass mesh. Swap its material between off/on (or animate one MID). No second overlay or duplicate screen. Preserve interactable label TV, room living, prompts and TvOn/TvOff SFX. Reconcile LV-TV-01:022 covers housing plus TV interaction.

Screen centre source(-.105,-.183,.992) at the frontmost centre = world **(1146.8,194.5,99.2)cm**. EdgeY-.143; centreY-.183; front bezelY-.210: even the convex glass centre is recessed27mm. Screen UV=(x+.404)/.598,(z-.785)/.414, normalized for radial ramp. Set the interactable Body offset appropriately for assembly-origin screen verts; do not move the full mesh to the screen centre. Position local light just forward into the room, aimed at the TV front area; keep it modest, not the old1500-unitless blue wash.

## Materials

Use explicit MIs by slot. These texture albedos are **sRGB**. FBX node translation is not a reliable material implementation.

| New housing slot | Base colour | Roughness | Metal |
|---|---|---|---|
| TV02_WalnutVeneer | T_TV02_Walnut.png, no extra tint | .55 | 0 |
| TV02_EndGrainTrim | T_TV02_Walnut.png, no extra tint | .59 | 0 |
| TV02_Bakelite | .029,.026,.022 linear | .50 | 0 |
| TV02_CRTSeal | .012,.015,.012 | .85 | 0 |
| TV02_AgedChampagneMetal | .39,.30,.17 | .40 | .65 |
| TV02_DialIvory | .64,.60,.46 | .58 | 0 |
| TV02_SpeakerCloth | T_TV02_SpeakerWeave.png | .95 | 0 |
| TV02_BackBoard | .065,.044,.027 | .90 | 0 |
| TV02_VentDark | .009,.010,.008 | .95 | 0 |
| TV02_CRTGlass | .035,.048,.042 | .19 | .08 |

T_TV02_Walnut is the original walnut albedo with its documented (.25,.23,.14) **linear** tint baked once, with sRGB decode/encode. No second tint. Stand and original door Walnut_Painted keep their original texture+linear tint; other original stand slots stay per LV-TV-01 README / engine FIX-032. Never remap the whole stand to brass or TV glass by numeric slot.

CRT OFF: dark gray-green reflective opaque glass surface, zero emission. ON: restrained warm-white phosphor. Source preview uses UV radial distance from(.5,.5): centre RGB(1,.90,.74) at radius.10, edge RGB(.16,.19,.15) at radius.65, smoothly interpolated, strength.7. Scale brightness in actual room so wood/face are not washed out. No saturated orange or blue fill. User did not request a programme/video feature; these are on/off lighting states.

## Validation and remaining engine work

Fresh imports pass: stand face positions/UVs/material slots identical within10um; finite UVs/nondegenerate faces; housing rests at64.75 and fits stand/art limits; screen closed with positive volume and front normals toward -Y, fully behind bezel. Submicron degenerate text cap faces were removed before export. Neutral off/on/front/oblique previews reviewed. Verify installed front and grazing views, actual TV on/off, local-light colour/intensity, and both cabinet-door real open/close/sweeps/interior access in PIE. Engine-only FIX-032 authorized, source does not prove runtime.

Build with build_tv.py (optional -- --skip-render) then validate_fbx.py. Original source is read-only. No engine or git writes.
