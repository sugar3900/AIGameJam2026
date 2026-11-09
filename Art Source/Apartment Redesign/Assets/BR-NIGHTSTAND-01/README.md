# BR-NIGHTSTAND-01 — bedroom nightstand

A 0.45 × 0.45 × 0.52 m vintage walnut nightstand with turned legs, lower shelf, hollow drawer box and an aged-brass bail pull. The selected concept sheet shows front, side, back and open/closed views. Two placements are planned in the bedroom; verify both bed clearances and drawer travel in the assembled room.

## Source and materials

`model/BR-NIGHTSTAND-01.blend` is the editable Blender source; `model/build_nightstand.py` rebuilds geometry, FBXs and studio previews. `previews/nightstand-closed.png` and `previews/nightstand-open.png` show the two states. The selected `textures/walnut-muted-b.png` is an independent painterly candidate reused from the living-room chest; Blender desaturates it to 0.68 and raises value to 1.35. The daybed wood candidates remain for comparison. Small geometry marks provide restrained rubbed edges. The drawer interior uses the same texture lightly mixed with a warm lighter color; the interior mix must be recreated in Unreal.

## Export and interaction

`BR_NIGHTSTAND_BODY.fbx` and `BR_NIGHTSTAND_DRAWER.fbx` are separate meshes with a common origin at floor centre in the closed position. In Blender coordinates the drawer slides 0.22 m toward -Y; verify the corresponding local axis and common transform after Unreal import. The open render uses this travel. A sliding movement is possible but is not yet connected to game code; collision, obstruction, camera clearance and material recreation require in-game testing.

Both FBXs passed `model/validate_fbx.py` reimport checks for finite geometry, UVs, non-zero-area triangles and origin. Body is approximately 0.45 × 0.451 × 0.52 m including edge wear; see validation output for triangle counts. Drawer is about 0.319 × 0.389 × 0.13 m. Its front was widened to leave a small, even clearance at the frame when closed. Blender uses 0.83 roughness for the wood and muted semi-metallic brass. Recreate these materials on import and check color, texture orientation, lighting, collision and the drawer travel in Unreal. The item has not yet been imported or tested there.
