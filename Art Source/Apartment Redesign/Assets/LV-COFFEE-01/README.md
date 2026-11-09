# LV-COFFEE-01 · Living-room coffee table

This asset follows `concepts/coffee-table-v1.png`, which already shows front, back, both ends, top and perspective. It has a rounded walnut top, four splayed tapered legs, an open apron, low shelf and shelf-end supports. The floor-origin export is 1.20 × 0.60 × 0.453 m. This item is static; the separate shelf is joined into the export.

`textures/walnut-candidate-a.png` and `walnut-candidate-b.png` were independently generated: A has finer, more photographic grain; B has broader brushwork and is used on the model. Both are base-color candidates rather than guaranteed seamless materials. The PNG is packed into the `.blend`; Unreal should assign it to the wood slots and use a rough finish. The `Table_Sage_Painted` slot name is inherited from the dining-table generator but uses the same walnut texture here. `Table_Edge_Wear` uses a muted honey solid color. Small raised-free scuffs are separate coplanar mesh details.

- `model/build_coffee.py`: reproducible background Blender build; generated parts are joined at floor origin.
- `model/LV-COFFEE-01.blend`: source with packed texture and lighting.
- `model/LV_COFFEE_01.fbx`: mesh export; coordinate unit metres, Z up before FBX conversion.
- `model/validate_fbx.py`: reimports the FBX and checks finite vertices, normals and UVs, zero-area polygons/triangles and size.
- `previews/`: 3/4, front, back, left, right and underside renders.

Validation: Blender FBX reimport reports 946 vertices, 874 polygons, no non-finite positions/normals/UVs and zero degenerate faces or triangles. This has not yet been imported into Unreal; validate scale, UV appearance, collision, material setup and how the shelf/table read in the room and lighting. The top and shelf touch their support geometry but the whole is one static mesh.
