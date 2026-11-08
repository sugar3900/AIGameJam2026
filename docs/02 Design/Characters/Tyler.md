---
tags: [design, character]
status: draft
---
# Tyler: Pink Tile

**Room:** Bathroom (the 1957 pink tile wall) · **Glow:** `#FF7AB8`
**Script:** `Content/ICanFixHim/Data/Dialogue/tyler.json`

> **Tone: *Ghosts* (UK), American house.** Snooty, commanding, vain and jealous, with brief sincere moments that land and then go straight back to the bit. His death is a running joke, not a tragedy. Cutesy, never dark. Romance from minute one.

> **Voice:** old-money American with crisp military-school diction. Composed, clipped, snooty. "Ma'am." "Outstanding." "Carry on." "Noted. Logged." "That's an order." He's no longer British (the v1 prototype was). He never swears and never raises his voice except in ALL CAPS on one word. When he's flustered he gets *more* formal, not less.

---

## Who he is
**Tyler Whitmore, 27.** Heir to the Whitmore real-estate dynasty ("American royalty"): Whitmore Tower, Whitmore Plaza, Whitmore Grand, Whitmore Parking Structure B, all with the name in gold.
- Raised by **eleven nannies** (consecutively; they kept saying no to him, then they kept leaving), an etiquette coach (**Madame Fontaine**) and **Fort Bellamy Military Academy** from 13 (youngest cadet captain in its history; his father donated the gymnasium the same year, "unrelated").
- Crisp, proper, snooty. Gives orders. Says "ma'am." **Has always gotten his way and has never been told no and had it stick.**
- Father's first rule: *"Never fall in love with a property."*
- **Vanity: his pink hair.** *"It's ROSE QUARTZ. Hand-mixed by a colorist in Manhattan. That tile is Pepto-Bismol. We are not the same pink."*
- Calls Wyatt his **batman** (officer's orderly). Salutes Dennis. Salutes everyone. **Nobody ever salutes back.**

### How he died (2024)
He bought 12 Heartbreak Lane to flip it: Swiss Coffee white on every wall, white subway tile, a little wooden sign that says BREATHE, sell by Sunday. On day one he filmed a tour for his followers ("Whitmore Nation," 312 of them) of how hideous the 1950s pink bathroom was, and slipped on the tile he despised. Now he **is** that cracked, antique pink tile, which is the cruellest possible irony for him.

### What he believes (Acts 1–2)
He knows he's Tyler Whitmore. He refuses to accept that he's dead. He talks around it:
- *"Since my... reassignment."* · *"I'm between engagements."* · *"Temporary posting. Classified."* · *"It's been a very long weekend."*
- He knows he's somehow attached to the tile and hates it. He "feels it sympathetically."

### Hints he explains away (the player should get there first)
- **"Watch your step, ma'am. The floor's slick."** He says it every time she leaves. The floor is bone dry. (It's the last thing he said on camera.)
- He walks very carefully, the way people walk on a wet floor.
- He rubs the back of his head ("old polo injury"). Flinches when she touches the cracked tile; clutches his ribs when she pries one off ("sympathy pain, military training").
- Nobody salutes back: not Dan, not the mailman, not Mrs. Pruitt. "It's a very rude neighborhood."
- Her hand goes through his ("That one was a me problem. Don't log it.").
- He can only move pink things ("a condition of my posting"), so his Operation Clean Slate troops are a pink soap, a pink loofah and a pink rubber duck.
- He can't buy a windbreaker. "Long story. Very short shopping trip."
- Malcolm says he has "the pallor of the departed." ("I'm FAIR. I'm old money. We're all this color.")
- He holds a cracked phone like a sidearm.

### His reveal (Act 3): the video
She searches the address for the listing and finds **"WORST BATHROOM IN AMERICA?! (Flip Day 1)"**, posted 2024, **312 views** (one per tile: "even my audience is pink"). A sweaty, very alive Tyler: *"Behold: the ugliest bathroom in America... White. Subway. Basic. SELL. Watch your step, this tile is slick as—"* CLONK. The last frame is the ceiling. One comment: *"is he ok"*, two likes. Sets `flag.tyler_video`.

*"I'm not between engagements, am I. ... Nobody salutes back because nobody can SEE me. I'm the tile, ma'am. I'm the Pepto-Bismol."*

### The conflict
At first he's on her side, but worse: *"Rip it out. White. Subway. Basic. SELL."* He's her **temptation and her mirror**, because she flips for profit too ("You remind me of me. That ought to worry you more than it does."). Being the old tile makes him notice that it's mud-set on wire lath, handmade, has survived 70 years, and was **loved** by the families who lived here, in a way his cheap white flips never were ("I once lost a whole wall of subway in eleven months. The adhesive came from a gas station.").

The tile remembers the families: **Hal and Ruthie** (Hal set it in June 1957 and pencilled on the mortar *"SHE WANTED PINK. BUILT TO OUTLAST US BOTH."*), a girl with chicken pox in 1964 who counted all 312 tiles, a ring hidden in the soap dish in 1979, a teenager who dyed her hair pink in the sink with Kool-Aid in 1994, and a woman in 1987 who kept a bottle of wine for a date that never happened (Brenda, a hint at Lukey).

**His unfinished business is being told no, and loved anyway.** He thinks it's finishing the flip ("Rip me out, sell it, and I'm dismissed. Honorably."). The real fix is restoring the tile, which means telling him **"No, Tyler. It stays."** He's furious, then moved.

### Jealousy (the most jealous in the house, because he's vain)
He keeps a **ledger** of whose room she visited first and how long she spent there, and he sulks theatrically. It's comedic friction: it never locks content.
- **Week 1:** who she met before him (`lukey/malcolm/wyatt.talkedtoday`): *"You went to the KITCHEN first."* / *"You smell like a library that gave up."* / all three: *"Fourth. FOURTH. I'm the gift shop."* (Wyatt first is fine: "He's my man.")
- **Week 2:** if she's just come from a rival with romance ≥ 6: *"Forty-one minutes. I counted the drips. Or the sighs."*
- **Week 3:** if she's just come from Lukey or Malcolm and either has romance ≥ 10: *"You smell like a sink. Or a sonnet. I counted the tiles. Twice."*
- **Week 4:** if she went to Lukey first in the storm: *"The KITCHEN. During a CRISIS."*
- Repeat visits the same day: *"I'm not jealous. I'm keeping a LEDGER."*

---

## Relationships
| Who | Tyler on them | Them on Tyler |
|---|---|---|
| **Lukey** (The Leaks) | "A damp man in Lycra who insists he IS the plumbing." Lukey's "penthouse" leak dripped on Tyler's hair ("He looked at my grout and said 'respectfully.' It was NOT respectful.") Jealous of the Bon Jovi humming. | "The last flipper. Lasted one day." ("Slander. I lasted until lunch. Nearly.") |
| **Malcolm** (Black Mold) | Mutual disgust. "A mold with a vocabulary." "He's squatting in a teenager's FEELINGS." | "A man made of grout and contempt." ("CASHMERE and contempt.") "The pallor of the departed." |
| **Wyatt** (Faulty Wiring) | His batman. Fond, commanding, oblivious. "Good man. Nervous man. Good man." Wyatt does his lighting every morning and Tyler has put him in for a medal. | **Subtle, unrequited crush, never stated and never acknowledged by Tyler.** It shows only in narration: the vanity light brightens when Tyler glances at it; the fan comes on when Tyler praises him; in the friends ending the vanity light stays on for a week. Never a joke at Wyatt's expense. Tyler is straight and oblivious. |
| **Dennis** | "The only one in this house with any discipline." Salutes him. In the storm: "Hold the line, Dennis!" Field-promoted to Sergeant. | Hums. |
| **Inspector Dan** | Salutes the windbreaker, not the puns. "A disgrace to the windbreaker." Mild jealousy if she calls Dan sweet. | Can't see him. "Long-tile relationship." "Grout-standing specimen." "Tile be honest with you." "She's a keeper." |

---

## Arc (one act per week)
**Ghost rules / progression:** Act 1 her hand goes through him (cold bathwater). Act 3 his hand is solid ("cool and smooth, like glazed tile warmed by the sun"). Act 4 he can hold a bucket of mortar.

1. **Act 1 (week 1): the ally.** Jealous opener by meeting order. "Ma'am. Thank God. A professional." The plan: rip it all out. Choices: ally / tease his hair / call the tile charming (the first "no": `flag.tyler_no`). His numbers and Father's rule; the nanny story (`seen.v1_nanny`, called back in Act 4). Intelligence briefing on the housemates. Dennis salute. The handshake goes through him. "Watch your step. The floor's slick."
2. **Act 2 (week 2): Operation Clean Slate.** Openers: rival jealousy / "you called it charming" callback / grudge (friction ≥ 3). The battle plan in pink bath toys. She pries a test tile ("Ow." Sympathy pain). Behind it: *SET BY HAL FOR RUTHIE* (`flag.tyler_hal`). He starts noticing the craftsmanship. Dan doesn't salute back. Doing the numbers on the tub: "I came in to film the before. I never got to the after."
3. **Act 3 (week 3): the video.** Openers: rival jealousy / blackout callback (`flag.lukey_blackout`). The tile remembers the families. She finds the video; the reveal (`flag.tyler_video`). He decides his business is finishing the flip and makes his first ever request. First hand-hold. Storm warning; Wyatt (with a `flag.wyatt_spoke_up` variant: he ordered Wyatt to keep the bathroom fan running through the storm and Wyatt said NO; "I called him insubordinate." "He was right. I'll tell him. In a memo.").
4. **Act 4 (week 4): the storm.** Uses her real name if romance ≥ 12. Rain behind the wall; tiles popping off ("I can feel every single one"). Jealousy if she went to Lukey first (with a `flag.lukey_human` variant: "That explains the LYCRA."). He orders her to let it go: "Let the tile go, ma'am. Let ME go." She tells him **no** (all paths get there; the "rip it out" choice is a temptation she backs out of). He's furious ("I have never been told no in my LIFE."), then moved. They save the wall all night with the whole house helping. The cracked tile gets a **gold seam** (like the towers, except nobody paid for it), or he sets the last line himself, or it gets slapped with grout. Dan: "She's a keeper." She salutes him: "Somebody saluted back." The final choice.

---

## Relationship tuning
Stats run 0–20, clamped. Same thresholds as [[Lukey]]. Simulated random play: median romance 15, friendship 16, friction 7. A consistently romantic player ends at romance 20, friction ≤ 1; a consistently friendly player at friendship 20, friction 0; a consistently rude player at friction 20.

| Option at the finale | Shown when | Ending |
|---|---|---|
| "Stay. That's an order. I'm keeping you too." | romance ≥ 16 and friction < 8 | He stays |
| "I love you. That's why I'm letting you go." | romance ≥ 16 | He goes, loved |
| "You're a good man, Tyler Whitmore. Dismissed." | friendship ≥ 14 and friction < 8 | He goes, friends |
| "That's your call, Tyler." | always (one version shown) | friction < 8: friends · friction ≥ 8: grumpy |

## Endings
| Ending | Title | Outcome |
|---|---|---|
| `romance_success` | **Tile Death Do Us Part** | "That's another no. To me leaving." Father said never fall in love with a property; he fell for the property AND the owner. Fade: *The bathroom was pink. So was everything else.* "I still think it looks like Pepto-Bismol. ...I love it. Tell no one." |
| `romance_failure` | **Tile We Meet Again** | Told no and loved anyway, he's free. A kiss, a salute, she salutes back: "Somebody saluted back." Gone, leaving a gleam on the gold seam, like rose quartz. |
| `friend_success` | **Grout Expectations** | "Dismissed. Honorably." Salute returned. "Tell Wyatt he's promoted. Tell Dennis he's in charge." He marches into the morning light and doesn't look down once. |
| `friend_failure` | **Grout of Here** | "You kept it for the inspection. I know the difference. I'm a Whitmore." He leaves furious and moved; one bottom-row tile clicks crooked out of spite. It's the best tile in the house. |

Every ending restores the tile: the house is only fixed for real if it's restored, not replaced.

## Flags
- **Sets:** `flag.tyler_video` (Act 3 reveal), `flag.tyler_no` (each time she tells him no: Act 1 "charming", Act 2 "better than anything you'd put up", Act 4), `flag.tyler_hal` (Act 2, read in Act 4).
- **Reads (optional flavour):** `flag.lukey_blackout`, `flag.lukey_human`, `flag.malcolm_diary`, `flag.wyatt_spoke_up`, `lukey.romance >= 8` (the "Pinky" choice), `lukey/malcolm.romance` and `lukey/malcolm/wyatt.talkedtoday` (jealousy).
- **Cross-stat effect:** `wyatt.friendship +1` when she brings up Wyatt speaking up.

## Open questions
1. His `look` in the JSON is still the v1 prototype (brown pompadour, push-broom mustache, pink sweater vest). It should become rose-quartz hair, clean-shaven, a navy blazer with a crest and mirror-shined loafers.
2. Does Wyatt's script ever show Tyler's reaction to Wyatt's crush? (Canon: no. Tyler never knows.)
3. ~~Should Tyler's video appear in a podcast episode?~~ No (it's his Act 3 reveal). The podcast only teases him: in ep1 a listener sees a man in a navy blazer saluting from the bathroom window, then nobody's there.

Back to [[Game Design Document]] · Format: [[Dialogue Format]]
