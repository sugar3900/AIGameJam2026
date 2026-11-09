# BA-HAND-TOWEL-01 — hook-hung hand towel

Provisional Blender asset for `P-BA-HOOK-TOWEL`, awaiting parent visual review and Unreal testing. `concepts/hand-towel-multiview.png` is the generated painterly multiview reference, including front/back and both sides; `previews/towel-perspective.png` and `towel-front.png` are Blender renders. The existing `BA-HOOK-01` hook is used only in the previews, not included in the towel export.

## Geometry and placement

`model/BA_Hand_Towel.fbx` contains one gathered cloth mesh with a 2.5 mm modeled thickness, not simulated fabric. It is **0.3215 m wide × 0.0434 m deep × 0.4593 m high**, with double rose stripes near the lower hem and slight asymmetry. The mesh uses **6,464 triangles**. The towel is a simplified single gathered drape, not a full physically folded cloth simulation.

Blender coordinates are metres, +Z up, +X across the wall and −Y toward the room. Its origin is `(0,0,0)` at the **same wall-plane/backplate-centre datum as BA-HOOK-01**. Place both at the same transform to reproduce the preview. The cloth extends from local Z ≈ −0.050 to −0.509 m and Y ≈ −0.069 to −0.113 m; the gathered top touches the hook's projecting tip in the Blender preview. The preview brass is a simplified proxy material, not the hook's final material. The hook has not been imported into Unreal with the towel, so verify axis conversion, cloth/hook contact, collision and room clearance together. The towel FBX uses Blender export **−Z forward, +Y up**, matching the hook's export convention; do not infer Unreal axis/rotation without checking the imported pair.

## Materials, interaction and checks

`textures/terry.png` is copied from `BA-TOWEL-RAIL-01` for consistency. Blender uses ivory tint `(0.94, 0.91, 0.84)` and rose-border tint `(0.61, 0.32, 0.30)` multiplied by this texture, roughness 0.93. FBX retains UVs and two material slots but does not reproduce the node graphs; recreate the materials in Unreal. The cloth has modeled thickness, but check both faces in-game and use a two-sided cloth material if the renderer or placement requires it. It is a static decorative mesh; pickup or cloth motion is not authored. Usually use no blocking collision unless gameplay needs it.

Rebuild using `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_towel.py`; validate with `... -b --python model/validate_fbx.py`. `model/validation.txt` records a clean round trip: one mesh, 3,234 vertices, 6,464 triangles, finite positions and UVs, no zero-area triangles, and the expected shared origin. The Blender scene includes a preview wall and imported hook; **only the towel is exported**. Unreal materials, contact, placement, collision and lighting are untested.

The concept was generated using the built-in image-generation tool from the painterly-fixer-upper reference; its prompt requested an off-white terry hand towel gathered on a brass hook with dusty-rose hem and front/back/side/three-quarter views. The actual model follows the hook datum and the concept's approximate 0.32 m width and 0.48 m hanging length.
