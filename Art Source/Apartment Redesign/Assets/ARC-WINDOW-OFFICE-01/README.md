# ARC-WINDOW-OFFICE-01 — office double-hung sash

A 1.40 m variant of `ARC-WINDOW-01`, sharing its period style, original concept reference and generated ivory paint texture. Jambs, rails, muntins, sill and casing are rebuilt for the new opening, preserving original cross-section widths rather than nonuniformly scaling the model. The multiview reference depicts the larger living window; this model and A+ plan govern dimensions.

## Dimensions and assembly

The A+ office opening is **1.40 × 1.40 m**, sill **0.90 m** and head **2.30 m** above finished floor. The outer edges of the modeled jambs are x = ±0.70 m; head and bottom edges are z = 2.30 m and 0.90 m. Casing, projecting sill and apron extend beyond the aperture: frame export bounds are **1.63 × 0.24 × 1.652 m**. Cut an actual wall aperture and ensure collision does not span it; verify desk, curtain and camera clearances in the office.

All five FBXs have a **floor-centered origin**, aperture centered on X, Z up, room-facing side toward −Y. Place them with the same transform:

- `model/ARC_Window_frame.fbx`: frame, casing, stops, projecting sill and apron.
- `model/ARC_Window_upper_sash.fbx` and `model/ARC_Window_lower_sash.fbx`: sashes, muntins and latch; both sash widths are 1.27 m.
- `model/ARC_Window_upper_glass.fbx` and `model/ARC_Window_lower_glass.fbx`: separately exported panes; parent each pane to its sash.

Exports are closed and include **no authored animation**. The `window-front-open.png` preview raises the lower sash and its pane together 0.35 m along local Z; upper sash stays in its track. Verify movement, stops, axes and collision in Unreal. The preview wall, exterior color card, lights and camera are not exported.

## Materials and verification

The paint texture is `textures/ivory-window-a.png`; recreate painted-wood shading in Unreal because Blender nodes do not transfer via FBX. The glass and flat exterior card are preview-only treatments; implement glass or an exterior view in Unreal and check lighting, reflections, opacity and depth sorting. No Unreal review has occurred.

Run `model/build_window.py` with headless Blender to regenerate the source, FBXs and previews. `model/validate_fbx.py` reimports all five exports; `model/validation.txt` records finite positions, normals and UVs, with no degenerate geometry or UV triangles. Closed and 0.35 m open poses were visually inspected in Blender. Wall fit, room lighting, material, sash motion and collision still require in-game validation.
