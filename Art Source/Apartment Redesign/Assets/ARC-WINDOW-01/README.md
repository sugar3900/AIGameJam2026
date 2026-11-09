# ARC-WINDOW-01 — double-hung window

Provisional modular window, modeled against the living-room 1.60 m wide × 1.40 m tall nominal opening, sill at 0.90 m and head at 2.30 m. `concepts/window-multiview-v1.png` is the generated multi-view design reference; `textures/ivory-window-a.png` is the generated paint surface. The finish is stylized, with no modeled paint relief.

## Pieces and dimensions

All FBX pieces share a floor-centered origin at the middle of the window, with the opening centered on X, Z up, and room-facing side toward −Y. Place pieces together at the same transform. The frame includes casing, apron, sill and stops and has overall FBX bounds **1.83 × 0.24 × 1.652 m**. It extends beyond the wall opening, which is intentional: the frame is not a wall or a cutout. The top trim reaches approximately 2.435 m above the floor and sill/apron extend below the 0.90 m opening. Specify and cut a real 1.60 × 1.40 m wall aperture, and avoid auto-convex collision spanning it.

- `ARC_Window_frame.fbx` — frame, casing and sill.
- `ARC_Window_upper_sash.fbx`, `ARC_Window_lower_sash.fbx` — separate six-pane sash geometry and latch pieces.
- `ARC_Window_upper_glass.fbx`, `ARC_Window_lower_glass.fbx` — one continuous glazing piece for each sash behind the muntins. Parent each pane to its corresponding sash if movement is implemented.

Sashes are separate but **no slide animation is authored**. Both use the same floor-centered export origin, so slide along the actual window's local up axis from the closed placement; confirm movement, track clearance, stops and collision in Unreal. UVs and painted texture are included, but FBX does not transfer the Blender shading graph. Import the diffuse texture separately and recreate a restrained rough painted-wood material. Glass is a Blender preview placeholder: author an Unreal glass material (or exterior-view treatment), adjust two-sidedness/translucency, reflections, depth sorting and exterior day/night appearance in context. The preview wall, exterior color card, camera and lights are not in the FBX exports. The `.blend` contains them, labeled `PREVIEW ONLY`.

## Adapting to other openings

The living opening is the only size this export is built for. Kitchen and bedroom use 1.10 × 1.40 m, office uses 1.40 × 1.40 m, and bathroom is 1.15 × 0.80 m with frosted glass. Do not silently fit by changing only the wall cutout: scale all five pieces together about their shared origin, or preferably revise component geometry so casing width, sill projection and muntin thickness stay plausible. Scaling X by 1.10/1.60 or 1.40/1.60 changes every trim and muntin width; bathroom also needs height and sill repositioning plus frosted glass. Recheck the sash overlap and aperture on each variant. A future parameterized Blender rebuild is preferable for final bespoke widths.

## Verification and remaining review

`model/build_window.py` rebuilds the model and previews with headless Blender; `model/validate_fbx.py` reimports all five FBXs. The latest run in `model/validation.txt` found finite positions and normals, UV layers, and no zero-area geometry or UV triangles. The studio renders include closed front/back and a 0.35 m open-sash pose. Frame joints and sash-to-sill overlap were adjusted to remove the visible corner gaps and black junctions in those views. These are studio renders, not Unreal renders. Glass currently reads flat in preview because the exterior is only a solid color card. Unreal materials, pivots, actual opening collision, sash movement, resized variants, exterior view and lighting remain untested.
