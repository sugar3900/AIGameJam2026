---
tags: [design, story]
status: draft
---
# Story Overview (by day)

A skimmable map of what actually happens in the scripts (`Content/ICanFixHim/Data/Dialogue/*.json`), for spotting mistakes without reading every line. Cast pages: [[Lukey]] · [[Malcolm]] · [[Tyler]] · [[Wyatt]]. Format: [[Dialogue Format]]. Design: [[Game Design Document]].

**Structure:** 30 days told as **4 playable days**, one per week. Each morning starts with the *Creaky Floorboards* podcast (you can't talk to anyone until it ends). The player visits each guy once per day, which plays **one act per guy per week**; talking to him again that day gives his `today` line ("come back next week"). A skipped week rolls over: next time you get the act you missed (so skipping anyone means his Act 4 can't happen in time and the house fails). **Day 30** is Inspector Dan's final inspection, then the epilogue.

**Legend:** R = romance, F = friendship, X = friction. *(if …)* = conditional. ⚑ = flag. Stats run 0–20. Asides are clickable words that come back to the same line.

---

## Week 1 / Day 1: "Moving day"

### Podcast: Ep1 "The Catfish of Heartbreak Lane"
- 12 Heartbreak Lane is condemned, damp, and a young flipper just bought it. Dripping inside the walls at night. Bev: "A catfish. Enormous." Trish: "I think SHE'S being catfished."
- Listener mail (Tyler tease): an enormous shirtless young man with a bright pink pompadour, pink all over, saluting from the bathroom window, then gone. "A military salmon." She did not salute back.

### [[Lukey]] Act 1: "I'm THE leaks."
- **Appears:** kitchen; a gush from under the sink and he slides out on the wave (wet copper curls, beard, soaked white tank top with a red valve, copper-pipe limbs with duct tape).
- **Beats:** "Oh, great. Another one." Flipper roast: gray paint, LIVE LAUGH LOVE, "sell it to a couple called Jasper and Pip". "Not A leak. THE leaks. I'm a franchise." "You're not just flipping a house. You're flipping ME." House rules: "You fix something, I break something." The deadline: "Bulldoze. As in BULLDOZER." The dehumidifier arrives: "a little white plastic assassin with a carry handle."
- **Choices:** open: "It's my house now" X+1 · "rude for a water stain. Cute" R+2 · "fixing what's broken" F+1 R+1 → price: "mortgage and then some" X+2 · "Everything I've got" F+2 R+1 · "always this grumpy?" R+1 X+1 → rules: "Game on" R+1 X+1 · "something that works for both of us" F+2 R+1 ⚑`lukey_both` · "call a plumber" X+2 (water in the face) → deadline: "Watch me" R+1 · "Then help me" F+1 · "I'm good with my hands" X+1 (he flinches: hint) → dehumidifier: "dry out your walls" X+1 · "help with the damp" F+1 · "Jealous?" R+1 X+1.
- **Topics:** `franchise` (F+1; HQ = sink, penthouse = bathroom ceiling, summer home = east wall, vacation home = hall radiator) → aside `Gerald` (dead moth, "since the first Bush administration. He's thriving.").
- **First touch:** she slips in his puddle; he lunges and catches her: one second of cold wet arm around her waist, then just water. "Can't even touch me. Good."
- **Sfx:** WaterSplash, TapDrip, PipeClank, Hum, Squelch.
- **Cross-refs:** none named. Borderline: "Last flipper wanted everything white... Lasted one day." (Tyler, unnamed; designer deciding).
- **Today:** "I'm a leak, not a talk show... Not that I'll be counting the days. I will be."

### [[Malcolm]] Act 1: "Ugh. Light."
- **Appears:** bedroom walk-in closet; the mold wall shivers and he unfolds from the plaster (ivory, black clovers, shoulder-length black hair, open moss-and-black coat, bare chest).
- **Beats:** "I don't compose, madam. I DEcompose." Keeps the bed between them "as a matter of etiquette". "I'll watch over your slumber... in a candlelit way." "Nobody bleaches Pompeii." / "Pompeii WISHES it were in your bedroom." "Everyone in this house is dead... Dead inside. Dead tired. Dead gorgeous, one or two." "I am not a 'fun guy.' I'm a fungus." Dehumidifier: "a guillotine with a water tank", hums in B-flat, "the key of funerals".
- **Choices:** open: "So dramatic. I kind of love it" R+2 · "Are you okay?" F+2 · "Health hazard. Out." R+1 X+1 → intentions: "walk-in... selling point" X+2 · "You're a lot" F+1 R+1 · "Convince me" R+1 F+1 → dead: "Okay, goth" R+1 · "Are YOU dead?" F+1 · "crawled through scarier" R+1 (Tacoma raccoons: "Was it handsome?") → dehumidifier: "dry this house out" X+1 · "just an appliance" F+1 · "scared of an appliance?" R+1.
- **Asides:** `chartarum` (Latin "of paper"; he gestures at the top-shelf shoebox, then stops) · `rot` (F+1; "Banana", forty pages, thirty-nine dramatic pauses) · `bleach` (a 2011 tenant; "I lost an entire stanza of myself") · `dead` ("Dead ringer for Mr. Darcy").
- **First touch:** none. She reaches to brush plaster off his lapel; he recoils into the coat hangers: "Don't touch the art. I'm toxic... on a government list." Bows instead.
- **Sfx:** DoorCreak, Squelch, Hum, DoorLatch.
- **Cross-refs:** none named. Borderline: "full of gentlemen who have overstayed their welcome. By decades." / "Dead gorgeous, one or two."
- **Today:** "My quota of human contact is exhausted."

