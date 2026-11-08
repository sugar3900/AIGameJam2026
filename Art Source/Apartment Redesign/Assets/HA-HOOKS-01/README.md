# HA-HOOKS-01 — hall coat-hook rail

Status: **ready for parent visual review**. This is a static hallway rail; coats and other objects are separate assets. The concept sheet `concepts/hooks-multiview-v1.png` is a painterly generated multiview reference. Geometry and measured dimensions take precedence where that illustration disagrees.

## Model and placement

- Blender metres, Z up; the wall plane is Y=0, visible face projects toward −Y, wall-center datum at (0,0,0).
- `model/HA_Hooks.fbx` contains a walnut board, four double brass hooks, mounting plates and fasteners. It is a static assembly; no animation or physics is authored. Combine the FBX's 29 mesh pieces at import or assemble them with their FBX transforms intact. Confirm placement/origin and collision in Unreal before use.
- Reimported bounds: **0.720 × 0.067 × 0.120 m** (width × wall projection × height). Mount back flush to the wall. The hall inventory maximum projection is 0.07 m; actual character and camera clearance remain to be checked. Place near the hall coat closet per the floor plan/elevation, without obstructing the sliding panels.
- The Blender source `model/HA-HOOKS-01.blend` includes a preview-only wall, camera and lights. Those are excluded from the FBX.

## Materials and validation

The wood texture is reused from `LV-CHEST-01` and the brass from `HA-SCONCE-01`, to match the approved palette. Blender applies the same walnut hue/saturation/value treatment as the chest: saturation 0.68, value 1.35. Brass uses metallic 0.60 and roughness 0.54; the wood is rough. Recreate these material treatments in Unreal because FBX does not transfer the complete Blender shader graph. Painterly variation is in the color texture, not physical paint relief. The two textures are packed into the blend and also under `textures/`.

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/HA-HOOKS-01/model/build_hooks.py'` from the worktree root to regenerate. Run `model/validate_fbx.py` similarly. A clean Blender FBX reimport (`model/validation.txt`) found 29 meshes, 6,296 vertices, 12,348 triangles, finite positions and UV coordinates, UV layers on all meshes, and no zero-area triangles. The exported geometry and previews were checked in Blender only. Unreal import, materials, collision, hallway placement and visual quality under game lighting remain untested.
