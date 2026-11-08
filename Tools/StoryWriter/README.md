# I Can Fix Him - Story Writer

A lightweight, Twine-style desktop editor for the game's dialogue (`Content/ICanFixHim/Data/Dialogue/*.json`).
Built with Avalonia 12 / .NET 10, so it runs on macOS and Windows.

## Run

```bash
# once: install the .NET 10 SDK (https://dot.net), or user-locally:
#   curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel LTS
dotnet run --project Tools/StoryWriter            # opens the project's Dialogue folder
dotnet run --project Tools/StoryWriter -- <dir>   # or any folder of dialogue JSON
dotnet run --project Tools/StoryWriter -- --selftest   # headless: round-trip, lint, auto-play every arc
```

## What's in it

**Graph tab** (one conversation = one character file at a time)
- Nodes are cards showing the first lines (Rosie in blue, narration in italics), how the node ends, and its effects.
- **Hypertext nodes** (only reached by clicking a `[word]`) are pink, dashed and tagged `LINK`; their arrows are dashed pink.
  They play as full nodes today; the separate look is there for when they become tangents.
- **Conditions** (`if` on entries, choices and links) are amber boxes to the **left of the node the arrow flows into**,
  not on the node. While previewing they show ✓/✗ against the preview state.
- `START` holds the entries; its lanes are laid out one per visit (`v1`, `v2`, ... `after_*`).
- Double-click a node to open its editor; double-click `START` for conversation settings (entries, ending cards).
- Each option (choice, "next", hypertext link) is drawn inside its node with a ● port on the right edge. Drag a port onto
  a node to make or change that link; drop it on empty canvas to drop the link.
- Drag the ● in a node's header onto another node to add a link (goto, or a new choice if it already has one);
  drop on empty canvas to create a node. Hold **Alt** to make a hypertext link instead.
- Right-click for more (preview from here, new node, conversation settings, fit, auto-arrange, rename, delete,
  edit/remove a condition). Drag empty space to pan, scroll to zoom (also the +/− box, lower right), `F` to fit,
  `P` to preview the selected node, `Delete` to delete. The Preview / State panel is hidden until you press the
  button at the top right (or start a preview). Hover a problem badge on a conversation for the messages; click it to
  step through the offending nodes. Links to nodes that no longer exist are cleared automatically.

**Node editor** — rich text lines with speaker colouring, `[topic]` links and `{player}`/`{name}` tokens,
a live "as it plays" preview, and tabs for choices, hypertext links and flow (goto / end / ending / fx / effects).
Select text and press *Hypertext link* to turn it into a link with its own new node. Any link target that
doesn't exist yet is created as a placeholder node on Apply (Twine style).

**Hypertext nodes** are dead ends in the preview: reaching one prints its text, then "Back" returns to the node it was
opened from and shows that node's continue / options (without printing its line again).

**Preview** (right panel) — plays from `START` (entries checked against the preview state) or from any node,
with clickable pink words, choices, locked choices shown with their condition (click to force), fx, and ending cards.
The current node is highlighted in the graph. The *State* tab edits stats, visits, endings and flags.

**Audio** — spoken lines play their voice-over clip (`Art Source/Audio/VO/<script>/VO_<script>_<node>_<index>.wav`, index = position
in the node's lines; never narration or `You:` lines) with a ♪ replay button on the card, and the preview loops the character's music
(`Art Source/Audio/BGM/BGM_<Id>.wav`, matched to the conversation id). *Voice* / *Music* toggles and a dropdown for the non-character
tracks (MainMenu, Explore, Finale) are in the preview header. The node editor shows ♪ play / "no clip" next to spoken lines.
Playback needs no packages: `ffplay` (or mpv/paplay/aplay) on Linux, `afplay` on macOS, winmm on Windows; without one the toggles are disabled.

**Play-through tab** — the whole game's dialogue with one shared save: pick a character, play every visit through to
his ending, then *Continue to* the next character. Cross-character flags and effects carry over.

## Files it writes

- Nothing is written until you press Save / Save All (or choose Save in a dialog); a new conversation stays in memory
  until saved.
- The dialogue JSON, in the same hand-formatted style (saving an untouched file is byte-identical; unknown fields are kept).
- Node positions in `Dialogue/.storywriter/<id>.layout.json` (the game only loads `*.json` directly in `Dialogue/`).

The preview runtime (`Runtime/`) is a port of `FixHimDialogueSubsystem.cpp` and `DialogueCondition.cpp`, and the
problems list mirrors `Tools/validate_dialogue.py`. If the game's rules change, update those too.

The app watches the folder: files edited elsewhere reload automatically (if you have unsaved edits you get one dialog
covering every changed file).
