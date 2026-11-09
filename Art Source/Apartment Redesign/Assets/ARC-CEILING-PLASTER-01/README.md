# ARC-CEILING-PLASTER-01 — warm ceiling plaster

Reusable preliminary painterly finish for a sound, subtly aged apartment ceiling. It is a surface module, not a structural slab or repair state.

## Art direction and selected texture

Three independently generated flat plaster candidates are in `textures/`: A has pronounced peach brushwork, B is also noticeably pink, and C is a more neutral warm ivory with restrained dry-brush variation. **C is selected** because it will harmonize better with the bedroom's white paneling and the other rooms without looking as though the ceiling itself is pink. All are albedo samples with no intended baked lighting. The texture is subtle at room scale, so judge brush visibility and warmth under real game lighting.

## Contents and use

- `model/ARC-CEILING-PLASTER-01.blend`: editable scene, with four linked modules for a 4 × 4 m repeat test, light and preview camera. The material's source image is packed.
- `model/ARC_Ceiling_Module_2m.fbx`: a single 2 × 2 m room-facing surface with origin at its (0,0,0) corner; the surface normal is local −Z. Each metre-square quadrant uses baked mirrored UVs: 0→1→0 along each axis. Adjacent unscaled tiles aligned on the 2 m grid share UV boundary values, avoiding a hard discontinuity with this non-seamless source image.
- `model/build_ceiling.py` regenerates the FBX, source scene and repeat preview; `model/validate_fbx.py` round-trips the FBX and checks bounds, downward normals, finite geometry/UVs, nonzero face area, and matching UV boundary values.
- `previews/repeat-4m.png`: four modules under neutral studio lighting. The planar swatch is intentionally simple; room-scale color and realistic character lighting are untested.

## Unreal handoff

Place the plane room-facing downward at approximately 2.75 m above floor, without coplanar overlap with other ceiling surfaces; the module is not load-bearing. Use the imported UV channel directly with `plaster-candidate-c.png` in sRGB as Base Color, a high roughness (~0.9), zero metallic; do not replace the mirrored UVs with ordinary wrapping of the raw, non-seamless image. Do not scale the UV axes independently unless appearance and seams are rechecked. A one-sided material should be visible from the room if imported normals are preserved. Use the apartment shell for structural ceiling collision; disable collision on this cosmetic plane if it would duplicate shell collision. Trim modules to room boundaries and keep them clear of fixtures.

Mirroring suppresses hard boundaries but the texture and its mirror repeat every 2 m and may form visible symmetry or brightness shifts in long uninterrupted areas. Validate under actual Unreal lighting and at both positive and rotated placements. Room-scale lighting, material import, seams, ceiling collision, fixture joins and appearance with walls are **not tested in Unreal**. Localized wear should be a separate, sparsely placed decal/overlay rather than baked into the module, so it does not repeat at every tile.
