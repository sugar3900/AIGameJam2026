---
tags: [audio, voice, characters]
status: draft
---
# Voice Casting

Every love interest is a **man, and attractive**: the voice should make the player lean in. Each one gets a distinct silhouette you could recognise with your eyes shut: pitch, accent, pace and the *kind* of charm.

**The player is never voiced.** She's a blank slate, and only her text appears. Narration (`*...*`) isn't voiced either.

| Character | Malady | The voice in one line | Reference ("in the spirit of") | ElevenLabs default fallback |
|---|---|---|---|---|
| [[Lukey]] | The Leaks | Big, grinning all-American golden retriever | Emmett Cullen in *Twilight* | **Liam** (alt: Chris) |
| [[Malcolm]] | Black Mold | Silky, theatrical, velvet-menace British baritone | Loki | **Callum** (alt: George) |
| [[Az]] | Asbestos | Bright, breathy K-pop idol with a soft Korean accent | A K-pop boy-band visual on a variety show | **Liam**, as a stopgap (see notes) |
| [[Tyler]] | Pink Tile | Clipped, posh, royal officer who has never heard "no" | A young prince in dress uniform | **Daniel** (alt: George) |
| [[Wyatt]] | Faulty Wiring | Smart, masculine Australian, soft and a little deferential | A gentle-giant Aussie engineer | **Charlie** |

> **Don't clone real people.** The references are about *vibe* only. ElevenLabs' terms forbid cloning someone's voice without their consent, and it would also be a legal problem for the jam. Use the **Voice Design** prompts below, which describe a voice without naming anyone, or the default fallbacks.

## How to use this page in ElevenLabs
1. **Best option: Voice Design.** Go to Voices, then *Create a voice*, then *Voice Design*, and paste the **Voice Design prompt** for the character. Generate 3 options, pick the hottest, and save it as `ICFH <Name>`.
2. **Second option: Voice Library.** Search the **library search** terms, and listen for the bullet points under *Must have*.
3. **Last resort: a default voice.** These come with every account (see the table above). None are a perfect match. They are there so we're never blocked.
4. **Model and settings:** Eleven v3 (or v4) with low stability, so audio tags like `[flirty]` and `[scoffs]` actually land. Make 2–3 takes per line. Pauses use `...` and `[pause]`, not `<break>` tags (v3/v4 ignore those). See the tips in [[Audio Direction]].

---

## Lukey: The Leaks
**All-American, big, warm and grinning.** The golden-retriever jock of the house: the guy who picks you up and spins you round, then makes a joke about it. Think Emmett Cullen: a booming laugh, a big chest, zero self-consciousness.

