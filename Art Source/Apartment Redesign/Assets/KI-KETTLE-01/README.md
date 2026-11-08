# KI-KETTLE-01 — enamel kettle

A small cream-enamel stovetop kettle, with a dark metal lid, metal handle arch, wooden grip and knob. The lid is a separate mesh group so it can be lifted for an interaction. `concepts/kettle-v1.png` contains the design and closed/open references; `previews/` shows the Blender render in each state. The off-lid preview is an illustrative position, not an animation.

## Files and assembly

- `model/KI-KETTLE-01.blend`: editable source, saved with the lid closed. Blender units are metres, Z up. The image texture is referenced relatively from `textures/`.
- `model/KI_Kettle_Body.fbx` and `model/KI_Kettle_Lid.fbx`: separate exports, retaining individual component objects. Import each as a combined static mesh using the same import settings and preserve their shared scene coordinates; verify alignment in Unreal before setting up a lid-lift interaction. The lid is designed to lift, not hinge. The source geometry is centered on the kettle body, with its base near Z = 0; the spout points in the negative X direction. The complete source bounds are approximately 26.9 × 20.4 × 21.6 cm.
- `model/build_kettle.py`: reproducible Blender 5.2 background build and preview generator. It overwrites the source, FBXs and previews.
- `model/validate_fbx.py`: imports both FBXs and checks each mesh for finite positions, normals and UV coordinates, nonzero triangle area, and presence of a UV layer.
- `textures/*-selected.png`: painted enamel, aged steel and warm wood base-color images. Two independent candidates for each surface are retained for art review; the selected steel and wood use candidate B. These images are external dependencies of the Blender file.

## Materials and review notes

`Painted_Ivory_Enamel` uses the selected image for base color (roughness 0.48, metallic 0). `Aged_Steel` uses a mottled warm patina image (roughness 0.43, metallic 0.48), `Warm_Wood_Grip` uses a brown wood grain image (roughness 0.52), and `Dark_Interior` is a uniform dark brown (roughness 0.8). Recreate these materials and connect the selected image in Unreal; the FBX is not a guarantee that Blender shader networks transfer. The enamel, metal and wooden surfaces have painted color variation. The spout has a dark inner throat for its silhouette, rather than a continuous passage into the body. Visual approval and in-engine material, scale, pivot and lid-animation checks remain outstanding.

## Validation

On Blender 5.2.3, `blender -b --python model/validate_fbx.py` passed: body 12 meshes / 6,840 vertices; lid 3 meshes / 1,634 vertices. This is geometry validation only; it does not validate UV distortion, collision, animation or Unreal import.
