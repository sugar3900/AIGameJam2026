# KI-LEAK-02 — vintage galvanized pail and sink leak handoff

Source revision for **FIX-003**, 2026-11-09. Source previews and geometry checks are complete; the water shader, falling-drop animation, repaired-state behavior and golden-hour appearance still require Unreal review. This package does not change the normal sink-tap action.

## Replace precisely

| File | Use |
| --- | --- |
| `models/KI_LEAK_02_sink_body.fbx` | Replace the mesh on the current narrow sink body, keeping its actor transform and existing sink materials. Removes only the old baked-in bucket and wire handle. |
| `models/KI_LEAK_02_bucket.fbx` | New separate vintage pail. Place at **the same assembly transform as the sink body**; position is already baked in. Includes 13 named UCX hulls. Keep after repair. |
| `models/KI_LEAK_02_bucket_water.fbx` | Optional separate water plane inside pail, at Z 0.115 m. Assign the engine water material, no collision; repaired-state treatment belongs to gameplay. |
| `models/KI_LEAK_02_puddle.fbx` | Optional planar irregular spill, Z 0.004 m. Prefer the decal-mask route below if it reads better on the painted tiles. Do not use both representations. |
| `textures/T_Leak_Puddle_Mask.png` | White RGBA mask with feathered alpha for a transparent wet-floor/decal shader. **Not a white puddle base color.** |

**Retire the whole original `KI_SINK_NARROW_damage` actor/mesh**: it contains both the five static beads and the old opaque puddle. Separately suppress/replace the `FixHimMalady::BuildBrokenFx` fallback drop and large oval/cylinder for this authored leak. Merely swapping the bucket leaves two obsolete water systems visible. Preserve Lukey's repair identity, inspect reach and encounter transform; damaged water effects stop/hide on repair. The bucket and sink remain.

The original L/R tap meshes are not replaced. Their source pivots remain L `(-0.25, 0.21, 1.075)` and R `(0.25, 0.21, 1.075)` m. The included assembly keeps the original taps as context only; it does not export copies or alter their axes.

## Coordinates and fit

All meshes use **metres, Z up, the original sink assembly floor-center origin `(0,0,0)`**. Source front is −Y. The established UE FBX conversion keeps X, reverses Y and multiplies metres by 100. Do not center individual meshes or add the bucket center a second time. Retain the existing sink yaw/scale/transform and transform the local points below through it.

| Feature | Blender assembly coordinate, metres | UE local coordinate, cm, before actor transform |
| --- | --- | --- |
| Pipe leak underside | `(-0.10, 0, 0.243)` | `(-10, 0, 24.3)` |
| Drop landing / ripple center | `(-0.10, 0, 0.115)` | `(-10, 0, 11.5)` |
| Pail floor center | `(-0.12, -0.055, 0.006)` | `(-12, 5.5, 0.6)` |
| Residual spill mask center | `(-0.0829865, -0.298254, 0.004)` | `(-8.29865, 29.8254, 0.4)` |

The drop travels only **12.8 cm** from the P-trap underside to water. The gravity-only fall takes approximately **0.162 seconds** at 980 cm/s². Use small, intermittent gravity-driven drops, a restrained impact/ripple **inside the pail**, and no static beads. The story is that this pail was recently placed under a leak: the surrounding irregular floor spill escaped earlier. It does not need perpetual floor-impact rings.

The new pail keeps the old center and approximately 30 cm mouth diameter. Its shell/rim now sits below the P-trap rather than intersecting it; the bail folds forward to clear the plumbing. Visual bounds: X `−0.2783..0.0383`, Y `−0.2082..0.0982`, Z `0.006432..0.231043` m. Rim top is 0.2312 m; trap minimum is 0.24299 m. The nearest sampled bucket vertex to trap surface is 0.036112 m, with **zero triangle intersections**. These are source-space checks, not an in-engine collision acceptance claim.

