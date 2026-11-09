# LV-BOOK-01 — Walnut bookcase

Vintage painted walnut bookcase, based on `concepts/bookcase-v1.png`. That sheet supplies front, back, left, right, 3/4 and joinery close-ups; the finish uses a separately generated color-only painterly texture `textures/walnut-painted.png`. It is a rendering style, not modeled surface buildup.

Dimensions: 1.25 m wide × 0.40 m deep × 2.056 m high, Z up, front toward −Y. The case FBX has a floor origin. The other FBXs contain independent scene objects laid out in the same model space: shelf books, the potted plant and the lidded tin. Their FBX object transforms carry placement; import as a scene or preserve transforms when splitting meshes. These dressing items are intentionally detachable.

- `model/LV-BOOK-01.blend`: source scene, with separate dressing objects.
- `model/LV_BOOK_CASE.fbx`, `LV_BOOK_BOOKS.fbx`, `LV_BOOK_PLANT.fbx`, `LV_BOOK_TIN.fbx`: exports.
- `model/build_bookcase.py`: regenerate from the source image in this folder using Blender 5.2.
- `model/validate_bookcase.py`: round-trip FBX checks for finite vertices and UVs, and zero-area triangles.
- `previews/bookcase-three-quarter.png`: standalone render; room lighting and UE material still require review.

Validation: Blender 5.2 FBX reimport found zero non-finite vertex/UV values and zero degenerate triangles in each of the four exports. Material slots on the FBXs include the generated `Bookcase_Walnut` base-color image; Unreal needs to import that image and wire the material. The revised dressing varies book sizes and tilts, adds visible page edges and gilt rules, and uses independently generated moss and russet cloth textures on selected books. The tapered pot and trailing plant are stylized, with a small painted botanical accent. The book and plant FBXs retain many individual mesh parts; combine or instance appropriately for the game and reassess material appearance in context. Collision, UE import scale/material appearance and lighting remain untested.
