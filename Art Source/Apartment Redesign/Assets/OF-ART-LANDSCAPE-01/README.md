# OF-ART-LANDSCAPE-01 — office north-wall coastal landscape

Provisional Blender art candidate for `P-ART-OF-N` in the A+ office; it has not been imported or reviewed in Unreal. `concepts/framed-multiview.png` shows a generated front, back, side and perspective design reference. The original `textures/coastal_landscape.png` depicts a quiet tidal estuary and distant lighthouse in soft blue, ochre and sage. It was generated against the painterly fixer-upper reference; the multiview's image is a separate conceptual depiction, so the actual painting texture and model are authoritative. `textures/walnut_painterly.png` is the independently generated walnut texture reused from `HA-ART-09` for a coherent apartment palette.

## Geometry and art

- Frame is **0.550 m wide × 0.035 m deep × 0.450 m high**. It contains mitered walnut moulding, raised lip, thin aged-brass fillet, artwork surface, backing and a small rear mounting plate. It is a static decoration; the hanging wire illustrated in the concept is not modeled.
- Blender coordinates use metres, +Z up, +X across the picture and front toward **−Y**. FBX is exported **−Y forward / +Z up** with unit scale. Its bottom-centre origin is at `(0,0,0)`; the rear frame plane is at Y=0 and the artwork spans Z=0.040–0.410 m. Verify FBX axis conversion and pivot in Unreal; mount the back flush to the north office wall and aim the front into the room. Use no decorative collision or a simple thin box if needed.
- The generated source painting has a ~1.777 horizontal aspect; the framed opening is ~1.270. Its single coherent UV island crops the left and right edges symmetrically to **U≈0.143–0.857** instead of stretching the landscape. The artwork keeps the lighthouse in frame. Preserve these UVs and connect `coastal_landscape.png` as an sRGB base-color texture in a rough opaque material. No glass or physically thick impasto is modeled.
- The mitered frame uses `walnut_painterly.png` as sRGB base color with roughness approximately 0.8. The brass fillet is a distinct material slot with metallic 0.6 and roughness 0.55. Recreate and tune materials in Unreal; Blender nodes and packed images do not establish an Unreal material graph.

## Files and validation

- `model/OF-ART-LANDSCAPE-01.blend`: editable Blender source with artwork and textures packed.
- `model/OF-ART-LANDSCAPE-01.fbx`: six-mesh static export. Preserve the assembled transforms or combine the meshes while keeping the bottom-centre origin.
- `model/build.py`: headless build/export/render script; `model/validate.py`: clean Blender FBX reimport checker; `model/validation.txt`: last result.
- `previews/art-front.png` and `previews/art-three-quarter.png`: studio renders, not game screenshots.

The FBX was cleanly reimported with Blender 5.2.3: **six meshes, 122 triangles, bounds 0.550 × 0.035 × 0.450 m**; finite coordinates and UVs, UVs present, and no zero-area geometry or UV triangles were verified. Example rebuild/validation from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/OF-ART-LANDSCAPE-01/model/build.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/OF-ART-LANDSCAPE-01/model/validate.py'
```

The actual room's lighting, artwork readability, mounting height, textures, collision and import orientation remain untested in Unreal.
