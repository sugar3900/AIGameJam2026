---
tags: [tech, ui]
status: implemented
---
# UI Component Library

Implementation companion to [[UI Design System]]. The visual decisions remain the authority; this page describes the reusable runtime pieces and how to review them. Measurements and screen compositions are a first implementation for design feedback.

## Source and assets

| Source | Responsibility |
|---|---|
| `Source/ICanFixHim/UI/FixHimDesign.h/.cpp` | Selected color/type tokens, scalable rounded slanted surface renderer, angled placement stack, icon helper |
| `Source/ICanFixHim/UI/FixHimUI.h/.cpp` | Runtime Barlow font families, text/button factories, slider/checkbox styles, popup shell, focus traversal |
| `Source/ICanFixHim/UI/FixHimDesignReview.h/.cpp` | Live component workshop (`FixHim.DesignSystem`) |
| `Source/ICanFixHim/Tests/FixHimDesignSystemTest.cpp` | Real-widget rendering and authored-content checks |
| `Art Source/UI/Design/` | Prepared font files, icon masks, logo and licenses |
| `Content/ICanFixHim/UI/Design/` | Imported cooked assets |

Imported font faces are assembled into strongly referenced runtime `UFont` families. Titles, buttons and HUD plates use the display face (Barlow Condensed ExtraBold); every other typeface name resolves to Barlow SemiBold. Both are upright cuts that `MakeText` shears the full 12° (`FixHimDesign::DisplayShear` = tan 12°), so glyph lean and line-to-line stepping match; `...Face` typefaces leave the shear to an already-sheared parent block. `MakeCardScreen` content columns are `UFixHimStack`s so rows step along the grid. Screen widgets should obtain text from `FixHimUI::MakeText` / `Font`, not the engine default font.

## Surface and placement primitives

`UFixHimSurface` is compatible with `UBorder`: add content, set padding, and set a brush tint. It draws a rounded 12° face with an even keyline (`BorderWidth`: white on teal/pink, orange on cream), a single extrusion in the face's darker colour (burnt orange, deep pink or ink) and, on popup-weight surfaces, a 50% ink shadow. Teal and pink faces carry their subtle gradient; cream stays flat. `bBorderless` (with `BorderlessRadius`) draws only the slanted fill, as used by the title backdrop and the interaction prompt.

The contour is generated at the current allocated size with tessellated rounded corners and an antialias fringe; it is not a stretched bitmap. Keyline, extrusion and shadow share the same contour. Content is laid out upright; text inside it is sheared by `MakeText`. Leave padding for the slanted edges and the extrusion reserve.

`UFixHimStack` is a vertical layout whose child anchors follow the 12° grid. It reserves the required horizontal space, adjusts row positions along the grid, and keeps each child's own geometry upright. It positions rows from their layout transform only, so a row's own render transform (text shear) is not applied twice. Use it for card content and menu columns. Keep spatial floor-plan cells rectangular so the room geometry remains truthful.

Use the common popup `MakeCardScreen` rather than building a new modal frame per screen. It supplies the scrim, surface, header, bounded scrolling, opening motion and click-outside boundary. A titleless shell supports ending cards. Actions stack vertically.

## Buttons and inline topics

| Variant | Behavior and usage |
|---|---|
| Primary | Pink gradient, white label; the main action |
| Secondary | Cream, ink label; fills pink with a white label on hover/focus |
| Reply | Secondary construction with left-aligned, wrapping authored text in the display face |
| Topic | Pink text and underline, stronger underline on hover/focus; hand cursor; inline conversation link |
| Spatial | Stock rectangular control for the floor-plan's actual room footprints |

`UFixHimButton::Make` creates a wrapping labelled action button and accepts its existing callback. `SetVariant(EFixHimButtonVariant)` selects a semantic variant. The legacy boolean overload remains for existing callers. `Label` is available for alignment and content updates.

`UFixHimButton::MakeStandalone` is the large standalone variant for menus that sit directly on the scene (the title). It has a taller face and a `StandaloneLabel` (32) label, a third larger than `Label`. It uses a 36-unit icon and casts the popup-weight 50% ink shadow (`bStandalone`), since there is no panel underneath.

Leading icons on any button are tinted by `GetIconTint`: orange on cream faces, white on pink or active faces, disabled ink when disabled. They sit 36 units in (38 on standalone buttons) instead of the bare label's 52. Buttons with an icon skip the focus pointer, because the white keyline and lift already mark focus.

Action labels use Barlow Condensed ExtraBold, mixed case, sheared 12°. Replies, spoken lines and narration all use Barlow SemiBold at 26 units, sheared 12° (narration in teal); the dialogue line area is sheared as one block so the typewriter and final topic layouts match. Actions have a content-driven height with a 72-unit minimum in menus, allowing enlarged text to grow.

States: idle, hover, keyboard/gamepad focus, pressed, selected and disabled. Selected reuses the focus treatment. Keyboard/gamepad focus shows a filled white pointer, a white contour and a small lift; hover changes only the fill. State meaning does not rely on pink alone. Pressing moves the face towards its extrusion; disabled uses neutral surface/ink. No heart is added to a reply to predict relationship outcomes.

Stock Slate button behavior still handles pointer capture, keyboard/gamepad activation and dynamic delegates. Existing hover/click/back/topic/choice sounds are retained. The component workshop can force focus/pressed samples without changing gameplay semantics.

## Forms, navigation and accessibility

