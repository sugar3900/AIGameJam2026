# ARC-KITCHEN-PLASTER-01 — warm kitchen plaster

A provisional kitchen wall surface and module for the A+ plan. The target is inviting old cream plaster behind sage cabinetry and the muted checker backsplash; painterly describes the rendered texture, not heavy modeled paint. See the selected fixer-upper reference and kitchen elevation in the apartment design wiki.

## Candidates and choice

`textures/plaster-candidate-a.png`, `-b.png`, and `-c.png` are independent original generations, retained for comparison. A is more yellow, B is light putty/ivory with warm muted strokes, and C is more peach. **B is the provisional selection:** it supports the sage and terracotta without making the kitchen uniformly yellow or pink. `previews/wall-repeat-{a,b,c}.png` show each over three adjacent modules. The repeat and color still need to be judged under Unreal lighting and against the actual cabinets and backsplash; the preview is not an in-game result.

These images were created with the built-in imagegen tool using the apartment reference. The prompts respectively requested: (A) buttercream with pale ochre brush strokes; (B) aged warm putty/ivory with delicate taupe broken strokes; (C) pale honey ivory with rosy warmth and stippled variation. All requested a flat, evenly lit, clean albedo without objects, strong damage, shadows or physical impasto. The three outputs are independent generations, not edits of a single seed.

## Model and projection

- `model/ARC_Kitchen_Plaster_Wall_2m.fbx`: 2.00 m wide × 0.12 m deep × 2.75 m high; floor-centred origin, visible face −Y, +Z up. The wall is solid; use separate fitted sections or appropriate wall geometry for openings. This module contains no trim, window, backsplash or collision setup.
- `model/ARC_Kitchen_Optional_Hairlines.fbx`: optional, non-repeating subtle branch of hairline marks. It is separate from the clean wall and positioned approximately 0.002 m in front of the module face. It is visual dressing, not Lukey's plumbing repair, and has no collision or repair wiring. Place sparingly and vary position. Preview `previews/wall-local-damage.png`. These hairlines are simple constant-color geometry rather than a generated decal; two generated transparent decal attempts were discarded because they had conspicuous halos.
- `model/ARC-KITCHEN-PLASTER-01.blend`: editable source plus three-module preview and optional hairlines. `model/build_wall.py` rebuilds exports and renders. The blend's preview duplicates are not included in FBX exports.

**The generated base images are not mathematically seamless.** The Blender material uses a *continuous world-space X/Z projection* scaled by 1/3.2 m, with **mirrored** repeats, so adjoining wall meshes sample the same location. A simple UV-wrapped material will not reproduce this look. FBX does not transfer this Blender material graph: in Unreal recreate a shared world-position-based projection, divide world coordinates by 320 cm, use mirror addressing (or `1 - abs(1 - fmod(abs(uv), 2))` per axis), and connect candidate B to an opaque, rough plaster material. World X/Z assumes the wall runs along world X; for walls running along Y use world Y/Z or a rotation-aware/triplanar projection. Keep the mapping consistent when the entire apartment is offset or rotated. If using arbitrary shell geometry rather than the supplied 2 m wall, apply the material to its appropriately oriented faces. Mirroring can still produce symmetric marks at a 3.2 m turn; inspect long runs and corners in the actual room and add limited, non-repeating detail separately. The module's fallback UVs cover 0–2 on each face; they are not equivalent to the world-space projection.

## Rebuild and checks

From the project root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/ARC-KITCHEN-PLASTER-01/model/build_wall.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/ARC-KITCHEN-PLASTER-01/model/validate_fbx.py'
```

Both FBXs passed a Blender reimport check for finite coordinates and UVs, nonzero polygon areas and the wall's 2 × 0.12 × 2.75 m bounds. **Not tested:** Unreal material graph, collision and light, wall intersections/openings, rotated-wall projection, full-room repetition and visual compatibility with finished art. Do not interpret the render or validation as proof of an integrated room.
