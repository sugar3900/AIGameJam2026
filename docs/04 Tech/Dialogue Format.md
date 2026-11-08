---
tags: [tech, dialogue]
status: implemented
---
# Dialogue Format

Each hunk is one JSON file in `Content/ICanFixHim/Data/Dialogue/<id>.json`. The game loads every file in that folder at startup (`UFixHimDialogueSubsystem`). Edit, then run `FixHim.ReloadDialogue` in the in-game console. No restart needed.

**Always lint before committing:**

```bash
python3 Tools/validate_dialogue.py
```

It checks broken `goto`s, `[topics]` with no handler, bad conditions, unknown stats, unknown `fx` names (node and inline), dead ends, unreachable nodes, and aside chains that can never reach a `"return": true` node.

## File shape

```json
{
  "id": "lukey",                       // matches AFixHimMalady.HunkId in the level
  "name": "Lukey",
  "malady": "Leaky Plumbing",          // shown on the intro card + dialogue header
  "room": "kitchen",                   // matches AFixHimRoom.RoomId (floor plan status)
  "tagline": "He's been dripping for you since 1987.",
  "look": { ... },                     // outfit + props, see below
  "entries": [ { "if": "visits == 0", "node": "v1" }, ... ],
  "endings": { "romance_success": { "title": "...", "text": "..." }, ... },
  "nodes": { "v1": { ... }, ... }
}
```

### kind and speakers
- `"kind"`: `"hunk"` (default, a love interest with a malady and room) or a story script such as `"podcast"` or `"epilogue"`. Scripts use the same node format but don't count as hunks (repairs counter, floor plan).
- `"speakers"`: extra names allowed as line prefixes, e.g. `"speakers": ["Bev", "Trish", "Mr. Giggles"]` lets you write `"Bev: Welcome back!"`. The dialogue box shows that name in the name plate.

- `"kind": "scene"`: a scripted scene played in the dialogue box with no portrait (e.g. `inspection.json`).

Current scripts: `inspection.json` (Dan's final inspection at the end of week 4; the house passes only when **every** story hunk is fixed, i.e. `fixedcount == storycount` / `housefixed`; the game's finale uses the same rule to decide whether the podcast plays), `podcast.json` (*Creaky Floorboards with Bev & Trish*, one short episode every morning per week, ~100–150 words; the finale episode needs `housefixed`) and `epilogue.json` (pass: Day 30 hearing → house choice, which sets `flag.house_choice` 1 = sell, 2 = stay, 3 = demolish → a beat per guy per ending → shared dinner if 2+ romances; fail: demolition walk-through).

**Branching without a click-free conditional goto:** a node whose choices have mutually exclusive, exhaustive `if`s shows exactly one choice, which works as a conditional "continue" (used by `inspection.json` and `epilogue.json`, e.g. `"if": "malcolm.ending_romance_success"`). The validator warns "every choice is conditional" on those nodes; make sure the conditions cover every case.

### entries
Checked top to bottom when you click the glowing fixture; the first matching `if` picks the starting node. This is how story beats per visit work (`visits` counts finished conversations).

Add `"counts": false` to an entry for conversations that shouldn't advance the story or use up the day's beat, e.g. the "come back next week" chatter:
```json
{ "if": "talkedtoday", "node": "today", "counts": false }
```

### nodes

| Field | Meaning |
|---|---|
| `lines` | Array of lines shown one at a time. Plain text = **him**. `You: ...` = **the heroine**. `Name: ...` = a declared extra speaker. `*...*` (whole line) = narration. |
| `choices` | `[{ "text", "goto", "if"?, "do"? }]`. Shown under the **last** line. Hidden if `if` is false. |
| `topics` | Clickable highlighted words. Write `[pipes]` or `[shown text|topicId]` in a line, then `"topics": { "pipes": "node" }` (one-way divert) or `{ "pipes": { "goto", "if", "do", "aside" } }`. With `"aside": true` the topic is a one-off detour that comes back to the line it was clicked on (see **Asides**). |
| `do` | Stat/flag changes applied when the node is entered (also allowed on choices and topics). |
| `goto` | Next node when the lines run out and there are no choices. |
| `end` | `true` ends the conversation (counts as a visit, auto-saves). |
| `ending` | `romance_success`, `romance_failure`, `friend_success`, `friend_failure` or `auto`. Ends the conversation, **repairs the malady** and shows the ending card. `auto` picks from stats. |
| `return` | `true` marks the last node of an aside: when its lines run out (and it has no choices) the conversation resumes the line the aside was clicked on. |
| `fx` | `"fade"` (fade to black with `fxText`) or `"hearts"`. Plays when the node is entered. Lines can also carry their own inline `{fx:name}` tag (see **Effects (`fx`)**). |

### Asides (one-off clickable detours)
A normal topic is a one-way divert: clicking `[pipes]` leaves the current node for good. An **aside** comes back:

