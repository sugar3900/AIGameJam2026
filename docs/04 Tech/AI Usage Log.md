---
tags: [tech, ai]
---
# AI Usage Log

Track where AI tools were used. Useful for jam disclosure rules and the [[Postmortem]].

| Date | Area (code / art / audio / design / text) | Tool | What it did | Notes |
|---|---|---|---|---|
| 2026-11-07 | infra | Claude Code (Claude) | Created the Obsidian docs vault, Unreal project, Git LFS/gitignore/config, build + editor tooling | Repo best practices; MCP on :8001 |
| 2026-11-07 | code | Claude Code | All C++ gameplay, dialogue runtime, save system, code-built UMG UI | ~5k lines in `Source/ICanFixHim` |
| 2026-11-07 | art | Claude Code | Python scripts that generate the apartment level, materials and palette; SVG pointer/heart icons | Primitives + UE template mannequins |
| 2026-11-07 | text | Claude Code | Wrote all four character arcs (Lukey, Malcolm, Wyatt, Tyler), endings and puns from David's character briefs | `Content/ICanFixHim/Data/Dialogue/*.json` |
| 2026-11-07 | design | Claude Code | Relationship thresholds, interconnections (leak feeds mold; Wyatt ♥ Tyler), UI layouts | Characters + beats from Scope & MVP |
| 2026-11-07 | QA | Claude Code + Unreal MCP | Drove PIE with scripted console commands and screenshots to verify every arc reaches an ending | `FixHimScript`, `FixHimAuto` |
| 2026-11-07 | text | Claude Code | Brainstormed the v2 story with Kirsten (flipper heroine, condemned house, Ghosts-UK tone), then wrote Lukey's v2 arc, the Bev & Trish podcast and the epilogues | `lukey.json`, `podcast.json`, `epilogue.json` |
| 2026-11-08 | audio | Kokoro-82M TTS (local, Apache-2.0) + Claude Code | Placeholder voice-over for all of Lukey's lines, generated and imported by script; in-game playback | `Tools/Audio/generate_vo.py`; final VO planned in ElevenLabs ([[Voice Casting]]) |
| 2026-11-08 | design | Claude Code | Voice casting briefs and ElevenLabs Voice Design prompts for all five hunks | [[Voice Casting]] |
| 2026-11-08 | text | Claude Code (four parallel writer agents) | Rewrote Malcolm, Tyler and Wyatt and revised Lukey in the v2 *Ghosts* tone, with character bibles | `malcolm.json`, `tyler.json`, `wyatt.json`, `lukey.json`, `docs/02 Design/Characters/` |
| 2026-11-08 | text | Claude Code (integration writer) | Podcast teases for all four guys and the exact ep4 newspaper quote; final inspection that needs all four fixes; whole-household epilogue (per-guy beats, shared dinner for multiple romances, demolition walk-through); consistency fixes across the four scripts | `podcast.json`, `inspection.json`, `epilogue.json` |
| 2026-11-08 | QA | Claude Code | Validator run plus a throwaway script that walks the inspection and epilogue for all 625 outcome combinations × house choices (every node reachable, no stuck choices) | Script kept out of the repo |
| 2026-11-08 | design | Claude Code | Updated the GDD (cast, interconnections, asides, inspection rule), Task Board and devlog for the v2 cast | |
| 2026-11-08 | code / audio | Claude Code + Kokoro-82M TTS | Merged `voices` (and `feature/character-models`) into the v2 dialogue branch: voice-over vs asides, one shared `EaseOutBack`, Voice Casting updated to v2 canon (Tyler American); regenerated Lukey's placeholder VO for his v2 lines (100 new or changed, 5 orphans removed) and re-imported | `generate_vo.py`, `import_vo.py`, [[Voice Casting]] |
| 2026-11-08 | text / design | Claude Code (integration writer) | Designer feedback pass on the integration scripts and docs: removed the named, sentient dehumidifier; made the day-30 inspection Dan's first and only visit (podcast ep3 is a radio guest spot); matched every appearance line to the 3D models; added `{sfx:Name}` cue tags; updated GDD, Task Board and devlog; re-ran the validator and the 1,137-playthrough finale simulation | `inspection.json`, `podcast.json`, `epilogue.json` |

## Prompts worth keeping
- "Pull an update and read the documents I wrote. We will be building this out using Unreal... work independently until you've completed the prototype."
