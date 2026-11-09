# KI-RANGE-01 — vintage kitchen range

Concept: `concepts/range-v1.png` supplies front, back, side, three-quarter and open-oven references. Generated painted enamel texture: `textures/range-enamel-v2.png` (also packed in the Blender source).

`model/KI-RANGE-01.blend` contains a real hollow oven, two fixed racks, four cast-iron burners and grates, controls, and a separate door. Regenerate with Blender `-b --python model/build_range.py`; validate FBX round trips with `model/validate_range.py`.

- Coordinates: metres, Z up, front is -Y. Main carcass is 0.75 m wide × 0.70 m deep; protruding controls bring total depth to 0.732 m. Backguard top is 1.07 m above floor.
- `KI_RANGE_Body.fbx` has a floor-level origin. `KI_RANGE_Door.fbx` is a separate mesh with hinge origin at `(0, -0.363, 0.23)` in assembly coordinates; rotate about local X toward +82° to open outwards. Place that pivot at the corresponding position relative to the body in Unreal; verify axis conversion on import.
- Knobs are fixed geometry; the oven door is the supported moving part. Oven window is an opaque stylized dark inset on both outer and inner faces; hinges and burner support details are modeled. Fixed racks are included with the body; no internal oven light is authored.
- `previews/range-closed.png` and `range-open.png` show both states. The generated enamel uses color-only brushwork and subtle wear, with no displacement.
- Both FBX round trips pass finite vertex/UV, UV-presence and nonzero-face-area checks. Unreal material wiring, collision, pivot behavior, interaction reach and in-context appearance have not been tested. Painterly treatment remains subtler than the concept and should be reviewed in room lighting.
