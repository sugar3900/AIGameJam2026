---
tags: [art, ui, review]
status: draft
date: 2026-11-12
---
# UI Review

**Ready for design feedback.** The reusable UI system is implemented in Unreal on `feature/reusable-ui-design-system`. This review covers component proportions and screen compositions. The approved colors, Barlow fonts, Phosphor icons, 12° grid and reticle family remain recorded in [[UI Design System]]. Implementation and rebuilding instructions are in [[UI Component Library]].

## Design feedback

- **Surfaces:** corner roundness; white keyline with ink depth on teal/pink, orange border and extrusion on cream.
- **Type and spacing:** display/body hierarchy, action-label sizing, angled columns and padding.
- **Dialogue:** portrait size, relationship row, reading width and the balance between four replies and visible scene.
- **Floor plan:** narrow rooms now use external name tags that overhang their footprint; room geometry is unchanged.
- **Interaction:** filled pointer, white contour and lift for keyboard/gamepad focus (hover changes fill only), pressed depth, transition feel, enlarged text and scrolling.

Open `FixHim.DesignSystem` from the development console in PIE or a standalone game to try the component workshop. Use Tab/Shift+Tab, arrows or D-pad to navigate and Enter/gamepad A to activate. Options provides 100–135% UI text size and reduced motion. Closing the workshop restores the previous game/pause state.

## In the apartment

[Title and initial Continue focus](../Attachments/UI%20Review/ui-title-final.png) · [Options over the title](../Attachments/UI%20Review/ui-options-final.png) · [Spoken dialogue and topic](../Attachments/UI%20Review/ui-topic-final.png) · [Three replies and focus](../Attachments/UI%20Review/ui-dialogue-final.png) · [Floor plan at 135% text](../Attachments/UI%20Review/ui-floor-plan-large-text.png)

These standalone captures predate the 2026-11-13 review fixes below and have not been regenerated. They show the UI over the real apartment at 1600×900. Reduced world-rendering settings keep the unattended capture responsive; they are UI composition checks, not environment-art references. Standalone dialogue uses the existing live character portrait; isolated stress cases use the painted portrait assets.

## Shared components

![Native Unreal component workshop](../Attachments/UI%20Review/01-components-1080p.png)

These are actual UMG/Slate widgets rendered by Unreal. Focused and pressed samples are held in their corresponding visual states for comparison. The body text and icons stay upright while their anchors follow the shared 12° columns.

## Dialogue

