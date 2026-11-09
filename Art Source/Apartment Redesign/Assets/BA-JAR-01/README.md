# BA-JAR-01 — bathroom ceramic toiletries jar

Provisional Blender asset for lead review and subsequent Unreal evaluation. A small rounded dusty-rose ceramic jar with cream stripe and removable cream lid; it is intentionally shorter and wider than the kitchen canister. `concepts/jar-multiview.png` is the selected generated front/back/left/right/perspective and open/closed design. `textures/rose-ceramic.png` is an independently generated painterly glaze; `textures/ivory-ceramic.png` comes from the existing KI-JAR-01 source. Texture variation is color only, not physical paint thickness.

## Geometry and assembly

- Blender coordinates: metres, +Z up, front −Y; both pieces are rotationally symmetric. The hollow jar body is **0.122 × 0.122 × 0.091 m** and the closed assembly is approximately **0.129 m** high.
- `model/BA_Jar_Body.fbx` has a tabletop-centre origin at (0,0,0). `model/BA_Jar_Lid.fbx` has a lid-centre pivot at **(0,0,0.089) m relative to the body** in the closed assembly; Blender FBX reimport retains this object location. Confirm Unreal import scale/axis/origin before assembling. The open preview lifts and tilts the lid; no animation is authored.
- Body mesh includes a hollow interior, ceramic rim, foot ring and cream stripe. The narrow stripe is a separate joined overlapping surface; inspect the join and depth ordering in Unreal. The lid includes its knob. Place on the bathroom shelf, keeping the 0.122 m width clear of adjacent items.
- Both texture PNGs are included under `textures/` and packed into the Blender source. The full Blender shader is not transferred by FBX: reconnect each as sRGB base color to its named material slot and use a muted, moderately rough ceramic glaze. The raw generated texture is not certified seamless; check UV seams and color against the assembled bathroom under game lighting. Use simple collision as needed.

## Files and validation

`model/BA-JAR-01.blend` is the source; `model/build_jar.py` rebuilds both FBXs and the transparent `previews/jar-closed.png` and `previews/jar-open.png` studio renders with headless Blender. `model/validate_fbx.py` imports both files and checks finite vertex and UV coordinates, UV presence and zero-area geometry triangles. `model/validation.txt` records passing reimport with Blender 5.2.3. Blender renders are not evidence of Unreal appearance, correct imported axes, collision, interaction or lid motion.

Concept generation prompt: period small bathroom jar, rounded dusty-rose ceramic pot with cream lid, subtle cream stripe, open/closed front/back/left/right/perspective views, matching the painterly fixer-upper apartment. Texture prompt: muted rose aged glazed ceramic, soft painterly color variation, no raised physical paint, objects, text or directional lighting.
