---
tags: [design, gdd]
status: draft
---
# Game Design Document: I Can Fix Him

## One-Pager
- **Title:** I Can Fix Him
- **Genre:** Dating sim / visual novel in a small explorable 3D space
- **Pitch:** A 29-year-old house flipper buys a condemned house with **30 days** to fix it before the city tears it down. Every broken thing in it is a hot, trapped ghost who thinks he *is* the broken thing. Fix the house together, help him remember who he was, and decide whether he passes on or stays with you.
- **Player fantasy:** "I can fix him." Literally.
- **Platform / controls:** PC (Mac/Win), mouse + keyboard, gamepad supported. Third-person walking, visual-novel conversations.
- **Session length:** Prototype ≈ 20-30 min to finish all four arcs once.
- **Tone:** ***Ghosts* (UK).** Petty, vain, flirty and pun-saturated, with brief sincere moments that land and go straight back to the bit. Deaths are running jokes, not tragedies. Cutesy, never dark or horror. Romance from minute one, escalating flirting → hand-holding → kissing → fade to black.

## Story direction (v2, current)
**Jam scope: four guys, all written in the v2 tone:** [[Lukey]], [[Malcolm]], [[Tyler]] and [[Wyatt]]. Each bible holds his backstory, four-week arc, hooks and endings.

