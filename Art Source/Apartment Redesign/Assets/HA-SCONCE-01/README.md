# HA-SCONCE-01 — hall gooseneck sconce

**Status: ready for parent visual review; Unreal integration untested.** One wall light, intended for the paired placements HA-SCONCE-01/02 in the gallery. `concepts/sconce-multiview-on-off-v1.png` shows the selected on/off and multi-view design. The preview is a stylized interpretation; generated references can disagree, so source geometry and stated dimensions govern.

## Dimensions, coordinates and assembly

Blender metres; wall plane Y=0, visible face toward -Y, Z up, origin at centre of wall plate. All three FBXs share the same origin and should receive the same world transform:

- `model/HA_Sconce_Hardware.fbx`: curved gooseneck, aged-brass mounting plate, socket, fasteners.
- `model/HA_Sconce_Shade.fbx`: opal bell and rolled lip.
- `model/HA_Sconce_Bulb.fbx`: separate bulb.

Assembly bounds are approximately **0.122 m width × 0.141 m projection × 0.207 m height**, against the inventory's nominal 0.14 × 0.14 × 0.24 m. Plate centre is at z=0; geometry extends approximately 0.042 m below and 0.165 m above it. Place the wall datum directly on the wall without z-fighting. The shade is an open, single-sided surface with a separate rolled lip, so configure double-sided rendering or add thickness if needed for visible underside views. Its rear reaches y=-0.019 m and does not meet the wall. Test corridor camera, collision and placement with the actual hall shell.

## Materials and light

`textures/aged-brass.png` and `textures/opal-glass.png` reuse the independently generated candidates selected for `ARC-CEILING-LIGHT-01`, keeping the fixtures visually coherent. Blender uses image color on the brass with metallic 0.60 / roughness 0.54, and image color on opal glass with roughness 0.43. The paint-like color variation is a rendering style, not physical thick paint. FBX does not transfer the full Blender shader network: recreate materials, including two-sided shade, in Unreal.

`previews/sconce-off.png` and `previews/sconce-on.png` use the same studio lights; the on state adds a warm point light and emission on shade/bulb. Those lights are **preview-only**, and the difference is deliberately subtle in a brightly lit studio. In Unreal, add a warm local light, make independently controllable material instances for bulb and shade, tune intensity/exposure in the hall and verify the switch state. Geometry itself does not toggle lighting.

## Rebuild and validation

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/HA-SCONCE-01/model/build_sconce.py'` from the worktree root. Run `model/validate_fbx.py` similarly. Each exported FBX was reimported in clean Blender; `model/validation.txt` records mesh bounds, vertex/triangle counts, finite geometry/UVs and zero-area checks. All three components share the wall-plate origin. The source blend includes preview wall, camera and lights; those are not exported. Unreal import, shade normals/underneath visibility, in-room material, lighting, collision and on/off interaction remain untested.
