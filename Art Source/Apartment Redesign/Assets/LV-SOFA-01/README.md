# LV-SOFA-01

A vintage three-seat floral sofa with rolled arms, separate cushions, rose and teal pillows, a draped throw and turned wood feet. Coordinates are metres, Z up, front faces −Y, and the assembled model is centred on the floor. The body is approximately 1.99 m wide and 0.84 m deep; including the throw, overall width is about 2.04 m and height 0.98 m.

- `concepts/sofa-v1.png`: selected concept, including front, side, back and three-quarter views.
- `references/side-views-v1.png`: generated left and right side study. AI views are design references and need not agree perfectly.
- `textures/`: generated painted floral fabric and rose pillow albedo. Material slots also include wood, ochre piping, teal pillow and cream throw.
- `model/LV-SOFA-01.blend` and `.fbx`: source and assembled export. FBX has multiple named meshes; import as a combined assembly with scene origin retained if a single asset is desired. Cushions and throw remain independently editable in Blender.
- `previews/sofa-three-quarter.png`: warm-lit Blender preview.

Rebuild with Blender background mode using `model/build_sofa.py`. Run `model/validate_fbx.py` in Blender to check the FBX round trip. Latest validation: 44 meshes, zero non-finite vertices or UVs, zero zero-area faces. Source texture images are external, alongside the model; reconnect or import them when building Unreal materials.

The original source review preceded Unreal integration; see the dated findings below. Review cloth/arm joins and textile scale under final room lighting; the throw is stylized geometry, not a simulation or a crochet transparency map. Collision and engine material setup remain to be checked.

## Integration feedback — 2026-11-08

The integration team verified that the Blender **−Y front imports as +Y** under the current Unreal FBX import settings. The previous in-level sofa faced the wall; they corrected that placement with **yaw −90°**. This yaw belongs to that specific placement, not every future layout. Use the imported +Y front to calculate the world-facing direction specified in a new floor plan; verify visually before accepting placement. The source geometry and export are unchanged.

The current FBX contains no authored simple collision. The team applied complex-as-simple collision to its Unreal import; re-run `Tools/Editor/build_redesign_collision.py` after re-import and check player blocking/click traces.
