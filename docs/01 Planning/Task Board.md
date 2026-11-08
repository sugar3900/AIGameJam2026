---
tags: [planning]
---
# Task Board

## Todo
- [x] Week flow: 4 playable days (bed ends the day), radio podcast each morning, daylight → dusk, week 1 must-meet rule, final inspection → epilogue → keepsake → title
- [x] Name entry at New Game (fills {player})
- [ ] Update the fallback `look` blocks (colours + props, used only if a model is missing) in all four scripts to match the 3D models: **Lukey** big bearded redhead, wet chin-length copper curls, copper-pipe limbs with duct tape, soaked white tank top with a red valve wheel, denim cut-offs, work boots; **Tyler** huge shirtless bodybuilder tiled hot pink with white grout, hot-pink pompadour, pink gym shorts, white socks, pink high-tops; **Malcolm** gaunt, pale ivory with black mold blotches, long black wavy hair, open moss-black coat over a bare chest, cropped trousers, ankle boots; **Wyatt** slight, ginger, round copper-rimmed glasses, singed open tan coat over a cream shirt, brown shorts, braided red/copper wire limbs
- [ ] Regenerate Lukey's placeholder VO (`Tools/Audio/generate_vo.py`, then `Tools/Editor/import_vo.py`) once his feedback-pass text changes settle
- [ ] Bed tooltip warning when a guy hasn't had his story conversation this week (skipping a week means his Act 4 can't happen before the inspection, so the house fails)
- [x] Free up disk space (31 GB free on 2026-11-08)
- [ ] Play the full finale in-engine: inspection pass/fail, ep5, every epilogue branch (simulated in text, not yet seen in the dialogue box)
- [x] Voice casting for all hunks ([[Voice Casting]]) + placeholder VO for Lukey that plays in game
- [ ] Placeholder VO for Malcolm, Tyler and Wyatt (hold until their v2 scripts settle; add them to `VOICES` in `Tools/Audio/generate_vo.py`)
- [ ] Record final VO in ElevenLabs (Lukey first; his v2 script is already in American English)
- [ ] Audio: music bed per room + SFX (drip, sparks, toggles, UI clicks, kiss "mwah")
- [ ] Remaining hunks: Az (asbestos), lead paint, broken floor joist, broken door (+ their rooms)
- [ ] Playtest pass on dialogue pacing + stat thresholds (are endings reachable without metagaming?)
- [ ] Packaged build (Mac + Win) and jam page
- [ ] Housewarming finale when all maladies are fixed
- [ ] Better faces (simple decals or blend shapes) and hair for the hunks
- [ ] Settings: key rebinding, subtitles size

## Doing
- [ ] Prototype polish
- [ ] Designer feedback pass (2026-11-08), all four writers + integration + engine; mark done when every agent has finished:
  - [ ] The dehumidifier is an unnamed, non-sentient appliance (no "Dennis") in every script and doc
  - [ ] Inspector Dan comes once, on day 30, for the final inspection only (no weekly / Friday visits; the ep3 podcast interview is a radio guest spot)
  - [ ] Every appearance line matches the 3D models (no blazer/crest/loafers/phone for Tyler; no Lycra except as what Lukey died in, no headband, sweatband, blow-dry or wrench)
  - [ ] Cross-character references: at most 0–2 per act, none in week 1; epilogue codas stay about their own guy
  - [ ] Day-1 touches vary (no handshakes; Malcolm isn't touched on day 1)
  - [ ] `{sfx:Name}` tags in the scripts where they add comedy (the podcast's radio panel doesn't play line cues yet)
  - [x] Integration files: `inspection.json`, `podcast.json`, `epilogue.json`, GDD, Task Board, devlog

## Done
- [x] Set up docs vault
- [x] Unreal 5.8 C++ project, Git LFS, MCP + Python remote execution tooling
- [x] Third-person Rosie with outfit + bandana, apartment with 4 rooms generated from script
- [x] Interactables: sparkle, hover outline, painted-nail pointer, toggles (lamp, TV, stove, fridge, drawers, wardrobe, bath faucet, toilet lid)
- [x] Maladies with broken-state FX (leak, sparks, mold, pink tile glow) and repair state
- [x] Dialogue system (JSON, conditions, effects, topics, fx) + validator
- [x] Four full character arcs with 4 endings each (Lukey, Malcolm, Wyatt, Tyler) and interconnections
- [x] All four arcs rewritten in the v2 (*Ghosts*) tone: Lukey, Malcolm, Tyler, Wyatt (2026-11-08)
- [x] Integration pass: podcast teases for all four, inspection needs all four fixes, whole-household epilogue, cross-script consistency sweep (2026-11-08)
- [x] Title, pause, options, credits, HUD, dialogue box, intro card, ending card, floor plan
- [x] JSON auto-save / continue
- [x] Automated playtest commands (FixHimScript / FixHimAuto / FixHimShot)
