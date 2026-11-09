# Integration handoff

This is a working checklist, not a claim of implemented functionality. The new apartment and its assets have not yet been imported or tested in the game.

## Closet and bedroom conditions

- Put Malcolm's existing `malcolm` malady, authored mold damage and encounter stand position inside the bedroom closet; keep the mold entirely behind the closed leaves. The closet has one bare hanging bulb. Check that the actual character fits, the doors can open without intersecting anyone, and the interior is readable from the bedroom.
- A closed door must occlude the mold and prevent its interaction prompt or glow from leaking through it. The two leaves, target visibility, interaction gating, light and audio need an explicit coordinated implementation; two unrelated rotate actors alone do not establish that behavior.
- `AFixHimMalady::RefreshRepairState` currently hides attached actors tagged `RepairDamage` after the relevant hunk is fixed. Verify that the authored mold follows this lifecycle on initial load, repair, save/load and reset, with no duplicate procedural damage visible. Verify the closed state after loading and the restored wall after repair.
- `BeginEncounter` currently teleports the player to `TalkSpot`, summons the hunk at `HunkSpawn`, and blends to the malady camera. Author and test all three positions for the confined closet, including line of sight, player capsule and camera clipping; `FindStandLocation` traces down from the spawn point, so its floor collision must be correct.
- The white bedroom wainscot and its local lead-paint damage are distinct from Malcolm's mold. The lead-paint character is currently backlog; do not map it onto `malcolm`, overwrite existing story progress, or represent an unimplemented encounter as playable. The damaged and sealed visual states need a separately keyed lifecycle when that character is implemented.

## Layout and persistence

- Place room volumes and entry transforms for the revised living room, kitchen, hall, bedroom, bath and office; verify crossings and floor-plan travel, including the closet threshold and door swings. Existing room IDs and existing hunk IDs must remain compatible with dialogue and saved progress.
- The controller currently restores saved world-space `PlayerLocation` directly. Add a versioned migration or validated safe-room fallback for old positions after moving walls, while preserving dialogue and repair progress. Exercise an old save located in each former room and a new save in the closet.
- Test collisions and third-person camera with the real player and character assets, not just nominal furniture footprints; test interactions while doors, drawers and curtains are in both positions. Check the hall console and runner, bedroom dresser passage, closet doorway, office chair and kitchen table in particular.
- Recreate or adapt exported materials rather than assuming Blender nodes transfer through FBX. Check mirrored world-space wall mapping at rotated walls and seams, glass, mirror reflection, masked mold, soft textiles, emissive bulbs, collision, pivots and curtain morph import. Compare the assembled scene with the painterly reference under game lighting.
- Capture representative room views and run an actual playthrough of interactions, repair, save/load, reset and floor-plan travel after integration. Record results and unresolved defects before declaring the apartment complete.
