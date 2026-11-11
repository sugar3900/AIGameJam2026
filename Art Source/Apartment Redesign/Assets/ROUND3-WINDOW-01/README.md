# Round 3 window header joins

Additive render-frame replacements for the five installed window types. Original released window kits, glass and moving sashes are unchanged. `model/build_patch.py` imports each original FBX, corrects only its head join and exports an editable blend and FBX. `validation.json` contains original paths, axes, material slots, bounds, gap-ray results and fresh-import checks.

| Export | Installed counterpart | FBX axes | Correction |
| --- | --- | --- | --- |
| `ARC_Window_Narrow03_frame` | Bedroom ARC_WindowNarrow frame | forward -Y / up Z | Casing lower edge 2.3225 → 2.292 m |
| `ARC_Window_Office03_frame` | Office ARC_WindowOffice frame | -Y / Z | Same 30.5 mm header extension |
| `ARC_Window_Bath03_frame` | Bath ARC_WindowBath frame | -Y / Z | Same 30.5 mm header extension |
| `ARC_Window_Kitchen03_frame` | Kitchen ARC_WindowKitchen02 frame | -Y / Z | Local casing lower edge 1.155 → 1.142 m |
| `ARC_Window_Living03_Casing` | Living ARC_Window_Casing_Sash | -Z / Y | Wooden head reveal liner joins casing to sash depth |

All FBXs are under `model/`. Keep each existing actor origin, orientation and scale. South window floor origins remain (BR 385,955,0), (OF 1040,955,0), (BA 582.5,955,0) cm at yaw 180. Kitchen retains its **sill origin** (215,0,125) cm, yaw 0. Living retains (855,0,0), yaw 0. Do not apply the kitchen sill offset to the floor-origin variants.

The three south-window casing boards originally stopped 22.5 mm above the jamb head, exposing the wall between them. Their extended lower edges now overlap the jamb by 8 mm to form a closed rebated join. The kitchen had a 5 mm version of the same gap and now has 8 mm overlap. Bevel widths, outer frame bounds, material slots and existing UVs are preserved; only the lower half of the header board changes height. The living kit already overlaps in elevation but lacked a head return across the depth gap. Its new liner stays within the original outer bounds, uses the original ivory trim material and projected UV0.

Kitchen custom frame hulls are copied unchanged from the original export with matching UCX names. All other frame collision should be retained from the installed original; do not auto-convex the whole frame. The small wood overlap lies inside the wall/header region. Preserve independent sash/glass actors, window view cards, lights and their day/night settings.

Validation covers nine rays through each former wall-revealing band, all blocked by wood after correction (the original failed), then repeats the ray check on freshly imported FBXs. Each closed component must have positive signed volume and manifold edges. All five exact outer bounds and slot names are asserted unchanged. Engine acceptance must additionally inspect every header from normal and low/oblique views, including day and night where relevant.
