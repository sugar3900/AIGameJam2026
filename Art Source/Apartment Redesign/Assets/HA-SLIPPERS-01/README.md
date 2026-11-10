# HA-SLIPPERS-01 — worn burgundy house slippers

FIX-016 replaces the four-shoe entry display and tray with **one pair** of soft open-back slippers. Source reviewed; engine placement and appearance pending.

Generated concept and two material swatches are saved locally. The modeled pair has hollow lined toe uppers, open heels, quilted footbeds, layered soles, stitched welts and surface-following botanical embroidery. Left/right contours differ and the pair is slightly splayed. No tray is included.

## Files and import

`model/HA_SLIPPERS_01.fbx` contains `HA_Slipper_Left` and `HA_Slipper_Right`, each 11,778 vertices / 22,260 triangles. Import together or separately while retaining their common pair origin; do not center each mesh independently. Blender scene and reproducible headless build/validation scripts are in `model/`.

Metres, Z up, toes point source −Y, FBX −Y forward / Z up. Unreal keeps X and flips Y, so the imported toes face +Y before yaw. Floor-center origin; pair bounds approximately 25.54 × 29.78 × 7.26 cm. No collision or UCX: these are small decorative textiles, and the floor supplies walking collision.

Proposed placement: **(1170, 362, 0) cm, yaw +90°, scale1**, toes facing west into the room. Expected X1155.11..1184.89 / Y349.23..374.77 cm, leaving room between the bench and entry casing. Verify actual bench and door sweeps in engine. Retire all five old display actors (`HA_ShoeTray`, `HA_Oxford_1/2`, `HA_SlipOn_1/2`); keep the bench and entry interaction unchanged. Record the replacement under the existing hall-bench dressing identity.

## Materials

Six slots on each mesh, exact order/constants in `assembly.json`. Use both sRGB textures directly as Base Color, not multiplied by fallback constants. All materials opaque, metallic0, roughness.88; no emissive. Quilted footbed UVs preserve equal physical scale in both directions. The lined upper is actual double-surface geometry.

1. Slipper_LeatherSole
2. Slipper_QuiltedOatmeal → `textures/T_Slipper_Quilt.png`
3. Slipper_WornBurgundy → `textures/T_Slipper_Velvet.png`
4. Slipper_RoseBinding
5. Slipper_FadedFlaxThread
6. Slipper_Embroidery

## Review

`previews/pair.png` and `heel-openings.png` are source renders, not in-game screenshots. Fresh FBX reimport passed geometry, UV, bounds and triangle checks (`model/validation.json`). In-engine acceptance still requires replacing the whole old display, checking fit/door clearance and inspecting the velvet/lining under the apartment lighting.

Image generation used the built-in imagegen tool. Prompt briefs are preserved in `concepts/prompts.md`; generated files are copied into this asset and are not dependent on the generation cache.