Clean sink body bounds remain X `−0.525..0.525`, Y `−0.340..0.3105`, Z `0..1.343217` m. Supports, basin, backsplash, back panel, exposed drain, faucet/manifold and valve bases retain their exact original faces, UVs, material slots and origins. `fbx-validation.json` records successful reimport of all four exports, all 13 bucket hulls, intact UVs/origins, and 35,963 partially transparent mask pixels with a fully transparent border. `validation.json` records the matching before/after hash of every surviving face, material index, smooth flag and per-loop UV.

## Materials

- Bucket slot 0, `KI_LEAK_02_Painted_Zinc`: `T_Bucket_Zinc_BaseColor.png` as sRGB; roughness and metallic maps as linear/non-color. Metallic is 0.72 and roughness is approximately 0.43–0.62. The generated zinc color uses broad painted flakes and subtle scratches; it has no baked specular or shadow lighting. Do not tint brown in Unreal. No normal map is required; the low-relief texture is primarily color and roughness, with rims/ribs/dents modeled.
- Slot 1, `KI_LEAK_02_Dark_Worn_Seams`: linear base color `(0.21,0.235,0.245)`, metallic 0.64, roughness 0.55.
- Slot 2, `KI_LEAK_02_Worn_Iron_Bail`: linear base color `(0.16,0.175,0.18)`, metallic 0.74, roughness 0.42.
- Clean sink slots remain `Sink_SagePaint`, `Sink_AgedEnamel`, `Aged_Chrome`; reuse current Unreal materials. Inherited source images are copied into this package for portable Blender review, not a request to change the sink material.
- Both water exports use `KI_LEAK_02_Water_REPLACE_IN_UE`. Blender transmission uses IOR 1.333, roughness 0.075, metallic 0. **FBX does not carry this renderer behavior into Unreal.** Assign a transparent water shader there, keep tile color visible, and avoid bright emissive fill. Bucket water should reflect the rim and respond gently at the stated catch point.

The spill mask maps to **68.2221 × 86.1652 cm including 2 cm transparent padding on every side**, centered as above. Image right is source +X; image up is source +Y, which becomes local −Y in UE. Use this basis rather than assuming an Unreal decal rotation. The optional mesh covers the unpadded silhouette and three small satellite wet spots, with planar UVs across its own bounds; the PNG mask includes the extra padding. Edge alpha is feathered over roughly 4% of its local radius; the interior is white mask coverage. Its mesh additionally carries `WaterEdge` vertex colors (center white, perimeter black) for an adjustable shader edge fade. No water geometry should block movement or click traces.

## Import and validation

Import the bucket with **legacy FBX** and named UCX collision enabled; the project observed UE 5.8 Interchange silently dropping UCX. Thirteen hulls approximate a hollow wall and bottom; the thin decorative wire does not receive collision. The clean body intentionally retains the original collision policy; use the integration team's existing static-mesh collision pass. Water is collision-free.

`build_leak.py` reads the original `KI-SINK-NARROW-01/models/KI_SINK_NARROW_assembly.blend` without writing it. It removes only the 192-vertex bucket-shell component and 810-vertex wire component. It asserts all other source faces/UVs are unchanged and checks the new pail against the original trap BVH before exporting. No source authoring is done in Content or shared engine tools.

Reproduce with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/KI-LEAK-02/build_leak.py'
```

Previews: `previews/bucket-three-quarter.png`, `previews/sink-context.png`, `previews/under-sink-clearance.png`. These use moderate warm/cool studio light. The saved assembly contains preview camera, lights and ground (ground hidden by default); these are excluded from all exports. The generated zinc base-color is stored locally and the blend packs its texture dependencies. No source work is held only in a temporary folder.

Final acceptance still requires the engine owner to remove both obsolete water systems, fit the wet shader under scene lighting, click the leak, verify Lukey and the repair transition, and confirm the normal sink-tap toggle is unchanged.
