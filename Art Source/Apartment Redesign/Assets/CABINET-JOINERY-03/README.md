# CABINET-JOINERY-03 — FIX-033 sink-side leaf clearance

A two-mesh patch to CABINET-JOINERY-02, which remains immutable. Only the 0775 left leaf changes; all other joinery, materials, drawers and placements remain installed as before.

## Geometry and fit

The hinge moves 32 mm toward the centre of the cabinet: source pivot (-.3455,-.253,0) metres, world (271.7,72.8,0) cm. The leaf is narrowed 32 mm on its hinge side only; its latch edge, pull and vertical dimensions remain in place. The 22 mm frame, 6 mm recessed panel and 96 mm bow pull are retained. A separate 22.5 mm-wide painted filler covers the hinge-side carcass strip; its front is recessed 3 mm behind the door back to clear the moving leaf. The filler ends 1 mm before the hinge barrel. This small hinge reveal is intentional.

## Install

- Replace ONLY Sink_Door_L's Body with models/KI_Cab04_0775_door_L.fbx. Identity pivot-local mesh, root at the new transformed pivot. World root (271.7,72.8,0), assembly yaw 0. Remove old mesh offsets. Keep existing label, prompts, room, SFX and authored materials.
- Restore +100 degrees engine yaw travel AFTER installed sweep passes. Source equivalent -100 degrees about Z. Keep temporary 54 degrees until validated.
- Add models/KI_Cab04_0775_Filler.fbx as stationary art at the 0775 BODY assembly transform: world (306.25,47.5,0), yaw 0. Its vertices are assembly-local; never attach it to the rotating door. Associate it as a child of the existing cabinet reconcile group; no extra furniture instance.
- Both meshes have one UCX hull, UV0, same Joinery_Sage / Joinery_AgedBrass slot names. Filler has Sage only. Reuse installed explicit materials; copied sage is unchanged from JOINERY-02.
- All other JOINERY-02 assets remain untouched. No material retuning or drawer edits.

## Validation

Fresh FBX imports: one UCX and UVs each. Source triangle sweep at every degree from 0 through 100: zero intersections with the original 0775 carcass, the fixed filler and the exact KI-FAUCET-02 sink. Sink placed using measured source offset (-.9125,.0145,0) m relative to the cabinet, from world origins (215,46.05,0) and (306.25,47.5,0). See validation.json and closed/open source previews.

Unreal must still repeat the full installed-neighbour sweep and real open/close clicks, verify access to the shelves and closed gaps, and provide off-hover closed/open evidence. Source checks do not certify engine collision or gameplay.

Build: Blender background, one thread, build_patch.py. Reuses geometry/export helpers from immutable CABINET-JOINERY-02/build_joinery.py and imports existing released source files; it writes only this directory.
