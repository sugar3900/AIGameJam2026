# BA-FOLDED-TOWEL-01 — folded bathroom towel

Status: candidate for visual review; Unreal import and in-room appearance are untested. The generated `concepts/folded-towel-multiview.png` guides the form and colors. The folded mesh uses the existing bathroom `BA-TOWEL-RAIL-01/textures/terry.png` texture, copied locally to keep this asset self-contained; the ivory and dusty-rose tints echo the hanging towels.

## Geometry and placement

`model/BA_Folded_Towel.fbx` is one static joined mesh with three softly rounded fold layers and two rose stripes assigned to actual top-surface faces. Reimported bounds are approximately **0.300 × 0.198 × 0.078 m**, with **1,060 triangles**. The tabletop/shelf-centred origin is at the bottom of the towel, Z up, long axis X. Place the origin on the shelf; the conceptual front is −Y. Export settings are −Y forward / Z up, but verify the Unreal importer conversion and contact with the actual shelf before placement. No folding animation, pickup logic or custom collision is authored.

The stripe boundaries split the upper fold’s actual top faces and use a second material slot; no separate overlapping stripe geometry is present. The stripes end at the start of the rounded side bevel. These are stylized folded layers, not a simulation of a continuous folded towel.

## Materials

The `Terry_Ivory` and `Terry_DustyRose` slots each use `textures/terry.png` in sRGB multiplied in Blender by their respective tint with factor 0.88 and high roughness (0.92). Tints are `(1.0, 0.91, 0.80)` and `(0.66, 0.25, 0.24)` in Blender's color-input convention; recreate or bake the material mix in Unreal, since the full node graph does not transfer via FBX. Recheck cloth texture scale, stripes and shading in room lighting. Decorative collision should generally be disabled unless a later interaction calls for it.

## Rebuild and checks

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_towel.py` and `... -b --python model/validate_fbx.py`. The source `.blend` contains the towel plus preview-only floor, lights and camera; only the selected towel mesh is exported. `model/validation.txt` records Blender FBX reimport geometry, UV presence/finiteness, nondegenerate geometry triangles and bounds checks. UE orientation, materials, collision, stripe material assignment and shelf contact remain untested.

The multiview concept was generated with the built-in image tool using the project painterly fixer-upper image as style reference and the requested ivory terry/dusty-rose stripe and 30 × 20 × 8 cm dimensions. The copied terry texture was previously generated for the bathroom basket and reused by the towel rail.
