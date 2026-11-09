# BA-HOOK-01 — bathroom wall hook

Provisional Blender candidate for `P-BA-HOOK`; not yet reviewed in Unreal. The five-view visual concept is `concepts/hook-multiview.png`; `previews/hook-perspective.png` and `hook-front.png` are studio renders. The `textures/aged-brass.png` is copied from the reviewed `BA-TOWEL-RAIL-01` for matching color and patina. The towel itself is a separate asset.

## Geometry and placement

`model/BA_Hook_01.fbx` is a single static joined mesh (plate, curved hook, rounded tip and screw heads). Blender uses metres, X across the wall, Z up, with the **origin at the backplate centre on wall plane Y=0**. The finished wall faces local **−Y** and the hook projects into the room to Y≈−0.077 m. Actual bounds are **0.060 × 0.077 × 0.105 m**; the original 0.08 × 0.08 × 0.12 m inventory dimensions are approximate, so judge scale next to the towel and other fittings in the assembled room. Place the asset origin on the wall at the desired plate centre; rotate the assembled hook to face the room. The FBX was exported with −Z forward / +Y up; recheck orientation after Unreal import and do not assume Blender axes transfer unchanged.

The aged-brass shader uses `aged-brass.png` as color, metallic 0.68, roughness 0.45; reconstruct and tune under actual room lighting because the FBX does not transfer Blender nodes. Screw recesses have a separate dark material slot. For decorative use keep collision simple or disable it; if a towel is made interactive, attach it independently and test hook/towel contact and visibility tracing. No towel, motion, actual wall, or interaction is included in this export.

## Build and checks

`model/BA-HOOK-01.blend` is editable source. Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_hook.py` to rebuild the FBX and previews, and `... -b --python model/validate_fbx.py` to reimport-check it. `model/validation.txt` records one mesh, 3,896 triangles, UVs, finite vertex/UV values, nonzero triangle areas, origin and bounds. Unreal import, shader appearance, collision, placement and scale next to the rail and towel remain untested.