### [[Tyler]] Act 1: the ally
- **Appears:** the 1957 floor-to-ceiling pink bathroom; the tile shimmers and he steps out of the wall (huge, shirtless, tiled pink with white grout, pink pompadour, pink gym shorts, white socks, pink high-tops). One cracked tile by the tub.
- **Beats:** "Ma'am. Thank God. A professional." Tyler Whitmore, "Of the Whitmores": towers in gold. "Pepto-Bismol... like standing inside a flamingo's mouth." "Rip it out. White. Subway. Basic. SELL." Father: "Never fall in love with a property." Push-ups on the bath mat: "It's been tiled at considerable expense." Salutes the dehumidifier ("the only disciplined thing in this house"); nobody salutes back, "not the woman next door with the crossbow."
- **Choices:** "speaks flipper" R+2 · "Bold words from a man with pink hair" R+1 F+1 (it was rose quartz; now it matches the tile) · "kind of charming" F+1 X+1 ⚑`tyler_no` → numbers: "That's the dream" R+1 F+1 · "fire a NANNY?" F+2 (eleven nannies; `seen.v1_nanny` pays off in Act 4) · "What about the people in it?" R+2 → PT: "what are YOU?" F+2 · "Need a spotter?" R+2 · "Put a shirt on, soldier" F+1 X+1 ("I don't OWN a shirt") → dehumidifier: "salute a dehumidifier?" F+1 · "adorable at attention" R+2 · "back to MY bathroom" X+2.
- **Asides:** `Whitmores` (F+1; Fort Bellamy Military Academy) · `reassignment` ("Classified"; rubs the back of his head) · `subway` (R+1; "love is for spaniels").
- **First touch:** "Watch your step, ma'am. The floor's slick." She wobbles and grabs his forearm: cool glazed tile for one second, then her fingers sink through like cold bathwater. The floor is bone dry. (Optional earlier: she rests a hand on the cracked tile and he flinches.)
- **Sfx:** TileCrack, Thud, Hum, WaterSplash.
- **Cross-refs:** none. Borderline: `today` says "I'm not jealous of wherever you're going next. I'm keeping a LEDGER."

