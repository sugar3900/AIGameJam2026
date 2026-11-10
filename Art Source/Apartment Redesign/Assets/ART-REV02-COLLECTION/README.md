# ART-REV02 collection

Seventeen distinct original generated paintings, individually fitted frames, and source handoff for FIX-006.

- `catalog.json`: painting briefs, unique frame profiles, mount widths and palette.
- `build_collection.py`: editable Blender geometry/UV recipe; optional IDs after `--` rebuild a subset.
- `finalize_collection.py`: native Blender frame-map bake, per-asset README, FBX roundtrip validation and contact sheet. Existing valid frame bakes can be reused; rebuilding an asset resets its manifest and makes it bake again.
- `build-manifest.json`: full17instance/asset/placement mapping.
- `validation.json`: source roundtrip evidence, distinct artwork hashes and UV/collision checks.
- `previews/contact-sheet.png`: all17framed previews.

Build with Blender `-b -t 2 --python-exit-code 1 --python <script>`. Each adjacent `ART-REV02-NNN` folder owns its artwork PNG, baked frame map,FBX,packed blend,manifest and README. Original source exports and KI-LEAK-02 are untouched. Engine import and scene-lighting acceptance remain pending.
