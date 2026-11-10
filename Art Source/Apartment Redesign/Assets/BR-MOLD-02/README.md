# BR-MOLD-02 — upper-right closet mold

FIX-001 source replacement for the central green BR-CLOSET-02 mold. Two thin overlay meshes spread neutral charcoal colonies across the upper-right back wall and onto a narrow strip of the adjoining east wall. The original closet source and exports remain unchanged.

## Files

- `textures/mold-colonies-rgba.png`: selected fresh generated variant B, original RGBA preserved. RGB pigment darkness and alpha together define coverage; see material below.
- `concepts/mold-a.png`, `concepts/mold-b.png`: independent generated alternatives, not incremental recolors of the old patch.
- `model/BR_Mold02_Back.fbx`, `model/BR_Mold02_Return.fbx`: overlay planes only. No walls, floors, furniture or collision are exported.
- `model/BR-MOLD-02.blend`: packed contextual preview with the existing closet. Preview geometry must not be imported.
- `model/build_mold.py`: reproducible headless build; loads the adjacent BR-CLOSET-02 source as preview context.
- `model/validate.py`, `model/validation.json`: FBX round-trip checks.
- `assembly.json`: placement, bounds, material contract and interaction guidance.
- `previews/corner-mold.png`, `corner-repaired.png`, `previous-central-mold.png`, `doorway-mold.png`, `inside-closeup.png`: same closet context with replacement, repair state and previous art.

## Placement

Metres, +Z up, front −Y. FBX export uses `axis_forward=-Y`, `axis_up=Z`. Both mesh object origins are `(0,0,0)` and vertex coordinates are in closet assembly space. Place both at the existing closet assembly floor origin, plan `(1.10,4.70,0)`. Tested project importer keeps source X and reverses source Y: `plan=(1.10+sourceX,4.70-sourceY,sourceZ)`. No negative actor scale is needed.

| Plane | Source bounds | Plan bounds (metres) |
|---|---|---|
| Back | X −0.55…1.037, Y 0.837, Z 1.12…2.64 | X 0.55…2.137, Y 3.863, Z 1.12…2.64 |
| East return | X 1.037, Y 0.20…0.837, Z 1.12…2.64 | X 2.137, Y 3.863…4.50, Z 1.12…2.64 |

The planes sit 3 mm ahead of the finished wall faces. Their top is 2.64 m to leave the ceiling/crown clear. Keep two-sided shading on. The return uses a crop of the same texture and shares the seam UV with the back plane. Its last 10 cm fades through vertex-color alpha to avoid a straight clipped outer edge. Import vertex colors (replace), not an all-white override.

## Neutral charcoal material

Do **not** inherit the old olive `Tint` or Blender's green multiplier. Use a fresh material instance/parent for this art.

- Texture: `mold-colonies-rgba.png` (1254 × 1254 original generated RGBA; use normal engine texture-build resampling if power-of-two storage is needed), **sRGB off** (linear sample for the pigment-coverage formula).
- Constant BaseColor, linear RGB: **(0.022, 0.021, 0.020)**.
- Roughness 1; Metallic 0; Specular 0; TwoSided true.
- Compute `gray = dot(Texture.RGB, (0.2126, 0.7152, 0.0722))`.
- Coverage: `VertexColor.A * Texture.A * pow(saturate((0.56-gray)/0.38), 1.35)`.
- In Unreal prefer Masked with DitherTemporalAA using this coverage to preserve stippled semitransparent edges; a plain mask with clip 0.1 is an available preview fallback but changes the soft boundary. Inspect under actual golden lighting.

The generated texture contains a pale wash behind some darker colonies. Raw alpha alone would create a broad solid silhouette. The darkness modulation suppresses that wash so the original wall shows between colonies. Blender uses the exact formula above with continuous alpha. No recolored wall background is baked into the output.

## Interaction / repair handoff

Replace/hide the old central mold overlay rather than leaving it underneath. Attach **both** new overlay actors/components to the existing Malcolm malady using the project's `RepairDamage` and `AuthoredMoldDamage` tags so both disappear on repair. These are decorative planes without collision; do not add room-blocking convex collision.

A suggested raised inspect target is plan **(1.82,3.89,2.16)**, slightly in front of the back wall. Resize the existing inspect bounds to cover the visible colonies, and test a real click from the open-closet approach. Move only the invisible inspect proxy body; do not move the malady actor root. Preserve the world transforms of the existing HunkSpawn, TalkSpot and DialogueCamera. Preserve Malcolm's identity and the bedroom sub-volume. Reposition the glow light separately, roughly 0.50 m out from the wall, to avoid another hotspot.

Source review does not replace in-engine mask, click reachability, encounter and repair-hide validation.

## Rebuild

From this asset folder:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/build_mold.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 --python model/validate.py
```

Generated using the built-in image-generation tool. Prompt intent and selection notes are retained in `concepts/prompts.md`.
