# BA-ROLL-01 — bathroom paper roll and holder

A vintage brass wall-mounted holder with a hollow ivory roll and hanging tail, corresponding to `P-BA-ROLL` in the bathroom elevation. The generated five-view concept is `concepts/holder-multiview-v1.png`; the selected concept is visual guidance rather than a measured blueprint. `previews/roll-perspective.png` shows the Blender model.

## Files and placement

- `model/BA-ROLL-01.blend` is the editable master; `model/build_roll.py` rebuilds it and the exports.
- `model/BA_Roll_Holder.fbx` contains the rosettes, screws, curved arms, collars and fixed spindle as 15 static meshes with their assembled transforms. The holder is 0.180 m wide × 0.081 m wall projection × 0.045 m high. Its rosettes sit on the wall plane at local Y=0; front faces local −Y, X is across the fixture, and Z is up. Preserve transforms or combine meshes when importing.
- `model/BA_Roll_Paper.fbx` is a separate hollow roll with the paper tail and small layer-edge rings. Its roll-axis origin is `(0, -0.071, -0.014)` m relative to the wall-plane midpoint of the holder. Reassemble the exports at their authored transforms; check importer axis/origin handling. The paper mesh extends approximately 0.118 m from the wall and down to 0.089 m below the rosette centre. Place around the actual toilet and check reach/clearance in the finished bathroom.
- The roll can rotate about its local X axis if desired, but the tail is part of the rigid roll. **No unrolling animation exists**; a believable unspooling tail requires a separate deformation/animation. The spindle is fixed in this export.

## Materials and validation

`textures/aged-brass.png` is reused from the reviewed hall sconce; `textures/paper.png` is a separately generated matte paper swatch. The Blender material multiplies these by the color tints in `build_roll.py`; reconstruct these materials in Unreal rather than assuming the FBX transfers the Blender shader graph. The paper tail is a zero-thickness mesh: use a two-sided paper material. Its layer-edge rings are geometry, not a normal map. No preview wall or lighting is exported.

Run `/Applications/Blender.app/Contents/MacOS/Blender -b --python model/build_roll.py` to rebuild and `Blender -b --python model/validate_fbx.py` to reimport and check the FBXs. `model/validation.txt` records finite geometry/UVs, nonzero geometry and UV triangle areas, and bounds. The holder has 6,604 triangles and the paper 5,552; inspect performance, paper seams, material appearance, mounting, axis/pivot orientation and interaction in Unreal. No Unreal import, collision or gameplay testing has been performed.
