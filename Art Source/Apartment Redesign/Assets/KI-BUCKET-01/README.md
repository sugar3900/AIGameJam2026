# KI-BUCKET-01 — galvanized repair bucket

A small 1950s galvanized bucket for the leaking kitchen sink. The selected [concept sheet](concepts/bucket-v1.png) already contains front, back, side, overhead and perspective views, with the handle raised/lowered and water levels. The model is a hollow tapered shell, rolled rim and base seam, a raised rib, paired lugs and a separate rotating wire bail.

## Files and texture choices

- `model/KI-BUCKET-01.blend` is the source scene. `model/build_bucket.py` regenerates it, all FBXs and the two state previews using Blender background mode.
- `model/KI_Bucket_Body.fbx` has a floor origin; the body measures approximately 0.338 × 0.324 × 0.245 m. `KI_Bucket_Handle.fbx` has a pivot at the axle midpoint, 0.225 m above the floor, with rotation about local X. `KI_Bucket_Water.fbx` shares the body floor origin and sits at approximately 0.17 m. Hide the water part when the sink is repaired.
- `textures/zinc-candidate-a.png` and `zinc-candidate-b.png` are independently generated flat zinc albedo alternatives. A was selected for its subtler gray/warm flecks and smaller brush scale; B is retained for stronger strokes. Neither was mathematically verified seamless. The metallic edging is a separate material. Source texture images are packed neither into the FBX nor automatically reconstructed by Unreal.
- `previews/bucket-empty-handle-up.png` and `bucket-water-handle-down.png` show the model. The water uses Blender Principled transmission 0.88, IOR 1.333, roughness 0.12 and a pale gray-green tint, plus very fine, partial ripple-arc geometry in a second material slot. In Unreal recreate these as a translucent reflective water material (start with IOR 1.333, roughness 0.12 and a restrained gray-green tint) and a subtle ripple material; tune opacity/refraction to the target renderer. These are material parameters, not baked light, and FBX does not transfer the Blender shader faithfully.

## Validation and remaining work

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/KI-BUCKET-01/model/validate_fbx.py'`. All three FBXs passed a fresh Blender import with finite vertices, normals and UVs and zero-area-triangle checks. This does not establish Unreal import scale, handle pivot/orientation, visible UV seam, collision, material settings, transparency, or lighting; verify those in the completed kitchen. The pail is a separate prop and should not obstruct the sink interaction trace.

The second water pass preserved the bucket body and handle FBXs byte-for-byte; only the water mesh, Blender water materials, warm preview lighting and previews changed. The water is a visual surface, not a fluid simulation; its reflection and translucency still need an Unreal renderer and room-lighting check.
