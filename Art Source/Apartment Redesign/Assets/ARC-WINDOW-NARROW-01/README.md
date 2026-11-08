# ARC-WINDOW-NARROW-01 — 1.10 m double-hung window

A kitchen/bedroom width variant of the reviewed `ARC-WINDOW-01`, using its concept and painted ivory texture. It is rebuilt from the component dimensions, not achieved by nonuniformly scaling the living-room window: casing, sash rails, muntins, sill projection and head trim retain their original profiles. Three muntin columns adapt to the narrower sash. The retained concept sheet illustrates the parent window's design and is not a blueprint for this width.

## Dimensions and placement

Designed for a **1.10 × 1.40 m** nominal wall opening, with sill 0.90 m and head 2.30 m above floor, as in the A+ kitchen and bedroom window schedule. Frame and projecting trim extend beyond the opening; measured frame export bounds are **1.33 × 0.24 × 1.652 m**. The sill/apron extend below the opening, and head trim rises to approximately 2.435 m above floor. Cut a real wall aperture and keep wall collision clear. Check furniture, window treatments and trim against the opening in the actual room; the bathroom and office use different sizes and need separate variants.

All components share the same floor-center origin, opening centered on X, Z up, room-facing side toward −Y. Place the five FBXs together using the same transform:

- `model/ARC_Window_frame.fbx`: frame, casing, stops, sill and apron.
- `model/ARC_Window_upper_sash.fbx`, `model/ARC_Window_lower_sash.fbx`: upper/lower sash and latch parts, each 0.97 m wide.
- `model/ARC_Window_upper_glass.fbx`, `model/ARC_Window_lower_glass.fbx`: separate continuous panes behind the muntins. Parent each pane to its respective sash.

Exports are in the closed pose and contain **no authored animation**. The front-open preview lifts the lower sash and pane by 0.35 m along local +Z while the upper sash remains in its track. This demonstrates the intended relationship, not an Unreal animation or collision test. Check track clearance, pivots, stops and importer axes in engine. The preview wall, exterior color card, camera and lights are not exported.

## Materials and checks

`textures/ivory-window-a.png` is the original generated painted texture; FBX does not transfer Blender's complete material graph. Recreate the restrained painted-wood material and age in Unreal. The blue-grey glazing and solid exterior card are illustrative only. Author actual glass or an exterior-view treatment in engine, including reflections, opacity, sorting, daylight and collision. No UE rendering or playtesting has been done.

`model/build_window.py` rebuilds the blend, exports and front, back, open and perspective studio previews; `model/validate_fbx.py` imports all five exports. `model/validation.txt` records the latest FBX round trip: finite positions/normals/UVs, UV layers present, and zero degenerate geometry or UV triangles on each export. The closed front, rear and 0.35 m open previews were visually inspected. In-room review of trim joints, glass, sash movement, wall aperture, lighting and camera is still required.
