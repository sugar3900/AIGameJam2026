# ARC-WINDOW-BATH-01 — frosted bathroom sash

A shorter, frosted variant of the reviewed `ARC-WINDOW-01` period kit. The existing multiview concept and generated ivory paint texture are retained as style references; the component positions and sash heights were rebuilt for the bathroom opening without squashing the original trim and muntin cross-sections. The reference sheet depicts the larger living window, not this variant's measured proportions.

## Dimensions and assembly

The A+ bathroom opening is **1.15 m wide × 0.80 m high**, from **1.50 m sill to 2.30 m head** above floor. The frame FBX occupies **1.38 × 0.24 × 1.052 m** including protruding trim, sill and apron. Frame jambs lie within the nominal aperture; the wall still requires a real opening and collision setup. Coordinate the sill, bath, shower and tile surround in the actual bathroom. Bathroom elevation may be viewed at `docs/03 Art & Audio/Apartment Design/elevations/bathroom.svg`.

All five FBX exports share a **floor-centered origin**, opening centered on X, Z up and room side toward −Y. Place them with the same transform:

- `ARC_Window_frame.fbx`: frame, stops, interior casing, projecting sill and apron.
- `ARC_Window_upper_sash.fbx`, `ARC_Window_lower_sash.fbx`: separate short sashes with muntins and latch.
- `ARC_Window_upper_glass.fbx`, `ARC_Window_lower_glass.fbx`: separate panes. Parent each pane to its sash for movement.

The lower sash and its pane move together upward in the 0.18 m open-pose preview; the exports are closed and **do not include an animation**. Test the actual track, latch, collision, axis and swing/slide in Unreal. Preview wall, card, camera and lights are excluded from FBX.

## Frosted glass and validation

The Blender glass is a rough, partially transmitting **preview material**, not a finished Unreal material. Rebuild frosted glass in Unreal with suitable opacity, roughness, reflections and privacy, and inspect it against the actual exterior and bathroom lighting; the preview card is not an exterior environment. Rebuild the painted-wood material from `textures/ivory-window-a.png`, since FBX does not preserve Blender's shading graph. The glass should obscure details rather than read as a blue-clear or opaque painted panel.

`model/build_window.py` regenerates the Blender file, exports and closed/open/front/back previews; `model/validate_fbx.py` reimports all five exports. The latest `model/validation.txt` confirms finite geometry and normals, UVs, no zero-area triangles, and the bounds above. The nominal aperture is derived from the jamb layout (outside edges x=±0.575 m, head z=2.30 m, bottom z=1.50 m), not verified in a game wall. Studio poses have been visually checked, but actual Unreal appearance, privacy, wall collision, operation and fit remain untested.
