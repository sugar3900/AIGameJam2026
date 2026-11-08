---
tags: [audio]
status: idea
---
# Audio Direction

## Mood
- Cutesy, flirty, funny (*Ghosts* UK). Cosy house sounds, with romance stings when the hearts fly.

## Voice-over
- Every love interest is voiced; **the player never is**, and neither is narration. Casting, briefs and ElevenLabs prompts: [[Voice Casting]].
- Lines play automatically when they appear and cut off when you click on (`UFixHimVoiceSubsystem`).
- **Now:** placeholder Kokoro TTS for Lukey. **Final:** ElevenLabs (v3/v4, low stability, 2–3 takes per line).
- ElevenLabs writing tips, from their prompting guide:
  - Audio tags go in square brackets: `[whispers]`, `[laughs]`, `[sighs]`, `[sarcastic]`, `[flirty]`, `[clears throat]`.
  - Tags should only describe sound. Don't use visual ones like `[grinning]`.
  - Pauses use `...`, `[pause]` and `[long pause]`. `<break time="1s"/>` isn't supported on v3/v4.
  - CAPITALS add stress.
  - Sound-effect tags (`[water dripping]`) are hit and miss, so real SFX in the game are more reliable.
  - Keep each request under about 2,000 characters.

## Music
| Track | Where it plays | Source | Status |
|---|---|---|---|
| | | | |

## SFX

All sound effects live in `Art Source/Audio/SFX/` as `SFX_<Cue>.wav` or `SFX_<Cue>_1.wav`, `_2`, ... (numbered files are random
variants; the game plays cue `<Cue>`). They're 44.1 kHz, 16-bit mono, trimmed so the sound starts within a few ms, and
peak-normalised to roughly 0.3 (footsteps, clicks) to 0.6 (impacts) of full scale. Interactions, maladies and the writer's
cues are **real recordings** (CC0, from BigSoundBank, Freesound and Kenney); the UI, reactions, stings and `HunkAppear` are
**synthesized** by `Tools/Audio/generate_sfx.py`. Import both with `python3 Tools/run_in_editor.py Tools/Editor/import_sfx.py`.

### Cue list

Use these names in dialogue as `{sfx:Name}` (inline) or `"sfx": "Name"` (node). R = recorded, S = synthesized.

