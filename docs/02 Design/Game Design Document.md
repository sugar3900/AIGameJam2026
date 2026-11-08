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

## Story direction (v2, current focus)
**Jam scope: one guy, done deeply: [[Lukey]].** His page holds the full backstory, the four-week arc, hooks and endings.

- **Heroine:** 29, ambitious house flipper, a deliberate blank slate for the player.
- **External problem:** the house is condemned. There are **30 days** to fix it for real, with **weekly Friday inspections** and a **storm** building toward week 4. We only fix things for real; there's no cosmetic flip.
- **Each love interest** genuinely believes he *is* the broken thing (Lukey is every leak in the house) and resents being "fixed," because each repair deletes a bit of him. He flirts with the heroine throughout, while they **solve the house's problems as a team**. The player can spot the hints, but **he only learns he was human in Act 4.** His death is played for laughs, and his unfinished business is something the heroine can help him finish (for Lukey: the first date he never got).
- **Weekly beats:** the *Creaky Floorboards with Bev & Trish* true-crime podcast (Wednesdays) and Inspector Dan's inspection (Fridays).
- **The mid-game conflict is a real difference in values:** she's a flipper here to profit from his home; he thinks a home is the people in it. It blows up at the end of Act 2 when he overhears her realtor call, and Act 3 opens with a compromise: fix it properly, for whoever lives here next.
- **Endings:** he passes on, or stays if you're in love. Final house choice: **fix for real & sell / stay / demolish.**

## Day structure (one playable day per week)
The 30 days are told as **4 playable days**, one per week. A week passes every time you sleep.

1. **New Game → name entry.** "What's your name, homeowner?" The **Move in** button stays greyed out until a name is typed (max 16 characters). The name is saved and fills `{player}` everywhere in the dialogue.
2. **Morning:** fade in from black on a **"Week N"** card ("Moving day" in week 1, "One week later..." after that).
3. **The podcast starts automatically** on the radio: an "ON AIR" caption panel plays the week's *Creaky Floorboards* episode (~30 s) while you explore. **You can't talk to anyone until the episode ends** ("Shh. The podcast's still on.").
4. **Free play.** Talk to as many of the guys as you like. Each has **one story conversation per day**; talking to him again that day gives a short "come back next week" line that doesn't advance his story.
5. **Daylight fades over ~15 minutes** (golden hour, then dusk, then dark), and then **stays dark**; there's no time limit. When it starts getting late, a one-time tooltip says *"It's getting late. End the day whenever you like by going to bed."*
6. **Go to bed** (click the bed in the bedroom) to end the day: fade to black → "Week N+1" → wake up in the bedroom.
   - **Week 1 only:** you must meet every guy first. Otherwise: *"You feel a presence in the house... someone you still need to meet."*
   - **Skipping a guy for a week is fine.** His story doesn't advance, so next time you get the week you missed.
7. **Going to bed on week 4** → "Inspection Day" card → **Inspector Dan's final inspection** (passes if the kitchen leak is fixed, otherwise the demolition goes ahead) → if it passed, Bev & Trish go live from the porch → **the epilogue** (Day 30 hearing + sell / stay / demolish) → if you got a **romantic ending**, an option to **see him** (a big portrait) → back to the title. The finished save is deleted.

| Week | Podcast at the start of the day |
|---|---|
| 1 | The Catfish of Heartbreak Lane |
| 2 | Something in the Walls Is Singing (Mrs. Pruitt) |
| 3 | The Inspector (Dan interview: "the only thing haunting that house is its water pressure"; storm warning) |
| 4 | We Went to the Library (the 1987 newspaper reveal) |
| Finale | Case Closed (Mostly), live from the porch, only if the house passed |

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

**Endings** (Lukey's thresholds; the player picks from whichever options they've earned at the finale, see [[Lukey]]):
- He stays (romance success): romance ≥ 16 and friction < 8 (fade to black)
- He goes, loved (romance failure): romance ≥ 16, the player chooses to let him go
- He goes, friends (friend success): friendship ≥ 14 and friction < 8 (or "that's your call" with friction < 8)
- He goes, grumpy (friend failure): "that's your call" with friction ≥ 8

