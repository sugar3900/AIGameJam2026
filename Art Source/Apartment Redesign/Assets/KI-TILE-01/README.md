# KI-TILE-01 — kitchen checker linoleum

A 1 m × 1 m floor module with alternating 0.25 m cream and terracotta squares, as specified by ARC-FLOOR-KI / KI-TILE-01. The floor surface is at local z=0; the substrate extends 0.030 m downward. `model/KI_TILE_TOP.fbx` contains 16 top quads with baked UVs. `model/KI_TILE_SUBSTRATE.fbx` supplies the solid underlay and very fine dark seams. The actual top surface has an intentional 0.45 mm inset on each tile edge; the substrate covers the gaps.

## Concept and appearance

`concepts/checker-a.png` and `checker-b.png` are independently generated directions based on the apartment reference. A was selected for its quieter color variation and controlled wear; B is brighter and more orange. `textures/checker-selected.png` is a copy of A. The UVs sample interiors of both color quadrants, rotated per square, and exclude the source image's borders. This produces painterly surface marks without simply repeating the whole generated image. The 1 m pattern still repeats; judge it at room scale, especially across the 6.5 × 3.8 m kitchen.

`previews/checker-repeat.png` shows a 4 × 3 m arrangement of the exported module design. Checker colors align across module boundaries because each module contains an even number of squares in both axes. `model/KI-TILE-01.blend` contains the 12-module preview arrangement; the FBX files are **single** modules. Run `build_floor.py` in headless Blender to rebuild, and `validate_fbx.py` to reimport and verify finite geometry, UVs, nonzero face area, expected size, and checker parity at one-metre boundaries. Those checks passed in Blender 5.2.3.

## Unreal handoff

- Import the top and substrate meshes at 100 cm per metre and assemble using their exported transforms so the top is at the intended floor height; verify pivots and axis conversion after import. The top mesh bounds are 0.9991 m square due to its intentional inset; the substrate is exactly 1 m square and 0.03 m thick.
- Assign `checker-selected.png` as sRGB base color using the baked UV0 on the top mesh; use a matte roughness around 0.72. Assign a muted warm-brown material to the substrate, which forms the fine seams. Blender shader nodes do not automatically carry over through FBX.
- Tile modules in whole-metre steps; cut perimeter modules to room footprint instead of scaling them and changing square size. Use appropriate simple floor collision on the substrate, not individual quads. Test imported seams, normals, placement, lighting and collision in Unreal. The asset has not yet been imported or judged in the apartment.

## Optional room-scale wear overlay

`textures/wear-overlay.png` is a separately generated transparent wear image, not baked into the one-metre checker. `model/KI_TILE_WEAR_4x3.fbx` is a 4 × 3 m plane containing one UV-mapped face and is positioned 1.1 mm above the floor in the preview. `previews/checker-worn.png` and `checker-worn-detail.png` show the overlay; compare with `checker-repeat.png`. The marks are intentionally restrained and do not repeat with each checker module. The specific overlay covers only a 4 × 3 m portion of the 6.5 × 3.8 m kitchen; its position, any additional coverage, and floor-edge clipping must be authored for the final room. Avoid tiling it visibly.

In Unreal, make a two-sided **translucent** material for the overlay, sampling the alpha of `wear-overlay.png` multiplied by an adjustable scalar initially 0.38; use a subdued warm umber base color (the preview uses linear RGB 0.24, 0.14, 0.085), high roughness and no metallic. Disable collision and shadow casting on the overlay, and position it slightly above the floor with correct exported pivot. Alternatively use the alpha in a deferred decal material if better suited to the renderer; the Blender preview is a translucent mesh and does not validate the decal path. Verify alpha import, z fighting, sorting and appearance under final lighting. The source is `build_wear.py` and `KI-TILE-01-wear-preview.blend`; FBX reimport and UV/bounds checks pass using `validate_wear.py`.
