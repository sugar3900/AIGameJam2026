# Screenshot batch 2 engine acceptance

All 30 visual findings have accepted targeted evidence in `accepted-views`, linked from `../../completion-batch2.json`. The mirrors intentionally retain indistinct room shapes and light. Early `b2_*` captures establish their named corrections only; unrelated later revisions are shown in the final `fin*` captures. Deliberately hidden exterior cards in the fill-specular A/B are isolation tests, not final window appearance. The manifest records the archived PNG hashes.

The engine owner reports the Mac Development Editor build succeeded after the frame-only outline correction, and every Rev02 material recompiled with zero final compile failures. Python syntax and git whitespace checks pass. Source review, fresh FBX import validation and subsequent installed corrections are described in `Source review.md` and the individual kit READMEs.

## Gameplay checks

- Room controls: PASS, six room switches, closet circuit and eight wall-switch traces.
- Real click open/close in Playing: 11 hinged doors (four base fronts, oven, fridge, pantry pair, cupboard pair and fuse door), with aim adjusted to the swung leaf. Four drawers toggle both ways. Burner, kitchen/bath taps, curtain, coat/office sliders and linked wardrobe pair toggle. Bed reaches the end-day prompt.
- Linen pair: targeted follow-up PASS in fresh Playing-state PIE. Both closed faces and swung leaves were trace-confirmed before real open/close clicks. The lower-door pass used a level camera aim at about 50 cm; steep standing-height rays from the chosen close approach caught the upper door. Upper-door clicks used standing height and a clear panel point. Setup set_on(False) is not counted as a click; see linen_clicks.txt. Full-travel sweeps and auto-close also pass.
- Ten cabinet/sink/upper/pantry/linen doors pass 21 full-travel sampled neighbour poses. Oven-to-body contacts near the closed pose and curtain-ring/rod contacts are identical to their predecessor meshes and represent authored seating. The moving curtain never contacts the fixed return.
- Day flow: tagged WindowSun lights (BR/BA/OF) are about 14,000 at day start, exactly zero at dusk, restored after valid Week 2 sleep and after title/Continue. Tests met all four hunks and each encounter returned to Playing.
- Repair persistence: after marking Lukey fixed, RefreshRepairState at morning/load hides both stain and film. The film is Movable and attached to Malady_Sink; the script asserts the parent. The final successful segment is labelled `rerun after film attach fix` in day_repair_load.txt; the earlier failed segment is excluded.
- Character reveal: PASS, 51 sampled frames including 13 partially dissolved; portrait materials stay independent. Conversation framing: PASS (Tyler crown 7.3%, face 20.7% from top).
- Auto-close: generic sequential validator passes 24/25 before OfficeCabinet_Door_L. Its fixed +Y retreat point lies inside the unchanged daybed footprint. The office-cabinet group passes 3/3 in isolation and manually; the generic full-run result is not represented as green.
- The older environment validator aborts at obsolete `Wardrobe_Door` (the wardrobe was previously split into a linked pair); this predates this batch. The linked pair is covered by actual clicks. Tick validators require the persistent namespace runner `Tools/run_in_editor.py`; failed runs under the other runner do not count.

Raw logs preserve failed harness/aim attempts as well as successful reruns. In clicks_final.txt, only the fresh Playing-state open/close pass and valid retries count. State 2/3 encounter interruptions, State 6 end-day prompt attempts and initial wrong-facing linen aims are excluded. These checks include state-driven repair application and debug-assisted encounter progression; they are not four complete repair-minigame playthroughs.

## Reconciliation and release

The generated Rev02 engine reconciliation reports 103 instances, zero problems and zero unaccounted actors. It records fitted backsplash bands/infills, paired pans, individual hangers, fixed curtain return, book runs, and the approved bench/switch moves. Dining-table grain remains lengthwise. The wall table and stool use their own walnut image throughout; their original front-to-back painterly tabletop strokes are retained as authored.

The linen follow-up is closed. Source files, scripts and saved maps are settled; the engine editor is saved and closed. All 30 requested visual issues are accepted, with the test scopes and harness limitations above explicitly retained. This acceptance permits the user-authorized commit and merge.