![Full line and four replies with Tyler's portrait](../Attachments/UI%20Review/04-dialogue-four-replies.png)

This combined capacity case pairs the 240-character spoken line with four complete replies, including the longest reply. It is a layout stress case, not a single authored exchange. The six actual exchanges below retain their authored text and topic markup. Relationship meters in isolated fixtures have no gameplay progress to display.

| Review | Native capture |
|---|---|
| Long narration, ultrawide | [2560×1080](../Attachments/UI%20Review/05-long-narration-ultrawide.png) |
| 135% text, long narration and four replies | [720p](../Attachments/UI%20Review/07-large-text-dialogue-720p.png) |
| Authored stress exchanges | [Case 1](../Attachments/UI%20Review/18-authored-case-01.png) · [Case 2](../Attachments/UI%20Review/18-authored-case-02.png) · [Case 3](../Attachments/UI%20Review/18-authored-case-03.png) · [Case 4](../Attachments/UI%20Review/18-authored-case-04.png) · [Case 5](../Attachments/UI%20Review/18-authored-case-05.png) · [Case 6](../Attachments/UI%20Review/18-authored-case-06.png) |

## Screen coverage

| Screen | Native capture |
|---|---|
| Pause | [720p](../Attachments/UI%20Review/02-pause-720p.png) |
| Options | [100% text](../Attachments/UI%20Review/03-options-1080p.png) · [135% text](../Attachments/UI%20Review/06-large-text-options.png) |
| Title with selected original logo | [1440p](../Attachments/UI%20Review/08-title-1440p.png) · [135% text](../Attachments/UI%20Review/19-large-text-title.png) |
| Name entry | [1080p](../Attachments/UI%20Review/09-name-entry.png) |
| End-day confirmation | [1080p](../Attachments/UI%20Review/10-end-day-confirmation.png) |
| Credits | [1080p](../Attachments/UI%20Review/11-credits.png) |
| Radio caption | [1080p](../Attachments/UI%20Review/12-radio-caption.png) |
| Character introduction | [1080p](../Attachments/UI%20Review/13-character-introduction.png) |
| Ending card | [1080p](../Attachments/UI%20Review/14-ending-card.png) |
| Week transition | [1080p](../Attachments/UI%20Review/15-week-transition.png) |
| Keepsake chooser | [1080p](../Attachments/UI%20Review/16-keepsake-chooser.png) |
| HUD labels and contextual reticle | [1080p](../Attachments/UI%20Review/17-hud-labels.png) |

The isolated captures use transparent space around the widgets; the workshop includes its own backdrop. 720p and 1440p captures scale the same 1920×1080 logical layout, matching the game's DPI policy. Ultrawide uses a wider logical viewport. Enlarged reading areas scroll when their content exceeds the available height.

## Visual review triage (2026-11-13)

An independent visual review compared the captures with the Exploration 01 #7 inspiration and the Foundation 02 slant study. Accepted findings are implemented, and the isolated captures above have been regenerated.

**Fixed**
- **Dialogue footprint:** the slant inset is no longer reserved twice. Narration collapses the portrait column. The portrait sits at the bottom-left, and replies step along the 12° grid with clear spacing below the line.
- **Scrolling:** cards have a fixed header, a scrolling body and a fixed action footer. Dialogue scrolls only the line text and keeps all replies visible. Scrollbars use a slim teal thumb inside the face.
- **Focus:** keyboard/gamepad focus uses a filled pointer, a white contour and a lift. Hover changes only the fill. Checkboxes and sliders have their own focus rings.
- **Labels:** an optical offset centres display and reply labels in their faces.
- **Forms:** checkboxes share one rounded box with a teal checked fill and a white check. Sliders show filled and unfilled tracks. Back and Close are secondary actions.
- **Meters:** neutral tracks; each stat fills in its own color.
- **Topics:** no gap before punctuation, and the underline matches the word width.
- **Floor plan:** no mid-word breaks, external tags for narrow rooms, an opaque pink current room and no space before "?". This change builds, but the floor plan has no isolated capture and the live capture has not been regenerated.
- **Character intro:** one teal band, a framed portrait and a shared Continue prompt.
- **HUD:** the prompt plate clears the reticle, and control hints hide while the reticle is hidden. The title footer contrast is raised.
- **Fidelity:** teal and pink surfaces use a white keyline with ink depth; cream keeps orange, matching the approved kit. Title actions have leading Phosphor icons. Continue comes first when a save exists. The title backdrop follows the 12° edge.

**Deferred:** splitting Week and Repairs into separate HUD plates; restructuring the dialogue header into a name-plate/malady/meter strip; rich-text topics.

**Left for the designer:** upright versus slanted bodies on very tall panels; whether the portrait shows when the speaker is already visible; centred versus left-aligned modal copy; a header plate on the week transition.

## Validation

On 2026-11-13, after the review fixes, the UE 5.8 macOS Development Editor build succeeded. Native-window automation completed `FixHim.UI.DesignSystem` and `FixHim.UI.Reticles` successfully. The 24 isolated captures cover 720p, 1080p, 1440p and ultrawide, with options, dialogue and the title tested at 135% text size. The suite checks imported fonts, full authored copy, allocated text heights, keyboard/D-pad traversal, disabled-action skipping, gamepad activation, editable-field navigation and text-size changes on cached screens. Its exported cream swatch matches `#FFF5E5`.

To regenerate the isolated captures, run `Automation RunTests FixHim.UI` in an editor started on `/Engine/Maps/Entry`. PNGs are written to `Saved/DesignSystem/Review/`. Native-window mode covers macOS input-method activation; `-RenderOffscreen` skips only that OS-context check. The live workshop is opened separately with `FixHim.DesignSystem`.

## Production follow-up

The title uses the selected v4 concept logo. Alpha-edge cleanup and an editable production master remain pending; the logo has not been redesigned. Packaged-build validation remains a release check. The reticle's fill opacity and motion feel remain separate review topics in [[UI Design System]].

Related: [[UI Design System]] · [[UI Component Library]]
