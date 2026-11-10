# HA-RUNNER-02 — fitted fringed hallway runner

FIX-020 replacement for HA-RUNNER-01. Source approved; in-engine placement and grazing-angle review remain pending.

The 5.00 × 0.80 m textile body has a thin linen backing, small woven binding and uneven 48–68 mm flax fringe at both short ends. Its 5.132 m overall length includes the fringe. Existing painterly floral artwork is sampled at its original physical scale with a centered crop; motifs are not stretched. This is a nearly flat textile, not a rigid raised slab.

## Export and placement

- Import `model/HA_RUNNER_02.fbx`: one mesh, 19,166 vertices / 35,784 triangles. Source scene `model/HA-RUNNER-02.blend` contains the export mesh only.
- Metres, Z up, floor-centered origin, long axis X, FBX forward −Y. Unreal conversion keeps X and flips Y.
- Place at **(523.4, 470.0, 0.118546) cm**, yaw 0°, scale 1.
- Expected world bounds: X266.802..780.013, Y429.790..510.210, Z0.200..0.871 cm.
- The west fringe stops **14.05 cm** before the documented cabinet front at X252.75 cm. The east end retains the previous runner endpoint at about X780 cm.
- Placement is derived from the original dressing pipeline's 6 m runner centered at (480,470), unchanged by Rev02. Verify actual cabinet feet, source-import units and both end clearances in the editor before accepting.
- Keep the existing actor identity `Art_HA_Runner_HA_RUNNER_01` when swapping the mesh, or explicitly map its successor in reconciliation.
- **No collision.** The floor supplies walking collision. Do not apply the blanket complex-as-simple collision pass to this decorative textile.

## Materials

Four slots, exact names/order and linear constants in `assembly.json`:

1. `Runner02_Painterly`: sRGB `textures/runner-albedo.png` directly into Base Color, not multiplied by a dark constant.
2. `Runner02_LinenBacking`: linear RGB (.29,.23,.16).
3. `Runner02_FadedRoseBinding`: linear RGB (.27,.14,.105).
4. `Runner02_FlaxFringe`: linear RGB (.55,.46,.31).

All opaque, metallic 0, roughness .96. Preserve the UVs and mesh normals. No emissive or alpha-card fringe.

## Validation and reproduction

`model/validation.json` records a fresh FBX reimport: finite positions/UVs, nonzero triangle areas, matching bounds/material slots, planned floor and cabinet clearance. Preview images show the source under neutral studio lighting, not Unreal.

Run Blender headlessly with `-b -t 2 --python-exit-code 1 --python model/build_runner.py`, then `model/validate_runner.py`. Logs should stay outside the repository. Do not run two builds on this asset simultaneously.

Engine acceptance: retain a visible floor gap to the cabinet including fringe, confirm no floor z-fighting, inspect woven edge from walking height and low angle, and walk the hall route. No interaction identities change.
