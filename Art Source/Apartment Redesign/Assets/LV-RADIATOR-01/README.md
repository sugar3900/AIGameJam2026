# LV-RADIATOR-01 — living room cast-iron radiator

The social elevation calls this asset `LV-RAD-01`. The original concept sheet is also a front, back, two-side and perspective modeling reference. Six rounded cast sections, manifolds, separate end caps, tapered feet, wall brackets and pipework with a small spoked valve echo that design. Two independent generated cream-enamel candidates are retained; candidate B is selected for its more visible brushwork. The pipe has a separate generated patinated brass texture. The fixture is decorative; no open/closed state was specified. The valve wheel consists of separate meshes in the Blender source, but the FBX is a static assembly with no rig or animation.

- Overall Blender FBX reimport bounds: **0.542 m wide × 0.254 m deep × 0.570 m high**, including pipe, mounting brackets and feet. This fits the approximate 0.65 m × 0.60 m elevation envelope in width and height; placement, bracket/wall alignment and clearances require in-room checking.
- Origin: approximately center of radiator core, at floor level. Blender uses meters. Meshes face front toward negative Y; brackets extend toward positive Y.
- `model/LV-RADIATOR-01.blend` is the editable file; `model/LV_Radiator.fbx` is the static export. Rebuild with Blender background mode and `model/build_radiator.py`. Keep the `textures/` directory alongside the source; its image paths are relative to the `.blend`.
- Material slots: `Aged ivory painted cast iron` uses `textures/enamel-selected.png`; `Tarnished brass` uses `textures/brass-patina.png`; `Recessed dark bronze` is a flat color. The generated image textures are base color, not normal or roughness maps. Check UV seams, material setup and color response during Unreal import; no engine import or collision has yet been tested.
- `previews/radiator-perspective.png` is a neutral studio render, not an in-game lighting result. Concept and texture sheets are not guaranteed to tile seamlessly.

Validation: Blender 5.2.3 FBX reimport produced 51 meshes, 7,824 vertices, 7,388 faces; every mesh has finite UVs, nonempty geometry and nonzero-area polygons. Re-run with `blender -b --python model/validate_fbx.py`.
