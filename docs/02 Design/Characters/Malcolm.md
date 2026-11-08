---
tags: [design, character]
status: draft
---
# Malcolm: Black Mold

**Room:** Bedroom, the walk-in closet (the same room as your bed) · **Glow:** `#6BCF7F`
**Script:** `Content/ICanFixHim/Data/Dialogue/malcolm.json`

> **Tone: *Ghosts* (UK).** Velvet, theatrical, silver-tongued, a little menacing and very mischievous, a Victorian poet who has never seen the Victorian era. Purple metaphor, constant puns, flirting from the first line. Brief sincere moments land and then go straight back to the bit. Cutesy, never dark.

---

## The premise (Malcolm's slice of the story)
- **The heroine** (29, house flipper, `{player}`) moves into the bedroom of 12 Heartbreak Lane and opens the closet. The back wall is velvet-black mold, and it unfolds into a tall, gaunt, ivory-pale man in a long open moss-and-black overcoat and no shirt, black clovers of mold wrist to brow: *"Ugh. Light. Who let the light in."*
- **He believes he's the tragic ghost of a dead poet.** "Once a man of letters, now a man of walls." He never says "ghost" outright before Act 3; he just implies a tragic past life.
- **The truth: he was never alive.** He's Stachybotrys *chartarum* ("of paper"), grown on a shoebox of a goth teenager's 2005–08 diaries on the top shelf. He soaked up her poetry, her period dramas and her emo playlists, and that's where his whole personality comes from.
- **Fix = the mold is cleaned out.** He can't pass on, because there's nothing to pass on from. His endings are about where a dry, harmless fungus goes to live.

## Looks (match the 3D model)
Tall, very lean and gaunt, 25–30. Heavy-lidded grey eyes with dark shadows ("the shadows are natural"), unsmiling. **Pale ivory skin** (not grey) with clover-shaped black mold blotches on his temple and brow, neck, chest, abs, forearms, hands and ankles ("wrist to brow"). Black, shoulder-length, loose waves, parted in the middle, tucked behind his ears, a little lank. Clean-shaven. A long, calf-length overcoat worn **open**, mottled moss-green and black like mold, sleeves pushed to the elbows; **bare-chested** underneath; cropped mottled green-black trousers, bare ankles, black lace-up ankle boots. Raven's 2005 drawing of him is exactly this, down to the boots (she drew the abs "with real commitment").

## Writing rules
- **No touch in Act 1.** He keeps a theatrical distance: the bed between them "as a matter of etiquette," and when she reaches to brush plaster off his lapel he recoils ("Don't touch the art. I'm toxic, madam. Literally.") and bows instead. No handshake. In Act 2 he reaches to tuck her hair and stops an inch short. In Act 3 they pull at the shoebox without touching hands and sit "with one careful inch of air" between their shoulders. **The first touch is the Act 3 hand-hold** (`v3_hand`, hearts: "You touched the art. On PURPOSE.").
- **Housemates:** none in Act 1 (only the unspecific "everyone in this house is dead" hint). At most two references per act from Act 2 on, never the main topic.
- **The dehumidifier** has no name and no personality. It's an appliance that dries him out, and he fears and resents it as a thing ("a guillotine with a water tank," "B-flat, the key of funerals"). He hisses at it; it doesn't react, "because it's a dehumidifier."
- **Inspector Dan** only comes once, on day 30 (`inspection.json`). In Act 2 the heroine mentions the inspection and Malcolm is thrilled to be "reviewed."

## Who he thinks he is (Acts 1–2)
- **A tortured poet.** *"I don't compose, madam. I DEcompose."* His magnum opus is **"Banana"**, forty pages long, thirty-nine of them dramatic pauses. Also "Ode to the Homeowner" and a haiku that's missing a line "because I am also missing something."
- **Rot is romance.** Ruins, ivy, roofless abbeys. *"Nobody bleaches Pompeii."* / *"Pompeii isn't in my bedroom."* / *"Pompeii WISHES it were in your bedroom."*
- **A sub, played sweet.** He keeps asking to be told what to do and goes weak at a firm voice (*"Say that again. ...No. Don't. I'm fine."*). Harsh orders give romance *and* friction. In the diary it turns out Raven wrote it in: *"Tell me what to do (because he respects women)."*
- **A colony, so he's polyamorous.** "Nine billion of me. One heart is for amateurs." He writes poems about her other boyfriends and is genuinely delighted for her.
- **Traumatized by bleach.** A tenant in 2011 "had a spray bottle and no mercy. I lost an entire stanza of myself." He won't say the word without clutching the doorframe.
- **Nemesis: the dehumidifier.** Not a character, just an appliance. "It drinks the very air. That's a guillotine with a water tank." It hums in B-flat, "the key of funerals." In the storm its bucket fills and it switches itself off, and Malcolm has never looked happier.
- **Forms of address:** "madam" (Act 1) → "my dear" (Act 2) → "my editor" (Act 3, after the diary) → her **name** in Act 4 if romance ≥ 12.

