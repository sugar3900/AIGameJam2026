# FIX-027 — KI-FAUCET-02 source handoff

Source rebuild and fresh FBX checks complete, 2026-11-09. Parent source review approved; ready for coordinated integration. No engine files, released KI-LEAK-02/KI-SINK-NARROW-01 assets or git state changed. All headless Blender processes have exited.

## Exact files

Folder: `Art Source/Apartment Redesign/Assets/KI-FAUCET-02/`.

- `models/KI_FAUCET_02_sink_body.fbx` — replacement clean sink body: 5,834 vertices / 5,306 polygons. Exactly the six original faucet components replaced; all 2,364 non-faucet faces preserve coordinates, UVs, smooth flags and material indices.
- `models/KI_FAUCET_02_L_tap.fbx`, `models/KI_FAUCET_02_R_tap.fbx` — new horizontal cross handles, each 1,384 vertices / 1,322 polygons and one named closed UCX convex hull. Each hull has 272 vertices; verify engine collision import/cooking or use the established complex click collision.
- `models/KI_FAUCET_02_assembly.blend`, `build_faucet.py`, `validate_fbx.py` — portable source and reproducible validation.
- `assembly.json`, `README.md`, `validation.json`, `fbx-validation.json` — pivots, fit, direct materials and test evidence.
- `previews/front.png`, `side.png`, `context.png` — reviewed neutral studio views.
- `textures/Sink_SageDirect.png`, `Sink_EnamelPainterly-v3.png`, `sage-A.png`, `sage-B.png` — direct-color export plus original material dependencies. Reuse installed engine sink materials by their unchanged slots.
- `file-manifest.json` — 17 files, paths relative to this asset folder. SHA256 **1d716a73807052062ba3fafe34ae1b3378de3c80df70bbaa38d3e57d88a4d525**.

## Import contract and measured corrections

Keep `Art_KI_SinkNarrow_body` at its current full transform. Source body origin remains `(0,0,0)` and non-faucet geometry is untouched. Bounds remain within the old fit: X ±.525, Y −.340...3105, Z 0..1.340757 m (old maximum1.343217). Bucket, water, leak point, trap, decals and repair animation remain unchanged.

Body slots remain `Sink_SagePaint`, `Sink_AgedEnamel`, `Aged_Chrome`; tap slots are `Aged_Chrome`, `Sink_AgedEnamel`. The original painterly textures remain intact; a direct-image sage bake avoids FBX losing the Blender MixRGB graph.

The audit's upstand face Y.226 differs from actual source mesh front **Y.23450002**. New escutcheon rear Y.2365 embeds2mm, face Y.2255; shank rear Y.240 embeds5.5mm. Suggested rear Y.2345 would have been coplanar. Bridge axis Y.200/Z1.040; visible hardware clears the upstand. The swan-neck riser is straight, with a solid aerator lip and recessed screen, and all new body components are closed with outward normals.

New tap pivots: L `(-.25,.200,1.075)`, R `(.25,.200,1.075)` m, source Z axes. Both have horizontal XY crosses, coaxial spindle/index discs and 13 mm clearance above the upstand throughout 0–90°. FBX reimport preserves these pivots; avoid double-applying assembled translation. The current `Sink_Tap` is **REVEAL**, not ROTATE. Keep its identity and behavior; source pivot availability does not require adding an animation.

## Explicit stream mismatch to resolve in engine

The supplied source outlet is exactly the audit-requested `(0,-.040,1.230)` m, downward. Lip bottom Z1.227. Read-only `rev02_04_furnish.py` sets body `SINK=(215,46.05,0)`, yaw0, so this outlet lands at **UE(215,50.05,123)** cm. `rev02_05_gameplay.py` currently sets `SPOUT=(215,50.05,121)`: a 2 cm center mismatch, or1.7cm gap below the lip.

**Recommended explicit integration correction:** set only the stream start to Z123 and recompute its cylinder from unchanged `BASIN=70`. Keep body transform, Sink_Tap label/toggle and leak system untouched. This source package has not silently changed the stream or shifted the sink. Confirm actual imported body transform and outlet before accepting.

## Evidence and remaining acceptance

Exact preservation SHA256 of the 2,364 surviving face/UV/material signatures: `543b860395000a92f63baf2af9bda2a6ecb0d32c84546353c8e1f20d4ecda516`. Released source blend hash before/after: `f12a9f3ac52575f8cbe53be29552002385523d0c0d7e462e314526dc04391589`.

Fresh FBX imports pass finite UVs, positive-area polygons, expected material slots/direct images, preserved tap origins and bounds within 0.000000116m. All 24 new faucet body shells and both tap assemblies are closed with positive signed volume. The copied body has 20 inherited nonmanifold edges, down from 40 in the old body; no new open faucet edges. Named tap collision hulls are closed with positive volume. Sampled0–90° tap clearance is 13 mm.

In-engine acceptance still requires verifying the explicit stream-start correction, click on/off, unchanged basin landing and leak/repair state, final window clearance and lit material appearance. Source previews do not certify Unreal rendering or collision cooking.