| Cue | Files | Type | What it sounds like |
|---|---|---|---|
| `LampOn` | 1 | R | Lamp pull-chain click (on). |
| `LampOff` | 1 | R | Lamp pull-chain click (off), a touch lower. |
| `TvOn` | 1 | R | Old CRT TV: power thunk, whine and degauss hum. |
| `TvOff` | 1 | R | CRT TV switching off: click and zip. |
| `StoveIgnite` | 1 | R | Gas hob: igniter ticks, flame catches, gas hiss. |
| `StoveOff` | 1 | R | Gas hob knob clicked off. |
| `FridgeOpen` | 1 | R | Fridge door seal unsticks, a bottle clinks. |
| `FridgeClose` | 1 | R | Fridge door thuds shut. |
| `DrawerOpen` | 2 | R | Wooden drawer sliding open. |
| `DrawerClose` | 2 | R | Wooden drawer sliding shut. |
| `WardrobeOpen` | 1 | R | Wooden wardrobe door opening (knob rattle, small creak). |
| `WardrobeClose` | 1 | R | Wooden wardrobe door shutting. |
| `CabinetOpen` | 1 | R | Kitchen cupboard door opening. |
| `CabinetClose` | 1 | R | Kitchen cupboard door shutting. |
| `FaucetOn` | 1 | R | Bath tap squeaks open and water starts running. |
| `FaucetOff` | 1 | R | Tap squeaks shut, water stops, last drips. |
| `ToiletLidUp` | 1 | R | Toilet seat lifted (clack). |
| `ToiletLidDown` | 1 | R | Toilet seat dropped (clack). |
| `ToiletFlush` | 1 | S | Toilet flush. |
| `DoorHandle` | 1 | R | Rattling the handle of a locked door. |
| `DoorOpen` | 1 | R | Front door: handle, latch, swing open. |
| `DoorClose` | 1 | R | Front door swinging shut. |
| `DoorLatch` | 2 | R | A latch clicking. |
| `DoorCreak` | 1 | R | Wooden door creaking open. |
| `DoorKnock` | 2 | R | Knock-knock-knock on a wooden door. |
| `BedRustle` | 2 | R | Duvet/sheets rustle with a bed creak. |
| `Footstep` | 6 | R | Soft slipper step on an old wooden floor. |
| `SwitchOn` | 1 | S | Cute UI-style switch blip (on). |
| `SwitchOff` | 1 | S | Cute UI-style switch blip (off). |
| `Interact` | 2 | S | Generic soft click. |
| `Hover` | 1 | S | Soft hover chime on an interactable. |
| `PipeClank` | 2 | R | Metal pipe knock/clank. |
| `Zap` | 2 | R | Electrical zap (burst of sparks). |
| `Spark` | 2 | R | Single electric spark. |
| `Sizzle` | 1 | R | Hot sizzle/fizz. |
| `Hum` | 1 | R | Electrical mains hum/buzz. |
| `PowerDown` | 1 | R | Power dying: buzz winds down, breaker clunk. |
| `PowerUp` | 1 | R | Power back: breaker clunk, buzz winds up. |
| `Squelch` | 2 | R | Wet mouldy squish. |
| `TileTap` | 3 | R | Knuckle tap on ceramic tile. |
| `TileCrack` | 1 | R | Ceramic tile cracking. |
| `TapDrip` | 3 | R | Single water drip. |
| `WaterSplash` | 2 | R | Small water splash. |
| `Thunder` | 1 | R | Thunderclap and rumble. |
| `Rain` | 1 | R | Rain on a window (fades in and out, ~3.8 s). |
| `Bonk` | 1 | R | Comedic head bonk. |
| `Thud` | 2 | R | Body/heavy object thud on a wooden floor. |
| `ShelfCrash` | 1 | R | Wooden shelf collapsing, things tumbling (2 s). |
| `RadioStatic` | 1 | R | Old radio tuning static. |
| `CameraShutter` | 1 | R | Film camera shutter click. |
| `Kiss` | 2 | R | Cute 'mwah' kiss. |
| `GlassClink` | 2 | R | Two glasses clinking. |
| `RubberDuck` | 2 | R | Rubber duck squeak. |
| `Whoosh` | 2 | R | Quick whoosh through the air. |
| `HunkAppear` | 1 | S | Gentle magical shimmer as a man appears. |
| `HunkPop` | 1 | S | Magical poof (older pop-in). |
| `HunkLeave` | 1 | S | Soft poof as a man leaves. |
| `BubblePop` | 2 | R | Cute bubble pop with a sparkle (a man vanishing). |
| `ReactHappy` | 1 | S | Happy reaction chime. |
| `ReactHearts` | 1 | S | Hearts reaction chime. |
| `ReactAngry` | 1 | S | Grumpy buzz. |
| `ReactSad` | 1 | S | Sad descending notes. |
| `ReactSurprise` | 1 | S | Surprised boing-up. |
| `FixComplete` | 1 | S | Repair finished: sparkly arpeggio. |
| `RepairFail` | 1 | S | Repair failed: low wobble. |
| `ErrorBuzz` | 1 | S | Not allowed buzz. |
| `DayStart` | 1 | S | New day chime. |
| `DayEnd` | 1 | S | End of day chime. |
| `IntroCard` | 1 | S | Intro card swoosh + chime. |
| `FadeOut` | 1 | S | Fade-to-black swoosh. |
| `EndingRomance` | 1 | S | Romance ending sting. |
| `EndingFriend` | 1 | S | Friend ending sting. |
| `EndingFail` | 1 | S | Fail ending sting. |
| `MenuStart` | 1 | S | Start game chord. |
| `ButtonHover` | 1 | S | UI hover. |
| `ButtonClick` | 1 | S | UI click. |
| `ButtonBack` | 1 | S | UI back. |
| `ModalOpen` | 1 | S | Panel opens. |
| `ModalClose` | 1 | S | Panel closes. |
| `SliderTick` | 3 | S | Slider tick. |
| `ToggleOn` | 1 | S | Toggle on. |
| `ToggleOff` | 1 | S | Toggle off. |
| `Toast` | 1 | S | Notification ding. |
| `ChoiceSelect` | 1 | S | Dialogue choice picked. |
| `TopicClick` | 2 | S | Hypertext topic clicked. |
| `DialogueAdvance` | 3 | S | Next dialogue line. |
| `TypeTick` | 4 | S | Typewriter tick. |
| `PauseOn` | 1 | S | Pause. |
| `PauseOff` | 1 | S | Unpause. |
| `MapOpen` | 1 | S | Map opens (paper). |
| `MapClose` | 1 | S | Map closes. |
| `DebugOpen` | 1 | S | Debug menu. |

