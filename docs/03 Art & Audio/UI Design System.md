---
tags: [art, ui, decision]
status: approved
date: 2026-11-11
---
# UI Design System

This is the wiki record of the selected UI direction and subsequent decisions. **Foundation decisions approved; selected world reticles implemented. The reusable UI implementation is now available for design review.** Exact tokens below come from the current design kit; dimensions remain starting values for in-engine testing.

## Direction and authority

Use original concept **#7, “Fixer-upper reality show”**: bold renovation-TV graphics supporting a comedic dating sim. Later refinements below supersede differences in generated mockups. Do not let each screen reinvent its logo, buttons, borders or typography.

The original #2 DIY direction and later hybrids were explored; #7 was selected. The initial scrapbook/editorial showcase was rejected. The 18-screen set explores coverage, not finalized screen layouts.

- [Selected reference](../../Art%20Source/UI%20Concepts/Exploration%2001/07-fixer-upper-reality-show.png)
- [Current machine-readable specification](../../Art%20Source/UI%20Concepts/Selected%2007/design-system.proposal.json)
- [Foundation kit](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/)
- [Exploratory screen set](../../Art%20Source/UI%20Concepts/Selected%2007/Screen%20Set%2001/)

Historical revision files and early foundation sheets may show superseded 7° geometry or filled idle reticles. Use this record, the current specification and selected assets below.

## Colors

The teal was shifted cooler and made lighter; friendship shares its approximately 190° hue. These are normalized sRGB tokens, not sampled raster-gradient colors.

| Token | Hex | Use |
|---|---|---|
| Teal | `#1F7384` | Headers, backing surfaces, floor plan |
| Ink | `#11414A` | Body text, outlines for contrast, offset shadows |
| Cream | `#FFF5E5` | Reading surfaces and secondary controls |
| Orange | `#FF7900` | Borders, tools, structural accents, friction |
| Pink | `#D9005C` | Primary actions, romance, focused replies |
| White | `#FFFFFF` | Text on teal/pink, separation keylines |
| Friendship | `#76CADB` | Friendship meter and cool accent |
| Disabled surface | `#E1E1DE` | Disabled controls |
| Disabled ink | `#565C60` | Disabled labels and icons |

Use subtle vertical gradients, lighter top to darker bottom:

| Surface | Top | Bottom |
|---|---|---|
| Teal buttons, labels and header plates | `#287F91` | `#1A697A` |
| Pink buttons and labels | `#E80C70` | `#C90055` |

Keep cream reading surfaces, disabled controls and reticles flat. Avoid glossy streaks, bevels and per-screen gradient variations. Avoid small white text on orange. Convert sRGB hex values correctly when supplying Unreal linear colors.

## Typography

| Role | Font | Treatment |
|---|---|---|
| Headings and short display labels | Barlow Condensed ExtraBold Italic, 800 | Effective 12° right lean |
| Dialogue, replies and helper text | Barlow Regular, 400 | Upright |
| Body emphasis and stronger labels | Barlow Semibold, 600 | Upright |

Barlow Condensed's native italic lean is 7°. The selected 12° treatment requires an additional synthetic shear on display glyphs, not a different native font variant. Added shear tangent: `tan(12°) - tan(7°) = 0.0897720008`. Text baselines stay horizontal. Do not skew body text or icons.

Use the [bundled font files and SIL OFL 1.1 license](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Fonts/). Final sizes, wrapping and UI scale need testing in Unreal. Do not shrink text or shorten authored dialogue to fit a layout.

## Shapes, buttons and panels

The selected treatment restores **rounded corners, thicker asymmetric borders and subtle pink/teal gradients** from the original mockup.

- Every element that uses a slant uses the same **12° right lean**: button silhouettes, panels, tabs, header plates, badges, outlines, focus contours and shadows.
- The **placement grid also uses 12°**. Control origins, text-block anchors and icon anchors align along shared angled columns; rows and text baselines remain horizontal.
- Rounded cream panel bodies pair with teal headers, orange borders heavier on the lower/right sides, and short ink offset shadows.
- Use common silhouettes and contour layers across button states and popup variants. Reuse one modal shell with width variants and content-driven height.
- Primary actions use pink; secondary surfaces use cream. Focus needs a pointer or keyline as well as color. Do not add hearts to focused replies or imply relationship outcomes.
- Body text and icons remain upright. Do not rotate a whole popup or shear a brand master.
- Remove construction stripes. Remove the three-ray flourish from the base kit; bringing it back selectively for surprises is deferred.

