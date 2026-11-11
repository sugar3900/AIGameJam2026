# ROUND3-CLOSET-FRAME-01 — regular-door casing match

Replace the fixed frame on both coat and office sliding closets. Panel art, panel roots, travel, guides and structural opening remain unchanged. Original ARC-SLIDING-CLOSET-02 and FEEDBACK-ROOM-03 files are immutable; this is an additive replacement.

## Matching profile

The new frame uses the actual ARC-DOOR-03 regular doorway sections on both faces: 90 × 25 mm vertical casing, 75 × 28 mm head casing, and 22 × 38 mm shallow top cap with 10 mm side overhang. Eased edges and paint image/node blend match the regular doorway. Width adapts to the closet's 900 mm clear opening, and the casing is seated against its existing 140 mm partition rather than the regular door's 120 mm partition. There is one head casing and one shallow cap per face, without another fascia or cornice.

Compared with the old sliding frame, side casings become 25 mm thick from 18 mm, the head 28 from 25 mm, the cap 38 from 40 mm, the head width becomes 1080 from 1060 mm and the cap width becomes 1100 from 1080 mm. The back receives the same shallow cap as the front. Side casings still meet the head underside at z 2.1625 m; no old 12.5 mm gap returns.

The reported screenshot may also include an overlapping installed header: the old source itself has only one front head plus cap. Integration should audit nearby fixed actors as well as replacing this mesh.

## Import and placement

- `model/ARC_ClosetFrame04.fbx`, floor origin `(0,0,0)`, metres, FBX **forward -Y / up Z**, matching ARC_Sliding03_Frame. Import its main mesh combined and its three UCX hulls, or reuse the old three hulls. They are exactly the old two jamb boxes and head box; none bridges the opening.
- Keep both installed fixed-frame actor transforms. Replace only their frame mesh. Keep the left/right panel source origins `(-.22,-.028,0)` / `(.22,.028,0)` m and +.44 / -.44 m local-X travel.
- Clear jamb opening remains `.90 × 2.15` m, rough opening `.96 × 2.18` m. Track coordinates are unchanged.
- Full decorative bounds are `(-.55,-.101,0)` to `(.55,.101,2.259)` m.
- **Baseboard stops use the floor casing, not the whole mesh bounds.** At z 0… .13 m, casing X remains `±.54` m, exactly the old stop width; front/back face depth becomes `±.0945`. The new `±.55` width is the high cap overhang only. Do not shorten floor baseboards by 10 mm based on that high cap.

`assembly.json` records exact component positions, sections, bounds, roots and collision contract. `model/ROUND3-CLOSET-FRAME-01.blend` includes old panels as display references only; they are not exported or replaced.

## Materials

Main mesh slots: `Painted warm ivory`, `Aged track`. Bind the former to the same installed ivory paint used on ARC-DOOR-03; source uses `paint-selected.png` (sRGB) mixed 35% toward `(.85,.79,.68)`, roughness .78, metallic 0. The copied image is byte-identical to ARC-DOOR-03's. Track is the retained dark aged metal `(.25,.22,.18)`, roughness .58, metallic .45. Every visible component has meaningful UV0; keep opaque surfaces single-sided. Imported FBX Phong is not a finished Unreal paint graph.

## Checks

Fresh FBX validation verifies 15 individually outward, closed manifold components, zero degenerate triangles, finite nonzero UV0 in both slots, the exact unchanged three structural hulls and section dimensions independently compared with the actual regular-door FBX. Forty-two samples across both complete ±44 cm panel strokes remain inside the old jamb envelope and retain at least 14 mm gap from the new casing backs. Original panel-to-guide seating is retained. Installed slide clicks, trim stops and close header views remain required before acceptance.
