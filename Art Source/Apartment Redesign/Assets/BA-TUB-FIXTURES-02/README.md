# BA-TUB-FIXTURES-02

FIX-007 moves bath plumbing to the west end while leaving the tub and water fill in place; the existing curtain is re-posed to gather at the east end. The old `BA_TubFixtures.fbx` combines plumbing with the full curtain rod; rotating that combined mesh would move the rod incorrectly. This kit separates those groups without modifying the original source kit.

## Files and transforms

- `model/BA_TubFixture02_Plumbing.fbx`: original mixer/backplates, spout, riser and shower head, plus two 25 mm mounting spacers.
- `model/BA_TubFixture02_CurtainRod.fbx`: original rod and both finials.
- `model/BA-TUB-FIXTURES-02.blend`: source plus contextual preview. Use the named exports, not preview duplicates.
- `model/build_split.py`: reproducible builder using the original tub blend.
- `assembly.json` and `validation.json`: exact bounds, pivots, transform and independent FBX checks.

Both exports retain the original tub assembly's floor origin `(0,0,0)`, metres, +Z up, front −Y. The **plumbing** origin is plan `(5.293,8.32,0)`, with source-to-plan mapping `(5.293−sourceY,8.32−sourceX,sourceZ)`; UE yaw −90° after the established import conversion, actor `(529.3,832,0)` cm. The west tile face is X=4.878; source mounting spacers at Y=.415 meet it without putting the riser inside the wall. Plumbing is centred on tub Y=9.07.

The **curtain rod** must use the exact old `Art_BA_Tub_BA_TubFixtures` actor transform. It does not use the new plumbing transform. Replace the old combined fixture only once all three groups (plumbing, rod and drain) are present. Keep the original tub body, Tyler repair overlay and BA-TUB-WATER-01 at their existing transforms. Keep the curtain source and Shower_Curtain identity; re-pose its gathered SLIDE endpoint to the east end so it does not cover the west riser. Validate both endpoints and full travel against the rod, linen doors and tub.

Reuse original `BA_TapLeft.fbx` and `BA_TapRight.fbx`. Their source pivots `(−.84,.29,.96)` and `(−.66,.29,.96)` become plan `(5.003,9.16,.96)` and `(5.003,8.98,.96)`. The valve axis line is world X; preserve the imported action's angular sign and verify motion rather than treating reflection as ordinary vector rotation. Keep all existing tap labels and `Tub_Faucet` behaviour. Re-anchor the fill effect from `(5.113,9.07,.73)` to `(5.113,9.07,.44)`.

## Materials, collision and review

Reuse existing `Aged_chrome` and `Drain_dark` materials; no texture-direction change. No new blocking collision is supplied for decorative plumbing or rod. Preserve the interactive valve collision. The original kit is unchanged.

`previews/west-end-context.png` shows the west-end source arrangement. Independent FBX import confirms source origins/bounds and UVs. Engine acceptance still needs real faucet clicks, water placement, curtain operation, tile/crown clearance and Tyler camera review.

## Drain correction from engine audit

The first split release omitted Drain_rim and Drain_insert. `model/BA_TubFixture02_Drain.fbx` now includes both at their original assembly coordinates, source origin (0,0,0). **Place at the exact original tub/combined-fixture actor transform, not the west-wall plumbing transform.** Bounds are X[-.542,-.458], Y[-.042,.042], Z[.184,.192] m; 128 vertices / 248 triangles, two materials Aged_chrome and Drain_dark, no blocking collision. It remains seated in the existing tub basin; it does not move with the wall spout.

The released Plumbing and CurtainRod FBXs are byte-for-byte unchanged. `model/export_drain.py` produces the additive drain and an editable drain-only blend, then independently reimports it to verify origin, bounds, materials, finite UVs and zero degenerate triangles. `model/drain-validation.json` records PASS with zero bounds error. The full build_split.py invokes that additive builder after its original export/render steps.
