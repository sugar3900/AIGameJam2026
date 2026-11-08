# LV-CHAIR-01: vintage upholstered armchair

A 0.749 × 0.689 × 0.935 m armchair for the living-room plan, with terracotta floral upholstery, rounded arms and seat, dark walnut feet, and a lace antimacassar. Front faces −Y, Z is up, and origin is on the floor. The piece is static.

- `concepts/armchair-v1.png`: selected generated multiview concept.
- `textures/floral-candidate-a.png` and `floral-candidate-b.png`: independently generated floral alternatives. A was selected for its warmer, coherent floral color against the concept; B remains for comparison. `lace-knit.png` supplies the lace treatment.
- `model/build_armchair.py`: headless source builder; `.blend` and `.fbx` are generated outputs.
- `previews/armchair-three-quarter.png`: Blender preview of the current asset.
- `model/validate_fbx.py`: reimports the FBX and checks finite positions, UVs and nonzero-area triangles.

The resumed pass flattened an unnecessarily protruding front apron and added upholstered roll ends and restrained seams. Validate in Unreal before approval: reproduce the fabric material's multiply tint (0.72, 0.66, 0.56) documented in the builder, verify texture seams and visual contrast in apartment lighting, collision, and the silhouette at gameplay distance. The lace uses a painted knit texture on a scalloped mesh with geometric openwork holes; it needs no alpha mask. It is an approximation rather than a cloth simulation. Turned wooden feet and finer arm seams were added after review. Compare the upholstery and roll ends against the concept before final art approval.

To rebuild and validate (from this directory):

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_armchair.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python-exit-code 1 --python model/validate_fbx.py
```
