# OF-WAINSCOT-02 — fitted office wainscoting

FIX-019 replaces the old scaled one-metre office wall modules with six fitted wall runs. The painterly ivory texture is retained. Maximum projection falls from 72 mm to **22 mm**; rails remain continuous along each uninterrupted run, stiles keep their 60 mm width, and inside/outside corners use matching 45° profile joints. Original source kits remain unchanged.

## Files and placement

Six exports: `model/OF_Wainscot02_N.fbx`, `_CS.fbx`, `_WF.fbx`, `_E.fbx`, `_S.fbx`, `_W.fbx`. Their geometry is baked to a common office floor origin; **place all six at UE `(796,566,0)` cm, yaw 0, scale 1**. Do not centre individual files or tile/scale them. Source metres, +Z up, X east, Y north; source-to-plan is `(7.96+sourceX,5.66−sourceY,sourceZ)`. The established Unreal import keeps X and flips Y.

`assembly.json` contains exact bounds, source transforms and termination dimensions. `model/build_fitted.py` rebuilds the kit and context views headlessly. `model/OF-WAINSCOT-02.blend` includes the assembled office run and actual original door, wardrobe and window frames for review; context geometry is excluded from FBXs. `model/validate_fitted.py` checks independent FBX imports and intersections with those actual frame meshes.

Remove only the old `Wainscot_OF_*` module actors when integrating. Retain office crown, plaster, windows, door/closet frames, sliding panels and gameplay. The new backing begins 1 mm in front of the finished wall, with its recessed face 7 mm forward. No new blocking collision is supplied; existing structural walls retain movement collision. Review all six placements and existing door/wardrobe sweeps in the game before accepting.

## Casing, corners and window fit

- Office room casing occupies X=9.390–10.560 m. North runs stop 2 mm outside its outer edges, not at the rough opening. Rails have closed painted profile end caps; no extrusion ends or raw wood remain open.
- Wardrobe casing occupies X=10.840–11.920 m. The usual outside closet corner is mitred through all profile layers. At the very tight eastern corner, only 20 mm of plaster remains: its return is a plain 7 mm backing, while the east run starts at Y=7.239 m, 2 mm in front of the casing face at 7.237. This avoids forcing the 22 mm rail through the casing. The actual wardrobe source frame stays unchanged.
- Office south window casing extends X=9.6125–11.1875, and its sill X=9.590–11.210, Z=.8715–.9165 m. The upper panel ends are relieved around the sill with 2 mm clearance.
- Under-window panels have a purpose-built top at **.778 m**, 5 mm below the actual apron bottom .783 m. Their field height changes, while base, lower rail, cap and stile profiles retain their dimensions. Lower rails/base continue across the window wall without modular seams. The regular top remains 1.10 m.
- The paint texture is applied at a consistent physical scale; profiles are not scaled to fit a bay. Closed caps use the same ivory paint on their end faces.

## Engine shell check at the outer closet corner

The current `rev02_03_shell.py` ends ClosetSide at Y=7.15 and begins WardrobeFront at X=10.75. With 120 mm walls, their finished planes leave a 60 × 60 mm outer quadrant unfilled at **X=10.69–10.75, Y=7.15–7.21, Z=0–2.75 m**. Verify the actual map, which may include later corrections, and extend one wall 60 mm or fill this quadrant with matching plaster. The fitted trim assumes the intended square corner at `(10.69,7.21)`; do not preserve that structural notch behind/above it. This is an engine shell correction, not another art export. Preview walls show the intended closed corner and actual rough openings behind the casings.

## Lead-paint overlay

Keep the existing `Damage_BR_LeadPaint` actor, material, alpha image, identity, tags and current scale. Its north-wall centre stays X=8.925, Z=.700 m. Move the **visible overlay plane** to plan **Y=5.668 m**, 1 mm ahead of the new recessed face Y=5.667. This is a mesh-plane/bounds-centre target, not a raw actor-origin value; the old source overlay has an offset baked into its vertices. The existing placement normally has plane Y=5.676, so this is an 8 mm move toward the wall.

The current original mesh at 1.49 X scale spans about .4619 × .22 m: X=8.69405–9.15595. The fitted northern recessed field stays clear from X=8.662–9.296, so the existing patch fits without crossing new stiles/beads. Keep its current visual size and scheduled region rather than stretching it to a new panel. The source preview reuses the original overlay only for context; no replacement damage mesh is exported.

## Materials and checks

`textures/painted-ivory.png` is an unchanged copy of the selected BR-WAINSCOT-01 ivory texture. Use it directly as sRGB Base Color, roughness .80, metallic 0, opaque. Do not multiply the image by a warm fallback tint. The blend packs its images; FBX shader graphs are not the material authority.

Source validation checks finite geometry/UVs, source origins, export bounds, zero-area triangles, closed profile ends and no intersection with the actual imported room/wardrobe/window frames. Context previews show the door, outside closet corner, tight wardrobe corner and under-window run. These checks support source release; actual engine lighting, trim joins, lead-paint interaction and traversal are separate acceptance steps.