### [[Wyatt]] Act 1: "Wire it wrong."
- **Appears:** living room; the fuse box pops and he tumbles out patting out a fire on his singed coat sleeve (round copper glasses crooked, braided red/copper/grey cable forearms).
- **Beats:** "Is this the doorbell?" (there is no doorbell). "Like 'wire it.' Like, wire it wrong." Forty-one theories (a surge; the millennium bug; #41 is a sad lightbulb). The budget: $40k rewire quote, $11k in the bank, "the minimum to scrape past"; the lamp sighs. Fuse box labels KITCHEN?, LOUNGE (PROBABLY), DON'T, MYSTERY. The dehumidifier is on the dodgy stairs socket: "I relate to the screw."
- **Choices:** "kind of electric" R+2 · "reason my lights flicker?" F+1 · "set my wall on fire" X+1 → "a surge with an Australian accent?" F+2 · "you're cute" R+2 · "I'm on a schedule" X+2 → budget: "What do you actually think?" R+1 F+1 ⚑`wyatt_asked` · "help me cut corners" X+1 · "be my assistant" R+2 → fuse box: "glasses keep sparking. Cute" R+2 · "Who writes DON'T?" F+2 · "live in a cupboard" F+1 X+1 → socket: "I'll move it" R+1 F+1 · "worried about a dehumidifier?" F+1 · "It stays" X+1.
- **Asides (all F+1):** `wrong` ("Have I got teeth?") · `theories` · `inspector` (Dan: "Windbreaker, moustache, clipboard." "Does he look behind the faceplates? ...The friend is the wiring.") · `MYSTERY` (it rang a doorbell they don't have).
- **First touch:** both reach for the lamp switch, fingertips meet, ZAP. Hair on end, "like dandelions". "Can I call you {player}? Is that... alright?"
- **Sfx:** Spark, Zap, Hum, Sizzle.
- **Cross-refs:** none.
- **Today:** "I'm a fuse box, not talkback radio."

---

## Week 2 / Day 2: "One week later..."

### Podcast: Ep2 "Something in the Walls Is Singing"
- Mrs. Pruitt next door (82, nine cats, one crossbow): Bon Jovi in the walls, "Very flat. Very confident." (Lukey).
- Wyatt tease: the porch light comes on for her and flickers back; it hums "something about partying like it's a certain year" and dips at the year. "Electric catfish." "That's an eel."
- Teases a very special guest next week.

### [[Lukey]] Act 2: "Strictly professional" → the fight
- **Openers:** *(if ⚑`lukey_both`)* "You said 'both of us.' ...I thought about it a LOT." · *(if X ≥ 4)* "I flooded your shoes twice this week. ...Truce. For today."
- **Appears:** kitchen; a heart-shaped damp patch that grows when you walk in and shrinks when you look. Nickname: "boss".
- **Beats:** "You patched the bathroom. I can't feel my left side." "I'm in the HYDRANGEAS now. I'm MULCH." "Since 1986. Er— since INSTALLATION" (humming *Livin' on a Prayer*, a Running Man). The east wall together, Kevin the wasp; "the most romantic plumbing you have ever done". "I'm... concentrated. Like an orange juice." The coffee pot fills itself; "In my day we called this 'grabbing a milkshake.' ...In my day?" **The realtor call:** rip out the kitchen, white cabinets, gray floors → every tap on: "WHITE CABINETS? Why don't you paint the whole place Swiss Coffee!" "Something happened in this kitchen. I don't know what. But it MATTERED." Then days of silence.
- **Choices:** "Is that patch a heart?" R+2 · "least fish-like thing" R+1 F+1 · "dehumidifier's doing a great job" X+1 → "how does a leak know Bon Jovi?" F+1 R+1 · "1986? Weirdly specific" F+1 · "Show me where" R+1 F+1 → "You look good concentrated" R+2 · "Does it hurt?" F+2 R+1 · "Two down, two to go" X+1 → "Is this a coffee date?" R+2 · "a kitchen I don't have to fix" F+1 R+1 · "onto the next one" F+1 X+1 · *(if any other R ≥ 5)* "not the only guy who's been sweet to me" R+1 F+1 → **fight:** "everything I own is riding on this" F+1 X+1 · "Houses are investments" X+3 · "You're right. Spreadsheet." R+1 F+1 X−1.
- **Asides:** `catfish` (R+1; "I'm wet in a SEXY way.").
- **Sfx:** TapDrip, Hum, WaterSplash.
- **Cross-refs (2):** "WYATT'S! DON'T!" at the wiring (narration) · optional jealousy "We're rival franchises" (names nobody).

### [[Malcolm]] Act 2: the poem and the quote
- **Openers:** *(if he was ordered out)* "I didn't go. But I thought about going. Twice. That's growth." · *(if X ≥ 4)* door note "NOT HOME. GO AWAY. WALK-IN, INDEED."
- **Appears:** the mold has grown into a heart with an arrow; he hides it behind his open coat. "That's a water stain with ambition." Now "my dear".
- **Beats:** "Ode to the Homeowner" ("Also thou hast a nice face. That is all I am hoping.") or the haiku "Damp. / Dark. / You." (missing a line "because I am also missing something"). "Damp romance." A colony: "One heart is for amateurs." The inspection: "I've never been reviewed before. Will he be harsh?" The hint: "Ask the electrician what year it is. Ask the tile boy when he last ate. Ask the leak why his hair never dries." Near-touch: he reaches to tuck her hair and stops an inch short. "Someone in this house is pining. ...It's me." Her cough + the remediation quote + her note "Or just prime over it?" → **"Can't you love a thing without fixing it?"**
- **Choices:** "Is that heart about me?" R+2 · "Read it to me" R+1 · "Only if it's short" F+2 → "beautiful" R+2 (a new clover blooms) · "doesn't scan" F+2 X+1 → *(if met any)* "Read me one about the others" R+1 F+1 · "No poems about anyone else" R+2 ("I've taken quite a lichen to you") · "a little weird" F+1 X+1 → "You say that about everything" F+2 (the toaster in 2014) · "trying to scare me?" R+1 · "dramatic for attention" X+1 → **fight:** "health hazard AND resale problem" F+2 X+1 · "Rot isn't character. It's damage." X+3 · "I can't breathe in here" R+1 F+2 X−1.
- **Asides:** `toolbelt` (R+1; "the most indecent object in this house") · `colony` ("Nine billion and four") · `pining` (F+1; "a love language").
- **Sfx:** Squelch, DoorCreak, DoorLatch.
- **Cross-refs (2):** the "electrician / tile boy / leak" line (always; all three by role) · optional poem "O leak, O tile, O nervous spark".

### [[Tyler]] Act 2: Operation Clean Slate
- **Openers:** *(if you just came from Lukey or Malcolm with R ≥ 6)* "Forty-one minutes... I counted the drips. Or the sighs." "We get LITIGIOUS." · *(if X ≥ 3)* "Temporary truce. Only because I need your crowbar." · *(if ⚑`tyler_no`)* "You called the tile 'charming'... I did my push-ups to it."
- **Beats:** battle plan on the bath mat with a pink soap, pink loofah and pink rubber duck ("The duck is you."); he can only move pink things. The test tile pops: "Ow." A tile-sized patch of skin on his ribs: "Sympathy pain." "Man down. Leave him." Behind it: **SET BY HAL FOR RUTHIE. JUNE 1957. SHE WANTED PINK. BUILT TO OUTLAST US BOTH.** Mud-set vs. gas-station adhesive. The day-30 inspection is "a parade. Boots, brass, bearing. I don't own boots." He salutes the mirror; nobody's in it. "I came in to film the before. I never got to the after."
- **Choices:** "Yes, sir" R+1 F+1 · "I'm in charge" R+2 X+1 · "Who made you general?" F+1 X+1 · *(if Lukey R ≥ 8)* "tell Pinky the penthouse says hi" R+1 F+1 → "Did that HURT you?" F+2 · "You flinched. Cute." R+2 · "Toughen up" R+1 X+1 → "somebody's home" F+2 ⚑`tyler_hal` · "good tile... better than yours" R+1 F+1 X+1 ⚑`tyler_no` · "Sentiment doesn't sell" X+2 (he puts the tile back anyway) → "the mirror didn't salute back" F+2 · "Your bearing is fine" R+1 F+1 · "not a parade" R+1 X+1 (his fingers pass through her shoulders) → "what happened to you?" F+2 · "Keep me company?" R+2 · "It's all coming out" X+2.
- **Asides:** `Operation Clean Slate` (the duck was requisitioned) · `tan` ("It's a GLAZE, ma'am.") · `mud-set` (F+1; "The way you know your own handwriting").
- **Sfx:** RubberDuck, TileCrack.
- **Cross-refs (2):** rival opener *(if)* · "Pinky" choice *(if)*: "He looked at my grout and said 'respectfully.'"

### [[Wyatt]] Act 2: "No worries." (There are worries.)
- **Openers:** *(if ⚑`wyatt_asked`)* "I've been thinking about that. A LOT a lot." · *(if X ≥ 4)* "I don't get upset. I get... slightly dimmer."
- **Beats:** tangled in an extension cord ("one of them checked me back"), humming the "certain year" song; a folded pink towel on the fuse box. "You're very grounding." The plan: 30-amp breakers on 15-amp wire + a "Greige Expectations" feature wall, "perfect for Dan on day thirty"; the lights go disco. Pushed, he explains: a breaker is "a smoke alarm for the wire". "Gary was always... Who's Gary?" Biscuits by the fuse box; "Theory fourteen: a really long-life light bulb." "I sound like a sparky... Where am I from?"
- **Choices:** "let me help untangle" R+2 (Zap) · "checking for what?" F+1 · "You look ridiculous" X+1 → plan: "The lights. What aren't you telling me?" F+2 R+1 · "Hand me the screwdriver" X+1 ⚑`wyatt_patch` · "You'd tell me, right?" R+1 → pushback: "the most useful thing anyone's said" R+2 X−1 ⚑`wyatt_pushback` · "properly AND cheaply?" F+2 ⚑`wyatt_pushback` · "the thirties go in" X+1 ⚑`wyatt_patch` → "most alive thing in this house" F+1 R+1 · clean his glasses R+2 ("the high-definition version") · "don't spark on my floor" X+1 → week: *(if any other R ≥ 8)* "a bit flirty around the house" (lamp browns out → "the lamp doesn't think it's fine" R+2 · "glad you're cool" X+1) · "Where are you from?" F+2 · "Busy" F+1 (ends) · "Why are you weird?" F+1 (a 1998 magazine: "ask about your pager").
- **Asides:** `a song` (F+1) · `towel` (Tyler's: "folded in thirds, Private. Like a flag.") · `grounding` (R+1) · `Greige Expectations` (F+1; "too scared to commit to being a color").
- **Sfx:** Zap, Hum, Spark, SwitchOn, Sizzle.
- **Cross-refs (2):** Tyler's towel aside · optional "flirty around the house".

---

## Week 3 / Day 3

### Podcast: Ep3 "The Inspector"
- Radio guest: Inspector Dan. "Never been inside. I go in once, on day thirty." "The only thing haunting that house is its water pressure." He phoned the owner about PERMITS (not coffee); stood on the sidewalk to look at the gutters and both shoes filled with water on a dry day ("That's the catfish, Dan").
- Malcolm tease: a man in a closet reciting forty pages of poetry about a banana. Dan: "A fungus among us!" Nobody laughs.
- **BIG STORM SATURDAY.** Next week: the library.

### [[Lukey]] Act 3: "It's not a date. (It's a date.)"
- **Appears:** ⚑`lukey_blackout` on entry: the power's out in this house only; from the fuse box, "That wasn't me!" (it was). Candles in the kitchen. Down to one sink (she did the radiator alone during the silence; Gerald's gone). Nickname: "sweetheart".
- **Beats:** "I wasn't sulking. I was RESTING." "I dripped on the dehumidifier. It didn't even notice. It's a DEHUMIDIFIER." The make-up: "a house isn't just walls and grout... Right now that's me, a wasp called Kevin and, unfortunately, you." Spaghetti by candlelight, "Purely coincidental"; water glasses filled to the same line. "I don't sing. I RESONATE." **First hand-hold** (brass rivets, cold). Radio: BIG STORM SATURDAY ("I don't like flooding. For leak reasons."). The window fog: "L +" → *"L + THE KITCHEN SINK + U (MAYBE)"*. "I like who I am when you're here."
- **Choices:** "fix it properly" F+2 R+1 X−2 ⚑`lukey_realfix` · "I missed you" R+2 X−1 · "I still have to sell it" F+1 X+1 → dinner: "It's a date. Sing for me" R+2 · "why do you know 80s stuff?" F+2 (leg warmers) · "You're terrible" F+1 R+1 X+1 (cracks a wine glass) · *(if any other R ≥ 7)* "I'm seeing other people too" R+1 F+1 → hand: "Hold on to it" R+2 (hearts) · "You're solid!" F+1 R+1 · "clammy" X+1 → storm: "together" R+1 F+1 · fish joke F+1 R+1 · "Pull yourself together" X+2 → window: "Finish it" R+1 F+1 · "stop writing on my windows" F+1 · "I'm staging this place" X+1.
- **Topics:** aside `Gerald` ("He's in a better place. The trash can.") · aside `table settings` ("some dinner I never got to?") · `Bon Jovi` (one-way, R+1; guitar solo with a ladle).
- **Sfx:** PowerDown, TapDrip, PowerUp, RadioStatic, Hum.
- **Cross-refs (2):** the blackout (Wyatt, unnamed narration) · optional "seeing other people".

### [[Malcolm]] Act 3: the diary
- **Openers:** *(if "It's damage")* "GONE TO SULK. BACK NEVER. ...Back now. Knock." (a villanelle rhyming damage with sandwich) · *(if ⚑`lukey_blackout`)* "Ode to a Man Serenading Pasta"; he and Lukey signed the **Damp Accord** against the dehumidifier ("mostly about dust").
- **Beats:** she measures for the remediation crew in a respirator. His will (darkness to the night sky, poems to the British Library). "Tell me what to do." The top shelf: "My reliquary... not mush room up there." The shelf collapses; the shoebox bonks her head. **PROPERTY OF RAVEN (KAYLEIGH)**; the real "Banana" (six lines, age 14); the drawing "MALCOLM ASHGROVE. My ghost boyfriend. Died 1847"; "THINGS MALCOLM WOULD SAY". "I was never even ALIVE. I'm a fourteen-year-old's imaginary boyfriend." June 2008: "I don't need Malcolm anymore. But I'm keeping him." "I wasn't a tragedy. I was a phase." → she's his **editor**. "Perhaps they're all just very committed to a look." Storm warning: "I'm a fungus with a conscience now. It's AWFUL."
- **Choices:** "hold the tape measure" R+2 · "you get to choose" F+2 · "Stop whining and hold the stool" R+1 X+1 → shelf: "I won't touch it" F+2 R+1 · "What's in it?" F+1 R+1 · "It's my shelf. Move." X+2 → reveal: "you're fan fiction" F+1 X+1 · "She loved you" R+2 · "Let's read the rest together" F+2 R+1 ("Polyamory is canon. Page forty-one.") → "Like the moon" R+2 · "good job for a phase" F+2 · "not really a poet" X+2 → ⚑`malcolm_diary` → "let me edit. Gently" R+2 · "keep the notebooks safe" F+2 R+1 · "fewer spores" F+1 R+1.
- **Asides:** `reliquary` ("NOT a shoebox from a mall") · `same` ("Like I'm a MOOD") · `Darcy` (the stolen hand flex, eighteen years).
- **First touch:** "let me edit" → he holds out a clover-knuckled hand and she takes it (hearts): "You touched the art. On PURPOSE." Optional; otherwise the first touch is Act 4's "It was you" (also optional) or the ending kiss.
- **Sfx:** DoorKnock, Whoosh, ShelfCrash, Bonk, RadioStatic.
- **Cross-refs (2):** blackout opener *(if)* · "they're all just very committed to a look".

### [[Tyler]] Act 3: the video
- **Openers:** *(if you just came from Lukey or Malcolm and either has R ≥ 10)* "Kitchen or closet. You smell like a sink. Or a sonnet." (312 tiles, counted twice) · *(if ⚑`lukey_blackout`)* by candlelight: "Power's out. Not my department."
- **Beats:** the tile remembers: chicken pox in 1964 (counted all 312), a ring in the soap dish in 1979, Kool-Aid pink hair in 1994, and a woman in 1987 who kept wine for a date that never happened (Brenda easter egg). **The video** (2024): "WORST BATHROOM IN AMERICA?! (Flip Day 1)", 312 views, a rose-quartz pompadour, "Whitmore Nation", "Watch your step, this tile is slick as—" CLONK. Comment: "is he ok" (two likes). "I'm not between engagements, am I." "I've been wearing my LEG-DAY SHORTS for two years. And the tank top... is now the BATHROOM." "Nobody salutes back because nobody can SEE me." He thinks his business is finishing the flip; his first ever request. Storm: "I'll be the chain."
- **Choices:** "falling for the tile" R+1 F+1 · "not who I thought" R+2 X−1 · "still coming out" X+2 → show the video F+1 · ask first F+2 · "internet famous" R+1 X+1 → ⚑`tyler_video` → "still you. Pompadour and all" R+2 · "I'm so sorry" F+2 X−1 · "312 views is not bad" F+1 R+1 → "I don't think that's your unfinished business" F+2 · "Take my hand" R+2 (hearts) · "Fine" X+2 → storm: "Together" R+1 · *(if !⚑`wyatt_spoke_up`)* "How's Wyatt?" F+2 · *(if ⚑`wyatt_spoke_up`)* "Wyatt finally spoke up" F+2, Wyatt F+1 · "scared of a little rain?" R+1 X+1.
- **Asides:** `chicken pox` · `date` (R+1; the 1987 wine) · `Whitmore Nation` ("All three hundred and twelve of them").
- **Touch:** his hand is solid now, "like glazed tile warmed by the sun" (hand-hold, or hands brush and he formally shakes yours).
- **Sfx:** RubberDuck, Bonk, RadioStatic.
- **Cross-refs (2):** jealous opener *(if)* · optional Wyatt choice ("my batman"; "Something about New Year's"). Plus the unnamed Brenda wine.

### [[Wyatt]] Act 3: "Who's Gary?"
- **Opener:** *(if ⚑`lukey_blackout`)* "The blackout. During Lukey's candle dinner. Wasn't me. ...It was me." "He said it in a very damp voice."
- **Beats:** the wall is warm and smells like toast (old rubber cooking); sparks follow his feet. Inside the wall: sticky-tape splices, a fossilized ham sandwich, "That's not insulation, Gary. ...Who's Gary?" *Heartbreak Lane Herald*, 2 January 2000, **"Y2K: NO CASUALTIES"**; small print: Wyatt Doyle, 26, of Wollongong. "They put me under the bug." Mr. Kowalski, four hundred tins of beans, a generator wired straight in by Gary; "Y2K was real. It just only happened to me." **He speaks up:** "Don't patch it. Please. Rewire it. Properly." "Who do you like? In the house. ...For the wiring." Radio storm bulletin: "People do silly things with generators." "I'm just a bloke who didn't say something."
- **Choices:** *(if ⚑`wyatt_patch`)* "It's the 30-amp breakers" F+1 · "Is my house going to catch fire?" F+1 R+1 · "Dan's never going to open a wall" X+2 → newspaper: "Take his hand" R+2 (zap turns to hum) · "You were a person" F+2 (his mum, reverse charges) · "Wollongong?" F+1 R+1 (the chicken shop) · "affect the budget?" X+2 → "So tell me" R+2 · "exactly like Gary" R+1 F+1 · "can't afford a rewire" X+2 → "We do it properly" R+2 F+1 X−2 ⚑`wyatt_realfix` · **"Kiss him"** R+3 ⚑`wyatt_realfix` (hearts; "like licking a nine-volt battery") · "I'll think about it" X+1 → who: *(if any other R ≥ 8)* "a thing with some of the others" (→ "okay to not be fine" R+1 F+1 · "Good." X+1) · "You." R+3 · "favorite weirdos" F+2 · "none of your business" X+2 → storm: "We'll do it right" R+1 F+1 · "Mrs. Pruitt's lending me her generator" F+1 · "scared of rain?" X+1.
- **Asides:** `toast` (F+1) · `bother` (R+1; he said sorry to a vending machine).
- **Sfx:** Spark, Sizzle, PowerDown, PowerUp, Kiss, RadioStatic.
- **Cross-refs (2):** blackout opener *(if)* · "Who do you like? In the house." (+ the conditional "some of the others" branch).

---

## Week 4 / Day 4: the storm (Saturday)

### Podcast: Ep4 "We Went to the Library"
- Microfiche, 1987: "Local aerobics instructor Luke Moretti, 34, died... when a cast-iron pipe fell on his head... before their first date." It was Brenda's house. "That's every man I've ever dated." "Most of them lived, Bev." No catfish.
- Wyatt tease: the 2 January 2000 paper is missing, "probably in somebody's wall."
- "The storm's here, listeners."

### [[Lukey]] Act 4: "Oh no. I'm a guy."
- **Appears:** kitchen floor, very solid, not grinning. *(if R ≥ 12)* he says **{player}** for the first time; otherwise "Sweetheart."
- **Beats:** ⚑`lukey_human`. "I'm not a leak. I'm a GUY. I'm a guy who died SHOWING OFF." Brenda, the mixtape, "Relax, babe. I'm great with my hands." Bonk. "I died in LYCRA... I was here for TWENTY MINUTES." "Thirty-nine years dressed as a SINK." "Malcolm KNEW." The storm: the dehumidifier fills in seconds (he looks at it with respect); "Lefty-loosey is how I DIED!" Fixed: no leaks, the dehumidifier clicks off, his curls dry for the first time since 1987: "The VOLUME." **The date:** an ironed see-through tank top, polished couplings, a mixtape "FOR ~~BRENDA~~ {you}", Bon Jovi.
- **Choices:** "you looked great in Lycra" R+2 ("Shiny. Teal.") · "You're a PERSON" F+2 R+1 ("DEFINITELY a Leo") · laugh F+1 X+1 → "I'll take you on that date" R+2 · "even if just as friends" F+2 ("A FRATE") · "focus on the sink" X+1 → "Talk me through it, instructor" F+2 R+1 · "I trust you" R+2 · "Step back" X+2 → date: dance R+2 · toast to Brenda F+1 R+1 (GlassClink) · check your phone X+1 (he steals a meatball) → **final choice** (see Endings).
- **Asides:** `Malcolm` ("'Thou art a dead man's tears.' I thought he was just being GOTH about it!") · `cast iron` ("We've been roommates this whole time.") · `ironed` ("Still see-through, though. That part's a choice.").
- **Sfx:** Bonk, Thunder, Rain, PipeClank, SwitchOff, GlassClink, Kiss, Whoosh, TapDrip.
- **Cross-refs (2):** "Malcolm KNEW" (+ aside) · "WYATT! STAY OUT OF THE KITCHEN! ...Love you, buddy!"

### [[Malcolm]] Act 4: the storm
- **Appears:** rain pours through the bedroom ceiling into the closet; "Mind the puddle. The puddle is also me." *(if R ≥ 12)* he says **{player}**, "like the first line of a poem"; otherwise "My editor."
- **Beats:** ENORMOUS, "spore-tacular", clovers joined into meadows; the full dehumidifier switches itself off. She can't stop coughing: "That's me, isn't it. In your chest." "Love isn't supposed to come with an inhaler." "It has to be tonight." The podcast vindicates him: "I SAID that. I said it in 2009." "Tell me what to do. One last time." The clean-out, **no bleach**; Raven's notebooks bagged and safe. Small and dry, clovers faded to grey freckles. "It was never the rot, was it. It was the stories." "I can't pass on. I was never alive."
- **Choices:** *(if ⚑`lukey_human`)* "You were right about Lukey" F+1, Lukey F+1 ("my mold-in-law") · "Focus" → "let me take care of you" R+2 · "What do YOU want?" F+2 R+1 (pottery, "Something DRY") · "Get in the bucket" R+1 X+1 → bleach: "No bleach. I promise." R+2 F+1 · hand him the sponge F+2 · "Industrial strength" X+2 (a full Victorian scream; it's dish soap) → "It was you. Rot or no rot." R+2 (dry hand on yours) · "Raven's stories are safe" F+2 · "Told you so" F+1 X+1 → **final choice**.
- **Asides:** `multitudes` ("Whitman. Or Raven. She wrote it on her pencil case.").
- **Sfx:** Thunder, Rain, Squelch, PowerDown, WaterSplash, ReactSurprise, Kiss, Whoosh.
- **Cross-refs (1–2):** the podcast line ("A man died under a sink") · optional Lukey follow-up (Bon Jovi through the wall).

### [[Tyler]] Act 4: "Did you just tell me NO?"
- **Appears:** holding the wall up with both hands while water runs behind the tile; tiles pop off and leave bare skin on him. *(if R ≥ 12)* "**{player}**! Report!"; otherwise "Ma'am! Report!"
- **Beats:** "I can feel every single one." "Let it go... white subway, four ninety-nine a square foot... Let the tile go, ma'am. Let ME go." Behind a fallen tile: SHE WANTED PINK. **She says no** (every path; "It's coming out" is a temptation she backs out of). "Nobody tells me no! Not eleven nannies, not Madame Fontaine, not Fort Bellamy!" All night: every tile she sets back reappears on him. "Hold the LINE! Not you, ma'am. The grout." The dehumidifier's light goes red: "It has no idea there's a war on." Dawn: he inspects the wall like a parade. "Let him bring TWO."
- **Choices:** *(if Lukey talked today)* "The kitchen was flooding. Lukey needed me." R+1 ("You went to the LEAK first") → *(if ⚑`lukey_human`)* "He found out he was a person" F+1 · "Right now it's you" R+1 · "I'm here" F+1 → **no:** "No, Tyler. It stays." R+2 X−1 · *(if ⚑`tyler_hal`)* "Hal built it to outlast them both" F+2 X−1 · "Stop giving orders and hold this" F+2 (he holds the mortar bucket) · "You're right. It's coming out." X+2 (all set ⚑`tyler_no`) → why: "because I love it. Including the part that argues" R+2 · "the real fix" F+2 · *(if `seen.v1_nanny`)* "I mean it" F+2 · "Because I said so" X+2 → the crack: gold seam R+2 · let him set the last line F+2 · slap on grout X+1 → dawn: salute him F+2 ("Somebody saluted back.") · kiss his cheek R+2 (hearts) · "a keeper" R+1 → **final choice**.
- **Asides:** `single one` ("Like losing teeth. Very small, very pink teeth.") · `the grout` (R+1; his own drill sergeant since thirteen).
- **Sfx:** Rain + Thunder (node), TileCrack, Thud, Hum, Squelch, Kiss.
- **Cross-refs (1):** the Lukey jealousy *(if)*. Plus the friend-ending card's vanity light (Wyatt, implied).

### [[Wyatt]] Act 4: "NO."
- **Appears:** power out since breakfast; the only light in the living room is Wyatt, glasses glowing. *(if R ≥ 12)* "**Love.** Sorry, that slipped out. No. It didn't slip."
- **Beats:** water under the back door; the sump pump needs power. Mrs. Pruitt's generator (crossbow sticker) and an old orange cord labeled GARY; she heads for the dryer socket: exactly New Year's Eve 1999. **"NO."** Every light blazes with no power (⚑`wyatt_spoke_up`). Backfeed explained (the lineman up the pole; "the house goes up like a Christmas tree. With you in it."). The fix his way: the pump on its own lead, generator outside. "It's so QUIET." "I used to spark. Now I just... have hands." "I said no to Tyler too... He's never called me anything but Private before." Then the second thing: "I'm mad about you" or "I'm a one-person bloke."
- **Choices:** "Wyatt. Say it." R+2 · "What would you do?" F+2 · "I'm plugging it in" X+2 (all lead to NO) → "You were right. Thank you." R+2 X−2 · "Bossy. I like it." R+2 · "Don't you dare shout at me" X+2 → "Dan's going to love this" F+1 · "Calm looks good on you" R+1 → "Say anything" R+1 · *(if any other R ≥ 8 or ⚑`lukey_blackout`)* "me and the others?" F+1 (→ *(if ⚑`lukey_blackout`)* "the blackout?": "Sorry about the dinner. Not sorry about the feeling.") → "so proud of you" F+2 · "Say all of it" R+2 · "Only took you 27 years" F+1 X+1 → **final choice**.
- **Asides:** `Mrs. Pruitt's` (F+1; "Why does a generator need a crossbow sticker?") · `transfer switch` (R+1; "I'd marry it.").
- **Sfx:** Thunder, Rain, WaterSplash, Zap, PowerUp, FixComplete, SwitchOn, Kiss.
- **Cross-refs (2):** Tyler "insubordinate" (always) · optional jealousy (with the Lukey blackout confession).

**After an ending** (visiting a fixed guy): a one-line `after_*` beat per ending (e.g. Lukey moved the dehumidifier to the garage; Malcolm's terrarium has "Eleven poems since breakfast"; Tyler: "Count my push-ups"; Wyatt: "I told the kettle it boils too loud").

---

## Day 30: inspection and epilogue

### Final inspection (`inspection.json`)
- Plays when you go to bed in week 4. Dan's **first and only visit** ("First time inside. I've read the file, I've heard the podcast, and I've dressed for it": brand-new waterproof shoes).
- **Pass** only if all four are fixed (`housefixed`). A pun per room: kitchen "turned the tide"; closet "No fungus among us... spore-adically"; living room "A real watt-ershed moment"; bathroom "I'll tile it again: she's a keeper". "My shoes are dry. I almost feel cheated."
- **Fail:** he walks to each broken room in order (kitchen → bedroom → bathroom → living room): the sink floods his shoes ("a pipe dream"); the closet sighs ("funnier on the radio"); two tiles come away ("Tile be honest"); the wiring sparks ("I don't have a pun for that one"). He recommends demolition.

### Finale podcast: Ep5 "Case Closed (Mostly)" (pass only)
- Live from the porch. Everything fixed; "Dan called it a keeper." The owner: "It's complicated." Dan's waterproof shoes stayed dry. Bev: "Never trust a man who says he's great with his hands." A bucket of water soaks Bev.

### Epilogue (`epilogue.json`)
**Pass:** City Hall hearing, four minutes. Dan: "as dry as my sense of humor, and twice as well grounded." Mrs. Pruitt fires a celebratory crossbow bolt into the ceiling. If Lukey stayed, he's on the counter: "What are we doing with it?"
1. **House choice** (⚑`house_choice` 1 sell / 2 stay / 3 demolish), with Lukey's beat:

| | Lukey stayed | Lukey gone (one-line keepsake per ending, then...) |
|---|---|---|
| **Sell** | Brenda (late sixties) at the open house: "A young man once tried to fix this sink for me." He hides in the radiator for six hours, cries the whole drive (wipers on inside the car); the new tap drips: "A man's gotta make an entrance." | Brenda at the open house: "I hope he's somewhere nice." Not Jasper and Pip. The kitchen never leaks again. |
| **Stay** | The dehumidifier is banished to the garage. Dan drops by socially; his shoes get soaked every time. "No he isn't." | Dan comes to Sunday dinner in waterproof shoes that stay dry. Faint Bon Jovi from the walls. |
| **Demolish** | You take the sink; he naps in it like a cat. The park fountain drips: "That's not me." | The lot becomes a park; Dan cuts the ribbon ("breaking ground"); the fountain never stops dripping. |

2. **Roll call** (one beat each by ending): **Malcolm** terrarium + poem "Dry", dehumidifier banned from the bedroom in the lease / Wisconsin blue every Valentine's Day / sourdough "Sorrow, Rising", Thursday bread night, Dan brings butter / Mrs. Pruitt's shed, cats deliver sonnets called "Bleach". **Tyler** (stayed, house kept) "I'd like the whole house pink." "No." "Outstanding." / (stayed, house sold or demolished) the gold-seam tile in bubble wrap above your new sink / you salute pink bathrooms / 0500 hospital corners / the crooked tile clicks back. **Wyatt** (stayed, kept) the fuse box giggles at Dan's pun / (stayed, moved) "Was it a Gary?", rewires the new place / the porch light flickers twice / the chicken shop's good day / his note on your fridge.
3. **Close:** 2+ romances → **Sunday dinner** (one line per guy who stayed: Lukey "I'm your favorite. Don't answer that."; Malcolm on a cake stand, poems all called "Also"; Tyler's LEDGER, "goodnight to me SECOND"; Wyatt "You can check the lamp."; Dan can't see half the table and brings butter) · 1 → "the two of you, a dehumidifier nobody likes" · 0 → a tap drips, a light flickers, a cat brings a sonnet. Then: "Four very stubborn men. (Three men and a fungus.)"

**Fail:** the hearing (Dan recommends demolition; Mrs. Pruitt fires in protest), then a last walk room by room: unfixed (a frowning damp patch; "ODE TO THE WRECKING BALL" in spores; the foreman salutes the pink tile; the lights stay on after the power's cut, then go out "like somebody saying sorry"), stayed with you (the sink; the terrarium in the passenger seat; the gold-seam tile; Wyatt in your new wiring: "Not sorry. Sad."), or gone. The lot becomes a park whose fountain hums Bon Jovi. "It's a nice park. It's not a home."

---

## Endings
The final choice shows every option the player has earned; "That's your call" always shows (one version).

### [[Lukey]]
| Ending | Title | How | Summary |
|---|---|---|---|
| `romance_success` | Head Over Heels Over Pipes | R ≥ 16 & X < 8: "Stay. With me. I'm in love with you." | Kiss, fade. Dry, ENORMOUS curls; fills your coffee pot every morning; the dehumidifier lives in the garage. |
| `romance_failure` | Love You to the Last Drop | R ≥ 16: "I love you. That's why you should go." | "You deserve a guy with a pulse. And a dry floor." A heart-shaped drop that never dries. |
| `friend_success` | Pipe Dreams Come True | F ≥ 14 & X < 8: "Go. You got your date." · or "your call" with X < 8 | "Best frate of my afterlife." Gone in warm steam that smells of copper. |
| `friend_failure` | Fixed It Myself (Mostly) | "your call" with X ≥ 8 | "...a woman who still calls my home an 'asset.'" Window fog: "YOU HELD THE FLASHLIGHT." |

### [[Malcolm]]
| Ending | Title | How | Summary |
|---|---|---|---|
| `romance_success` | Terrarium Ever After | R ≥ 15 & X < 8: "Move into a terrarium on my nightstand." | A respectable fungus in a small cap; a poem a day; poem "Dry" is her name. |
| `romance_failure` | Blue for You | R ≥ 15: "Go somewhere your rot is adored." | A Wisconsin cheese cave, "finally cultured"; a wheel with a poem every Valentine's Day. |
| `friend_success` | Bread Poets Society | F ≥ 13 & X < 8: "The kitchen needs a sourdough starter." · or "your call" with X < 8 (his first ever choice) | A sourdough starter with a JOB; Raven's diaries archived; Thursday bread night. |
| `friend_failure` | Rot in Peace | "your call" with X ≥ 8 | Mrs. Pruitt's shed, growing on her crossbow case; a forty-page poem "Remediation" that just says "no". |

### [[Tyler]]
| Ending | Title | How | Summary |
|---|---|---|---|
| `romance_success` | Tile Death Do Us Part | R ≥ 16 & X < 8: "Stay. That's an order." | "That's another no." Fell for the property AND the owner. Gold seam; you count his push-ups. |
| `romance_failure` | Tile We Meet Again | R ≥ 16: "I love you. That's why I'm letting you go." | Told no and loved anyway; a kiss, a returned salute, a gleam like rose quartz. |
| `friend_success` | Grout Expectations | F ≥ 14 & X < 8: "You're a good man... Dismissed." · or "your call" with X < 8 | "Somebody saluted BACK. Log it TWICE." The vanity light stays on for a week. |
| `friend_failure` | Grout of Here | "your call" with X ≥ 8 | "You kept it for the inspection." One spiteful crooked tile, the best in the house. |

### [[Wyatt]]
| Ending | Title | How | Summary |
|---|---|---|---|
| `romance_success` | Watt a Keeper | R ≥ 16 & X < 8: "Stay. With me. I love you, Wyatt." | Kiss, no zap; "That's me wanting something, out loud." Says no once a day. |
| `romance_failure` | Yeah, Nah | R ≥ 16: "Go home. Go find your chicken shop." · or "Stay. With me." with R ≥ 16 & X ≥ 8 (his loving no) | "I love you too. Said it first go." The porch light flickers twice when you come home. |
| `friend_success` | Current Besties | F ≥ 14 & X < 8: "Go. You've earned it." · or "up to you" with X < 8 | "Best mate I've ever had." DON'T relabeled DONE. |
| `friend_failure` | No Worries (Some Worries) | "up to you" with X ≥ 8 | "...someone who only asks what I think when the house is on fire." A note on the fuse box. |

Everyone switches to a name in Act 4 at R ≥ 12 (Lukey, Malcolm and Tyler say `{player}`; Wyatt says "love").

---

## Flags and cross-script dependencies

| Flag / read | Set by | Read by |
|---|---|---|
| ⚑`lukey_both` | Lukey A1 ("both of us") | Lukey A2 opener |
| ⚑`lukey_blackout` | Lukey A3 (on entry: the blackout) | Malcolm A3 opener (serenade, Damp Accord) · Tyler A3 opener (candlelight) · Wyatt A3 opener ("It was me") and A4 jealousy confession |
| ⚑`lukey_human` | Lukey A4 reveal | Malcolm A4 ("mold-in-law", Lukey F+1) · Tyler A4 ("Pipes don't know Bon Jovi") |
| ⚑`wyatt_spoke_up` | Wyatt A4 "NO." | Tyler A3 storm choice (variant) |
| ⚑`wyatt_asked` / `wyatt_patch` | Wyatt A1 / A2 | Wyatt A2 opener / A3 "It's the breakers" |
| ⚑`tyler_no` / `tyler_hal` | Tyler A1–A4 / A2 | Tyler A2 opener / A4 "Hal built it" choice |
| ⚑`house_choice` | Epilogue | Epilogue (Tyler/Wyatt "home" vs "moved" beats) |
| Set but never read | ⚑`lukey_realfix`, `malcolm_diary`, `tyler_video`, `wyatt_pushback`, `wyatt_realfix` | (nothing yet) |
| Stat reads | Jealousy: Lukey reads others' R ≥ 5 (A2) / ≥ 7 (A3); Tyler reads Lukey/Malcolm `talkedtoday` + R ≥ 6 / ≥ 10 and Lukey R ≥ 8 ("Pinky"); Wyatt reads any other R ≥ 8; Malcolm's poem reads `met` | |
| Endings | Every hunk's `ending_*` | Inspection (`fixed` per room, `housefixed`) · Ep5 (`housefixed`) · Epilogue (every beat) |

---

## Things to check
1. **Lukey A1, "Last flipper wanted everything white... Lasted one day."** An unnamed Tyler reference in week 1. Left as is; designer's call.
2. **Two more week-1 borderlines, same kind:** Malcolm A1 "full of gentlemen who have overstayed their welcome... Dead gorgeous, one or two" (deliberate in his bible; nobody named), and Tyler's `today` line "I'm not jealous of wherever you're going next" (abstract jealousy). Also, podcast ep1's Tyler tease plays on day 1 by design.
3. **Blackout timing (week 3).** Lukey's A3 sets ⚑`lukey_blackout` and ends with the lights back on. If you see Lukey first, the other guys' A3 openers play the same night: Tyler's says the power is *still* out; Malcolm's says "The night the lights went out..." and that he and Lukey "have since signed" the Damp Accord; Wyatt's says it happened "during Lukey's candle dinner". Malcolm also says he heard Lukey *sing*, which only happens on some of Lukey's choices.
4. **An Act 3 that rolls over into week 4** still plays the "BIG STORM SATURDAY" forecast on the day of the storm. Tyler's `v3_wyatt_spoke` variant can *only* appear in that case (Tyler A3 in week 4 after Wyatt A4), and it talks about the storm in the past tense in the same node as the forecast.
5. **Lukey's curls after his romance ending.** A4 and his ending card say he's dry and his curls are dry and ENORMOUS; the epilogue has "copper curls still dripping" (`intro_together`) and "dripping onto the tablecloth" (`fh_lukey`). The model has wet curls, so pick one.
6. **"Since 1986"** (Lukey A2) vs. dying in 1987 (A4, ep4). Intended slip or typo?
7. **Ep4's Wyatt tease comes after his reveal.** On a normal run Wyatt's newspaper is found in week 3, so "the January 2000 paper is missing" lands as a callback, not a hint.
8. **Lukey A3: "Did you hear the podcast? Mrs. Pruitt... Bon Jovi."** That was ep2 (last week); the morning of A3 is Dan's ep3. Also A2 ends "for the next few days the house is silent" and A3 says "silent for three days", but the acts are a week apart.
9. **Dan before day 30.** Ep3 has him on the sidewalk outside the house looking at the gutters (his shoes fill up). The devlog approves it as the waterproof-shoes setup, but it's technically a trip to the house; Wyatt's day-1 aside also has the heroine describing his windbreaker and moustache though she's only phoned him.
10. **Inspection pass: "Seventy years old and not a crack in her."** Tyler's fix mends the crack with a gold seam (or lumpy grout); the crack is still visible.
11. **Malcolm A3:** "The remediation crew comes after the storm", but she does the clean-out herself in A4. That's fine if intended (he asks for it tonight), but worth a glance.
12. **Flags with no reader:** `lukey_realfix`, `malcolm_diary`, `tyler_video`, `wyatt_pushback` and `wyatt_realfix` are set and never read. The GDD says later acts "call back to whichever reveals have happened"; only `lukey_human`, `lukey_blackout` and `wyatt_spoke_up` actually do.
13. **Bible inaccuracy:** [[Wyatt]] says ⚑`wyatt_spoke_up` is "Read by Tyler and Malcolm"; only Tyler reads it.
14. **Leftover internal IDs** from cut content: Lukey's `v4_aside_blazer` / topic `blazer` (the shown word is "ironed") and `v2_permits` (the coffee-date reply). Players never see them, but renaming them orphans Lukey's placeholder VO for those lines.
15. **Lukey's VO for the renamed dehumidifier nodes** (`v1_dennis` → `v1_dehum`, `v2_dennis` → `v2_dehum`): the old files `VO_lukey_v1_dennis_1` / `VO_lukey_v2_dennis_1` (and their `manifest.json` entries) no longer match, so those two lines are silent until `generate_vo.py` + `import_vo.py` are re-run.
16. **Tyler "since 2011"** (A2 opener: "first time anyone's disagreed with me since 2011") sits oddly with "never been told no and had it stick" and the eleven nannies. Minor.