```json
"v2": {
  "lines": [
    "I got these [pipes] in 1987.",
    "Anyway. Where was I?"
  ],
  "topics": { "pipes": { "goto": "v2_pipes", "aside": true, "do": { "friendship": 1 } } },
  "choices": [ { "text": "Tell me more.", "goto": "v2_more" } ]
},
"v2_pipes": {
  "lines": [ "Copper. Original. Don't let anyone tell you otherwise." ],
  "return": true
}
```

- Clicking an aside topic remembers the current node and line, applies the topic's `do`, and enters its `goto`.
- The chain can be several nodes long and can have its own choices; **every branch must end in a node with `"return": true`**. That node's lines play, then the conversation goes back to the exact line the word was clicked on and continues from there (its remaining lines, then its choices or `goto`). The original node's `do` and `fx` are **not** applied again.
- Asides nest: a line inside an aside can have its own aside topic.
- An aside is **spent** after one click: for the rest of that conversation the word renders as plain text. String-shorthand topics and topics without `"aside": true` behave as before.
- A `return` node reached with no open aside ends the conversation (logged as a warning).

### Effects (`fx`)
Node-level `"fx": "name"` plays on the node's first line; an inline tag `{fx:name}` anywhere in a line plays when that line appears and is stripped from the text (`"*{fx:hearts} He blushes.*"` shows as `*He blushes.*`). A line tag wins over a node fx on the same line. Effects do not replay when a line is re-shown after an aside.

| Name | Effect |
|---|---|
| `fade` | Fade to black showing the node's `fxText` (`...` if none). |
| `hearts` | Hearts burst. |

Text substitutions: `{player}` (the name the player typed at New Game; "Rosie" if none) and `{name}` (the hunk).

### Effects (`do`)
```json
"do": { "romance": 2, "friction": 1, "flag.knows_secret": 1, "malcolm.friendship": 1 }
```
- `romance`, `friendship`, `friction`: this hunk's relationship axes (meters in the dialogue box, 0-10 scale).
- `<otherHunk>.<stat>`: cross-character effects (Monster Prom-style interconnections).
- `flag.<name>`: global integer flags shared by every hunk.

### Conditions (`if`)
Integer expressions: `! && || == != < <= > >= + - ( )`.

| Identifier | Value |
|---|---|
| `romance`, `friendship`, `friction`, `visits`, `met`, `fixed` | this hunk |
| `lukey.romance`, `tyler.met`, `malcolm.fixed`, ... | another hunk |
| `ending_romance_success` (etc.) | 1 if this hunk got that ending |
| `seen.<nodeId>` | 1 if this hunk's node was visited |
| `flag.<name>` | global flag |
| `fixedcount` | number of story hunks whose malady is repaired (scripts never count) |
| `storycount` | number of story hunks (`kind: hunk`) |
| `housefixed` | 1 if every story hunk is fixed (`fixedcount == storycount`) |
| `week` | current week / playable day (1–4; 5 after the final inspection) |
| `talkedtoday` | 1 if this hunk already had his story conversation this week |

Example: `"if": "romance >= 4 && friction < 3"`.

### look
```json
"look": {
  "skin": "#C98A6B", "shirt": "#B3282D", "pants": "#3A4F78", "shoes": "#5A3A22",
  "pattern": 1,                 // 1 = plaid shirt
  "glow": "#4FA8FF",            // fixture glow, outline and intro card colour
  "scale": 1.08,
  "props": [ { "shape": "cylinder", "socket": "head", "loc": [x, y, z], "rot": [roll, pitch, yaw], "scale": [sx, sy, sz], "color": "#2F6FD1", "emissive": 0 } ]
}
```
Props are engine primitives (`cube`, `sphere`, `cylinder`, `plane`) in **character space**: X forward, Y right, Z up from the feet, centimetres (mannequin is ~181 cm, head bone at 162). They're glued to `socket` (a bone name: `head`, `neck_01`, `spine_03`, `spine_05`, `pelvis`, `hand_r`...) so they follow the idle animation.

## Arc structure used by the four prototype hunks
1. **v1, intro.** Meet, malady explained, first impression (+romance / +friendship / +friction choices).
2. **v2, getting to know him.** Backstory, cross-character gossip (sets flags).
3. **v3, crossroads.** "What are we?" Romance and friendship branch; first kiss (`fx: hearts`); interconnection choices gated by flags.
4. **v4, finale / the fix.** Choices gated by stats choose the ending:
   - romance ≥ 4 & friction < 3 → **romance success** (fade to black)
   - romance ≥ 4 & friction ≥ 3 → **romance failure**
   - friendship ≥ 3 & friction < 3 → **friend success**
   - fallback → `auto` (resolver picks by stats; usually friend failure if you've been rude)
5. **after_\*.** Short post-ending chats per ending.

## Moving to an LLM later
`UFixHimDialogueSubsystem` exposes a UI-agnostic `FDialogueView` and `Advance / Choose / ClickTopic`. An AI-driven provider can produce the same view (text, choices, topics) and apply the same `do` effects, so the UI and the save format don't change. The JSON character sheets (`name`, `malady`, `tagline`, endings, existing lines) double as the prompt context.

Related: [[Tech Overview]] · [[Game Design Document]]