### Adding a sound

- **Recorded:** find a CC0 recording (BigSoundBank, Kenney, or a Freesound sound whose licence is Creative Commons 0), add it
  under `sources` and add an entry under `files` in `Art Source/Audio/SFX/recorded.json` (cue, source page, author, licence,
  edit recipe), put the download at its `local` path under a folder of your choice and run
  `python3 Tools/Audio/process_recorded_sfx.py --src-root <that folder> --only <Cue>` (needs numpy, scipy, soundfile). You can
  also edit a WAV by hand and just list it in `recorded.json` with notes on the edits. Then run `generate_sfx.py` once so
  `manifest.json` picks it up, and import.
- **Synthesized:** add a recipe function and a `SOUNDS` row in `Tools/Audio/generate_sfx.py`, run it, import.
- `generate_sfx.py` never synthesizes a cue that has files in `recorded.json`, deletes synthesized leftovers it no longer
  makes, and writes `manifest.json` as synthesized + recorded. Run `python3 Tools/validate_dialogue.py` after adding cues the
  writer uses.

### Recorded sources

Every source is CC0 1.0 (public domain); credit is optional but kind. Freesound items are the public HQ previews (128 kbps MP3)
of CC0 originals. All files: mono mix, resample to 44.1 kHz, 40 Hz high-pass, trim, short fades, peak-normalise. Full recipes
(cut points, gains, pitch) are in `recorded.json`.

