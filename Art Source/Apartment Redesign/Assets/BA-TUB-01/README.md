# BA-TUB-01 — vintage bathtub and shower

## Source and references

- `concepts/tub-tile-states-v1.png`: selected before/after repair concept. Tile damage and wall are separate assets.
- `refs/multiview-v1.png`: generated multi-view guide. Reference views contain AI inconsistencies; the source blend and A+ plan govern dimensions and construction.
- `textures/enamel-albedo.png`, `textures/enamel-brush-v2.png`, `textures/floral-albedo.png`: generated color textures. The enamel preview mixes the first two at 0.6 for visible medium brush marks. Hook both into Unreal materials after import; Blender material nodes do not automatically transfer as finished Unreal materials.
- `model/build_tub.py`: original static assembly generator (does not include the animated curtain; running it overwrites the authored source). Run with `/Applications/Blender.app/Contents/MacOS/Blender -b --python <script>`.
- `model/BA-TUB-01.blend`: editable source. `previews/three-quarter.png`: Blender studio render.

## Dimensions and placement

Blender units are metres. The tub body is 1.67 m long by 0.68 m wide, with rim at z=0.57 m and feet down to z=0.01 m. Length lies along X, front is -Y; fixture mounting side is +Y. The tub is centred at the origin in XY and the common placement origin is at floor height. The riser is shifted to the west end to clear the A+ south-wall window when the tub centre is placed at x=5.80 m. Confirm plumbing, placement and window clearance with the final room shell in 3D.

The model has five FBX groups: `BA_Tub.fbx`, `BA_TubFixtures.fbx`, `BA_Curtain.fbx`, `BA_TapLeft.fbx`, and `BA_TapRight.fbx`. They preserve their common assembled coordinates; import with combined meshes or preserve FBX transforms as appropriate. Fixtures and curtain can be placed independently from the tub. Tap handle pivots are at (-0.84, 0.29, 0.96) and (-0.66, 0.29, 0.96), rotating about local Y; the curtain and rings are one rigid sliding panel with pivot (0.92, -0.35, 2.18), sliding along local X. These exports round-trip in Blender with those transforms; confirm the Unreal importer retains the intended pivots before wiring gameplay.

## Checks and review status

A headless Blender FBX round trip found 0 nonfinite vertices, 0 nonfinite face normals, and 0 zero-area faces on each export. All 49 imported mesh objects have UV layers. The Blender preview shows a hollow basin, trim, feet, drain, tap and shower, with the floral image texture. The enamel now blends two generated painterly color maps, with visible warm/cool strokes and localized specks. The warm studio preview and sculpted feet remain subject to lead review and in-context texture/lighting iteration. No Unreal import or material validation has yet been run. A wall tile crack/repair state must be supplied separately.


## Animated shower curtain (full-fabric drape revision)

Use `model/BA_Curtain_Animated.fbx`; the old static `BA_Curtain.fbx` remains
unchanged. Rebuilt from the original pre-morph source, preserving the cloth's
65-column topology, original loop UVs, `Floral_cotton` / `Aged_chrome` slots,
seven rigid rings, single `CurtainRoot` bone and `Skin` Armature modifier.
The other 48 original mesh objects retain their geometry and transforms in the
hidden `Original tub and fixtures (preserved)` collection. Preview references
are in `Preview assembly (not exported)`.

### Morph control

Keys are **Basis**, **Closed**, **Closed_Mid**. For draw amount `a` in [0,1], set:

- `Closed = a` (0 gathered at the east end; 1 drawn west).
- `Closed_Mid = 4*a*(1-a)`.

`Closed_Mid` is a relative residual key: its stored coordinates are
`Basis + desired_halfway - (Basis + Closed)/2`. It is not an absolute halfway
pose. With this curve, Basis + 0.5 of the Closed delta + 1 of the corrective
delta gives the full-fabric halfway pose. Without correction, halfway rows
shrink to about 193 cm (8% loss); the correction removes that visible contraction.
There are no actions or animation bakes.

