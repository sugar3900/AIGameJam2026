# KI-FAUCET-02 — FIX-027 vintage bridge faucet

Additive source replacement for the faucet in the clean KI-LEAK-02 sink. This package does not modify either released source kit. It replaces the six old faucet islands in a copy of the clean body and supplies two new rotating tap meshes. The original basin, upstand, legs, supports and P-trap remain unchanged, including their exact floating-point vertices, face order, smooth flags, material indices and per-loop UVs. `validation.json` records the preserved 2,364-face signature. Materials retain the original slot names/order.

## Exact import set

| File | Integration |
| --- | --- |
| `models/KI_FAUCET_02_sink_body.fbx` | Replace KI_LEAK_02_sink_body mesh on its existing actor, keeping its complete transform and current sink materials. |
| `models/KI_FAUCET_02_L_tap.fbx` | Replace the left tap mesh and update its pivot/axis contract below. One named UCX hull. |
| `models/KI_FAUCET_02_R_tap.fbx` | Replace the right tap mesh and update its pivot/axis contract below. One named UCX hull. |

Retain Sink_Tap identity, stream/toggle behavior and all authored leak actors. The bucket, still water, drip, puddle mask/materials and repair behavior are outside this replacement. No source mesh in this kit includes a bucket. The clean body retains its existing static collision policy; the taps include simple convex collision and can also use the integration team's established complex click collision.

## Geometry and datums

Source units are metres; front is −Y, Z up, body origin `(0,0,0)`. Standard project conversion is X unchanged, Y negated, metres multiplied by 100. Do not center mesh bounds. Body bounds are X `−.525..+.525`, Y `−.340...3105`, Z `0..1.340757`; the rebuilt faucet stays below the original 1.343217 m maximum. All room-fit geometry is preserved.

- Left tap pivot `(-.25,.200,1.075)`; right `(.25,.200,1.075)`. Both rotate around source **Z**. The cross arms lie horizontally in XY; the stem, bezel and ivory index are coaxial. Source closed pose is 0°, nominal travel 90°. The old tap pivot had Y .210 and a cross in the wrong plane; do not copy its old axis unexamined. Engine action/reveal semantics remain unchanged.
- Bridge axis Y .200, Z 1.040, joining valves at X ±.250. Shanks connect the valve bodies to the wall; their rear Y .240 embeds 5.5 mm into the measured upstand face.
- **Measured source front of upstand is Y .23450002**, not .226. Escutcheon backs therefore use Y .2365 for 2 mm embed; front is .2255. The suggested rear .2345 would have been coplanar. No upstand geometry moved. Visible bridge rear is 14.5 mm ahead of the face; valve rear is 7.5 mm ahead.
- The swan neck rises straight before its smooth forward bend. Outlet center is `(0,-.040,1.230)`, pointing down `(0,0,-1)`. The thick annular aerator lip reaches Z 1.227 with a recessed screen at 1.230. It is not a zero-thickness open ring.
- Rotating crosses have 13 mm minimum vertical clearance above the upstand in their 0–90° sweep. Shank/valve, bridge/valve and stem/bonnet junctions overlap more than 3 mm. The center union embeds the riser and bridge; no floating hardware.

**Explicit stream mismatch:** read-only inspection of `rev02_04_furnish.py` confirms `SINK=(215,46.05,0)` and yaw 0. The requested source outlet therefore maps to **UE `(215,50.05,123)` cm**, while `rev02_05_gameplay.py` currently starts the stream at `(215,50.05,121)`. This is a 2 cm center mismatch (1.7 cm from the aerator lip). Engine owner should explicitly update only the stream start to Z123 and regenerate its cylinder with the unchanged basin landing Z70, leaving the body, label and toggle behavior untouched. No stream or engine file was changed by this kit. Current `Sink_Tap` is a **REVEAL** action; it does not rotate a valve. Preserve that behavior; the separate source-Z tap pivots are supplied for correct geometry/possible future rotation, not a request to change gameplay.

## Materials

Body slot order is unchanged: `Sink_SagePaint`, `Sink_AgedEnamel`, `Aged_Chrome`. Reuse the installed body materials. Tap slots are `Aged_Chrome`, `Sink_AgedEnamel` (ivory index).

The portable source uses direct base-color image links supported by FBX. `Sink_SageDirect.png` is the original sage-B/sage-A MixRGB blend baked pixel-for-pixel, retaining original UVs. The existing enamel image is copied unchanged. Both are sRGB color textures. No new water, bucket, mask or engine material is supplied. Chrome preserves the existing aged metal values (metallic .75, roughness .32); it is intended to inherit the room's light rather than emit.

## Reproduce and verify

Run one headless process at a time on this Mac:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 1 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/KI-FAUCET-02/build_faucet.py'
/Applications/Blender.app/Contents/MacOS/Blender -b -t 1 --python-exit-code 1 --python 'Art Source/Apartment Redesign/Assets/KI-FAUCET-02/validate_fbx.py'
```

The builder loads KI-LEAK-02 read-only and verifies its SHA256 before/after. It identifies the six old faucet islands by connected geometry, removes only those, and asserts exact preservation of every surviving polygon signature after joining the new hardware. Fresh FBX reimports verify dimensions, UVs, slots, direct images, and named closed positive-volume UCX hulls. The separate tap sweep check samples every degree through 90° against the upstand.

`previews/front.png`, `side.png` and `context.png` are small neutral studio renders. They are source review evidence; the final warm in-game material appearance, click target and stream must be checked in the environment editor. No editor or engine files were changed here.
