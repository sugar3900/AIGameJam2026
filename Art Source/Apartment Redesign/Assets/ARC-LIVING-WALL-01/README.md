# ARC-LIVING-WALL-01 — living-room wall and window study

A modular wall and sash-window set for the A+ apartment's 2.75 m ceiling, referenced to `concepts/wall-v1.png` and the selected painterly fixer-upper environment concept. These are provisional assets for a room-level art and gameplay review, not the completed apartment shell.

## Included geometry

All dimensions are metres. Front is **−Y**, Z is up, and exports share a floor-centred origin so a window wall, casing and glazing can be placed together.

| Export | Size / use |
|---|---|
| `ARC_Living_SolidWall_2m.fbx` | 2.00 m wide × 2.75 m high wall, 0.12 m core; includes base and crown trims. |
| `ARC_Living_WindowWall_2p4m.fbx` | 2.40 m wide × 2.75 m high wall and trims around a centered 1.60 m opening, sill 0.90 m / head 2.30 m. Matches the nominal living-room window in A+. |
| `ARC_Window_Casing_Sash.fbx` | Independent 1.86 m overall casing, sill, apron, fixed muntins and sash. |
| `ARC_Window_Glazing.fbx` | Separate window panes so Unreal can use its own glass or exterior-view material. |

The window is static. Opening the sash would require separating its moving parts and assigning pivots; that behavior is not implemented. This module also does not contain curtains, a window view, crack damage, or room-wide architectural return pieces. It is meant to be assembled with the rest of the planned room.

## Texture comparison and repeated-module test

Four independently generated plaster candidates are retained. `plaster-candidate-a.png` has finer and more uniform diagonal strokes; B has broader warm-toned variation. New candidate C is deliberately rose/peach, with strong larger strokes, while new candidate D is neutral warm greige with muted amber and cool notes. C and D have distinct shapes and palette; neither is an edit of the other. Compare `previews/adjacent-modules-c.png` and `previews/adjacent-modules-d.png`, which show the same 2.4 m window-wall and adjoining 2 m solid-wall placed edge-to-edge. **D is the selected provisional plaster:** its color fits the warm existing apartment reference without the distinctly pink cast of C, and its brush size reads across the full 4.4 m sample. `trim-candidate-a.png` remains the cream-painted trim. All textures are color only; brushwork is visual style, with no normal or displacement map.

The generated source images are **not mathematically seamless**, despite asking for seamless tiles. The Blender material instead projects the selected plaster with a continuous world-space X/Z coordinate at 3.2 m per image and uses a mirrored repeat; adjacent modules share the same sampling coordinates, and the mirrored turn avoids a hard edge at each tile boundary. The sample render shows no obvious color discontinuity at the module join, though long runs can reveal mirrored repetition. The module meshes retain their original local UVs, so **the material node graph is essential**. FBX does not carry this mapping into Unreal. Recreate a world-space or rotation-aware equivalent there: project along the plane of each wall using a continuous coordinate, divide by 320 cm, and mirror rather than wrap each UV component. For perpendicular walls use a rotation-aware or triplanar projection; a fixed world X/Z projection only works for walls along X. Confirm the appearance at corners and in the finished room and break up obvious repetitions with separately placed, non-repeating localized wear.

## Glass and exterior preview

The Blender preview uses clear pale-tinted, smooth glass (transmission 1, roughness 0.08, IOR 1.45) and an **unexported preview-only** image card behind the window, drawing the existing project `Art Source/Environment Textures/T_WindowView.png`. This replaces the old opaque gray preview, but the picture card and Blender shader nodes do not carry to the exported FBXs. In Unreal, recreate a low-roughness translucent glass material and use a separate non-shadow-casting exterior-view card or the final external environment; retain any existing day/night brightness behavior. Tune reflections and transparency in the real scene, and inspect for z-fighting around sash/panes. The preview card is not an architectural wall and should not be included in the room mesh or collision.

## Rebuild and validation

From the repository root, run:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/ARC-LIVING-WALL-01/model/build_wall.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/ARC-LIVING-WALL-01/model/validate_fbx.py'
```

All four FBXs passed a Blender round trip with finite vertex positions, face normals and UVs, no zero-area triangles and no zero-area UV triangles. The solid and window wall measured 2.00 × 0.189 × 2.75 m and 2.40 × 0.189 × 2.75 m including projected trim. `build_wall.py` uses render visibility only for its standalone preview; the saved Blender file still contains the solid module.

**Still required in Unreal:** recreate and validate the world-space mirrored material and glass/exterior card, inspect texture and trim seams, window/glazing alignment, actual scale and exterior view, and explicitly author/verify collision around the opening (a single auto-convex hull may fill the window). Recheck full-room layout, lighting, gameplay visibility traces and camera clearance after assembling the shell. The user-requested closet and bedroom wainscoting are separate assets and are not part of this module.
