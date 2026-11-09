# BA-TOWEL-RAIL-01 — bathroom towel rail

Status: candidate for visual review, not imported or tested in Unreal. `concepts/towel-rail-multiview.png` is the generated multiview design and `previews/towel-rail-perspective.png` is the current Blender render. The aged-brass and terry albedo textures were reused from `HA-SCONCE-01` and `BA-BASKET-01`, respectively, and copied into `textures/`.

## Assembly and export

The rail is **1.13 m wide × 0.13 m deep × 0.08 m high**, including brackets and finials, close to the 1.12 m design target. The ivory towel is approximately 0.432 × 0.079 × 0.687 m and the rose towel approximately 0.434 × 0.079 × 0.727 m. They hang folded over the bar with their back panels shorter than the front. Each towel is separate, has a modeled 2.5 mm thickness and border material slots, and could be used independently. It is a static sculpt, not simulated cloth or an authored pickup animation.

Blender uses metres and Z up. The assembly datum is the **midpoint of the wall-facing rail at bar height**, with X along the bar, +Y toward the wall and −Y out into the room. The towels extend into negative Z from the bar; mount at the chosen rail height and ensure the bottoms and their depth clear the other fixtures. `BA_Towel_Rail.fbx` contains multiple meshes for the bar, brackets and screws; combine meshes on import while preserving their transforms, or assemble the individual parts at their exported transforms. `BA_Towel_Ivory.fbx` and `BA_Towel_Rose.fbx` share the same assembly coordinate frame and are exported in place. Confirm the Unreal FBX axis conversion and assembly transforms before placing them.

## Materials and validation

`terry.png` is tinted through separate Blender multiply nodes for ivory, rose and contrasting border slots; recreate these color tints and the high-roughness fabric material in Unreal. `aged-brass.png` uses a subdued tint, metallic 0.68 and roughness 0.45 in the preview; tune for actual room lighting. FBX does not carry Blender's shader graph. Towels have modeled thickness, but inspect backface shading and consider a two-sided material if needed. The rail should have simple wall-hardware collision; the decorative towels should generally be nonblocking unless interaction requires otherwise.

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_rail.py` from any directory to rebuild; run `... -b --python model/validate_fbx.py` to round-trip exports. `model/validation.txt` records finite geometry and UV data, UV layer presence and nonzero triangle area: **4,548 rail triangles** and **6,464 triangles per towel**. The model and previews were revised to prevent visible rail penetration at the towel folds. Unreal import, collision, lighting, material seams, contact and in-room clearances remain untested.
