# BA-TUB-01 — vintage bathtub and shower

## Source and references

- `concepts/tub-tile-states-v1.png`: selected before/after repair concept. Tile damage and wall are separate assets.
- `refs/multiview-v1.png`: generated multi-view guide. Reference views contain AI inconsistencies; the source blend and A+ plan govern dimensions and construction.
- `textures/enamel-albedo.png`, `textures/enamel-brush-v2.png`, `textures/floral-albedo.png`: generated color textures. The enamel preview mixes the first two at 0.6 for visible medium brush marks. Hook both into Unreal materials after import; Blender material nodes do not automatically transfer as finished Unreal materials.
- `model/build_tub.py`: reproducible Blender script. Run with `/Applications/Blender.app/Contents/MacOS/Blender -b --python <script>`.
- `model/BA-TUB-01.blend`: editable source. `previews/three-quarter.png`: Blender studio render.

## Dimensions and placement

Blender units are metres. The tub body is 1.67 m long by 0.68 m wide, with rim at z=0.57 m and feet down to z=0.01 m. Length lies along X, front is -Y; fixture mounting side is +Y. The tub is centred at the origin in XY and the common placement origin is at floor height. The riser is shifted to the west end to clear the A+ south-wall window when the tub centre is placed at x=5.80 m. Confirm plumbing, placement and window clearance with the final room shell in 3D.

The model has five FBX groups: `BA_Tub.fbx`, `BA_TubFixtures.fbx`, `BA_Curtain.fbx`, `BA_TapLeft.fbx`, and `BA_TapRight.fbx`. They preserve their common assembled coordinates; import with combined meshes or preserve FBX transforms as appropriate. Fixtures and curtain can be placed independently from the tub. Tap handle pivots are at (-0.84, 0.29, 0.96) and (-0.66, 0.29, 0.96), rotating about local Y; the curtain and rings are one rigid sliding panel with pivot (0.92, -0.35, 2.18), sliding along local X. These exports round-trip in Blender with those transforms; confirm the Unreal importer retains the intended pivots before wiring gameplay.

## Checks and review status

A headless Blender FBX round trip found 0 nonfinite vertices, 0 nonfinite face normals, and 0 zero-area faces on each export. All 49 imported mesh objects have UV layers. The Blender preview shows a hollow basin, trim, feet, drain, tap and shower, with the floral image texture. The enamel now blends two generated painterly color maps, with visible warm/cool strokes and localized specks. The warm studio preview and sculpted feet remain subject to lead review and in-context texture/lighting iteration. No Unreal import or material validation has yet been run. A wall tile crack/repair state must be supplied separately.