Stats are clamped to 0–20.

*Older prototype thresholds for Malcolm/Wyatt/Tyler, still in their JSON:*
- Romance success: romance ≥ 4 and friction < 3
- Romance failure: romance ≥ 4 and friction ≥ 3
- Friend success: friendship ≥ 3 and friction < 3
- Friend failure: everything else (enemies)

**Interconnections (Monster Prom-style):** global flags and cross-character effects. In the prototype:
- Lukey's leak *feeds* Malcolm's mold. Fixing Lukey dries Malcolm out and changes his finale. *(Prototype v1; revisit when Malcolm is rewritten in the v2 tone.)*
- Wyatt has a crush on Tyler; you can play matchmaker across both arcs.
- Characters gossip about each other, and some choices only appear if you've met someone.

## Cast (prototype = first four)
| Hunk | Malady | Room | Personality | Status |
|---|---|---|---|---|
| [[Lukey]] | The Leaks (every leak in the house) | Kitchen + walls | Vain, flirty 1987 aerobics instructor who thinks he's a franchise of leaks; Bon Jovi; died showing off for a date | ✅ v2 arc (Ghosts tone) |
| [[Malcolm]] | Black Mold | Bedroom | Toxic emo poet, a sub, nothing positive | ✅ full arc |
| [[Wyatt]] | Faulty Wiring | Living room | Confused, crossed wires, bisexual ("AC/DC") | ✅ full arc |
| [[Tyler]] | Pink Tile | Bathroom | Obnoxious, bad taste, outdated on gender, pink is masculine | ✅ full arc |
| Az | Asbestos | (attic?) | Diva; protects against fire spreading | 📝 backlog |
| Lance? | Lead Paint | (?) | Pure, chaste, heroic, self-righteous, chivalric | 📝 backlog |
| Joey? | Broken Floor Joist | (?) | TBD | 📝 backlog |
| Dorian? | Broken Door | (?) | TBD | 📝 backlog |

## Mechanics
- **Interactables:** everything clickable sparkles faintly from a distance; on hover it gets an outline and the reticle becomes a pointing finger with painted nails. Ordinary objects toggle (lamp, TV, stove, fridge, drawers, wardrobe, faucet, toilet lid); clicking again reverts.
- **Malady fixtures:** glowing in the hunk's colour, with broken-state dressing (drips + puddle, mold blotches, sparks + flicker). Clicking summons the man. After the arc he's repaired: the dressing disappears and the glow becomes a soft heartbeat.
- **Presence rule:** he only exists while you're in his room. Leave and he's gone until you click again.
- **Intro card:** first meeting only. A swooping banner with the malady name, tagline and his silhouette.
- **Floor plan:** blueprint-style 2D map; click a room to fast-travel. Shows each room's malady/hunk status.
- **Auto-save:** JSON, after every conversation and room change.

## UX / UI
- **Title:** I Can Fix Him. New Game, Continue, Options, Credits, Exit, over a drifting live view of the apartment.
- **Pause (Esc):** Resume, Options, Main Menu.
- **Options:** master volume, mouse sensitivity, text speed, invert Y, fullscreen.
- **HUD:** centre reticle (dot → painted-nail pointer + prompt), room name, repairs counter, controls hint, "Saved" toast.
- **Dialogue:** bottom quarter of the screen: live portrait, name plate, typewriter text, clickable highlighted words, choices (click or 1-5), relationship meters, floating "+1 Romance" pills, hearts, fade-to-black.
- **Ending card** after each arc, with ending type, title and epilogue.

## Look & Sound
[[Art Direction]] · [[Audio Direction]]
Stylized pastel primitives, a different pastel per room, UE mannequins painted with outfits by a custom material, plus primitive props (caps, berets, mustaches, bandanas). No audio in the prototype yet.

## Open Questions
- Names for the backlog hunks (Az is set; lead paint / joist / door TBD).
- Should repairing everyone unlock a final "housewarming party" scene where all the hunks interact?
- Decorating / house-upgrade mechanic (stretch).
- When to move from authored JSON to LLM-generated conversation (see [[Dialogue Format]]).
