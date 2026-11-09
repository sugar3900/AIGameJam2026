# HA-SHOES-01 — hallway tray and two pairs of shoes

Provisional art for the A+ hallway; Blender export only, not imported or tested in Unreal. `concepts/shoe-tray-multiview.png` is the generated reference for a shallow tray with brown lace-ups and sage slip-ons. The models are intentionally simplified stylized footwear; the brown pair has modeled lace bows, both styles have toe and vamp seams, and the left/right uppers are subtly offset with tapered heels; these remain simplified shoes rather than anatomically exact lasts. The shallow openings are modeled with a cut and an inset lining. Review their appearance from the actual hallway camera.

## Dimensions and assembly

Blender uses metres, Z up, tray center at floor origin, long dimension X, toe direction −Y. The tray with its inset handles measures **0.378 × 0.248 × 0.0525 m**. Four individual shoes measure **0.080 × 0.222 m** each, narrower than the inventory's approximate 0.11 m shoe width so they fit side by side. The tray and shoes therefore occupy essentially the entire 0.38 × 0.25 m nominal footprint, leaving almost no tolerance for collision, trim or the door. Check the intended hall placement, actual capsule and entry-door swing in engine; shoe scale is a design tradeoff, not verified against the character.

`model/HA_ShoeTray.fbx` and the four `HA_Oxford_1/2.fbx` and `HA_SlipOn_1/2.fbx` are separate static mesh exports; `model/HA-SHOES-01.blend` is the editable source. In the Blender scene the tray origin is (0,0,0) and shoe origins are `(-0.135,0,0.008)`, `(-0.045,0,0.008)`, `(0.045,0,0.008)`, `(0.135,0,0.008)` m relative to it. These positions are present on FBX reimport in Blender. Verify Unreal's imported origins and axis conversion before assembly; shoe parts are movable but no pickup animation or gameplay is included. Each shoe sole contacts the tray floor at z=0.008 m. Two pairs use repeated geometry and textures.

## Materials

`textures/leather-canvas-sheet.png` is an independently generated material sheet. In Blender the leather samples UV × `(0.47,0.94)` + `(0.02,0.03)` and the sage canvas samples UV × `(0.47,0.94)` + `(0.51,0.03)`; the two regions have no seam guarantee and should be remapped the same way in Unreal or baked to separate textures. The tray is a simple aged-metal material with a lighter rim; soles, lining and laces are separate color materials. All stylistic texture is color only. FBX does not transfer the Blender shader graph; reconstruct and evaluate colors, roughness, UV seams and wear in Unreal. The image generator's material sheet is a reference for the chosen palettes, not a guarantee of a seamless UV texture.

## Rebuild and validation

From the worktree root run Blender headlessly with `--background --python 'Art Source/Apartment Redesign/Assets/HA-SHOES-01/model/build_shoes.py'`; this rebuilds, exports and renders. `model/validate_fbx.py` reimports each FBX in a clean scene and checks finite geometry/normals/UVs, a UV layer, no zero-area mesh triangles and footprint limits. `model/validation.txt` records the latest reimport: tray 2,508 triangles, each oxford 8,806 and each slip-on 5,734. Converted lace/handle meshes use solid-color materials and have an active UV layer; their unused UVs are not asserted nondegenerate. The original boolean operation leaves tiny triangles that are explicitly removed before export.

`previews/tray-perspective.png` and `previews/tray-top.png` are studio renders. Unreal import, texture/material reconstruction, collision, actual door clearance, shoe pickup and in-room appearance are untested.
