# BA-TILE-GLAZE-02 — FIX-038

A material-only glaze update for the existing pink bathroom tile. Preserve the installed colour palette, 100 mm grid, cropped panels, window wraps, grout geometry, caps and independent Tyler repair crack. No replacement mesh, displacement, new crack pattern or collision change.

## Surface maps

All maps are 1024 square, periodic and isotropic. Use the EXISTING tile UV0 unchanged. Each 97 mm tile face spans 0.40 UV units, so one full map repeat represents 242.5 mm. Existing per-tile random UV offsets and quarter-turns make the highlight variation differ between tiles. Do not project a new grout grid or apply these maps across grout slots.

- `textures/T_BathGlaze_NormalDX.png`: tangent-space DirectX normal. Import as Normal Map compression, sRGB OFF, sampler Normal, wrap U/V. Green is already DirectX; start with Flip Green OFF. Connect Normal at strength 1.0. Verify highlight direction on a lit grazing tile before acceptance; mirrored/rotated original tile UVs must use mesh tangents. Original physical edge bevels provide the larger tile shape.
- `textures/T_BathGlaze_Roughness.png`: linear scalar, sRGB OFF, Masks/Grayscale compression, wrap U/V; R to Roughness. Nominal .42, measured .3745–.4663. Soft satin glaze variation, no metallic. If the live light makes the result excessively glossy, add a small uniform roughness bias (up to +.08) rather than flattening variation.
- `textures/T_BathGlaze_Height16.png`: optional 16-bit linear height data for a bump shader/debug reference. White-to-black physical range is only 0.18 mm. It is the source surface used to derive the normal. Do NOT add it as another bump on top of the supplied normal, and do not use displacement/parallax. Black/white texture contrast does not mean deep relief.

Only the eight Pink glaze material slots get glaze normal/roughness. Keep Warm ivory grout matte and its existing geometric recess. Plum cap remains separately controlled, since it has different UV scale. Preserve all face assignments on the ten fitted tile panel meshes; changing the old module's material alone may not reach the cropped copies.

## Colour

These are numerical surface data, not colour textures. Retain the installed pink palette and existing colour texture. Audit whether `T_BathTile_Glaze` / BA-TILE-01 `candidate-b.png` is actually used by the installed glaze instances: old FBX Phong fallback drops Blender colour mixing. The source uses eight pink tints with subtle painterly glaze variation, but a blind material replacement could change the user's pink. If the installed slots are flat, introduce restrained existing glaze-colour variation while matching each slot's current mean pink. Do not use candidate-a (contains a baked tile/grout grid).

## Validation

`build_maps.py` deterministically produces periodic Fourier height variation, analytical derivatives and unit normals. `map-validation.json` records finite values, normal lengths, physical amplitude, roughness bounds and wrap-edge step comparisons. Maximum unquantized normal tilt is about 1.32 degrees; height RMS is 0.025 mm. This is intentionally subtle ceramic glaze.

`preview_material.py` loads the original source tile scene and renders the same close/grazing view before and after with unchanged colour graph and lighting. For Blender only it inverts DirectX green to OpenGL. Those previews establish source appearance, not in-game acceptance.

Engine acceptance: compare lit eye-level and close/grazing views under actual bathroom lights; confirm the pink stays recognisable, highlights softly break up without stone-like relief or shimmer, grout and tile edges remain aligned, and Tyler's repair crack hides normally without changing the surrounding glaze. No global exposure or lighting change is part of this fix.
