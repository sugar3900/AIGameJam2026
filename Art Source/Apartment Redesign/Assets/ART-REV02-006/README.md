# ART-REV02-006 — The orchard gate

Unique replacement for `HA-ART-02:058`. Frame: **Broad aged gilt ogee with walnut outer edge and leaf corners**.

- Outer dimensions 1.300 m wide × 0.900 m tall × 0.055 m deep. Origin bottom-center at rear wall plane, source front −Y, Z up. The established import keeps X and flips Y. Place using the unchanged instance wall orientation, frame center and bottom height in `manifest.json`; do not use old source dimensions.
- Original generated artwork is `textures/T_Artwork.png`, unmodified. Its mesh UV center-crops with equal horizontal/vertical pixel scale; no stretching. The exact crop is recorded in the manifest.
- Frame wood/paint uses `textures/T_Frame_BaseColor.png` (sRGB), roughness 0.64. `T_Frame_Grain.png` is the existing painterly walnut source used for the native Blender material bake, kept for reproducibility. Gilt accents: linear base `(0.38,0.26,0.095)`, metallic0.64, roughness0.48. Ivory mount `(0.72,0.67,0.55)`, roughness0.90. Backboard `(0.12,0.085,0.055)`, roughness0.90. Artwork is opaque and rough0.86; no reflective glass hides the image. Reconnect the material maps in Unreal.
- One visual FBX mesh and one UCX box. Import legacy FBX with UCX enabled. This is static wall dressing with no interaction identity or RepairDamage tag. No collision is necessary if wall collision already covers it, but the simple box is included.
- `models/ART-REV02-006.blend` packs textures and includes a disabled preview wall, camera and light, excluded from FBX. `previews/framed.png` is the neutral studio review.
- Reproduce through `../ART-REV02-COLLECTION/build_collection.py -- 006`, then run the collection finalizer. Source validation reimports the FBX and verifies UVs, bounds, origin, UCX and artwork SHA. Engine installation/lighting and in-room screenshots remain pending.

Exact exported material-slot order and all numeric parameters are in `manifest.json` under `materials`. When `base_color_texture` exists, use it directly instead of multiplying it by `base_color_linear`; the constant is the fallback only.
