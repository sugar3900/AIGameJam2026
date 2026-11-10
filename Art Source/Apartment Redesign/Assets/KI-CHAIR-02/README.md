# KI-CHAIR-02 — corrected dining-chair back

FIX-018 replaces the three incorrectly bowed, individually vertical back slats of KI-CHAIR-01. The new front faces are gently concave toward the sitter, with rearward recline following the original curved posts. The seat, cushion, frame, legs, stretchers and post caps retain the original geometry, UVs and materials. This is a source replacement for every existing KI-CHAIR-01 instance; preserve each actor’s transform and table relationship.

Source appearance approved by parent review of the context, side, seated-eye and rear-detail renders. Engine import and map verification remain with the integration owner.

## Export and placement

- Export: `model/KI_CHAIR_02.fbx`, one visible mesh `KI_CHAIR_02` plus 26 separately named convex `UCX_KI_CHAIR_02_*` hulls.
- Editable source: `model/KI-CHAIR-02.blend`. Only the chair source collection is exported; preview floor, cameras and lighting are excluded.
- Source units metres; origin `(0,0,0)`, up `+Z`, front `−Y`. Existing Unreal convention keeps X and flips Y, so the visible front imports as `+Y`. Keep the old actor rotation, scale and position.
- Render bounds in metres: X `−0.230000…+0.230000`, Y `−0.237722…+0.275000`, Z `+0.012380…+0.910000`. They match the actual old FBX within floating-point serialization tolerance. The inherited 12.38 mm lowest-point offset is intentional here: do not compensate it a second time in the replacement transform.
- Use the legacy FBX importer to retain UCX. Hulls cover individual seat/frame, leg/post, stretcher and slat members; openings remain open. All collision is clipped to the old render envelope. Verify walking/click behavior around the table after import.

## Back construction

The original front is `−Y`, but its slat centres protruded 22.24 mm in that direction relative to their outer bands. Each old slat also had 0° individual recline. The replacement samples the original post Bezier centreline at every slat height and reverses the bow.

| Slat centre Z | Designed centre recess | Recline following posts | Minimum end embed into posts |
|---|---:|---:|---:|
| 0.615 m | 12 mm | 7.280° | 6.106 mm |
| 0.715 m | 12 mm | 10.774° | 6.145 mm |
| 0.835 m | 8 mm | 12.405° | 6.268 mm |

Slats have 20 mm thickness with restrained 2.8 mm edge wear. Their ends widen naturally with the posts and overlap inside the timber. The six existing-style wooden pegs are rebuilt aligned to the new front normals. Concavity and recline are independently measured again after FBX re-import; sampled outer-band recess is approximately 11.59/11.60/7.73 mm because the samples fall slightly inboard of the true endpoints.

## Materials

See `materials.json` for the explicit slot contract. All slots are opaque, roughness 0.65, metallic 0. Wood and vinyl base-color textures use sRGB and no tint multiplier. `Chair_Piping` uses constant linear RGB `(0.25,0.075,0.035)`. Original texture bytes are preserved and locally included.

| Slot | Name | Base color |
|---|---|---|
| 0 | Chair_Walnut | `textures/wood-selected-v2.png` |
| 1 | Chair_Rust_Vinyl | `textures/vinyl.png` |
| 2 | Chair_Piping | Constant listed above |

## Validation and review

`validation.json` records a fresh FBX import: 7,742 render vertices, 15,264 triangles and 26 closed convex collision hulls. The 3,668 preserved vertices and their 14,192 material/UV face corners match the original; maximum positional serialization difference is below 0.000000075 m and UV difference is zero. All new slat UV triangles are nondegenerate, positions/normals/UVs are finite, and no render geometry triangles have zero area. The 288 zero-area UV triangles inherited in untouched original members remain unchanged; this scoped back correction does not remap the original chair.

Six endpoint tests compare replacement slat surfaces against the actual preserved post meshes. They all establish at least 6.1 mm overlap. Collision is manifold/convex and stays inside the original render bounds. These source checks do not replace the integration owner’s legacy-import and real-map collision check.

Eight previews include context, front, back, left, right, seated-eye, slat-detail and rear-detail views. `original-diagnosis.json` records the measured original bow. `assembly.json` records the new source dimensions, slope and joint tests. `release-manifest.json` hashes the delivered files.

## Rebuild

Run headless Blender with two threads, sequentially:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/build_chair.py -- --no-render
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/validate_export.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/render_views.py
```

The builder reads the sibling `KI-CHAIR-01` FBX and textures and writes only this revision folder. The original asset and all other source kits remain untouched. No engine content, map, shared tracker or git changes are included in this delivery.