- Sliders retain a 48-unit hit row, 30-unit thumb, thick rounded track, hover enlargement, keyboard adjustment, live numeric value and soft stepped feedback.
- Checkboxes use the shared palette and Phosphor check glyph. Their padding makes the control's hit area at least 48 units.
- Name entry retains a distinct focus outline and its existing validation/commit behavior.
- Tab/Shift+Tab and up/down or gamepad D-pad traverse buttons, sliders, checkboxes and editable fields, skipping controls under hidden/disabled ancestors. Focused descendants scroll into view. Screen opening selects an initial enabled control when a field does not already have focus. Dialogue focuses the first reply when choices appear. Escape/gamepad Back dismiss screens that already permit dismissal.
- Options include UI text size (100–135%, reapplied when cached screens reopen) and reduced motion. They are saved alongside existing options. Body/reply copy is never shortened or scaled down to fit.
- Reduced motion removes popup scaling, intro entry/exit swoops and scaling, room/map pulses and decorative dialogue hearts/movement; transitions retain necessary narrative fades. Existing reticle motion has separate tuning and is not changed by this component migration.
- Large reading areas and menus scroll inside bounded surfaces, preserving their outer contours. This is a fallback for larger text and unusually long content, not permission to hide normal-size choices unnecessarily.

## Screen patterns

Shared components are used by title/name entry, pause/options/credits, end-day confirmation, dialogue, ending cards, HUD labels, radio captions, character introductions, transitions and keepsakes. The floor plan keeps actual runtime room rectangles and applies the selected palette to its surrounding sheet and statuses.

Dialogue retains its typewriter, clickable topic callbacks and authored choices. The header row (name plate and a teal meter strip whose bars carry Phosphor heart/users/flame icon badges) straddles the panel via `MakeHeaderedSurface`; narration and generic script scenes hide the relationship group. Four replies stack and wrap. Dialogue has no portrait. Character introductions use visible painted portraits where available.

Keyline width comes from `FixHimDesign::ButtonBorder` (6) and `PopupBorder` (12); set `UFixHimSurface::BorderWidth` for large containers. The extrusion is derived from it (`DepthOffset`, `DepthReserveX/Y`: border down, half that across) and coloured `OrangeDepth`, `PinkDepth` or ink. To centre text on a surface, use `bottom = top + FixHimDesign::Extrusion` padding and fill (not centre) alignment for button content: Slate's centred slot alignment ignores asymmetric padding and would lift labels by half the extrusion. `FixHimDesign::CapCentre` (-0.05 em) centres capitals rather than the line box.

`UFixHimWidget::MakeHeaderedSurface` wraps any slanted surface with a teal title plate straddling its top edge. `MakeCardScreen` and the floor plan use it; the plate position is re-fitted each tick from measured sizes, so text scaling and content changes stay aligned.

The selected v4 logo is imported once for the title screen. Its raster edge speckling and a final editable brand master still need a dedicated finishing pass; it has not been silently replaced by a different logo. Construction stripes and routine ray flourishes remain excluded.

## Rebuilding assets

From the repository root on macOS:

```sh
python3 Tools/Art/DesignSystem/prepare_assets.py
python3 Tools/run_in_editor.py Tools/Editor/import_design_system.py
```

Run the import in an initialized editor: the stock font importer requires Slate, even in unattended mode. Import and preparation touch only the shared design asset directory. Font OFL and Phosphor MIT licenses are included with the prepared source assets. `/Game/ICanFixHim/UI/Design` is explicitly included in cooking.

## Review and validation

In a development game or PIE session, execute `FixHim.DesignSystem` to open the live workshop. It displays shared button states, full-length reply text, a slider, checkbox and icon samples. Closing restores the prior gameplay/pause state. It does not change progress.

Run engine automation `FixHim.UI.DesignSystem` with a renderer to write actual widget PNGs under `Saved/DesignSystem/Review/`; null-RHI runs check construction and content without rendering. The suite checks imported font faces and preserves the authored long narration and replies. Captures cover 720p, 1080p, 1440p and ultrawide layouts, plus enlarged text. Use `FixHim.UI.Reticles` for the independent reticle regression suite.

The render suite includes all six audited authored exchanges, with full markup, active topics and conditional-choice snapshots. A separate combined stress case pairs the 240-character spoken line with four replies; it tests capacity and is not presented as a single authored node. Captures wait for font/texture compilation and wrapped-layout convergence. A linear HDR target is converted explicitly to sRGB for PNG export, with a swatch assertion against the selected cream token. Native macOS text-input context tests require a real window; offscreen runs do not activate the OS IME.

Selected text/surface contrast ratios: ink on cream 10.35:1; prompt text relies on its solid ink drop shadow over bright scenes rather than on the 25% plate; teal on cream 5.06:1; white on flat pink 5.12:1; disabled ink on disabled surface 5.18:1. The pink gradient is reserved for large action/reply labels; small ON AIR text uses flat pink.

Validation on 2026-11-13 (UE 5.8, macOS): `ICanFixHimEditor Mac Development` built successfully; the suite additionally asserts that the spoken line and replies render at the same font size. Earlier, on 2026-11-12: `FixHim.UI.DesignSystem` and `FixHim.UI.Reticles` both passed in a native-window renderer run. The design suite wrote 24 PNGs and checked Barlow font loading, full authored copy, text-height bounds, keyboard/D-pad wrapping and disabled-control skipping, gamepad activation, editable-field traversal, and text-size changes on reused screens. The exported cream swatch matched `#FFF5E5`. The title is also captured at 135% text size. A standalone apartment pass verified title focus, options, clickable-topic presentation, dialogue/reply layout and the floor plan at 135%. Narrow map cells wrap full names; their labeling treatment is a design-feedback topic.

See [[UI Review]] for the versioned captures and design-feedback topics. Evaluate contour/border proportions, typographic hierarchy, spacing, focus treatment and the dialogue's balance between reading area and scene visibility. A packaged-build smoke test remains a release check.

Related: [[UI Design System]] · [[Tech Overview]]
