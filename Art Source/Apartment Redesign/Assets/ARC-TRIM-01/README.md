# ARC-TRIM-01 — period painted trim kit

Three matching straight one-metre period trim strips, modeled in metres and Z-up. The selected multi-view concept and two independently generated paint candidates are included. The `trim-junction.png` studio preview shows actual mitered baseboard and crown meeting at an inside corner, plus a short vertical casing sample. `crown-inside-close.png` and `baseboard-inside-close.png` show the joins close up. Preview walls and floor are context only.

| Export | Nominal dimensions, length × projection × height/width |
|---|---|
| `model/Baseboard_1m.fbx` | 1.00 × 0.030 × 0.130 m |
| `model/Crown_1m.fbx` | 1.00 × 0.035 × 0.100 m |
| `model/Casing_1m.fbx` | 1.00 × 0.026 × 0.080 m |

Each strip runs from X=0 to X=1 m; its origin is the bottom/back/start at (0,0,0), with wall surface at Y=0 and trim projecting toward negative Y. Casing runs along X in the exported file; rotate it for jambs. Crown uses the same local bottom/back/start convention; place its bottom 0.10 m below the ceiling. The `.blend` includes an arranged preview scene, while the exported FBXs contain individual isolated strips. The procedural generator `model/build_trim.py` rebuilds the exports and preview.

The original `_1m` strips have square ends. For a 90-degree inside corner use `Baseboard_Inside_End.fbx` with `Baseboard_Inside_Start.fbx`, or the corresponding Crown pair. In Blender coordinates, place the End at `(0,0,z)`, the Start at `(1,0,z)` and rotate the Start -90° around Z. The angled mating profiles coincide at the interior corner; verify FBX axis conversion in Unreal. Each variant is one metre nominal along the wall; cut or extend the opposite square end to fit the wall. Mitered **outside corners and casing corners are not included**. Trim/cut those and inspect each junction; avoid blindly scaling the cross-section. Scaling length also stretches its texture: repeat or adjust UV scale. The generic casing is a straight piece; door and window assets have their own frames, so avoid doubled casing.

`paint-A.png` and `paint-B.png` are independently generated candidates. B was chosen for its subtle nondirectional brushwork. The Blender shader mixes the selected texture at 64% with warm neutral `(0.82, 0.76, 0.65)` at 36%, roughness 0.84; recreate or adjust this material in Unreal because FBX will not faithfully carry the node graph. The generated texture is not certified seamless, and trim UVs repeat once per metre; check seam visibility and paint appearance in a lit room. This is restrained surface aging, not the bedroom's separate lead-paint damage overlay.

`model/validate_fbx.py` independently reimports all three FBXs and checks dimensions, UV existence/finite values, finite vertex coordinates, and nonzero triangle areas. Passed: straight and mitered baseboard 28 triangles each, crown 40 each, casing 36. `model/validate_miters.py` also reimports both matched pairs, rotates/translates them to a 90° corner and checks matching edge coordinates (8 baseboard and 11 crown profile vertices). Unreal import, light response, collisions, long-run texture continuity and exact corner/jamb fits remain untested.
