# BR-CLOSET-LIGHT-01 — FIX-029

Short vintage brass pendant, closed glass envelope, visible filament, beaded pull chain and weighted grip. Source preview reviewed in on/off and socket close views; all four FBXs re-imported into a fresh Blender scene and validated. Integration/PIE remains engine-owned.

## Placement and import

Source metres, X right / -Y forward / Z up. Assembly root is the existing closet floor origin **(110,470,0) cm**, yaw0. Exports are **functional-pivot local vertices at identity transforms**. They are NOT already assembled-floor vertices. Do not add their original floor height twice.

| File in models/ | Actor/component world position cm | Relative to assembly root cm |
|---|---|---|
| BR_ClosetLight01_Hardware.fbx | 114,468,275 | 4,-2,275 |
| BR_ClosetLight01_Glass.fbx | 114,468,275 | 4,-2,275 |
| BR_ClosetLight01_Filament.fbx | 114,468,275 | 4,-2,275 |
| BR_ClosetLight01_Chain.fbx | 118,474,264.5 | 8,4,264.5 |

Import yaw0, scale1 after standard metre-to-cm conversion. Hardware/glass/filament share the ceiling mount pivot. Chain has its top attachment pivot. A single UCX box surrounds the chain/grip, 2.6 cm square, full length; **query-only**, never pawn blocking. All other components NoCollision. Retire the old bulb mesh and Bulb_Closet light after replacing them.

Canopy top275, bulb bottom246, chain rest bottom201.5 cm. Pull -Z1.5 cm gives bottom200, then returns over0.25 s. Socket guide encloses the chain top during travel. Full geometry and bounds are recorded in geometry.json; that file uses pendant-centred source coordinates before export pivot subtraction. fbx-validation.json records actual pivot-local imports.

## Material contract

FBX names are slots, not working Unreal shader graphs. Recreate authored materials explicitly; do not accept default opaque Phong glass.

| Slot | Linear base RGB | Metal | Roughness |
|---|---|---|---|
| Closet_AgedBrass | .17,.105,.046 | .75 | .40 |
| Closet_BrassEdge | .31,.20,.085 | .72 | .36 |
| Closet_BraidedCord | .022,.017,.012 | 0 | .85 |
| Closet_Ceramic | .50,.43,.31 | 0 | .60 |
| Closet_SupportWire | .09,.075,.055 | .70 | .48 |
| Closet_ClearAmberGlass | .94,.86,.70 | 0 | .16 |
| Closet_Filament | .25,.08,.012 | .10 | .50 |

Glass is transparent, IOR1.46, closed shell0.8mm, lightly warm clear tint. Preserve view of filaments OFF and ON. Both glass and filament engine materials expose **GlowStrength**, driven by the same Light toggle alpha; zero when OFF. Glass emission must remain faint to avoid an opaque glowing globe. Filament is the main visible glow (preview RGB1,.36,.075, strength6; engine may tune against actual exposure). Point light supplies illumination:60lm,2300K,radius8cm,specular.35,attenuation260cm, near bulb centre (114,468,250), not old z200. Keep dim/warm intent; no global exposure change.

## Binding and acceptance

New Light_Closet, room bedroom, initially ON, prompt “Pull chain” in both states. Chain is interactable Body with outlined chain/bead. One opt-in toggle drives point intensity and both emissive slots with existing0.29s fade; one opt-in click animation pulls1.5cm and returns0.25s. Existing light defaults unchanged. Check real on/off from closet approach, no shelf/head/mold collision or trace interference, and UI-visible Malcolm near/far/lateral/16:9 framing and settled lighting after relocation. Source checks do not establish those runtime results.

Build with build_light.py; validate separately with validate_fbx.py. One CPU Blender process at a time. No engine files or git changed by source build.