### The running gag: "Everyone in this house is dead"
He keeps telling her, in purple metaphor, that everyone here is dead, and keeps it deniable: *"Dead inside. Dead tired. Dead gorgeous, one or two. Dead set against you, mostly."* Nobody takes him seriously (he says it about everything; he once said it about the toaster. *"The toaster WAS dead. Nobody ever apologized."*).
- Act 1: "gentlemen who have overstayed their welcome. By decades." (unspecific; nobody is named)
- Act 2: "Ask the electrician what year it is. Ask the tile boy when he last ate. Ask the leak why his hair never dries." / "I speak only in metaphor and spores."
- Act 3 (after the diary): he loses his nerve. *"If I'm not a ghost, perhaps nobody is. Perhaps they're all just very committed to a look."* (misdirect)
- Act 4: the week 4 podcast vindicates him on Lukey (*"I said it in 2009"*), plus an optional `flag.lukey_human` callback.

### Hints the player spots before the twist
He quotes emo lyrics and teen-girl culture as if they were "very old, very Victorian" verse: *"I'm not okay. I promise."* He knows Mr. Darcy suspiciously well. He gestures at the top shelf ("I grew from the page") and then very quickly stops. His "reliquary" is "absolutely NOT a shoebox from a mall."

## Who he actually is (revealed in Act 3)
**Fan fiction.** The shelf he's been eating since 2008 gives way, and the shoebox bounces off her head ("things are always falling on heads in this house"). Inside are five composition notebooks: **PROPERTY OF RAVEN (KAYLEIGH). KEEP OUT. THIS MEANS YOU, MOM.**
- **"Banana," by Raven (age 14):** *You were yellow once. / Now you are brown. / Like everything. / Like me. / (Mom put it in my lunch AGAIN.)* It's six lines, not forty pages.
- **A drawing of him** ringed with hearts: *"MALCOLM ASHGROVE. My ghost boyfriend. Died 1847 (consumption + heartbreak). Lives in my closet. Hates sunlight (same)."*
- **"THINGS MALCOLM WOULD SAY,"** a list of all his catchphrases, including *"Basically anything Mr. Darcy says but sadder."* (His dramatic hand flex is Darcy's. He's been doing a stolen hand flex for eighteen years.)
- Later entries: 2006 vampire Malcolm, 2007 cello-in-a-band Malcolm, and a Darcy duel that ends with them agreeing to share her ("Polyamory is canon. Page forty-one.").
- **The last entry, June 2008:** *"I think I'm okay now. Like, actually okay. I don't need Malcolm anymore. But I'm keeping him. Just in case somebody else does."*

**Mortified, then freed.** *"I wasn't a tragedy. I was a phase. ...A PHASE, my dear."* ("Like the moon.") If he's fiction, he isn't doomed: fiction can be revised. She becomes **his editor**. Sets `flag.malcolm_diary`.

## The conflict: can you love something without fixing it?
- **Him:** rot is character. *"You want to bleach the character out of this house. Nothing left that ever rotted or wrote a single bad poem."*
- **Her:** it's a health hazard and a resale problem, and she's sleeping ten feet from it. Her throat has been scratchy since week 1. Her own note on the quote reads *"Or just prime over it? Buyers never look in closets."* That's the cosmetic flip the game doesn't allow.
- **Act 2** blows it up. **Act 3** reframes it: Raven revised him every summer, so editing isn't erasing. **Act 4** lands it: she coughs, he realizes he's the reason (*"Love isn't supposed to come with an inhaler"*), and he asks for the clean-out himself. She does it without bleach, and the diaries are kept dry and safe. *"It was never the rot, was it. It was the stories."*

