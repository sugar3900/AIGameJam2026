# LV-PLANT-02 — rim-safe painterly pothos

FIX-014 source replacement for LV-PLANT-01. Preserve the existing plant actor identity and its stand/riser actors; replace the plant mesh only. Source approval does not replace the in-engine placement and lighting review.

## What changed

The original trailing stems descended from inside the pot and crossed its rim. The new seven vines first rise above the 19.5 cm rim, then descend outside the pot. Sixty-five heart-shaped leaves use closed 0.45 mm shells with outward normals; their undersides remain visible with ordinary backface culling. Stem endpoints and leaf roots coincide. The original painted terracotta, leaf texture and cream line remain.

The pot now has an opaque bottom. All original pot vertices, existing polygons and original UV coordinates are unchanged; one underside face was added. The original soil disk faced downward: only its face winding was reversed so the soil is visible from above. The soil shape and UV mapping, cream decoration and pot silhouette are preserved.

## Import and materials

Import `model/LV_Plant02.fbx` through the legacy FBX path to retain UCX collision. It contains five visual meshes and one convex pot hull. Either retain five parts at the same origin or combine visual parts while mapping materials by the names in `manifest.json`. The hull is `UCX_LV_Plant02_Pot_00`. Foliage and stems deliberately have no blocking collision.

| Node | Material | Texture |
|---|---|---|
| LV_Plant02_Pot | Painted weathered terracotta | textures/terracotta.png |
| LV_Plant02_Leaves | Variegated pothos painted leaf | textures/pothos-leaf.png |
| LV_Plant02_Stems | Olive green stems | constant |
| LV_Plant02_Soil | Dark potting soil | constant |
| LV_Plant02_Decoration | Worn cream slip decoration | constant |

Use opaque materials, alpha 1 and transmission 0. Leaf shells do not require Two Sided. Textures are colour/sRGB; connect them directly to Base Color rather than multiplying by the fallback colour. Exact linear constants and roughness appear per node in `manifest.json`. No new procedural or generated texture is required. The two original painted PNGs are copied unchanged and packed into the editable blend.

## Origin and stand fit

Source units are metres, +Z up, front −Y. FBX export uses forward −Y/up Z, matching LV-PLANT-01. The original origin is retained: the actual pot bottom is Z +0.005 m. All five groups share that origin and identity scale.

For the actual `LV-PLANT-STAND-01` source geometry:

- Stand tabletop top: Z 0.480 m; optional riser top: Z 0.516 m.
- **Plant origin: Z 0.511 m relative to the stand floor origin.** This seats its Z +0.005 m base exactly on the riser. The old documented +0.516 placement floated the pot by 5 mm.
- If omitting the riser, use plant origin Z 0.475 m.
- Pot base radius 0.065 m fits the riser radius 0.078 m with 13 mm radial margin.
- Lowest leaf is Z +0.033681 m in plant space: 64.7 mm above the stand tabletop at the supported placement.
- Overall source bounds: X −0.213583…+0.216943, Y −0.219319…+0.198280, Z +0.005…+0.367855 m. Foliage is 43.1 × 41.8 cm; allow this real envelope when checking nearby walls, fusebox and encounter positions. No leaf reaches the stand surface.

`previews/plant-stand-context.png` uses the actual original stand and riser geometry, with the plant seated at +0.511 m. Its stand finish is the original walnut source finish; the current engine white override is a separate integration decision. The stand is not included in the new plant FBX.

## Validation and reproduction

`model/build_plant.py` loads the preserved LV-PLANT-01 source, copies its two textures, reconstructs only foliage/stems, caps the pot bottom and fixes soil winding. It asserts original pot surface/UV preservation, zero leaf/pot and stem/pot triangle intersections, closed leaf shells and root/stem connectivity. It exports the source kit and renders top, side, underside, three-quarter and actual stand context views with two Blender threads. The context stand is never exported or saved into the source plant blend.

Run with headless Blender: `Blender -b -t 2 --python model/build_plant.py`, then `Blender -b -t 2 --python model/validate_fbx.py`. Both resolve paths relative to themselves and depend on the retained original plant/stand source folders.

`model/validation.json` records a real FBX reimport: five visual nodes, one closed convex hull, finite UVs, unchanged material names, leaf manifold topology/outward volume, a ray hit on the new underside, and source/import bounds agreement within 0.00001 m. `source-audit.json` contains construction checks. The original pot interior terminates behind the soil; original decorative strip endpoints remain open. These are not leaf shell or collision holes.

Final Unreal acceptance must check the five material assignments, opaque leaf visibility from above/below, pot seating, actual wall/fusebox clearance, and any other instances sharing the old plant mesh. No editor/map changes are included in this source release.