Place the moving skeletal mesh on the shared assembly transform (580,907,0) cm,
yaw 180, with no old +125 cm parking offset or rigid slide. The asset uses the
assembly floor origin. Rings translate only along the straight rail at world
Y 872 cm; the permanent east selvage follows the corner to overlap the fixed
return around X 676.5 / Y 886 cm. Header clips connect the ring lower-front
quadrants to the cloth. Ring shapes do not change under the corrective.

### Fabric and clearance

Every front-layer row has **210 cm** arc length in Basis, Closed, and the corrected
halfway pose. The seven open waves have approximately **13.92 cm** peak-to-peak
depth at the top and **13.63 cm** at the hem (excluding the corner flap). There
is no shallow-fold exception or fabric-width reduction below the rim.

The open cloth centre leans outward 5.5 cm from its header centre, an angle of
**2.13 degrees**, then hangs vertically. Measured from the ring centre to the
lower cloth centre, the outward offset is 9 cm and the angle is **3.39 degrees**.
The knee is centred at **world Z 65 cm**, with a smooth 14 cm transition over
**Z 58–72 cm**. The lean diminishes with draw; Closed has zero tilt and its
wave centre remains at world Y 867.5 cm. Fold amplitudes are solved independently
for each row against actual polyline arc length, including the unchanged corner
reach. The original hem remains around Z 22–23 cm.

| Draw amount | Top arc cm | Mid arc cm | Arc at Z 60 cm | Hem arc cm | Minimum tub clearance cm |
| --- | --- | --- | --- | --- | --- |
| 0 | 210.000 | 210.000 | 210.000 | 210.000 | 4.963 |
| 0.25 | — | — | — | — | 2.416 |
| 0.5 (corrected) | 210.000 | 210.000 | 210.000 | 210.000 | 1.989 |
| 0.75 | — | — | — | — | 2.104 |
| 1 | 210.000 | 210.000 | 210.000 | 210.000 | 2.638 |

Validation also samples 21 draw amounts at 0.05 increments. All row lengths
remain 207.369–211.757 cm (within 1.3% of 210 cm); minimum sampled tub clearance
is 1.975 cm. Clearance uses the actual BA_Tub03_Body triangulated front surface,
matching X/Z, on both moving cloth layers below Z 60 cm. Triangle interiors are
sampled at barycentric subdivision 8; points outside the tub silhouette are
excluded. These are geometric sampling results, not a continuous collision proof.

| Draw amount | World X bounds cm | World Y bounds cm | World Z bounds cm |
| --- | --- | --- | --- |
| 0 | 622–676.5 | 856.181–886.2 | 22–219.8 |
| 1 | 490–676.5 | 864.735–886.2 | 22–219.8 |

Bounds include rings, clips and corner overlap. Conversion, verified against the
original assembly references:
`world_cm = (580 - 100*BlenderX, 907 + 100*BlenderY, 100*BlenderZ)`.

**UV observation:** the original floral mapping tiles twice across roughly
114 cm of fabric width and once down roughly 197 cm. Its vertically stretched
flowers remain unchanged; this revision preserves UVs while preserving the
geometric cloth width through the morph.

### Export and review

FBX settings match ARC-CURTAINS-01: selected mesh + armature only,
`apply_unit_scale=True`, `add_leaf_bones=False`, `bake_anim=False`,
`path_mode='AUTO'`; default forward -Z, up Y, global scale 1, all local scaling.
Scene units are metric, scale_length 1 (metres). The clean FBX round trip confirms
all three shape keys, two BlendShapeChannels, and one CurtainRoot bone.
Only the moving mesh and rig are exported; assembly references stay in the blend.

Updated room-side previews: `previews/curtain-open.png`,
`previews/curtain-halfway.png`, `previews/curtain-closed.png`, and the east-end
close-up `previews/curtain-open-clearance.png`.

`model/validate_curtain_shape.py` reopens the saved blend, imports the FBX into
a factory-empty scene, checks morphs/rig/rings/row lengths/clearance, and writes
`curtain-validation.json`. `model/author_curtain_shape.py` rebuilds from an original
pre-morph blend supplied after `--`; obtain that file from Git before commit
5b70f94. It refuses to stack changes on an already-authored source. Run with
Blender `-b --python <script> -- <original.blend>` (validation needs no `--` path).
No Unreal files were modified or editor launched for this source revision.
