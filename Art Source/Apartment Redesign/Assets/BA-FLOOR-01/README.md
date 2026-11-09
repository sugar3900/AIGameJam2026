# BA-FLOOR-01 — bathroom mosaic floor

A period-inspired ivory hexagonal mosaic with muted blush flowers, designed to complement the existing BA-TILE-01 pink bathroom wall tile. The material should look hand-painted through its color and brushwork, while the floor remains an attractive, usable old surface.

## Design and files

- `concepts/hex-floral-a.png` and `concepts/square-diamond-b.png` are independent generated concepts based on the apartment reference. A was chosen: its small hexagons and flowers give the bathroom a distinct period character without duplicating the square wall tile. B is a viable alternative but reads more regular and glossy. The selected concept has baked lighting and imperfect geometry and is a design reference, not the repeating texture.
- `textures/ivory-glaze.png` is an independently generated, ungridded painterly ceramic texture. In Blender, geometry samples many portions of the texture; the ivory shader blends it 30% toward linear RGB `(0.79, 0.66, 0.57)` and the rose shader 80% toward `(0.56, 0.28, 0.27)`. Recreate those mixes in Unreal. Grout is warm cream. The texture need not tile on its own because it is sampled inside individual hexagons.
- `model/BA_FLOOR_MODULE.fbx` contains one mosaic top mesh with two material slots plus a solid grout substrate. Extents **0.9000 × 1.03923 m**, surface Z approximately +0.002 m, substrate bottom -0.025 m. Flat-topped hexagons have 0.030 m circumradius, with ~0.001 m edge inset. Modules repeat at exactly +0.9000 m along X and +1.03923048 m along Y; these dimensions follow the hex lattice and preserve the stagger. Partial perimeter tiles are clipped to the module rectangle. Do not stretch to fill the room, as that distorts hexagons and seams; cut perimeter geometry or author a floor-shaped mesh.
- `model/BA_FLOOR_WEAR.fbx` is a separate 1.80 × 2.07846 m optional overlay using generated alpha `textures/wear-overlay.png`; it is not part of the repeating module. The preview places it over four modules at Z +0.0035 m. It does not cover the full 3.1 × 3.95 m bathroom. Place selectively or author further nonrepeating coverage; don't repeat identical scuffs on every module.
- `model/BA-FLOOR-01.blend` contains the four-module demonstration, wear plane, preview lighting and camera. `model/build_floor.py` regenerates source, exports and preview renders. `previews/mosaic-repeat.png` shows four modules, while `previews/mosaic-worn.png` adds the independent wear overlay.

## Unreal handoff and limitations

Import FBX with the intended 100 cm/m scale and verify axis and pivots. Assign an sRGB glaze texture and recreate the two color mixes described above, with roughness ~0.79; assign warm cream grout separately. The physical tile UVs and two material assignments are baked; node graphs are not transferred by FBX. Two material slots for the mosaic have a draw-call cost, so consider a baked color mask or vertex colors later if profiling warrants it.

Use simple floor collision on the substrate rather than collision for individual tiles. The optional wear mesh should have no collision or shadow, and a two-sided translucent material using the alpha channel of `wear-overlay.png`, initially multiplied by 0.35 and tinted subdued umber (preview linear RGB 0.30, 0.18, 0.12). Alternatively implement it as a decal; the preview only establishes the mesh approach. Check alpha import, sorting, z-fighting, floor-edge clipping, contact shadows and the chosen amount of wear in engine. The regular flower pattern repeats within each module and remains a design choice to judge in the assembled bathroom. Unreal appearance, materials, collision and room-scale placement have not been tested.

`model/validate_fbx.py` reimports both FBXs and checks finite vertices and UVs, nondegenerate triangulation, dimensions, and matching position/UV/material at 42 X-edge and 22 Y-edge vertices. Both exports passed in Blender 5.2.3. The module's perimeter UV seams match at the authored cadence; this does not replace a visual in-engine seam check.

## Image generation prompts

Built-in image generation produced the two design candidates, independent ungridded glaze and transparent wear image. Prompts requested (A) small ivory hexagonal mosaic with blush flowers; (B) small square ivory mosaic with rose diamond accents; (glaze) continuous painterly ivory ceramic without tile lines; and (wear) sparse translucent soft warm scuffs. Candidate A and B used the project's painterly-fixer-upper concept as a style reference.
