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

## Prompts worth keeping
- "Pull an update and read the documents I wrote. We will be building this out using Unreal... work independently until you've completed the prototype."
