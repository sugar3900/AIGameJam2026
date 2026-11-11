# Pantry meeting reveal and paint UV correction

Additive door-only replacement for CABINET-JOINERY-02. The installed pantry uses that kit's `KI_Pantry02_LeftDoor` and `KI_Pantry02_RightDoor`, rather than the older KI-PANTRY-01 leaves. Its 454 mm leaves centred at ±235 mm left a 16 mm meeting gap. The old paint UV projection scaled height by 1.7, repeating the image about 2.8 times on each 1.65 m door.

`build_patch.py` reads the released editable `CABINET-JOINERY-02/models/Pantry.blend`. It extends each leaf's latch edge 6 mm, retaining the 40 mm meeting stile width by translating that stile and its complete knob assembly; horizontal rails and inset fields extend to meet it. Hinge-side stile, hardware, outer edge, height and depth remain unchanged. The resulting centre reveal is 4 mm. The carcass is unchanged.

UV0 maps fields and stiles continuously over the full door height without restarting at the centre rail or crossing an image wrap. Left and right doors sample separate crops, with the right leaf reversing the brush order. Rails use rotated crops for horizontal brushing. The existing `T_Joinery_Sage.png` is copied unchanged and its tint is already baked. Reuse the installed `MI_Joinery_Sage` with ordinary UV0 sampling, plus the existing aged-brass and ivory-knob finishes. All three slot names and ordering remain identical.

## Integration contract

| New FBX | Replaces | Existing source hinge pivot, metres | Engine swing |
| --- | --- | --- | --- |
| `models/KI_Pantry03_LeftDoor.fbx` | `Joinery02/KI_Pantry02_LeftDoor` | (-0.470, -0.318, 1.020) | +100° yaw |
| `models/KI_Pantry03_RightDoor.fbx` | `Joinery02/KI_Pantry02_RightDoor` | (+0.470, -0.318, 1.020) | −100° yaw |

Both exports use pivot-local vertices and identity object transforms, with FBX forward -Z / up Y, matching Joinery02. Swap meshes at the current interactable and hidden art-copy transforms. Do not translate or scale actors, move roots, change travel, or use the scene's assembled object locations as another offset.

Each FBX includes one appropriately widened `UCX_<mesh>_00` slab: 460 × 22 × 1650 mm. Import the new authored UCX hull rather than keeping the old 454 mm slab or generating a box around the knobs. Preserve the current collision response policy. The hinge barrels and protruding knobs remain outside the slab, as in the previous release.

`validate_fbx.py` imports both new FBXs and the previous exports afresh. It checks the measured 16 → 4 mm gap, identity transforms, unchanged outward edge and Y/Z bounds, matching slot order, finite geometry, manifold edges, no degenerate faces, bounded nonwrapping paint UVs and exact slab/leaf bounds. It tests both leaves against the original pantry carcass and against the opposite leaf in 21 poses from 0° to 100°: each moving alone and both opening together, 105 triangle-surface comparisons. `validation.json` records zero contacts. Installed fridge/wall neighbours, hover, real clicks and engine material appearance remain the integration owner's checks.

`models/Pantry03.blend` retains the assembled editable scene; UCX boxes are visible as wireframes and hidden from renders. `previews/Pantry-closed.png` and `Pantry-open.png` show the corrected source appearance. The file manifest hashes both exports and the unchanged copied image.

Review follow-up: thin painted edge/end faces use a depth coordinate selected by face normal, preserving the front crops while avoiding collapsed UVs when doors open. `fix_edge_uv.py` migrates the released blend/FBXs; `edge-uv-validation.json` and the fresh-FBX validator assert zero collapsed painted UV triangles. Geometry, pivots and hulls are unchanged.