Placement formula: `x = originX + u - v * tan(12°); y = originY + v`. A slanted edge of height `h` has horizontal inset `h * tan(12°)`.

[Selected placement-grid source](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/selected-placement-grid-guides.svg) and [rounded-surface/slant comparison](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/rounded-surface-slant-study.png).

### Provisional construction measurements

These are kit starting values at 1920×1080, **not independently finalized engine measurements**: 8-unit spacing grid (8/16/24/32/48); small-control corner radius 12, large-panel radius 22; top/left border 3; lower/right extrusion offset (4, 7); ink shadow offset (9, 12).

Complete state designs, hit targets, responsive layout and contrast still need validation.

## Icons

Use **Phosphor Bold** consistently, with upright geometry and aligned optical sizes. Do not mix arbitrary weights or shear icons to match panel edges.

The [local SVG library and MIT license](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Icons/Phosphor/) includes heart, users, lightning, wrench, house, door-open, gear, play, check, info, eye, chat-circle-text, hand-pointing, moon, x-circle and cursor.

Relationship mapping: heart/pink for romance, users/cool teal for friendship, lightning/orange for friction. Keep labels so meaning does not depend on color alone.

## Reticles — finalized selection and behavior

Selected family: **C contextual icons + A dot-and-ring default**, with matching rim and line weights across states. Since 2026-11-12 the idle ring sits at 75% radius and expands into the full ring when there is an actionable target. The game rasterizes animation layers from the individual selected SVGs into UI textures, with semantic contextual actions, transparent idle and short transitions. The world reticle is hidden outside exploration.

| State | Appearance | Use |
|---|---|---|
| Default / idle | White dot and ring at 75% radius (same line weights) with thin ink contrast outlines; transparent interior | Exploration without an actionable target |
| Inspect | Contextual inspect icon, white rim/icon, full-size ring, ink fill (currently 50% opacity, under review) | An inspect action is available |
| Talk | Contextual conversation icon, same circle and fill | A conversation is available |
| Use / open | Contextual use icon, same circle and fill | An object can be used or opened |
| End day | Contextual end-day icon, same circle and fill | A target opens the end-day flow |
| Unavailable (reserved) | White X with thin ink outline like the default dot; matching ring/radius, transparent interior | No current runtime use |
| Hidden | No world reticle | Outside exploration; UI cursor is separate |

**Fill the circle only when there is something actionable.** Idle and unavailable interiors remain transparent. The unavailable X has a white center and dark outline matching the dot's contrast treatment.

### Unavailable is reserved

No current gameplay case needs this state. Invalid or out-of-range targets are filtered before reaching the HUD and fall back to idle. Do not show unavailable for empty space, ordinary scenery, out-of-range targets or brief character-transition locks.

Beds and doors remain actionable when they open a confirmation dialog; any restriction belongs inside that dialog. Only introduce unavailable for a recognizable target with a deliberately blocked action and a clear reason the UI can explain. Do not add a new blocking mechanic just to use the artwork.

### Assets and implementation handoff

Use the individual [reticle SVGs](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/) as the source:

- [Default](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/default.svg)
- [Inspect](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/inspect.svg)
- [Talk](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/talk.svg)
- [Use/open](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/use.svg)
- [End day](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/end-day.svg)
- [Reserved unavailable](../../Art%20Source/UI%20Concepts/Selected%2007/Foundation%2002/Reticles/unavailable.svg)

Kit scale reference at 1080p: 32 px box, 14 px nominal circle radius, 1 px white rim, 2.5 px default dot radius, 19 px contextual icon box. SVGs use a 64-unit viewBox with radius 28; thin ink outlines extend beyond the white geometry. Test optical size and contrast against both light and dark rooms rather than treating these reference values as locked engine sizes. The runtime now uses larger sizes by decision; see the runtime implementation below.

Implementation must expose explicit semantic action metadata for inspect/talk/use/end-day; **do not classify actions by parsing localized prompt text**. Preserve target range/validity rules, interaction prompts and existing input behavior, including radio playback. Keep the arrow UI cursor and hand for clickable dialogue topics separate from the world reticle.

Verify target changes, return to transparent idle, menu/dialogue visibility, scaling, and every real actionable target category. Keep unavailable unused until a supported gameplay case exists.

### Runtime implementation (2026-11-11, updated 2026-11-12)

