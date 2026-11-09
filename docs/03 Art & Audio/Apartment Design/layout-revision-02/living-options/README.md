# Living-room furniture options

**Selected: A, by the user.** These studies preserve the latest room boundaries and the user's closet, wainscoting, hallway furniture and entry fusebox decisions. Option A is now applied to `../proposed-plan.json` and the full-floor-plan SVG/HTML, including replacement walking routes. Elevations and engine maps have not changed. B and C are retained as alternatives considered.

Open [the interactive comparison](review.html). Separate drawings: [A](option-a.svg), [B](option-b.svg), [C](option-c.svg). [Coordinates and facing directions](options.json) include the base-plan content hash to identify the exact proposal used.

## Diagnosis

The previous proposal spreads the small vintage television and sofa across much of the room. The sofa and coffee table use different long-axis orientations, the chair sits apart, and the room lacks a clear seating boundary beside its open hall. These alternatives bring the sofa and table together, give the chair a deliberate role and retain walking routes outside the furniture group.

The former proposal also used approximate dimensions for several objects. These studies use the source README dimensions for sofa, armchair, TV cabinet, bookcase, coffee table and end table. They retain the existing 2.50 × 1.80 m rug, rotating it as needed. Lamp sits on the side table; the rug is not blocking geometry. Radiator and plant remain planning footprints.

## Alternatives

### A — Floating sofa, east-wall TV

Sofa faces east toward a TV on the east wall, north of the entry bench. The armchair faces south from the north end of the rug. Bookcase remains on the kitchen partition; circulation to the kitchen passes west of the sofa.

This makes one compact group with the TV away from the window. Its tradeoff is a stronger division between kitchen circulation and lounge, made by the visible sofa back. Seat-to-screen distance is approximately 2.90 m; sofa-to-table gap is 0.46 m. The TV clears the bench by 0.15 m in plan, before any later trim/hardware review.

### B — Sofa defines the room — earlier recommendation, not selected

Sofa faces north, with its low back along the southern edge of the seating group. The TV is on the north wall east of the window. Chair faces east from the west side of the rug; the kitchen opens onto the side of the group. The entry route stays behind the sofa, and a second route passes to the east to reach the TV/window side.

This most clearly uses the enlarged living/entry space. It creates an edge without rebuilding a wall and gives views toward seating, window, bookcase, kitchen and entry repair. It also leaves a 1.28 m nominal passage between the sofa back and hall-console front. The sofa back must look good from the entrance, and the TV needs a lighting/glare check because it is beside the window. Seat-to-screen distance is approximately 3.01 m; sofa-to-table gap is 0.45 m.

### C — TV snug and reading corner

TV remains on the kitchen partition, but the sofa moves closer and faces west. The chair, lamp and bookcase form a separate northeast reading corner near the window. Main entry circulation remains in the open east/south portions of the room.

This provides two distinct activities and a more collected apartment feeling. It is weaker for a single large conversation group because the armchair is intentionally separate. Seat-to-screen distance is approximately 2.86 m; sofa-to-table gap is 0.45 m.

## Checks and limits

- Generation checks closed furniture footprints for overlap and tests that movable furniture stays inside the nominal room faces. All three pass.
- Samples along the drawn walking routes maintain at least 0.50 m from the represented floor-furniture rectangles, including the fixed hall console and entry bench. This is a planning check, not an Unreal capsule/camera or animation test. Door and cabinet sweeps, handles, curtains and collision hulls still need validation.
- The approximately 0.45 m coffee-table gaps are for seated access, **not** the primary walking routes. Those routes go around the groups.
- TV viewing distances are from a nominal seated point to the screen plane, not a prescribed viewing standard.
- Options keep the entry repair approach clear. The sofa, TV, chair and bookcase have explicit north/east/south/west facing in JSON. The integration team's corrected source −Y → imported +Y sofa conversion must be used to calculate the selected option's engine rotation; do not copy the old yaw −90° without checking the intended world direction.
- Door/frame wall-cut allowances from the integration team are recorded in the asset READMEs and integration handoff. They do not authorize widening or rebuilding openings during this comparison.

Option A has been reconciled with the full apartment floor plan and its circulation. The user subsequently authorized revised elevations; those are saved alongside the full floor plan. A newer compact-kitchen/dining study is separate. No new furniture, texture generation, Blender export, commit, push or editor operation was performed for these options.
