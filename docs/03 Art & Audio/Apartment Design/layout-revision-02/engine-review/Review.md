# Rev02 engine visual review

Reviewed 2026-11-09. These are actual Unreal viewport captures of the separate `L_Apartment_Rev02` map. They are not Blender renders. The original default map remains unchanged.

## Result

Art visual review passed after the corrections below. Independent review of the room captures found no additional high/medium visual issues. Final recaptures of the plant and mold corrections were checked by the art owner. This is visual acceptance, not blanket gameplay or merge approval.

## Corrections completed

- Range-side cabinet doors: 40 mm recessed fillers and narrower carcasses preserve countertop spans and click identities. Full 100 degree engine sweeps reported passing after reimport.
- Office east botanical frame: bottom raised from 1.50 to 1.65 m to clear display shelf :074; source elevation schedule updated.
- Bedroom bookcase and display shelf: populated using existing books, plant, box and tin props.
- Bedroom plant: pot base seated on bookcase; trailing leaves hang below it.
- Closet mold: matte material and interaction light moved away from the wall remove the white hotspot.

## Validation boundaries

Source exports passed independent geometry review. Integration reports all 97 elevation instances reconciled, real-capsule routes and full door/drawer travel checked, and forced-overlap controls confirmed. Original click-action preservation and all four repair identities remain part of the engine acceptance record.

PIE reports Malcolm conversation, room-id continuity between closet and bedroom, travel to all six main rooms, and traversal through the open closet at centre and ±2/±4 cm offsets. At this snapshot, Malcolm visibility across the closet boundary was inferred from room identity/code rather than directly observed. Later PIE captures confirm Malcolm during conversation and his expected automatic departure after conversation ends; Lukey and Tyler conversations were also exercised. Further click/reveal/repair coverage belongs in the final engine acceptance report.

A later real movement test found the old cross-bedroom route at y=6.55 blocked by an open leaf. The authoritative plan now uses the successfully tested y=6.65 route, with 8.9 cm capsule clearance to the leaf and 36.9 cm to the bed. Final code review also found disabled collision on the three posed-open room leaves; correction and repeated doorway route checks are required before engine acceptance.

Some direct sun highlights lose surface detail. This is low-priority polish; the intentional warm golden painterly palette is retained.

## Final engine acceptance — 2026-11-09

Reviewed source, room captures and C++/pipeline changes have no unresolved high/medium findings. The room-leaf collision finding is fixed: bedroom, bath and office leaves collide and stand at 90 degrees. The full pipeline was rebuilt and doorway/encounter checks repeated.

- **57 interactions:** all 54 A+ labels retained (13 original plus 41 added), plus Cabinet_Door_2, Kitchen_Drawer_2 and Sconce_Kitchen.
- **17 sampled real clicks pass:** new/rebound cabinet fronts, fridge/closet/cupboard/pantry doors, console, lights, sink water, burner flame and bath-water fill. The remaining 40 actors are reconciled and trace-reachable, not individually clicked in PIE.
- **Four repair identities retained:** wyatt, lukey, tyler, malcolm. All four conversations ran to met=1; Wyatt used actual clicks, the other three used FixHimTalk.
- **Repair visual application passes:** a state-driven test set all four repaired after meeting them, then slept into the next day. Six hunk-associated damage overlays hide, verified by flags and before/after captures. This does not claim four complete repair-minigame playthroughs. Office lead paint remains intentionally visible.
- **Traversal:** the real 38 cm radius pawn clears the corrected y=6.65 bedroom route and open closet. Collision checks clear every planned room route except its starting point inside the deliberately closed entry leaf. All four encounter locations clear.
- **Motion:** 33 moving parts pass sampled collision sweeps with a forced-overlap sensitivity check; pantry/upper doors and curtain were bounds-checked. Range-side cabinet doors have their full 100 degree travel.
- **Room continuity:** closet and bedroom retain the bedroom room ID; travel skips the sub-volume. Malcolm automatically leaves after conversation. Persistence of an idle hunk while crossing the boundary is code-backed, not an observed reachable test state.

Full methods, labels and intentional dressing omissions: [Gameplay parity plan](../../Gameplay%20parity%20plan.md#revision-02-integration-2026-11-09) and [engine reconciliation](../../Rev02%20engine%20reconciliation.md).

Art and engine acceptance permit default-map promotion in a separate revertible config commit. PR review/checks and coordinated merge remain the final release step.

## Reviewed captures

### Kitchen north counter

![Kitchen north counter](r2_kitchen.png)

### Kitchen pantry and wall table

![Kitchen pantry and wall table](r2_kitchen_west.png)

### Kitchen return and portal

![Kitchen return and portal](r2_kitchen_east.png)

### Kitchen doors open

![Kitchen doors open](r2_kitchen_open.png)

### Living from dining

![Living from dining](r2_living.png)

### Dining from living

![Dining from living](r2_dining.png)

### Bedroom bookcase and closet

![Bedroom bookcase and closet](r2_bedroom_west.png)

### Bedroom dresser and display shelf

![Bedroom dresser and display shelf](r2_bedroom_east.png)

### Office wainscot and corrected picture

![Office wainscot and corrected picture](r2_office_east.png)

### Office daybed and desk

![Office daybed and desk](r2_office_alt.png)

### Bath north

![Bath north](r2_bath_north.png)

### Bath basin and tub

![Bath basin and tub](r2_bath_west.png)

### Hall end cabinet

![Hall end cabinet](r2_hall_end.png)

### Entry and fuse box

![Entry and fuse box](r2_entry.png)

### Relocated coat closet

![Relocated coat closet](r2_coat.png)

### Walk-in closet open

![Walk-in closet open](r2_closet_open.png)

### Mold closet interior

![Mold closet interior](r2_closet_inside.png)

## Repair state evidence

Scene-capture images verify damage visibility; their exposure and interaction highlights differ from the reviewed viewport images above.

### Lukey

[Before repair](pie_repair_lukey_before.png) · [After repair and sleep](pie_repair_lukey_after.png)

### Wyatt

[Before repair](pie_repair_wyatt_before.png) · [After repair and sleep](pie_repair_wyatt_after.png)

### Tyler

[Before repair](pie_repair_tyler_before.png) · [After repair and sleep](pie_repair_tyler_after.png)

### Malcolm

[Before repair](pie_repair_malcolm_before.png) · [After repair and sleep](pie_repair_malcolm_after.png)