- **Age / pitch:** sounds late 20s to early 30s (he died at 34). A warm, chesty baritone with a bright top end when he gets excited.
- **Accent:** general American, a touch of East-coast Italian-American swagger (he's a Moretti), but never a caricature.
- **Pace:** fast and bouncy when he's showing off; drops right down and goes quiet for the sincere bits. That contrast is the whole romance.
- **Signature moves:** laughs mid-sentence; SHOUTS single words for emphasis ("I am being HOSTILE"); a fitness-instructor bark ("And REACH!"); a soft, almost-whisper "sweetheart".
- **Act 1 vs Act 4:** Act 1 is a sulky, defensive jock ("Get out of my house"). By Act 4 he's tender and a little shy. Same voice, with the armour off.
- **Must have:** a smile you can *hear*. **Avoid:** surfer-dude stoner, game-show announcer, or anything nasal.
- **Voice Design prompt:**
  > A handsome American man in his early thirties with a warm, chesty baritone and a big, easy smile you can hear. Playful, confident and a little cocky, like a charming college athlete. He laughs easily and his voice gets soft and tender in sincere moments. Clear, natural studio recording.
- **Library search:** "American male, warm, playful, young adult, conversational, charming".
- **Default fallback:** **Liam** (young, American, articulate). **Chris** (American, casual, conversational) if Liam sounds too polished.
- **Placeholder in the game now:** Kokoro (free, local) voice blend `am_fenrir` 50% / `am_michael` 30% / `am_puck` 20%, at speed 1.05. See *Placeholder VO pipeline* below.

## Malcolm: Black Mold
**Silky, theatrical and dangerous, in a way you shouldn't find hot.** A trickster prince of the damp corner, in the spirit of Loki: velvet British RP, a smile that's slightly too wide, every line a performance for an audience of one.

- **Age / pitch:** sounds early to mid 30s. A smooth, resonant baritone that can curl up into an amused purr.
- **Accent:** refined British RP. Crisp consonants and long, savoured vowels.
- **Pace:** unhurried. He *lingers* on words, uses pauses as power, then snaps with sudden venom or glee.
- **Signature moves:** a low, private chuckle; dramatic whispered asides; mock-wounded sighs; reading poetry like it's a confession.
- **Personality fit:** an emo poet and a sub. The menace is a costume over neediness, so the voice cracks into vulnerability when you give him an order.
- **Must have:** velvet, mischief, control. **Avoid:** a pantomime villain cackle, or old and gravelly.
- **Voice Design prompt:**
  > A seductive British man in his early thirties with a smooth, velvety baritone and refined received-pronunciation accent. Theatrical, silver-tongued and mischievous, with a hint of danger and wounded vulnerability underneath. Speaks slowly, savouring words, with amused pauses and soft, intimate delivery. Clear studio recording.
- **Library search:** "British male, smooth, seductive, villain, theatrical, deep".
- **Default fallback:** **Callum** (Transatlantic, intense, husky, good for characters). **George** (British, warm) if you need it softer.

## Az: Asbestos
**A K-pop idol: bright, sweet and polished, with a diva streak.** Soft, breathy charm that's been media-trained to perfection, with a sharper edge when he doesn't get his way. He's *protective* (asbestos stops fire spreading), so there's warmth under the sparkle.

- **Age / pitch:** sounds early to mid 20s. A light, clear tenor that drops into a soft, husky low register when he flirts.
- **Accent:** fluent English with a gentle Korean accent. Mostly the rhythm and vowel colour; keep it natural and affectionate, never a joke.
- **Pace:** smooth and musical; slightly breathy; playful sing-song on teasing lines; a little pout in "wae~?" moments.
- **Signature moves:** soft breathy laugh; playful aegyo-style whine when sulking; a fan-service purr ("you're welcome"); a diva gasp.
- **Must have:** idol polish, softness, sparkle. **Avoid:** an exaggerated accent, or a cartoon high pitch.
- **Voice Design prompt:**
  > A charming young Korean man in his early twenties speaking fluent English with a soft, natural Korean accent. Light, clear tenor with a gentle breathy quality, like a K-pop idol: sweet, polished, playful and a little bit of a diva, with a soft husky tone when flirting. Clear studio recording.
- **Library search:** "Korean male English, young, soft, idol, sweet, breathy". The Voice Library has Korean-accented English voices from the community. None of the defaults have this accent.
- **Default fallback:** **Liam** (young, bright American). This is only a stopgap, because it loses the accent, so use Voice Design or the Library for Az.

## Tyler: Pink Tile
**A royal officer who has always got his way.** Grew up in a palace, commissioned at 18, has never once been told "no". Snooty, proper and drill-sergeant crisp, but the posture hides a soft heart (he *is* pink, after all). The hotness is the composure, and the fun is watching it crack.

- **Age / pitch:** sounds late 20s. A firm, bright baritone with excellent projection; parade-ground clarity.
- **Accent:** upper-class British, the received pronunciation of a palace and a military academy. Clipped, precise, faintly bored.
- **Pace:** measured and decisive; short commands; long-suffering sighs; every sentence ends like an order.
- **Signature moves:** an affronted "I beg your *pardon*?"; a sniff of disapproval; barking an order then immediately softening into gentlemanly courtesy; flustered spluttering when complimented.
- **Personality fit:** keeps his outdated opinions about pink and taste, but they now come from privilege and tradition rather than obnoxiousness. He's defending the 1957 tile like a regimental colour.
- **Must have:** entitlement, poise, command. **Avoid:** an old colonel, a cartoon toff, or nasal.
- **Voice Design prompt:**
  > A handsome, aristocratic British man in his late twenties, a royal army officer raised in privilege who has always gotten his way. Crisp, upper-class received-pronunciation accent, a firm, clear baritone with commanding projection. Proper, snooty and composed, with a hidden softness. Clear studio recording.
- **Library search:** "British male, posh, aristocratic, upper class, officer, commanding, young".
- **Default fallback:** **Daniel** (British, authoritative). **George** (British, warm) for his softer moments.

## Wyatt: Faulty Wiring
**A smart, masculine Australian who's sweet on you and a little bit submissive.** Big, capable and clever (he understands circuits better than anyone), but deferential and eager to please. He asks permission, apologises too much and lights up when you take charge.

- **Age / pitch:** sounds late 20s to early 30s. A deep, relaxed, masculine baritone kept soft and gentle.
- **Accent:** general Australian. Warm, easy vowels and a natural rising lilt; not ocker or broad.
- **Pace:** thoughtful; trails off ("if that's... alright?"); gets quick and nerdy when explaining something technical, then catches himself.
- **Signature moves:** a shy laugh; a soft "yeah, nah"; deferring ("whatever you reckon"); a breathy, overwhelmed little exhale when complimented.
- **Personality fit:** keeps the crossed-wires comedy (his lights flicker when he thinks), but it now reads as overthinking, not confusion. He's smart and *flustered*, not dim. Bi ("very AC/DC").
- **Must have:** a big man with a gentle voice; intelligence; softness. **Avoid:** a Crocodile Dundee caricature, a surfer bro, or anything weak or whiny.
- **Voice Design prompt:**
  > A handsome Australian man around thirty with a deep, warm, masculine baritone and a natural Australian accent. Smart and articulate but gentle, a little shy and deferential, eager to please, often trailing off politely. Soft-spoken and sweet with quiet confidence when talking about technical things. Clear studio recording.
- **Library search:** "Australian male, deep, gentle, warm, soft-spoken, conversational".
- **Default fallback:** **Charlie** (Australian, natural, conversational).

---

## Placeholder VO pipeline (in the game now)
Until we record the real cast, the game uses free, local text-to-speech so we can hear the pacing and test playback.

- **Model:** [Kokoro-82M](https://github.com/hexgrad/kokoro) via `kokoro-onnx` (Apache-2.0). It runs locally, so there's no account or cost. It reads naturally, but it can't *act*: no audio tags, no accents beyond US/UK. The model files (~350 MB) download to `Saved/VOModels/` on first run.
- **Generate:** `uv run --python 3.11 --with kokoro-onnx --with soundfile Tools/Audio/generate_vo.py`. Only changed lines regenerate (tracked in `Art Source/Audio/VO/manifest.json`). Add a character by adding an entry to `VOICES` in the script.
- **Import:** with the editor open, `python3 Tools/run_in_editor.py Tools/Editor/import_vo.py`. That creates `/Game/ICanFixHim/Audio/VO/<script>/VO_<script>_<node>_<line>`.
- **In game:** `UFixHimVoiceSubsystem` plays the clip for a line when it appears, cuts it when you click on, and stops when the conversation ends. Any line without a clip is silent, so voicing another character is data-only.
- **Your name:** the player's chosen name can't be pre-recorded. Lines that say `{player}` are recorded with the name left out ("{player}, did you listen..." becomes "Did you listen..."). A line that is *only* the name stays silent.
- **Swapping in ElevenLabs takes:** export the line as WAV and save it over the placeholder in `Art Source/Audio/VO/<script>/` under the same name (`VO_<script>_<node>_<line>.wav`), then re-run the import. The generator leaves it alone unless that line's text changes, or you run it with `--force`.

Related: [[Audio Direction]] · [[Lukey]] · [[Malcolm]] · [[Az]] · [[Tyler]] · [[Wyatt]] · [[AI Usage Log]]
