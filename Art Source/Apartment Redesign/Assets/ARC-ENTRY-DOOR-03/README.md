# ARC-ENTRY-DOOR-03 — seated entry hardware and matching strikes

Source fix for **FIX-010**. Keeps the fitted02 door’s frame envelope, clear/rough opening, hinge axis, leaf slab, collision and existing exit-action placement. Original01/02 exports remain unchanged.

## Audit and corrections

The defect was authored in source. The old knob and deadbolt center X0.382 m crosses a panel molding spanning X0.367–0.383 m. Panel beads hovered7.5 mm from the slab; knob and deadbolt plates hovered3.5–4 mm. No matching latch/deadbolt strike hardware had been authored. The apparent strike on the opposite jamb was hinge hardware.

Rev02 placement is correct: frame `(1200,452.5,0)` cm/yaw90, leaf `(1196.5,403,0)` cm/yaw90, positive unit scale. The original source hinge offset `(-0.495,-0.035,0)` m becomes `(-3.5,-49.5,0)` cm after the established Y flip and yaw90. This exactly explains those actor transforms; mirroring the leaf would introduce a new defect. See `source-audit.json`.

The new knob and deadbolt center is X**0.435 m**, with **53 mm backset** from the latch edge. Their full maximum50 mm footprint fits the105 mm latch stile, leaving **27 mm clear of the panel molding and28 mm to the leaf edge**. Interior thumbturn and exterior key cylinder are distinct. Escutcheons sit directly against the slab, stems connect into them, and the peephole is seated too.

Panel moldings are seated against the slab and use closed continuous mitered rings, removing the old overlapping/gapped bead corners. Their outer panel rectangles remain the same. Vertical casing ends now meet the head casing instead of stopping12.5 mm short. This changes only the cosmetic casing joint; the opening, outer frame bounds and UCX are unchanged.

Real edge recesses contain latch/deadbolt faceplates and flush retracted tongues. Matching jamb strike plates, countersunk screws and actual pockets share the same Y0 centerline and Z1.025/Z1.20 m heights. Default bolts remain **flush/retracted**, preserving the previous sweep and static exit behavior. Throw dimensions in the manifest are construction proof, not new lock interactions.

| Feature | Latch | Deadbolt |
| --- | --- | --- |
| Height | 1.025 m | 1.200 m |
| Leaf edge / strike plane X | .488 / .495 m | .488 / .495 m |
| Closed edge gap | 7 mm | 7 mm |
| Strike opening Y × Z | 19 ×22 mm | 22 ×26 mm |
| Optional throw from flush | 12 mm | 25 mm |
| Resulting jamb engagement | 5 mm | 18 mm |
| Current Rev02 strike world cm | `(1200,502,102.5)` | `(1200,502,120)` |

Both throws stop inside the25 mm deep strike pockets. Geometry ships in the retracted state; no new actuator or lock state is introduced.

## Exact replacement contract

- `model/ARC_Entry_Door03_Frame.fbx` replaces `ARC_Entry_Door02_Frame` on **Door_Entry_Frame**. Origin: opening-center floor. Three separate UCX jamb/header members, identical to02; no collision spans the opening.
- `model/ARC_Entry_Door03_Leaf.fbx` replaces `ARC_Entry_Door02_Leaf` on **Door_Entry_Leaf**. Origin: original barrel axis. Closed source offset from frame `(-0.495,-0.035,0)` m. Same slab UCX and same visible outer bounds as02.
- Keep **FrontDoor** and its existing “Leave the apartment” behavior, click target and actor transform unchanged. The static source variants do not add a lock action.

Source metres, Z up, front/interior−Y. FBX uses the existing default export axes−Z forward/Y up. Keep the existing import conversion and positive scale. Do not center the leaf on import. Clear opening remains0.99 ×2.11 m, rough opening1.05 ×2.14 m, leaf slab0.976 ×0.05 ×2.094 m, original hinge pose and nominal7 mm side gaps. Source open preview is−80° about the existing hinge. Engine handling remains authoritative for gameplay.

## Material slots

Existing slots are retained so current material overrides stay valid:

| Part | Slots in order |
| --- | --- |
| Frame | 0 Painted warm ivory;1 Muted aged brass;**2 Recess darkness (new)** |
| Leaf | 0 Aged walnut entrance leaf;1 Muted aged brass;2 Edge rub, warm timber;**3 Recess darkness (new)** |

Reuse the existing engine walnut, door-paint, brass and edge-wood materials. The new recess material is opaque, linear base `(0.025,0.018,0.012)`, roughness0.95, metallic0. The source reuses unchanged `walnut-aged.png` and `paint-selected.png` maps. Walnut is direct sRGB base color, roughness0.82; paint retains the original mix of65% map/35% warm ivory `(0.85,0.79,0.68)` and roughness0.78. Brass is linear `(0.31,0.205,0.075)`, metallic0.68, roughness0.46. Edge wood is linear `(0.43,0.29,0.16)`, roughness0.9. `assembly.json` records the exact slot contract and geometry.

## Review and reproduction

`model/build_entry.py` is the reproducible headless Blender builder; `model/validate_fbx.py` reimports both FBXs, checks UVs/origins/material order/UCX, compares outer bounds directly with fitted02 and verifies lock alignment and stile clearance. The old source hash is checked unchanged. Use `Blender -b -t 2 --python-exit-code 1 --python <script>`.

Previews: `closed-interior.png`, `closed-exterior.png`, `hardware-mounted-detail.png`, `leaf-edge-detail.png`, `jamb-strike-detail.png`, `open-hinge-check.png`. Detail views hide the opposite component only to show the actual edge fittings; exported closed transforms remain exact. The packed blend contains only preview lights/camera beyond the two exported parts and UCX.

Source validation does not replace engine closed-pose alignment, collision, material and FrontDoor click review. Import through legacy FBX to preserve UCX.