- `EFixHimInteractionAction` / `GetInteractionAction()` expose explicit metadata, independent of localized prompts. Ordinary interactables use **Use**; unmet maladies use **Inspect**, met maladies use **Talk**; beds and the apartment exit use **EndDay**, including when they open a confirmation.
- `UFixHimHUDWidget` stacks the reticle layers in one centered box: the ink **background** disc (actionable targets only); the **ring**, either the full ring (`T_Reticle_Ring`) or the smaller idle ring (`T_Reticle_RingIdle`), both with the same ink outline and white rim; and the **center** (idle dot, or the inspect/talk/use/end-day icon). The eight layer textures (`T_Reticle_Background`, `_Ring`, `_RingIdle`, `_Dot`, `_Icon_Inspect`, `_Icon_Talk`, `_Icon_Use`, `_Icon_EndDay`) live in `/Game/ICanFixHim/UI/Reticles`, are configured through `UFixHimSettings` / `DefaultGame.ini` and are explicitly included in cooking. Idle stays transparent; there is no unavailable runtime enum, texture or behavior.
- Size (2026-11-12): the runtime box defaults to **64 UMG units** (`ReticleSize`), double the 32 px kit reference, chosen for legibility of the thin rim; UMG DPI scaling keeps it the same share of the screen at every resolution (64 px at 1080p, ~85 px at 1440p, 128 px at 4K). Layers are rasterized at 2× their box (128×128; 96×96 for the 48-unit idle ring), so 4K draws 1:1 and 1080p/1440p minify at most 2×, where plain bilinear sampling is exact: the textures use **no mips** and bilinear filtering, since mips only blended in a blurrier half-size level at these sizes (the earlier 32-unit box minified 128 px sources 4:1 without mips, which caused the "crunchy" aliasing). Below ~1080p tall, e.g. small PIE windows, minification exceeds 2× and edges may alias slightly. The prompt sits `ReticleSize / 2 + 20` units below centre.
- Idle ring and fill (2026-11-12, under review): the idle ring is its own 96 px texture (`T_Reticle_RingIdle`), drawn in a 48-unit box (`ReticleIdleRingScale` 0.75 of `ReticleSize`) with radius 21 and the **same** 4-unit ink outline and 2-unit white rim as the full ring, so idle line weights match and it minifies at most 2× like the other layers. On acquiring a target both rings scale so their radii always match (idle 1→1.33×, full 0.75→1×); the full ring sits underneath at full opacity and only the idle ring on top fades, so the swap never dims. The ink background is drawn at 50% opacity (`ReticleBackgroundOpacity`); on bright surfaces this gives white icons less contrast.
- Transitions (`ReticleTransitionSeconds`, default 0.14 s, 0 snaps): the ink background fades in while growing from 50% scale for actionable targets, the ring expanding with it, and both reverse for idle; the center cross-fades, the new dot/icon popping in from 60% scale while the old one shrinks out. Interrupted transitions continue from their current state. Hiding or reappearing (outside exploration) shows the settled state without animating.
- The controller passes the already filtered target's action to the HUD each hover update. Existing trace/range rules, prompt text, confirmation flows, radio input priority, arrow cursor and clickable-topic hand remain unchanged. The icon is centered independently of the prompt and hidden with the prompt outside Playing.
- Rebuild assets on macOS with `python3 Tools/Art/Reticles/render_reticles.py`, which splits the approved SVGs into layer SVGs by copying elements (asserting the ring is identical across states) and rasterizes them; then run `Tools/Editor/import_reticles.py` in Unreal (editor or Python commandlet). The source remains the individual SVG directory above; the scripts touch only the eight runtime layers (re-importing re-saves unchanged layers too; restore pure churn from git). Background + ring + icon composites back to each original contextual SVG raster within 1/255, and ring + dot matches the default exactly.
- Validation: Development Editor build; `FixHim.UI.Reticles` engine automation (passes with and without `-nullrhi`) covers ordinary props, beds, exit, inspect/talk progress changes, layer texture loading and import settings (2× source size per box, no mips, bilinear, UI group, sRGB), center/background per action, background opacity, the idle/full ring swap (shared radius mid-transition, settled visibility and scale), cross-fade start/mid/settled states, interrupted transitions, prompt retention/visibility, instant hide/reappear, the configured box sizes and prompt offset.
- In-game review (2026-11-12, standalone game at 1920×1080): screenshots of idle, use, inspect, talk and end-day in light and dark rooms, plus transitions slowed to 2 s with `-ini:Game:[/Script/ICanFixHim.FixHimSettings]:ReticleTransitionSeconds=2.0`. Edges are clean with no aliasing, including the idle rim on pale walls, and the ring swap shows no double ring. At 50% the ink fill reduces white-icon contrast on bright surfaces (bed quilt, pink tile). Still pending: feel of the 0.14 s transitions in motion, 1440p/4K checks (the test display cannot fit a 1440p window, and macOS game mode renders Retina at half resolution), a final fill opacity, and a packaged-build smoke test.

