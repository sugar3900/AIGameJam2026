---
tags: [design, gdd]
status: draft
---
# Game Design Document: I Can Fix Him

## One-Pager
- **Title:** I Can Fix Him
- **Genre:** Dating sim / visual novel in a small explorable 3D space
- **Pitch:** Rosie buys a decrepit house. Every broken thing in it is a hot, trapped man. Fix the house, get to know the men, and decide who you romance, who you befriend and who ends up hating you.
- **Player fantasy:** "I can fix him." Literally.
- **Platform / controls:** PC (Mac/Win), mouse + keyboard, gamepad supported. Third-person walking, visual-novel conversations.
- **Session length:** Prototype ≈ 20-30 min to finish all four arcs once.
- **Tone:** Flirty, warm, pun-saturated. Romance escalates from flirting → kissing → fade to black.

## Pillars
1. **Every malady is a man.** The house's problems *are* the cast; fixing the house = finishing his arc.
2. **Puns are load-bearing.** Every character's jokes come from what's wrong with him.
3. **Your choices have weight.** Three relationship axes per man; endings range from love to bad blood.

## Core Loop
See [[Core Loop]].
Explore a room → spot a subtle sparkle/glow → hover (outline + painted-nail pointer) → click → *he* appears (first time: intro card with the malady name + silhouette) → visual-novel conversation → stats change → leave the room (he vanishes) → come back later for the next beat → on the final beat, repair the malady and get an ending.

## Relationship system
Every hunk tracks three axes (0-10 meters in the dialogue box):

| Axis | Raised by | Means |
|---|---|---|
| **Romance** | flirting, tenderness | love-interest track |
| **Friendship** | curiosity, kindness, listening | platonic track |
| **Friction** | rudeness, dismissing him, cruelty | bad blood |

**Endings** (decided at the finale, see [[Dialogue Format]]):
- Romance success: romance ≥ 4 and friction < 3 (fade to black)
- Romance failure: romance ≥ 4 and friction ≥ 3 (breakup, bad blood)
- Friend success: friendship ≥ 3 and friction < 3
- Friend failure: everything else (enemies)

**Interconnections (Monster Prom-style):** global flags and cross-character effects. In the prototype:
- Lukey's leak *feeds* Malcolm's mold. Fixing Lukey dries Malcolm out and changes his finale.
- Wyatt has a crush on Tyler; you can play matchmaker across both arcs.
- Characters gossip about each other, and some choices only appear if you've met someone.

## Cast (prototype = first four)
| Hunk | Malady | Room | Personality | Status |
|---|---|---|---|---|
| [[Lukey]] | Leaky Plumbing | Kitchen | Grizzly, good-natured, the flirtiest; pipe & wet puns | ✅ full arc |
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
