# LV-FUSE-DAMAGE-01 — removable fusebox plaster damage

**Status:** provisional Blender visual pass; Unreal integration has not been tested. For Wyatt's existing `LV-FUSE-01` fusebox, the selected before/after concept is `concepts/fuse-plaster-before-after.png`. The BEFORE view calls for thin irregular cracks and shallow localized plaster chips, while AFTER leaves the wall intact. Actual damage remains separate from the intact wall, the fusebox and both wire-state meshes.

## Contents

- `model/LV_Fuse_Plaster_Damage.fbx` — one static mesh containing irregular shallow chipped plaster patches and tapered hairline crack ribbons. Its seven independent material slots are `Age worn grey`, `Age worn ochre`, `Exposed plaster ochre`, `Exposed plaster midtone`, `Chipped light edge`, `Crevice brown`, and `Hairline brown`. The age slots are subtle irregular opaque scuffs rather than a rectangular overlay; match their colors to the actual wall finish.
- `model/LV-FUSE-DAMAGE-01.blend` and `model/build_damage.py` — editable source and reproducible headless build. The `.blend` contains the non-exported wall and imported fusebox solely for preview; export/use only the damage mesh. The FBX does **not** contain the wall, fusebox, wires, light or camera.
- `previews/fuse-damaged.png` and `fuse-repaired.png` — Blender studio views showing the same actual fusebox with damage visible and hidden. They are not Unreal screenshots.
- `model/validate_fbx.py` and `validation.txt` — independent reimport geometry, UV and bounds checks.

The cracks were refined with denser irregular paths; the angular chips were reduced and subdued, with small restrained ochre/grey scuffs around the fuse. The damage is actual thin opaque geometry, **not a rectangular decal or alpha card**, so no alpha mask or mask threshold is needed. There is no painted grunge texture; painterly appearance comes from the irregular shape, restrained colors and underlying room finish. Recreate/tune the seven rough opaque material colors in Unreal (Blender material nodes are not a finished UE material). Consider batching the seven slots if draw calls matter. Set decorative collision and shadow casting off; the base wall remains the collision surface. The patch is a stylized visual overlay, not a physically recessed hole.

## Transform and fitting

Source convention matches `LV-FUSE-01`: metres, Z up, X across the box, **−Y toward the room**, wall face at Y=0. The origin is **(0,0,0) at the wall behind the centre of the fusebox's lower box edge**, exactly the same source origin as `LV_FUSE_01_Shell.fbx` and its wire states. Load with the same scale, orientation and wall-plane origin as the shell. The FBX uses Blender's default export axis settings; test the *same* Unreal import conversion as the existing fuse shell, rather than assuming an unverified world yaw. The reimported mesh has origin (0,0,0); local bounds in metres are X=−0.4051…0.3962, Y=−0.0032…−0.00065, Z=−0.1632…0.8102. Fusebox body itself is 0.45 m wide and 0.58 m high. The visual face is only 0.65–3.2 mm in front of the wall; check depth sorting, normal facing, door sweep and material contrast at the actual transformed wall. If a wall is offset from the fusebox's wall datum, move the overlay a small amount **toward the room**, not behind the wall, and adjust as a unit. Do not blindly place against a second coincident wall.

The existing placement script `Tools/Editor/place_redesign_remaining_furniture.py` documents fuse shell placement at `(312.5,374,120)` cm and yaw 180° in its own map convention; this is historical guidance only. Match the actual placed shell in the current level after import, not a hard-coded location if the integration thread has adjusted it.

## Repair lifecycle

Place the damage as a separate nonblocking actor or component; attach the actor to the actual Wyatt malady and tag it `RepairDamage` (and `wyatt` if the level's conventions require it). `AFixHimMalady::RefreshRepairState` currently hides **attached actors** with `RepairDamage` when fixed; an unattached actor or a tag only on a mesh component is not automatically equivalent. Verify initial broken, repair, save/load, reset and repaired state in Unreal. Hiding this mesh must leave the wall and fusebox visible; the existing damaged/repaired wire swap remains a separate responsibility.

## Validation and rebuilding

The checked FBX reimport has one mesh, 970 vertices, 860 triangular faces, seven material slots, finite coordinates/UVs and zero zero-area faces; see `model/validation.txt`. Run from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python 'Art Source/Apartment Redesign/Assets/LV-FUSE-DAMAGE-01/model/build_damage.py'
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python 'Art Source/Apartment Redesign/Assets/LV-FUSE-DAMAGE-01/model/validate_fbx.py'
```

The first command regenerates the asset FBX, previews and `.blend` **inside this folder only**, while reading existing fuse FBXs. It does not change the source fusebox. Blender's reimport checks do not verify Unreal transforms, materials, depth sorting, collision or repair/save behavior.

## Concept generation

Built-in imagegen was given the approved painterly fixer-upper reference and asked for two front views of the same vintage fusebox and warm plaster: before with localized irregular hairline cracks and shallow chips, after with clean repaired plaster, warm light and no people or text. The image is design guidance; the actual removable mesh is constructed to the fusebox's measured coordinates rather than copied from the concept.