## Dialogue and reusable component scope

The dialogue audit found lines up to 355 characters, spoken lines up to 240 characters, replies up to 92 characters and exchanges with four choices. The runtime shows one line at a time, then choices beneath the final line.

Use the [authored stress cases](../../Art%20Source/UI%20Concepts/Exploration%2002/dialogue-stress-cases.json) for layout checks. Keep full authored text, vertically stacked replies that grow with wrapping, an expandable reading area and visible character faces. Do not use shortened generation samples as capacity evidence.

The kit specification also proposes reusable dialogue assemblies, relationship meters, HUD labels, name fields, sliders, checkboxes, floor-plan status cells and modal variants. Their detailed layouts and interactions still need implementation review; the generated screens do not finalize every component. Earlier suggestions such as collapsed relationship meters are not approved decisions.

## Logo

Use one reusable master rather than regenerating the mark for each screen. The current [transparent concept PNG, v4](../../Art%20Source/UI%20Concepts/Selected%2007/Logo/logo-isolated-v4.png), incorporates these requested changes:

- Remove the extra heart-and-wrench emblem above the roof.
- Retain the orange roof, distressed orange FIX plaque, white FIX lettering and heart beside HIM.
- “I Can” uses the shared vertical teal gradient.
- “HIM” uses the shared vertical pink gradient.

The image still has alpha-edge speckling; cleanup and an editable production master remain pending. Do not treat it as production-ready. Exact edit prompts are preserved in the [logo manifests](../../Art%20Source/UI%20Concepts/Selected%2007/Logo/). A compact brand mark remains a proposed deliverable.

## Reusable UI implementation (2026-11-12)

The shared Unreal components and first screen migration are implemented on `feature/reusable-ui-design-system`. See [[UI Component Library]] for APIs, source files, asset rebuilding, validation and the review captures. The selected palette, licensed fonts/icons and 12° placement grid are reused across screens; new component proportions and screen compositions still await design feedback.

The implementation includes resizable rounded surfaces and asymmetric borders, shared action/reply/topic controls, visible focus/pressed/disabled states, bounded reading areas, sliders/checkboxes, text-size and reduced-motion settings, and an in-engine component workshop (`FixHim.DesignSystem`). Short action labels use the selected display treatment; authored dialogue/replies remain upright. Continue is the primary title action when a save exists. Small status labels use flat or sufficiently dark surfaces; pale relationship colors remain accents beside readable labels.

## Remaining work and provenance

The selected world reticles and first reusable UI implementation are integrated. Component proportions, screen compositions and motion feel are ready to be reviewed after the recorded checks in [[UI Component Library]]. Production logo cleanup and an editable brand master remain pending; the current isolated logo is explicitly a concept asset. A packaged-build smoke test remains a release check. Reticles were reviewed from in-game screenshots at 1080p on 2026-11-12 (layers, 64-unit size, idle ring and transitions; see above). The fill opacity, transition feel in motion and higher resolutions still need review; family selection is settled.

Decision sequence: original #7 selected; cooler/lighter teal and matched friendship hue requested; stripes and routine flourish removed; Barlow/Phosphor established in the kit; C contextual reticles selected with A's transparent idle dot/ring and an outlined reserved X; rounded asymmetric surfaces and gradients restored; 12° slant selected and extended to the placement grid; isolated logo revised through v4; runtime reticle doubled to 64 units and split into layers with short transitions; idle ring set to 75% radius with full-size line weights, expanding on targets; ink fill trialled at 50% opacity.

Source discussion: Improve Game UI and UX (thread `b0806708-59a3-49a6-86a6-d40b82cf6d24`), followed by this continuation. Numerical tokens and provisional geometry are recorded in `design-system.proposal.json`; older revisions are historical.

Related: [[Art Direction]] · [[UI Component Library]] · [[Tech Overview]] · [[AI Usage Log]]
