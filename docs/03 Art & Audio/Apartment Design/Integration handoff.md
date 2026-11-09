# Integration handoff

The user approved the **compact kitchen/dining layout on 2026-11-09**, with the fridge beside north-wall prep. The [current handoff](layout-revision-02/README.md), [approved plan](layout-revision-02/kitchen-dining-study/approved-plan.svg), [coordinates](layout-revision-02/kitchen-dining-study/approved-plan.json) and [matching elevations](layout-revision-02/kitchen-dining-study/elevations/README.md) supersede earlier A+ and revision 02 layout coordinates. Geometry, motion and gameplay validation remain pending; this approval records the design choice, not completed engine work. The integration team's editor/Content/Tools reservation remains active.

The original sections below predate engine assembly; dated integration feedback takes precedence over older untested-status statements.

## Integration feedback — 2026-11-08

Reported by the environment integration team; these are their in-engine findings, not new editor tests by the art thread.

- The delivered FBX imports had no authored simple collision. The team changed **226 redesign meshes** to **Use Complex Collision As Simple** to restore player blocking and click traces. Re-run `Tools/Editor/build_redesign_collision.py` after re-import. Do not assume this workaround is preserved by a re-import or establishes physics-simulation suitability.
- Future moving doors, drawers and lids should include convex `UCX_<render mesh name>_<index>` hulls tied to each moving mesh/pivot. Validate imported hulls, click tracing, player blocking and open/closed sweeps. Existing exports were not retrofitted in this documentation pass.
- `ARC-DOOR-01` and `ARC-ENTRY-DOOR-01`: rough width = clear width + 6 cm; rough header at 214 cm. `ARC-SLIDING-CLOSET-01`: same width allowance, rough header at 218 cm. These are for current unscaled kits; the team already corrected the level walls. Casings cover the cut. A different planned clear width still requires a matching frame and leaf.
- Sofa orientation: source −Y front becomes imported +Y under their import settings; **yaw −90° corrected the existing placement**. Future furniture options specify plan-facing directions; calculate their own world rotations rather than copying that yaw universally.
- The user subsequently moved the proposed white wainscoting and separate lead-paint feature to the **office/guestroom**. Original bedroom references below are historical A+ instructions; the pending revision documents the new location. Closet mold stays in the bedroom.

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
