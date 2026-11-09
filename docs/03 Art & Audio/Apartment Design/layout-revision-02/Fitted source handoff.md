# Rev02 fitted source handoff

Source snapshot: 2026-11-09. The new kits have parent visual review and FBX round-trip validation. They are ready for integration, with final independent source review passed and engine checks still pending. Original exports remain untouched.

| Kit | FBX parts | Placement / caveat |
|---|---:|---|
| ARC-WINDOW-KITCHEN-02 | 5 | North kitchen aperture1.60×1.15; common sill origin plan(2.15,0,1.25), not old floor origin. Window/sink paired geometric check passed; align sink rear bound Y=.15. |
| BR-CLOSET-02 | 6 | Closet centre plan(1.10,4.70); no shell walls in kit. Use assembly.json offsets and source-Y conversion. Single bulb bottom2.06. Keep Malcolm/camera space clear. |
| KI-CABINET-02 | 11 | 425/775/450mm fitted base fronts,650mm closed depth,910mm countertop. 775 paired doors/twin drawers retain four Sink_* identities. Manifest lists pivots. |
| KI-FRIDGE-02 | 2 | NOT SELECTED: measured imports keep X. Original KI-FRIDGE-01 already has west hinge; use it with corrected interaction pivot. This +X/east-hinge variant is retained unused. |
| ARC-SLIDING-CLOSET-02 | 3 | Coat/guest front only; .90clear/.96rough,2.18roughhead; .03linings. Source panels±.22X/±.028Y; slides±.44X. |
| ARC-DOOR-02 | 2 | Room doors .99clear/1.05rough,2.14roughhead. Source leaf hinge(-.495,-.035,0), source open-80Z. Match approved hinge jamb. |
| ARC-ENTRY-DOOR-02 | 2 | Entry .99clear/1.05rough,2.14roughhead; same hinge convention as room kit. Opens outward; casing/damage spacing requires engine check. |
| KI-WALL-TABLE-02 | 1 | Small table .90×.45×.74 at plan centre(2.45,3.455); source-sized joinery, floor contact corrected. Open underside collision. |
| ARC-CLOSET-STORAGE-02 | 1 | Separate shelf/rail/hangers repeated in coat and guest closets; rear-floor origin plan(11.375,6.34,0)/(11.375,6.46,0), front north/south. Shelf depth.30, full hanger envelope.485m. |
| KI-STOOL-02 | 1 | Stool .30×.30×.45 at plan centre(2.45,3.50), intentionally tucked under table; no animated interaction assumed. |

## Materials and collision

Reuse established painterly textures and tuned Unreal materials where compatible. Blender graphs do not transfer automatically; cupboard sage and ivory trim need in-room color review. Do not replace masked mold/stain with opaque materials. UVs and original generated textures are retained.

All moving wood/door parts include named UCX collision. Verify importer recognition, pivot and motion in Unreal. Keep aperture frame hulls separate; never auto-convex the complete opening into a blocking box. Glass, mold and thin repair overlays have intentional collision exceptions.

The integration team confirmed that UE5.8 Interchange drops authored UCX for these files; use legacy FBX import and verify hull counts. All tested kits preserved source X and flipped Y into Unreal, with fronts at+Y. These are measured import findings, not source README assumptions.

The source exports use more than one FBX axis convention. Each kit README/manifest controls. Do not copy an old yaw or mirror a complete actor with negative scale.

## Source fixes from review

- Table/stool feet corrected from a17mm float to floor contact; reimport bounds verified.
- Room/entry door pivot aligned to the barrel axis; matching UCX offset and negative source opening direction.
- Kitchen window casing overlap corrected; rear-bound-aligned sink/faucet has25.76mm nominal sill clearance through five sash positions.
- Closet mold toned to a textured dark olive patch.
- Closet box footprint corrected from a schematic thin wall projection to .30×.253m; one box at plan centre(.21,4.35).

## Ownership and acceptance

Art thread owns Art Source and layout-revision-02 docs. Integration thread owns editor8002, Content,Tools,Config,Source and maps. Separate L_Apartment_Rev02 / L_Apartment_Rev02_Gameplay pair preserves the existing default pending review. Both sides must say **files settled** before git operations.

Acceptance requires inventory-instance reconciliation, all41 click actions, four repair identities, real capsule routes, moving-part sweeps and encounter-camera checks in PIE, plus final room screenshots and no unresolved high/medium review findings. Source review alone does not meet those requirements.

## Review corrections — final pass

- CT/WG shelf records now use the separate ARC-CLOSET-STORAGE-02 kit instead of the door-only front.
- Kitchen cabinet pivots now align to barrelY−.2705; internal shelf fronts were recessed10mm. All11 exports and sampled0–100degree sweeps pass. Reimport complete body/door sets together.
- Original fridge artwork retained after imported-vertex measurement disproved the earlier handedness report.

## Independent source acceptance — 2026-11-09

Final read-only recheck found no remaining high or medium source/docs blockers. Cabinet pivots/shelf clearance, actual closet storage assignment, low box coordinates and original fridge selection were verified. Engine motion, material appearance, collision recognition and gameplay remain separate acceptance checks.

## Completed source revision — range fillers

KI-CABINET-02 was revised after the engine found range-side interference beyond42degrees. Overall .775/.450 worktop spans and origins stay unchanged. Final geometry: .735 carcass shifted−.020m with east filler for0775, and .410 carcass shifted+.020m with west filler for0450; filler faces recessed behind hinges. Final manifests and actual neighbour sweep results control. All11 FBX round trips,16 actual-neighbour door/drawer configurations and101 simultaneous poses pass. Tests include range body/controls, oven closed/open82degrees, sink, fridge and other cabinets. Doors sampled eachdegree0–100; drawers each5mm0–300. Reimport all0775/0450 bodies, doors and drawers together;0425 unchanged. Final engine sweeps remain required.

Independent range-filler recheck found no high/medium issues. Fresh FBX imports passed all 16 configurations and 101 combined poses; forced-overlap controls correctly failed. These are sampled render-mesh tests, with the fridge closed and oven at closed/82 degrees, not proof of every continuous state combination. The historical 42 degree failure was not reproduced with the revised narrower leaves. Integration subsequently reports full 100 degree engine neighbour sweeps passed after reimport, with a forced-overlap control. Final PIE and visual acceptance remain pending.
