# LV-TV-01 — vintage television and stand

## Design and references

`concepts/tv-v1.png` is the selected image-generated front/back/left/right/perspective and on/off sheet. `textures/walnut-painted.png` is an image-generated painted wood albedo based on that sheet. The model uses a simplified but dimensioned period silhouette; the standalone render is a modeling preview, not proof of final in-game appearance.

## Source and exports

- `model/LV-TV-01.blend`: source, with named separate geometry and packed wood image.
- `model/build_tv.py`: reproducible headless build. Coordinates are metres, +Z up and -Y front.
- `LV_TV_body.fbx`: cabinet shell, television housing, dial details, vents, bezel, shelf and legs; origin at floor center. Overall body bounds 1.10 m wide × 0.46 m deep × 1.257 m high.
- `LV_TV_left.fbx`, `LV_TV_right.fbx`: distinct hinged cabinet doors. The hinge origins are respectively (-0.483, -0.218, 0) and (+0.483, -0.218, 0) in assembly coordinates; open left -90° / right +90° around Z. They are exported at the original world positions and retain hinge-local pivots.
- `LV_TV_screen_off.fbx`, `LV_TV_screen_on.fbx`: identical curved screen geometry with distinct materials. Use **one** screen mesh with a switchable material, or toggle the meshes, never show both simultaneously. The on material uses UV-based radial warm emission; recreate the radial ramp and emissive strength in Unreal. The off state is dark reflective glass with curved surface highlights.
- `previews/tv-off.png`, `tv-on.png`, `tv-doors-open.png`: Blender renders of the two screen states and hinged doors.

## Verification and limits

`model/validate_tv.py` reimports each FBX and checks finite vertices, UVs, and nonzero polygon areas. All five FBXs passed in Blender 5.2.3. The circular-dial detailing and painted wood are intentionally modeled at game-view scale. The Blender wood shader multiplies the image by (0.25, 0.23, 0.14) in linear space; recreate the tint in Unreal instead of importing the raw image alone. Check UV appearance, emissive screen, imported pivot transform, doors, collision and lighting in Unreal; none has been checked there yet. The standalone model has a smoother shaded finish than the richly rendered concept and needs review in the final room.
