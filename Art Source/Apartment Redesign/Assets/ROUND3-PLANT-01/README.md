# ROUND3-PLANT-01 — shelf pot repair

Replaces the living-room and office shelf plant's inherited faceted pot and four detached tan decoration spheres. The original `LV-BOOK-01` builder placed `pot botanical accent` UV-spheres at fixed Y=−0.173 m, with X=−0.38/−0.34/−0.30/−0.26 m and Z=1.58 m. They did not follow the tapered pot surface, so the side decorations floated. `FEEDBACK-ROOM-03` retained them by prefix alongside the original 32-sided cone, cylindrical lip and raised soil disc.

This additive kit removes those four ornament spheres and replaces the vessel with a smooth hollow terracotta pot, rounded rolled lip, recessed soil and small matching saucer. It retains the existing painted `LV-PLANT-02/textures/terracotta.png` image. All 19 existing leaf meshes and 19 existing curved petiole meshes retain their exact geometry, positions, UV corners and material names. One short central green root continuation joins their original root point to the lowered soil; foliage is otherwise unchanged.

## Import and placement contract

- Replacement: `model/LV_Book04_Plant.fbx`. One assembled static mesh, floor/assembly origin **(0,0,0)**, metres, FBX forward **−Z**, up **Y** (`apply_unit_scale=True`, `mesh_smooth_type='FACE'`). This matches `FEEDBACK-ROOM-03/model/LV_Book03_Plant.fbx`'s original axes; do not use the architectural kit's −Y/Z settings.
- Replace or reimport `/Game/ICanFixHim/Environment/Rev02/Room03/LV_Book03_Plant` using the installed mesh's import settings. Check its live path before replacement. `combine_meshes=True` is safe; this FBX has only one mesh. Preserve actor transforms for both `Art_LV_Book_LV_BOOK_PLANT` and `Art_LV_Book_LV_BOOK_PLANT_OFTop`.
- Slot 0 `Plant_Leaf` → existing `MI_Plant03_Leaf`, two-sided foliage material. Slot 1 `Plant_Leaf_Light` → `MI_Plant03_LeafLight`, also two-sided. Slot 2 `Ceramic_Pot` → `MI_Plant03_CeramicPot`, **single-sided** painted terracotta. Slot 3 `Pot_Soil` → `MI_Plant03_PotSoil`, single-sided dark matte soil. The obsolete `Pot_Botanical` slot is removed. Preserve bindings by name, not old slot index.
- Source pot centre is `(−0.33,−0.08)` m. Maximum pot/lip radius remains **0.107 m**, shelf base remains **Z=1.49 m**, rim top remains **Z=1.6625 m**. Soil top is **Z=1.6563 m**, 6.2 mm below the lip. The saucer fits inside the old lip's footprint. Fresh original/patched FBX world bounds match to 0.001 mm, so both existing shelf placements remain valid.
- Existing materials/textures and gameplay are reused. No collision, actor placement or engine files are part of this kit.

## Source and validation

`model/build_plant.py` reads the settled `FEEDBACK-ROOM-03/model/BooksPlant03.blend` without modifying it, identifies the four accent spheres, preserves the current foliage, builds the new 96-segment vessel and saucer with outward normals and inward cavity normals, and exports the replacement plus editable `model/ROUND3-PLANT-01.blend`. Cylindrical UVs use arc length through the lip/foot profile, so horizontal bands retain UV area. `model/source-validation.json` records the input hash, removed accents, source signed volumes and foliage preservation.

`model/validate_fbx.py` freshly imports the original FBX and replacement in separate scenes, comparing all **6,688 original foliage corners** by world position, UV and material. The only 96 added foliage corners form the short central root continuation. It independently finds exactly two connected ceramic components (vessel and saucer), verifies both are closed manifold surfaces with positive signed volumes, checks smooth side faces and noncollapsed ceramic UV triangles, and tests outward exterior versus inward cavity radial normals. There are no floating ornament islands or `Pot_Botanical` material.

Fresh FBX result: **PASS**, 6,057 vertices, **11,072 triangles**. Vessel volume +0.000748907 m³; saucer +0.000186990 m³. Minimum outward side radial dot +0.98163; maximum cavity radial dot −0.98060. Full results are in `model/fbx-validation.json`.

`previews/plant-before.png` and `plant-after.png` show isolated source before/after. `pot-close.png` shows the painted curved vessel, lip and recessed soil; `pot-close-single-sided.png` is the backface-culling diagnostic. These are source previews; the integrator must verify the two installed instances in Unreal.

Rebuild in Blender 5.2 with `--background --threads 2 --python-exit-code 1 --python model/build_plant.py`, followed by `model/validate_fbx.py` in a fresh Blender process. Acquire the shared `/tmp/apartment_blender.lock` around each Blender process while working in this checkout.