## The cast, through Malcolm
Kept deliberately light (see Writing rules). Every housemate reference in his script:
- **Act 2:** the "ask the electrician what year it is / the tile boy when he last ate / the leak why his hair never dries" hint (`v2_house`), and the optional colony poem "To the Other Gentlemen of the House" (`v2_p_others`, shown once she's met any of them): *O leak, O tile, O nervous spark, / She lights you all up. I live in the dark. / I'd duel you for her, but I'm rather a crowd. / So I'll love her in shifts. It's allowed.*
- **Act 3:** if `flag.lukey_blackout`, he heard Lukey serenade her ("Ode to a Man Serenading Pasta") and they've signed the Damp Accord against the dehumidifier ("mostly about dust"). After the diary: "Perhaps they're all just very committed to a look."
- **Act 4:** the podcast vindication ("A man died under a sink in 1987. I SAID that.") and, if `flag.lukey_human`, "Give my mold-in-law my regards."
- **Inspector Dan:** only on day 30. Malcolm has never been reviewed before and hopes he'll be harsh.
- **Mrs. Pruitt:** her garden shed is where he ends up in the grumpy ending.

---

## Arc by act
| Act (week) | Beats |
|---|---|
| **1: Ugh. Light.** | He unfolds from the closet. Dramatic / okay? / "health hazard, out." She's sleeping in his room ("in a candlelit way"), and he keeps the bed between them. Her intentions: walk-in selling point / "you're a lot" / convince me. "Everyone in this house is dead" (nobody named), then "Okay, goth" / "Are YOU dead?" ("a man of letters, once; now a man of walls") / the Tacoma crawlspace ("Was it handsome?"). The dehumidifier in the hall. He recoils when she reaches for his lapel: "Don't touch the art." No housemates, no touch. |
| **2: The poem and the quote.** | The mold forms a heart ("a water stain with ambition"), hidden behind his open coat. "Ode to the Homeowner" or the short haiku. The colony and "damp romance": one optional poem about the other gentlemen, or "just you." She mentions the day-30 inspection ("I've never been reviewed before. Will he be harsh?") and he drops the "ask the electrician" hint. A near-touch (he stops an inch from her hair). "Someone in this house is pining. ...It's me." Then her cough and the remediation quote: **"Can't you love a thing without fixing it?"** |
| **3: The diary.** | She's measuring for the remediation crew. His will (darkness to the night sky, poems to the British Library). "Tell me what to do": tape measure / your choice / hold the stool. The top shelf collapses (ShelfCrash, Bonk) and the diary comes out: "Banana," a drawing of Malcolm Ashgrove that's exactly him ("I don't remember posing for this"), THINGS MALCOLM WOULD SAY, the June 2008 entry. Fan fiction, a phase "like the moon," revision, and she becomes his editor. **First touch:** the hand-hold (hearts) / keep the notebooks safe / "fewer spores." Then the storm warning. |
| **4: The storm.** | Rain pours through the ceiling and he's ENORMOUS ("spore-tacular") while the dehumidifier fills up and switches itself off. She can't stop coughing; he realizes it's him. The podcast vindicates him (optional Lukey callback). "Tell me what to do, one last time." The clean-out, NO BLEACH. The stories stay. "Where do I go?" leads to the endings. |

Callbacks: the Act 2 opener changes if she ordered him out in Act 1 (`seen.v1_boss`, "I THOUGHT about going. That's growth") or if friction ≥ 4 (the "NOT HOME" note). The Act 3 opener changes after "Rot isn't character. It's damage" (`seen.v2_damage`, a villanelle rhyming "damage" with "sandwich") or after Lukey's blackout (`flag.lukey_blackout`). The "today" node is his "quota of human contact."

### Hypertext asides (clickable words, return to the same line)
`chartarum` (v1), `rot` → "Banana" (v1), `bleach` (v1, from two nodes), `dead` (v1), `toolbelt` (v2), `colony` (v2), `pining` (v2), `reliquary` (v3), `same` (v3), `darcy` → the stolen hand flex (v3), `multitudes` (v4).

## Relationship tuning
- **Stats run 0–20 and are clamped.** Romance is generous: most teasing or tender choices give it. Harsh orders give romance + friction (he's a sub).
- **Simulated random play:** median romance 14, friendship 14, friction 7 (re-run after the Act 1–4 cuts; all four endings still reachable at the same thresholds). A consistent romantic maxes romance at 20, a consistent friend maxes friendship at 20, and a rude player maxes friction at 20. A kind player who always takes the first ending offered gets the terrarium about 90% of the time.

| Option at the finale ("Where do I go?") | Shown when | Ending |
|---|---|---|
| "Move into a terrarium on my nightstand. I'm in love with you." | romance ≥ 15 and friction < 8 | Terrarium |
| "I love you. Go somewhere your rot is adored." | romance ≥ 15 | Cheese cave |
| "Stay as my friend. The kitchen needs a sourdough starter." | friendship ≥ 13 and friction < 8 | Sourdough |
| "That's your call, Malcolm." | always (one version shown) | friction < 8 → he makes his first ever choice (sourdough); friction ≥ 8 → Pruitt's shed |

"That's your call" is the cruellest and kindest thing you can say to a sub: with low friction it's his growth moment ("Nobody's written this bit for me").

## Endings
| Ending | Title | Outcome |
|---|---|---|
| `romance_success` | **Terrarium Ever After** | A respectable fungus in a little cap, in a moss terrarium on her nightstand. A kiss (cold, earthy, very sincere), fade. New poem: "Dry." It's one line: her name. The dehumidifier is banned from the bedroom. |
| `romance_failure` | **Blue for You** | He loves her enough to go where his rot is adored: an award-winning blue in a Wisconsin cheese cave. "I'll finally be cultured." A wheel arrives every Valentine's Day, poem pressed into the rind, always a little too strong. |
| `friend_success` | **Bread Poets Society** | A sourdough starter in a jar on the kitchen counter: "a fungus with a JOB." "I knead this. Oh no. I'm already doing bread puns." Raven's diaries live in an acid-free box with a gel-pen label. Thursday is bread night; Dan brings butter. |
| `friend_failure` | **Rot in Peace** | He storms off to Mrs. Pruitt's garden shed and grows on her crossbow case out of spite. He leaves a forty-page poem, "Remediation," which is the word "no" over and over. Her cats deliver weekly sonnets titled "Bleach." |

**Unfinished:** if his Act 4 hasn't happened by the end of week 4, the mold isn't fixed and (once inspection checks all four maladies) the house fails.

## Flags and cross-references
- **Sets:** `flag.malcolm_diary` (v3_free).
- **Reads (optional flavour only):** `lukey.met || tyler.met || wyatt.met` (Act 2 colony poem), `flag.lukey_blackout` (Act 3 opener), `flag.lukey_human` (Act 4 callback). Cross-effect: `lukey.friendship +1` when you tell him Lukey knows.

## Sound cues
Inline `{sfx:Name}` tags: DoorCreak + Squelch as he unfolds (v1), Hum for the dehumidifier (v1), DoorLatch when the closet shuts (v1, v2), DoorCreak (grudge note), Squelch for the damp scroll and his spreading (v2), DoorKnock (Act 3 sulk note), Whoosh as he lunges, **ShelfCrash + Bonk** when the shelf collapses and the box hits her, RadioStatic for the storm warning (v3), **Thunder + Rain** and a Squelch puddle when the storm hits, PowerDown when the full dehumidifier gives up, Thunder at the clean-out, WaterSplash/Squelch for scrubbing, ReactSurprise for his Victorian scream, Kiss (terrarium, cheese cave), Whoosh as he leaves through the window (cheese cave, shed).

## Voice
**Silky, theatrical, velvet-menace British baritone**, in the spirit of Loki: refined RP, unhurried, savouring every word, with a private chuckle and sudden flashes of venom or glee. It's a goth teen's idea of a Victorian poet (all Mr. Darcy), so the accent is part of the costume. The menace cracks into neediness when you give him an order. ElevenLabs fallback: **Callum**. Full brief and Voice Design prompt: [[Voice Casting]]. Not voiced in the game yet.

## Open questions
1. Does Raven (Kayleigh, now about 35) ever turn up, e.g. at the sell epilogue's open house, like Brenda?
2. ~~The epilogue could nod to him.~~ Done: `epilogue.json` gives him a beat per ending (the terrarium goes wherever your nightstand goes and gets the cake stand at the shared dinner; the cheese wheel arrives on Valentine's Day; sourdough bread night with Dan's butter; sonnets called 'Bleach' delivered by Mrs. Pruitt's cats), plus a demolition beat.

Back to [[Game Design Document]] · Format: [[Dialogue Format]] · Cast: [[Lukey]] · [[Tyler]] · [[Wyatt]]
