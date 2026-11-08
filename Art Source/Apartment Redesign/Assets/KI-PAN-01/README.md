# KI-PAN-01 — vintage hanging frying pan

Status: Blender candidate for parent visual review; **not imported or tested in Unreal**. `concepts/pan-multiview-v1.png` is the generated multiview target. The hollow seasoned-iron bowl and separate walnut handle have subtle painterly color variation. The wooden handle includes a real through-hole for hanging; the hanging rail/hooks are a separate asset.

## Dimensions and assembly

Blender units are metres, Z up. The bowl has a 0.260 m outer diameter and is approximately 0.055 m deep. The handle extends along local +X; total assembled length is approximately 0.483 m. These are cooking-pan dimensions; the inventory's 0.35 m overall length was schematic and should be reconciled in room. The assembled pose has the bowl bottom at floor/tabletop z=0.

- `model/KI_Pan_Body.fbx`: hollow iron bowl, ferrule and two rivet meshes.
- `model/KI_Pan_Handle.fbx`: separate walnut handle with through-hole.
- Both have a common origin at the centre of the pan bottom; place with the same transform. A hanging placement needs a rotated assembly: aim handle toward the hook and check wall clearance and actual opening. These exports do not contain an animation or a rail.

`textures/iron.png` is the newly generated painterly dark iron texture. `textures/wood-selected.png` is reused from KI-KETTLE-01 for visual consistency. Blender uses image color plus iron metallic 0.18/roughness 0.77 and wood roughness 0.7; FBX does not carry a complete Unreal material graph. Reconnect the textures and tune metal response in room lighting. Check the generated image edges if tiling or remapping; seamlessness has not been established. The studio render `previews/pan-three-quarter.png` is not an Unreal appearance test.

## Build and validation

Run Blender headlessly with `--python model/build_pan.py` to rebuild source, FBXs and preview; `--python model/validate_fbx.py` reimports both FBXs. `model/validation.txt` records the latest run: 4,120 body triangles, 828 handle triangles, finite geometry, normals and UVs, no zero-area geometry or UV triangles. Separate FBX pivots, hanging orientation, collisions, texture materials and final appearance remain to be verified in Unreal.