| Cue | File(s) | Source | Author | Licence | Edits |
|---|---|---|---|---|---|
| `BedRustle` | `BedRustle_1` | [Blanket Movement 6](https://freesound.org/people/OwlStorm/sounds/320144/); [Bed creak.wav](https://freesound.org/people/MootMcnoodles/sounds/444389/) | OwlStorm (Freesound); MootMcnoodles (Freesound) | CC0 | 0.04-1.05 s + 0.3-1.1 s, -8 dB @0.12 s; Duvet being rustled, with a little bed-frame creak underneath. |
| `BedRustle` | `BedRustle_2` | [Sheets Rustling.wav](https://freesound.org/people/MootMcnoodles/sounds/444405/); [Bed creak.wav](https://freesound.org/people/MootMcnoodles/sounds/444389/) | MootMcnoodles (Freesound) | CC0 | 2.6-3.6 s + 1-1.75 s, -7 dB @0.05 s; Bed sheets rustling, with a bed creak underneath. |
| `Bonk` | `Bonk` | [Bonk.wav](https://freesound.org/people/facklere/sounds/458572/); [Impact Sounds: impactPunch_medium_000.ogg](https://kenney.nl/assets/impact-sounds) | facklere (Freesound); Kenney | CC0 | 0-0.62 s + whole, -5 dB; Low tonal 'bonk' drum hit layered with a punch thud: cartoony but physical. |
| `BubblePop` | `BubblePop_1` | [Bubble Pop](https://freesound.org/people/TheBuilder15/sounds/411462/); [Chimes "butterfly" #1](https://bigsoundbank.com/chimes-butterfly-1-s2087.html) | TheBuilder15 (Freesound); Joseph SARDIN (BigSoundBank) | CC0 | 0.14-0.62 s + 1.38-1.95 s, -17 dB @0.05 s; Mouth bubble pop with a quiet, high-passed chime cluster as a sparkle tail. |
| `BubblePop` | `BubblePop_2` | [Bubbles Burst](https://bigsoundbank.com/bubbles-burst-s1074.html); [Chimes "butterfly" #1](https://bigsoundbank.com/chimes-butterfly-1-s2087.html) | Joseph SARDIN (BigSoundBank) | CC0 | 18.98-19.4 s + 1.38-1.95 s, -17 dB @0.05 s; Another mouth bubble pop with the same sparkle tail. |
| `CabinetClose` | `CabinetClose` | [Cupboard](https://bigsoundbank.com/cupboard-s0046.html) | Joseph SARDIN (BigSoundBank) | CC0 | 1.28-2.3 s; Cupboard door shutting, take 1. |
| `CabinetOpen` | `CabinetOpen` | [Cupboard](https://bigsoundbank.com/cupboard-s0046.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.28-1.2 s; Cupboard door opening (latch + squeak), take 1. |
| `CameraShutter` | `CameraShutter` | [Instamatic, Triggering #1](https://bigsoundbank.com/instamatic-triggering-1-s2821.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.05-0.45 s; Kodak Instamatic 133-X film camera shutter. |
| `DoorClose` | `DoorClose` | [Apartment Door, Closing #1](https://bigsoundbank.com/apartment-door-closing-1-s1704.html) | Joseph SARDIN (BigSoundBank) | CC0 | 2.3-3.7 s; End of the closing swing and the door shutting into its frame. |
| `DoorCreak` | `DoorCreak` | [Creaking Door #2](https://bigsoundbank.com/creaking-door-2-s3205.html) | Joseph SARDIN & Axeline T. (BigSoundBank) | CC0 | 0.12-1.6 s; Creak of a wooden door being opened. |
| `DoorHandle` | `DoorHandle` | [Door Locked](https://freesound.org/people/BenjaminNelan/sounds/321087/) | BenjaminNelan (Freesound) | CC0 | 0-0.62 s; Trying the handle of a locked door (rattle, no give). 22 kHz original, resampled. |
| `DoorKnock` | `DoorKnock_1`, `DoorKnock_2` | [Door](https://bigsoundbank.com/door-s0015.html) | Joseph SARDIN (BigSoundBank) | CC0 | 3.33-4.2 s / 0.11-0.4 s + 0.86-1.15 s, +1 dB @0.21 s + 2.82-3.15 s, -1 dB @0.43 s; Knock knock knock on a light wooden door (knuckles). / Three single knocks from the same recording re-spaced into a triple knock. |
| `DoorLatch` | `DoorLatch_1` | [RPG Audio: metalLatch.ogg](https://kenney.nl/assets/rpg-audio) | Kenney | CC0 | whole; Metal latch click. |
| `DoorLatch` | `DoorLatch_2` | [Apartment Door, Opening #1](https://bigsoundbank.com/apartment-door-opening-1-s1702.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.52-0.95 s; The latch clack from the apartment-door opening take. |
| `DoorOpen` | `DoorOpen` | [Apartment Door, Opening #1](https://bigsoundbank.com/apartment-door-opening-1-s1702.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.05-1.95 s; Parisian apartment front door: handle, latch, and the start of the opening grind. |
| `DrawerClose` | `DrawerClose_1` | [Wooden drawer, closing](https://bigsoundbank.com/wooden-drawer-closing-s1500.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.1-1.25 s; Wooden drawer sliding shut with a knock at the end. |
| `DrawerClose` | `DrawerClose_2` | [Wooden drawer #1](https://bigsoundbank.com/wooden-drawer-1-s1267.html) | Joseph SARDIN (BigSoundBank) | CC0 | 6.3-7.24 s; Second closure in the same recording. |
| `DrawerOpen` | `DrawerOpen_1` | [Wooden drawer, opening](https://bigsoundbank.com/wooden-drawer-opening-s1499.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.06-1 s; Wooden drawer sliding open on wooden runners. |
| `DrawerOpen` | `DrawerOpen_2` | [Wooden drawer #1](https://bigsoundbank.com/wooden-drawer-1-s1267.html) | Joseph SARDIN (BigSoundBank) | CC0 | 4.3-5.25 s; Second opening in 'two openings and closures of a wooden drawer'. |
| `FaucetOff` | `FaucetOff` | [Bathtub Faucet Running](https://freesound.org/people/quantumriver/sounds/552131/); [Small metal grinding #1](https://bigsoundbank.com/petit-grincement-metal-1-s0322.html) | quantumriver (Freesound); DavidGreck (BigSoundBank) | CC0 | 13.9-16.9 s + 0.12-0.55 s, -9 dB @0.05 s; Bathtub faucet being shut off (flow dwindles, last drips), with a small metal squeak layered on the handle turn. |
| `FaucetOn` | `FaucetOn` | [bath tap on.wav](https://freesound.org/people/Walter_Odington/sounds/26767/) | Walter_Odington (Freesound) | CC0 | 0-2.9 s; Bath tap squeaking open and the water starting to run; faded out after ~2.9 s. |
| `Footstep` | `Footstep_1`, `Footstep_2`, `Footstep_3`, `Footstep_4`, `Footstep_5`, `Footstep_6` | [feet (slipper on floor)](https://bigsoundbank.com/feet-slipper-on-floor-s0373.html) | Joseph SARDIN (BigSoundBank) | CC0 | 6 cuts from the take; One slipper step on an old wooden floor (of 13 in the take). |
| `FridgeClose` | `FridgeClose` | [refrigerator door close](https://freesound.org/people/Yoyodaman234/sounds/183537/) | Yoyodaman234 (Freesound) | CC0 | 0.06-0.95 s; Fridge door thudding shut (exterior take). |
| `FridgeOpen` | `FridgeOpen` | [refrigerator door open](https://freesound.org/people/Yoyodaman234/sounds/183531/); [Bottles of beer, shocks #2](https://bigsoundbank.com/bottles-of-beer-shocks-2-s1394.html) | Yoyodaman234 (Freesound); Joseph SARDIN (BigSoundBank) | CC0 | 0.05-1.25 s + 0.08-0.4 s, -14 dB @0.3 s; Door seal unsticking and swinging open, with a quiet clink of two beer bottles mixed in at 0.3 s. |
| `GlassClink` | `GlassClink_1` | [Cheers, red wine glass #2](https://bigsoundbank.com/cheers-red-wine-glass-2-s1329.html) | Joseph SARDIN (BigSoundBank) | CC0 | whole; Two red-wine glasses clinking. |
| `GlassClink` | `GlassClink_2` | [Cheers, small wineglass #1](https://bigsoundbank.com/cheers-small-wineglass-1-s1325.html) | Joseph SARDIN (BigSoundBank) | CC0 | whole; Two small wine glasses clinking. |
| `Hum` | `Hum` | [Neon or transformer #1](https://bigsoundbank.com/neon-or-transformer-1-s2118.html) | Joseph SARDIN (BigSoundBank) | CC0 | 1-2.5 s; 50 Hz mains buzz from a neon tube / transformer. |
| `Kiss` | `Kiss_1` | [Cartoon - Smoochy Squeak + Plop](https://freesound.org/people/Breviceps/sounds/444494/) | Breviceps (Freesound) | CC0 | 0-0.25 s + 0.52-0.66 s, -4 dB @0.19 s; Cartoon smoochy squeak with its little plop moved up right behind it: a cute 'mwah'. |
| `Kiss` | `Kiss_2` | [Kisses #1](https://bigsoundbank.com/kisses-s0178.html) | Joseph SARDIN (BigSoundBank) | CC0 | 6.46-6.78 s; One small dry kiss (the longest of 7 in the take). |
| `LampOff` | `LampOff` | [Desk Lamp - Chain Pull (Fast).wav](https://freesound.org/people/PhillipArthurSimmons/sounds/541762/) | PhillipArthurSimmons (Freesound) | CC0 | 0.53-0.95 s, pitch -1 st; Second click (release) of the same pull-chain, pitched down 1 semitone so on/off differ. |
| `LampOn` | `LampOn` | [Desk Lamp - Chain Pull (Fast).wav](https://freesound.org/people/PhillipArthurSimmons/sounds/541762/) | PhillipArthurSimmons (Freesound) | CC0 | 0.22-0.53 s; First click (pull) of a desk-lamp pull-chain. |
| `PipeClank` | `PipeClank_1`, `PipeClank_2` | [Hollow Metal Pipe Hits](https://freesound.org/people/Zott820/sounds/271170/) | Zott820 (Freesound) | CC0 | 0-0.62 s, pitch -3 st / 12.88-13.55 s, pitch -4 st; Two hollow 1/2" metal pipes hit together, pitched down 3 semitones for a heavier plumbing clank. / Another hit from the same take, pitched down 4 semitones. |
| `PowerDown` | `PowerDown` | [Neon or transformer #1](https://bigsoundbank.com/neon-or-transformer-1-s2118.html); [Circuit Breaker 3 DP.wav](https://freesound.org/people/sribubba/sounds/130154/) | Joseph SARDIN (BigSoundBank); sribubba (Freesound) | CC0 | 2-3.1 s, pitch +0→-14 st + 0.03-0.42 s, -2 dB @0.78 s; Mains buzz sliding down ~14 semitones and fading (wind-down), then a circuit-breaker clunk. |
| `PowerUp` | `PowerUp` | [Circuit Breaker 2 DP.wav](https://freesound.org/people/sribubba/sounds/130153/); [Neon or transformer #1](https://bigsoundbank.com/neon-or-transformer-1-s2118.html) | sribubba (Freesound); Joseph SARDIN (BigSoundBank) | CC0 | 0-0.4 s + 3-4 s, pitch -14→+0 st, -3 dB @0.1 s; Circuit-breaker clunk, then mains buzz rising ~14 semitones up to pitch (wind-up). |
| `RadioStatic` | `RadioStatic` | [Radio, frequency sweep #1](https://bigsoundbank.com/radio-frequency-sweep-1-s2617.html) | Joseph SARDIN (BigSoundBank) | CC0 | 1.62-2.9 s; Manual radio-tuner scan: static with faint tuning whistles (section with no station audio). |
| `Rain` | `Rain` | [Rain on car windshield](https://bigsoundbank.com/rain-on-car-windshield-s1295.html) | Joseph SARDIN (BigSoundBank) | CC0 | 20-23.8 s; Big raindrops on a car windscreen, recorded inside (reads as rain on a window); 0.5 s fade in, 0.9 s fade out. |
| `RubberDuck` | `RubberDuck_1`, `RubberDuck_2` | [Rubber duck toy squeaking.wav](https://freesound.org/people/panmaterac/sounds/201285/) | panmaterac (Freesound) | CC0 | 1.74-2.32 s / 6.8-7.3 s; Small yellow rubber duck squeezed once. / Another squeeze from the same take. |
| `ShelfCrash` | `ShelfCrash` | [Impact Sounds: impactWood_heavy_000.ogg](https://kenney.nl/assets/impact-sounds); [Wood Crash.mp3](https://freesound.org/people/benjaminpotter/sounds/343164/); [Impact Sounds: impactSoft_heavy_002.ogg](https://kenney.nl/assets/impact-sounds) | Kenney; benjaminpotter (Freesound) | CC0 | whole + 0.6-2.75 s @0.02 s + whole, -6 dB @1.05 s; Heavy wooden thump, then blocks of wood crashing off a plank, then a soft box-like thud as it settles. |
| `Sizzle` | `Sizzle` | [Frying pan #3](https://bigsoundbank.com/frying-pan-3-s0145.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.5-1.8 s; Hot-oil sizzle (steak in a pan), 1.3 s with soft edges. |
| `Spark` | `Spark_1` | [Spark](https://freesound.org/people/elliott.klein/sounds/189630/) | elliott.klein (Freesound) | CC0 | whole; Single spark from a bug-zapper racket. |
| `Spark` | `Spark_2` | [Spark.wav](https://freesound.org/people/BMacZero/sounds/94132/) | BMacZero (Freesound) | CC0 | 0.1-0.34 s; Single spark from a Tesla generator. |
| `Squelch` | `Squelch_1` | [Slime Squish](https://freesound.org/people/qubodup/sounds/442772/) | qubodup (Freesound) | CC0 | whole; Slime squish (game SFX made from a real squelch recording). |
| `Squelch` | `Squelch_2` | [squelching.mp3](https://freesound.org/people/tiddles451/sounds/547446/) | tiddles451 (Freesound) | CC0 | 3.45-4.05 s; A sodden wet sponge squelched into a glass. |
| `StoveIgnite` | `StoveIgnite` | [Gas stove #2](https://bigsoundbank.com/gas-stove-2-s0058.html); [Gas stove #1](https://bigsoundbank.com/gas-stove-1-s0057.html) | Joseph SARDIN (BigSoundBank) | CC0 | 1.395-1.43 s + 1.395-1.43 s, -2 dB @0.16 s + 2.2-3.7 s @0.32 s; Two piezo-igniter ticks from take 2, then take 1's tick + flame catching + gas hiss; hiss faded out. |
| `StoveOff` | `StoveOff` | [Gas stove #1](https://bigsoundbank.com/gas-stove-1-s0057.html) | Joseph SARDIN (BigSoundBank) | CC0 | 21.05-21.75 s; End of take 1: last of the gas hiss and the knob clicking off. |
| `TapDrip` | `TapDrip_1`, `TapDrip_2`, `TapDrip_3` | [Drops of water #1](https://bigsoundbank.com/drops-of-water-1-s1384.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.13-0.42 s / 4.42-4.7 s / 11.6-11.88 s; Single drop of water. |
| `Thud` | `Thud_1`, `Thud_2` | [Impact Sounds: impactSoft_heavy_000.ogg](https://kenney.nl/assets/impact-sounds); [Impact Sounds: impactWood_heavy_002.ogg](https://kenney.nl/assets/impact-sounds) | Kenney | CC0 | whole + whole, -3 dB / whole + whole, -3 dB; Soft heavy body impact layered with a heavy wood impact: a body on a wooden floor. / Same recipe with the other takes. |
| `Thunder` | `Thunder` | [Thunder #2](https://bigsoundbank.com/thunder-2-s3113.html) | Joseph SARDIN & Axeline T. (BigSoundBank) | CC0 | 0.6-4.7 s; A single short thunderclap and rumble, no rain. |
| `TileCrack` | `TileCrack` | [Breaking Ceramic Tile](https://freesound.org/people/deleted_user_7146007/sounds/383720/) | deleted_user_7146007 (Freesound) | CC0 | 0.85-1.75 s; A ceramic tile breaking. |
| `TileTap` | `TileTap_1`, `TileTap_2`, `TileTap_3` | [Knock-knock on a tiled wall](https://bigsoundbank.com/knock-knock-on-a-tiled-wall-s0401.html) | Joseph SARDIN (BigSoundBank) | CC0 | 7.44-7.85 s / 8.69-9.1 s / 4.27-4.68 s; Single knuckle knock on a tiled bathroom wall. / Another knock from the same take. |
| `ToiletLidDown` | `ToiletLidDown` | [toilet seat down.wav](https://freesound.org/people/jrssandoval/sounds/67171/) | jrssandoval (Freesound) | CC0 | 0.66-1.65 s; Toilet seat dropped down onto the bowl. |
| `ToiletLidUp` | `ToiletLidUp` | [toilet seat up.wav](https://freesound.org/people/jrssandoval/sounds/67172/) | jrssandoval (Freesound) | CC0 | 0.86-1.75 s; Toilet seat lifted up, clacking against the tank. |
| `TvOff` | `TvOff` | [On/Off Button](https://freesound.org/people/Fission9/sounds/693859/); [CRT TV Switches Off](https://freesound.org/people/Fission9/sounds/693861/) | Fission9 (Freesound) | CC0 | 1.06-1.4 s, -5 dB + 0-0.55 s @0.02 s; Power-button press layered with the CRT switch-off zip (take 1). |
| `TvOn` | `TvOn` | [CRT TV Switches On](https://freesound.org/people/Fission9/sounds/693860/) | Fission9 (Freesound) | CC0 | 0.18-0.72 s + 1.2-2.3 s, -2 dB @0.4 s + 3.06-3.95 s, -4 dB @0.55 s; Power-button thunk, the start of the CRT whine, then the degauss 'bvoom' (all from take 1), overlapped to ~1.4 s. |
| `WardrobeClose` | `WardrobeClose` | [Door_wood_wardrobe_1.WAV](https://freesound.org/people/o_ciz/sounds/475488/) | o_ciz (Freesound) | CC0 | 4.7-5.85 s; Closing a wooden wardrobe door. |
| `WardrobeOpen` | `WardrobeOpen` | [Open-Wardrobe-2.wav](https://freesound.org/people/toefur/sounds/280240/) | toefur (Freesound) | CC0 | 0.15-1.95 s; Wooden wardrobe door opening: knob rattle and a small wobble/creak of the wood. |
| `WaterSplash` | `WaterSplash_1` | [Splash, Small #1](https://bigsoundbank.com/splash-small-1-s1529.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0.04-0.95 s; Small splash (a pebble into a pond). |
| `WaterSplash` | `WaterSplash_2` | [Splash, small #3](https://bigsoundbank.com/splash-small-3-s1531.html) | Joseph SARDIN (BigSoundBank) | CC0 | 0-0.55 s; Small splash (a pebble into a pond). |
| `Whoosh` | `Whoosh_1` | [Whoosh #4](https://bigsoundbank.com/whoosh-4-s1796.html) | Joseph SARDIN (BigSoundBank) | CC0 | whole; Whoosh of a long rope swung through the air. |
| `Whoosh` | `Whoosh_2` | [Whoosh #3](https://bigsoundbank.com/whoosh-3-s1795.html) | Joseph SARDIN (BigSoundBank) | CC0 | whole; Whoosh of a long rope swung through the air. |
| `Zap` | `Zap_1`, `Zap_2` | [Electric Sparks.wav](https://freesound.org/people/kev_durr/sounds/396470/) | kev_durr (Freesound) | CC0 | 3.56-4.2 s / 4.43-5.08 s; Burst of sparks from a 35 kV supply. / Another burst from the same take. |

Related: [[Art Direction]] · [[AI Usage Log]]