- **Heroine:** 29, ambitious house flipper, a deliberate blank slate for the player, named by the player (`{player}`). Unvoiced.
- **External problem:** the house is condemned. There are **30 days** to fix it for real, a **storm** that hits in week 4, and **one inspection**: Inspector Dan comes **once, on day 30**, for the final inspection (inspectors don't drop by weekly; before that the player only hears him as a guest on the week-3 podcast). We only fix things for real; there's no cosmetic flip.
- **Each love interest is the broken thing** (every leak, the closet mold, the pink tile, the wiring), flirts with the heroine from minute one, and solves the house's problem with her as a team. Each has a mystery the player can spot early, but **nothing states plainly that anyone is a ghost before his own reveal**:
  - **Lukey** (leaks): learns he was a 1987 aerobics instructor from the week-4 podcast (Act 4). Unfinished business: the first date he never got.
  - **Malcolm** (mold): the diary on the top shelf of his closet shows he was never alive; he's a goth teenager's fan fiction (Act 3).
  - **Tyler** (pink tile): his last video shows how he died on flip day one, in 2024 (Act 3). Unfinished business: being told no, and loved anyway.
  - **Wyatt** (wiring): a January 2000 newspaper inside the wall (Act 3). Unfinished business: the "no" he never said on New Year's Eve, 1999.
- **Every morning:** the *Creaky Floorboards with Bev & Trish* podcast. **Day 30:** Dan's final inspection, his first and only visit to the house.
- **Each guy's mid-game conflict is a real difference in values** (Lukey: profit vs. home; Malcolm: can you love a thing without fixing it; Tyler: rip it out vs. restore it; Wyatt: cheap patch vs. doing it right).
- **Endings:** per guy, he stays (romance) or passes on / moves on (three other endings). Final house choice: **sell / stay / demolish**, then a whole-household epilogue.

## Day structure (one playable day per week)
The 30 days are told as **4 playable days**, one per week. A week passes every time you sleep.

1. **New Game → name entry.** "What's your name, homeowner?" The **Move in** button stays greyed out until a name is typed (max 16 characters). The name is saved and fills `{player}` everywhere in the dialogue.
2. **Morning:** fade in from black on a **"Week N"** card ("Moving day" in week 1, "One week later..." after that).
3. **The podcast starts automatically** on the radio every morning: an "ON AIR" caption panel plays the week's *Creaky Floorboards* episode (about a minute, 100–150 words; captions auto-advance at ~1.1 s + 0.36 s per word) while you explore. **You can't talk to anyone until the episode ends** ("Shh. The podcast's still on.").
4. **Free play.** Talk to as many of the guys as you like. Each has **one story conversation per day**; talking to him again that day gives a short "come back next week" line that doesn't advance his story.
5. **Daylight fades over ~15 minutes** (golden hour, then dusk, then dark), and then **stays dark**; there's no time limit. When it starts getting late, a one-time tooltip says *"It's getting late. End the day whenever you like by going to bed."*
6. **Go to bed** (click the bed in the bedroom) to end the day: fade to black → "Week N+1" → wake up in the bedroom.
   - **Week 1 only:** you must meet every guy first. Otherwise: *"You feel a presence in the house... someone you still need to meet."*
   - **Skipping a guy for a week is allowed.** His story doesn't advance, so next time you get the week you missed. But each guy needs all four acts by the end of week 4, so skipping anyone means his Act 4 can't happen before the inspection and the house fails.
7. **Going to bed on week 4** → "Inspection Day" card → **Inspector Dan's final inspection** (day 30, his first and only visit): it passes **only if all four maladies are fixed** (`housefixed`), with a pun per room; otherwise Dan walks to each room that's still broken and the demolition goes ahead → if it passed, Bev & Trish go live from the porch → **the epilogue** (pass: Day 30 hearing, sell / stay / demolish, a beat for each guy's ending, and a shared Sunday dinner if two or more stayed; fail: a last walk through the house and the demolition) → for each **romantic ending**, an option to **see him** (a big portrait) → back to the title. The finished save is deleted.

| Week | Podcast every morning (each also teases one of the other guys, hints only) |
|---|---|
| 1 | The Catfish of Heartbreak Lane (tease: an enormous shirtless man with a pink pompadour, pink all over, saluting from the bathroom window) |
| 2 | Something in the Walls Is Singing (Mrs. Pruitt: Bon Jovi in the walls; tease: a porch light that hums about "a certain year") |
| 3 | The Inspector (radio guest spot; Dan has never been inside and only goes in on day 30: "the only thing haunting that house is its water pressure"; tease: poetry in a closet; BIG STORM SATURDAY) |
| 4 | We Went to the Library (Lukey's 1987 newspaper reveal; tease: the missing January 2000 paper) |
| Finale | Case Closed (Mostly), live from the porch, only if the whole house passed |

## Pillars
1. **Every malady is a man.** The house's problems *are* the cast; fixing the house = finishing his arc.
2. **Puns are load-bearing.** Every character's jokes come from what's wrong with him.
3. **Your choices have weight.** Three relationship axes per man; endings range from love to bad blood.

## Core Loop
See [[Core Loop]].
Explore a room → spot a subtle sparkle/glow → hover (outline + painted-nail pointer) → click → *he* appears (first time: intro card with the malady name + silhouette) → visual-novel conversation → stats change → leave the room (he vanishes) → come back later for the next beat → on the final beat, repair the malady and get an ending.

## Relationship system
Every hunk tracks three axes (0-20 meters in the dialogue box). Romance is generous: most kind or teasing choices count as flirting.

| Axis | Raised by | Means |
|---|---|---|
| **Romance** | flirting, tenderness | love-interest track |
| **Friendship** | curiosity, kindness, listening | platonic track |
| **Friction** | rudeness, dismissing him, cruelty | bad blood |

**Endings** (stats are clamped to 0–20; the player picks from whichever options they've earned at the finale):

| Ending | Lukey / Tyler / Wyatt | Malcolm |
|---|---|---|
| Romance success: he stays | romance ≥ 16 and friction < 8 | romance ≥ 15 and friction < 8 |
| Romance failure: he goes, loved | romance ≥ 16, she lets him go | romance ≥ 15 |
| Friend success | friendship ≥ 14 and friction < 8 (or "that's your call" with friction < 8) | friendship ≥ 13 and friction < 8 |
| Friend failure | "that's your call" with friction ≥ 8 | same |

Multiple romances are allowed and coexist (nobody in the house is exclusive). Each bible has the exact options and his ending titles.

**Interconnections (Monster Prom-style):** global flags and cross-character reads, all optional flavour that never locks content:
- Shared flags: `flag.lukey_blackout` (week 3: Wyatt blacks out the house during Lukey's candlelit dinner; it was jealousy), `flag.lukey_human`, `flag.malcolm_diary`, `flag.tyler_video`, `flag.wyatt_spoke_up`. Later acts call back to whichever reveals have happened.
- Jealousy beats read the other guys' `romance` (Lukey and Tyler are petty about it, Malcolm is thrilled, Wyatt says "fine" until he learns to say how he feels).
- Running cast: Inspector Dan (on the radio in week 3, in person only on day 30), Mrs. Pruitt, Bev & Trish. **The dehumidifier is just an appliance:** it has no name and isn't sentient. The damp-loving guys can resent it as a thing (Lukey and Malcolm sign the Damp Accord against it), but it never acts, hums at anyone or gets promoted.
- **Cross-references are seasoning, not the meal.** Each guy's weekly script mentions the other housemates **at most 0–2 times per act**, and **not at all in week 1** (Act 1 is just him and her). The epilogue can have household beats (the roll call, the shared dinner), but no guy's own coda is mostly about the others.
- **Day-1 touches vary per guy** (no handshakes), and **Malcolm isn't touched at all on day 1**.
- Wyatt's crush on Tyler is subtle, unrequited and never stated; it isn't a route.
- Characters gossip about each other, and some choices only appear if you've met someone.

**Asides (hypertext):** clickable words in a line can be one-off detours (`"aside": true` topics ending in a `"return": true` node). The heroine makes a remark, he answers, and the conversation resumes at the exact line she clicked. Each word works once per conversation. See [[Dialogue Format]].

## Cast (the first four)
| Hunk | Malady | Room | Personality | Status |
|---|---|---|---|---|
| [[Lukey]] | The Leaks (every leak in the house) | Kitchen + walls | Vain, flirty 1987 aerobics instructor who thinks he's a franchise of leaks; Bon Jovi; died showing off under Brenda's sink before their first date (in Lycra, which is the only Lycra in the game). **Look:** a big, bearded redhead with chin-length copper curls that are always wet; copper-pipe neck, arms and legs with duct-tape patches; soaked white tank top with a red valve wheel; denim cut-offs; work boots | ✅ v2 arc |
| [[Malcolm]] | Black Mold | Walk-in closet in the bedroom | Velvet, theatrical "tragic poet" who was never alive (a goth teen's 2005–08 fan fiction); polyamorous colony, sweet sub, terrified of bleach. **Look:** gaunt and pale ivory with black mold blotches; long black wavy hair; a long open moss-black coat, bare-chested; cropped trousers; ankle boots | ✅ v2 arc |
| [[Tyler]] | Pink Tile | Bathroom | Snooty old-money heir with military-school manners; slipped on the tile he hated on flip day one (2024); has never been told no. **Look:** a huge shirtless bodybuilder tiled hot pink from the neck down with white grout lines; a hot-pink pompadour the same pink as the tile; pink gym shorts, white socks, pink high-tops | ✅ v2 arc |
| [[Wyatt]] | Faulty Wiring | Living room fuse box | Shy, sweet, nerdy Australian apprentice electrician (died NYE 1999); apologizes constantly; the lights tell the truth. **Look:** slight and ginger with round copper-rimmed glasses; a singed open tan coat over a cream shirt; brown shorts; braided red/copper wire neck, arms and legs | ✅ v2 arc |
| [[Az]] | Asbestos | (attic?) | K-pop idol diva; protects against fire spreading | 📝 backlog (voice cast) |
| Lance? | Lead Paint | (?) | Pure, chaste, heroic, self-righteous, chivalric | 📝 backlog |
| Joey? | Broken Floor Joist | (?) | TBD | 📝 backlog |
| Dorian? | Broken Door | (?) | TBD | 📝 backlog |

Voices for every hunk: [[Voice Casting]]. The player is never voiced.

## Mechanics
- **Interactables:** everything clickable sparkles faintly from a distance; on hover it gets an outline, the reticle switches to the target's contextual icon (inspect, talk, use or end day) and a prompt appears under it. Ordinary objects toggle (lamp, TV, stove, fridge, drawers, wardrobe, faucet, toilet lid); clicking again reverts.
- **Malady fixtures:** glowing in the hunk's colour, with broken-state dressing (drips + puddle, mold blotches, sparks + flicker). Clicking summons the man. After the arc he's repaired: the dressing disappears and the glow becomes a soft heartbeat.
- **Presence rule:** he only exists while you're in his room. Leave and he's gone until you click again.
- **Intro card:** first meeting only. A swooping banner with the malady name, tagline and his silhouette.
- **Floor plan:** blueprint-style 2D map; click a room to fast-travel. Shows each room's malady/hunk status.
- **Auto-save:** JSON, after every conversation and room change.

## UX / UI
- **Title:** I Can Fix Him. New Game, Continue, Options, Credits, Exit, over a drifting live view of the apartment.
- **Pause (Esc):** Resume, Options, Main Menu.
- **Options:** master volume, mouse sensitivity, text speed, invert Y, fullscreen.
- **HUD:** centre reticle (idle dot and ring, expanding to a contextual icon on interactable targets; see [[UI Design System]]) + hover prompt, room name, repairs counter, controls hint, "Saved" toast.
- **Dialogue:** bottom quarter of the screen: live portrait, name plate, typewriter text, clickable highlighted words (one-way topics or one-off asides), choices (click or 1-5), relationship meters, floating "+1 Romance" pills, hearts, fade-to-black. There are no light effects (flicker etc. were cut); lights are described in narration.
- **Ending card** after each arc, with ending type, title and epilogue.

## Look & Sound
[[Art Direction]] · [[Audio Direction]]
Stylized pastel primitives, a different pastel per room. The four guys are rigged 3D models (the appearance summaries in the cast table above match them; the JSON `look` colours and props are only the fallback mannequin). Dialogue can trigger one-shot sound cues: inline `{sfx:Name}` tags in a line or a node-level `"sfx"` (cue names come from `Art Source/Audio/SFX`; see [[Dialogue Format]]). The podcast's radio caption panel strips the tags but doesn't play them yet, so podcast cues are kept minimal.

## Open Questions
- Names for the backlog hunks (Az is set; lead paint / joist / door TBD).
- Should repairing everyone unlock a bigger "housewarming party" scene? (The epilogue's shared Sunday dinner covers the romance version.)
- Decorating / house-upgrade mechanic (stretch).
- When to move from authored JSON to LLM-generated conversation (see [[Dialogue Format]]).
