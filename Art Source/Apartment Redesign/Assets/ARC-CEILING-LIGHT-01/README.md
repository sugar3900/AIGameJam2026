# ARC-CEILING-LIGHT-01 — period flush ceiling light

Aged brass flush-mount fixture with a lightly fluted warm opal diffuser for the living room or hall. Concept and multi-view on/off reference are in `references/concept-multiview-on-off.png`. `previews/fixture-off.png` and `fixture-on.png` are Blender studio renders; the preview ceiling is not exported.

## Files and dimensions

- `model/ARC-CEILING-LIGHT-01.blend`: editable source with preview scene.
- `model/ARC_CeilingLight_Hardware.fbx`: ceiling plate, mounting neck, retaining rim, clips, and finial.
- `model/ARC_CeilingLight_Glass.fbx`: single-surface fluted opal diffuser with UVs. Both FBXs share the ceiling attachment origin `(0, 0, 0)` in Blender metres, and point down along -Z. Import together at the same transform. Overall hardware bounds are ~0.339 × 0.335 × 0.180 m; diffuser is ~0.329 m wide.
- `textures/aged-brass.png`: existing selected aged-brass candidate reused from `OF-DESK-LAMP-01` for visual continuity. `textures/opal-glass.png` is a newly generated painted ivory material reference. Both are UV textures, not physically based maps.
- `model/build_light.py` regenerates source, exports and previews; `model/validate_fbx.py` cleanly reimports both FBXs and validates finite geometry, nonzero face area and UVs. Latest output is in `model/validation.txt`.

## Unreal handoff

The glass is a thin open mesh, not a physically enclosed glass volume. In Unreal, recreate the warm off-white opal look using `opal-glass.png`, roughness around 0.42, and a subtle warm emissive parameter for the on state; use a two-sided material if either face can be seen. Recreate aged brass from `aged-brass.png`, metallic about 0.6 and roughness about 0.54, then tune under level lighting. Blender nodes and preview light do not transfer as an Unreal fixture; add a warm point light and connect light intensity and glass emissive to the game's toggle. These values are starting points only. Avoid blocking visibility traces with the glass, and use simple collision only if needed. Check mounting, scale, lighting and toggling in the level.

## Concept generation

Built-in image generation, stylized-concept prompt: “A small 1930s flush-mounted fixture for a cozy painterly fixer-upper apartment, approximately 34 cm wide and 18 cm tall. Shallow warm ivory opal glass bowl with gently ribbed or scalloped rim, understated aged antique brass ceiling canopy, narrow brass rim, small central finial and three fine brass retaining clips; attractive and functional, gently aged with restrained patina. Show the exact same fixture as off and warmly lit on, plus orthographic bottom, side and back/top views and an underside perspective, consistent proportions.” The supplied painterly fixer-upper image was the style reference. The model follows the shared proportions and gently fluted surface; generated views are not measured blueprints.

The opal texture was separately generated with the built-in image tool from a prompt for a square flat diffuse warm ivory opal material with subtle cloudy painted brush texture and no objects, text, highlights or shadows.

## Status

Geometry and FBX reimport passed. Parent review, Unreal import, material recreation, collision and game lighting remain untested.
