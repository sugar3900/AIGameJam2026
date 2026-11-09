# Rev02 implementation status

Updated 2026-11-09. User authorized the full approved-layout implementation, review and coordinated merge.

## Source complete

- All existing source folders reconciled with destinations/replacement/omission decisions; no unresolved IDs.
- Approved plan and36 matching wall elevations regenerated with fitted source IDs and explicit rough door widths.
- Ten new source kits built; nine selected, opposite-hinge fridge variant deliberately unused. Original fridge correctly west-hinged; old click-action pivot requires correction in engine.
- Selected fitted kits: kitchen window, three cabinet widths in one kit, mold-closet interior/doors, sliding fronts, coat/guest storage, room doors, entry door, small kitchen table and stool.
- Parent render review and FBX round-trip checks passed. Independent final source recheck reports no high/medium blockers.
- Reusable wainscot/trim, portal/header and shell cuts handled in engine with existing materials/profiles.

## Engine acceptance in progress

Integration team owns editor8002 and Content/Tools/Config/Source. It is building separate L_Apartment_Rev02 and L_Apartment_Rev02_Gameplay, preserving the current default pending review. It must confirm all41 click identities, four repair identities, real-capsule circulation, furniture sweeps, encounter cameras, full scene dressing and final screenshots. Actual imported vertices established that sourceX is retained and sourceY flipped; legacy FBX is required for authored UCX recognition in this setup.

## Review fixes

- Table/stool feet lowered to actual floor contact.
- Room/entry leaf pivots aligned with barrel axes and UCX.
- Cabinet door pivots aligned; internal shelves recessed10mm; full0–100degree sampled sweeps pass.
- Closet storage now its own exported shelf/rail/hanger kit; box footprint corrected.
- New window casing seam corrected; actual narrow sink/window assembly checked across sash travel.
- Erroneous fridge import diagnosis corrected; original artwork retained.

## Git coordination

Do not commit while either thread is writing. Each side must explicitly report **files settled**. Source files are uncommitted until the integration team coordinates the commit; no push/rebase/merge is implied by source approval. Final engine and PR review still required.

## Range-neighbour fit revision

The engine sweep found the 0775 right door and 0450 door contacting the range after about42 degrees. The selected fix is40mm recessed fillers on both range sides, narrower carcasses and unchanged overall countertop spans. Keep every door/drawer identity. This supersedes the earlier standalone-carcass sweep acceptance: actual range-neighbour mesh sweeps and engine reimport must pass before release. A temporary40degree engine limit is not the final design.

Engine reports all approved circulation paths clear at38cm capsule radius, except the intentionally closed entry and closet leaves; closet path clears when opened. Wyatt and Lukey standing points were repositioned after actual overlap tests. All four encounter points pass reported capsule/room/line-of-sight checks. Complete PIE interaction and screenshot review remains pending.

Cabinet filler revision is complete: all 11 round trips and actual-neighbour sampled sweeps pass. Independent exported-geometry review found no high/medium issues and verified forced-overlap controls. Integration reports successful reimport and full 100 degree neighbour sweeps; the temporary 40 degree limits are removed. Final PIE and visual acceptance remain pending.

Integration also reports all 97 elevation instances reconciled without outstanding placement problems. Actual pawn movement through the open closet clears at the centreline and at ±2/±4 cm offsets. Malcolm transition/encounter behaviour and final screenshots are still under review.

## First engine visual review

The first kitchen, kitchen-west, living, dining and office captures were reviewed by the art owner and an independent reviewer. One medium finding: office east botanical frame :073 overlapped shelf :074. The authoritative elevation generator/schedule now raises the frame bottom from 1.50 m to 1.65 m; engine placement and recapture requested. No other high/medium visual issues in those five views. Bedroom bookcase and shelf dressing are being supplemented with existing reusable book/plant/tin assets. Remaining room captures and final visual acceptance are pending.

PIE report confirms Malcolm conversation, bedroom room-id continuity through the closet, six-room travel and full cabinet sweeps. Malcolm visibility across the closet/bedroom boundary is inferred from room identity and code, not directly observed; do not count that as a direct visibility test.

## Art visual acceptance

All reviewed Rev02 room views pass after correcting the office frame/shelf overlap, seating the bedroom plant pot and removing the mold hotspot. The independent reviewer found no additional high/medium visual issues; art owner checked the final two recaptures. Seventeen PNGs and their checksums are archived in [engine-review/Review.md](engine-review/Review.md). Source exports and art docs are settled. Final engine gameplay report, code review and coordinated git work remain outstanding.

## Final traversal and code review follow-up

Real PIE movement found the old y=6.55 cross-bedroom path blocked by the right closet leaf. The authoritative plan/SVG now uses y=6.65, tested east–west then north into the walk-in and back. Measured hinge axis y=5.678, leaf tips y=6.181, bed north y=7.399: a radius 0.38 capsule has 8.9 cm leaf clearance and 36.9 cm bed clearance. No architecture or capsule change.

Independent final code review found one medium: three posed-open room leaves were spawned with NoCollision despite authored UCX. The engine team must enable their collision and repeat route checks before acceptance. No other high/medium C++ or pipeline findings were reported. Malcolm automatically leaves 0.35 seconds after conversation; post-talk disappearance is expected. Closet/bedroom room continuity is observed, while hypothetical idle-hunk persistence there is supported by code only. Lukey and Tyler conversations have now also been exercised in PIE.

## Final engine acceptance — 2026-11-09

Reviewed source, room captures and C++/pipeline changes have no unresolved high/medium findings. The room-leaf collision finding is fixed: bedroom, bath and office leaves collide and stand at 90 degrees. The full pipeline was rebuilt and doorway/encounter checks repeated.

- **57 interactions:** all 54 A+ labels retained (13 original plus 41 added), plus Cabinet_Door_2, Kitchen_Drawer_2 and Sconce_Kitchen.
- **17 sampled real clicks pass:** new/rebound cabinet fronts, fridge/closet/cupboard/pantry doors, console, lights, sink water, burner flame and bath-water fill. The remaining 40 actors are reconciled and trace-reachable, not individually clicked in PIE.
- **Four repair identities retained:** wyatt, lukey, tyler, malcolm. All four conversations ran to met=1; Wyatt used actual clicks, the other three used FixHimTalk.
- **Repair visual application passes:** a state-driven test set all four repaired after meeting them, then slept into the next day. Six hunk-associated damage overlays hide, verified by flags and before/after captures. This does not claim four complete repair-minigame playthroughs. Office lead paint remains intentionally visible.
- **Traversal:** the real 38 cm radius pawn clears the corrected y=6.65 bedroom route and open closet. Collision checks clear every planned room route except its starting point inside the deliberately closed entry leaf. All four encounter locations clear.
- **Motion:** 33 moving parts pass sampled collision sweeps with a forced-overlap sensitivity check; pantry/upper doors and curtain were bounds-checked. Range-side cabinet doors have their full 100 degree travel.
- **Room continuity:** closet and bedroom retain the bedroom room ID; travel skips the sub-volume. Malcolm automatically leaves after conversation. Persistence of an idle hunk while crossing the boundary is code-backed, not an observed reachable test state.

Full methods, labels and intentional dressing omissions: [Gameplay parity plan](../Gameplay%20parity%20plan.md#revision-02-integration-2026-11-09) and [engine reconciliation](../Rev02%20engine%20reconciliation.md).

Art and engine acceptance permit default-map promotion in a separate revertible config commit. PR review/checks and coordinated merge remain the final release step.
