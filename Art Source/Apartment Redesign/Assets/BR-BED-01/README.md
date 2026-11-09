# BR-BED-01 — vintage double bed

A painterly double bed based on `concepts/bed-v1.png`; the generated modeling sheet is `references/multiview-v1.png`. The complete bed is 1.498 × 1.902 × 1.179 m after FBX round trip. The origin is centred on the floor, Z up, +Y toward the headboard.

`model/BR-BED-01.blend` contains named frame, mattress, pillows, quilt and throw objects; `model/build_bed.py` regenerates the source and previews in Blender. Textures are in `textures/` and use paths relative to the blend. FBXs include complete, separate frame and separate bedding variants, all sharing the floor origin. The quilt uses an original generated floral-patchwork albedo with arc-length UVs across the hanging sides; walnut, ivory linen, and the rose knit use newly generated painterly albedos. Preview: `previews/bed-three-quarter.png`.

Round-trip validation: in Blender 5.2, run `Blender -b --python model/validate_bed.py -- BR_Bed_Complete.fbx` (or the frame/bedding filename). All three exports have finite world-space vertices and UVs, zero zero-area faces and UVs on every mesh. Final Unreal import, collision, materials, and in-room lighting still need verification. The rest interaction belongs to the game actor, not the mesh.
