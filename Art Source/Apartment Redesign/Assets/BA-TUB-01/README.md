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


## Animated shower curtain (source revision)

Use `model/BA_Curtain_Animated.fbx` for the new moving curtain. The existing
`BA_Curtain.fbx` is deliberately unchanged so the static export remains usable.
The saved `BA-TUB-01.blend` contains `Curtain_panel_sliding`, its single-bone
`Curtain_panel_sliding_Rig`, and shape keys **Basis**, **Closed**. Drive Unreal's
**Closed** morph weight from **0 = gathered open at the east end** to **1 = drawn
west to world X 490 cm**. Linear interpolation at 0.5 is acceptable; there is no
corrective key or action. All vertices are weighted 1.0 to **CurtainRoot** through
an Armature modifier named `Skin`, matching ARC-CURTAINS-01.

The moving asset now uses the assembly floor origin, rather than the old sliding
pivot. Place it on the shared (580, 907, 0) cm / yaw 180 assembly transform; the
old +125 cm parking offset and rigid slide are no longer appropriate. Rings
translate on the straight rod (world Y 872 cm); their centres span approximately
X 625–659 cm open, and 502–650 cm closed. Original circular ring geometry is
preserved. Seven metal clips join their lower front quadrants to the cloth header.
The cloth's east selvage has a short permanent corner overlap to meet the fixed
return near X 676.5, Y 886 cm while the rings stay on the straight run. Main cloth
folds are on the room side, clear of the tub rim; the hem is around Z 22–23 cm.

The original cloth topology, loop UVs, and material slot names `Floral_cotton`
and `Aged_chrome` are retained. **UV observation:** the original mapping tiles the
floral twice across roughly 114 cm of fabric width and once down roughly 197 cm,
so the flowers appear vertically stretched. This mapping was not corrected.

FBX export matches the precedent: selected mesh + armature, `apply_unit_scale=True`,
`add_leaf_bones=False`, `bake_anim=False`, `path_mode='AUTO'`; default forward -Z,
up Y, global scale 1, all local scaling, with morphs preserved. Scene units are
metric, scale_length 1 (metres). No animation bake or leaf bone is required.

Room-side previews with the L rod, ROUND3 tub and fixed return:
`previews/curtain-open.png`, `previews/curtain-halfway.png`,
`previews/curtain-closed.png`. The original tub/plumbing objects are preserved
in a hidden `Original tub and fixtures (preserved)` collection; preview references
are in `Preview assembly (not exported)`. Only moving mesh + rig go into the FBX.

`model/validate_curtain_shape.py` reopens the saved blend and imports the FBX into
a factory-empty scene. `curtain-validation.json` records the keys, single bone,
FBX BlendShapeChannel, ring checks, and round-trip bounds. The conversion verified
against the supplied original/rod/tub bounds is:
`world_cm = (580 - 100*BlenderX, 907 + 100*BlenderY, 100*BlenderZ)`.

| Closed weight | World X cm | World Y cm | World Z cm |
| --- | --- | --- | --- |
| 0 | 622–676.5 | 862.656–886.2 | 22–219.8 |
| 0.5 | 556–676.5 | 862.656–886.2 | 22–219.8 |
| 1 | 490–676.5 | 862.656–886.2 | 22–219.8 |

Bounds include the corner overlap, so open cloth extends beyond the roughly
40 cm ring gather. Closed covers the tub X 496.5–663.5, meets the return, and
retains the original ring-top height 219.8 cm. Rod radius along the straight run
is 1.2 cm (3.2 cm is the wall flange radius); the existing rings clear the tube.
No Unreal import was performed.

For authoring reproducibility, `model/author_curtain_shape.py` accepts the original
pre-morph blend path after `--`; obtain that file from Git before this revision.
It preserves the old cloth loop UVs and builds both poses, rig, export and previews.
It refuses to run on an already-authored blend. Run either script with Blender
`-b --python <script>` (and `-- <original.blend>` for rebuilding).
