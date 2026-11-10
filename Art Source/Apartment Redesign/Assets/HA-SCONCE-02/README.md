# HA-SCONCE-02 — closed opal gooseneck sconce

Source correction for **FIX-008**, preserving the original wall-plate center, facing and three-part assembly contract. The original HA-SCONCE-01 files are unchanged.

## What was wrong

The screenshot is consistent with near-side shade faces disappearing, rather than transparent opal being intentional. The old single-sheet bell has **inward radial normals** (mean radial normal dot −0.893) and **128 boundary edges**. A one-sided Unreal material therefore hides the near surface and shows the bulb and far shell.

There were also genuine source geometry problems: **65 hardware/shade triangle intersections**, located on the projecting arm socket and lower gooseneck, plus a **28 mm gap** between the bulb top and socket bottom. These are measured in `source-audit.json`; the preview renderer rendering both sides had hidden the normal problem.

## Replacement parts

| Existing source part | Replacement file | Treatment |
| --- | --- | --- |
| `HA_Sconce_Hardware` | `models/HA_Sconce02_Hardware.fbx` | Original-style plate, shorter spigot, wall-hugging gooseneck, hollow retaining cup and connected ceramic holder. Optional one-box UCX collision. |
| `HA_Sconce_Shade` | `models/HA_Sconce02_Shade.fbx` | Closed opal bell with inner and outer surfaces, seated cylindrical neck and integrated rounded lip. No collision. |
| `HA_Sconce_Bulb` | `models/HA_Sconce02_Bulb.fbx` | Frosted bulb with a real glass neck seated inside the threaded holder. No collision. |

All three files retain **origin `(0,0,0)` at the wall-plate center**, Blender metres, Z up, front −Y. Apply the existing same world transform to all three components; no recentering, relative offsets or new actor positions. The established engine import keeps X and flips Y. Exact bounds and material slots are in `manifest.json`. Overall scale remains approximately 12.1 cm wide, 14.05 cm projecting from the wall and 20.5 cm tall.

The new shade is a closed manifold with positive signed volume and nominal **2.5 mm radial wall thickness** (about 1.9–2.5 mm normal thickness along the flare). It has no hardware intersections. The nearest sampled shade/arm surface gap is **4.73 mm**. The bell sits 19.5 mm clear of the wall; plate and retaining cup deliberately connect their own hardware components. The bulb now seats through its neck rather than floating. The open lower mouth reveals the bulb only from below; it does not protrude beyond the lip.

## Material and toggle contract

Use **opaque** opal, alpha1, transmission0, regular outward normals and one-sided rendering. Do not fix this by making the shade translucent. Both faces physically exist, so no double-sided workaround is needed. The existing generated `opal-glass.png` and `aged-brass.png` maps are reused unchanged to keep the fixture family consistent.

- Aged brass: `aged-brass.png` as direct sRGB base color, metallic0.60, roughness0.54.
- Opal shade: `opal-glass.png` as direct sRGB base color, metallic0, roughness0.43, opaque. Optional warm controlled emission.
- Bulb: linear base `(0.92,0.82,0.68)`, roughness0.40, metallic0, opaque. Separate controlled emission.
- Ceramic holder: linear base `(0.74,0.69,0.58)`, roughness0.57, metallic0.

`manifest.json` lists exact material-slot order. When a texture is present, it replaces the fallback color rather than multiplying it.

**Keep existing engine actor/component labels and light-toggle actions**, including `Sconce_Kitchen`. Replace meshes on those existing components; do not rename or replace the interaction actor. The source part names only identify replacement FBX files. Hardware stays fixed; shade emission, bulb emission and the existing local light follow the same on/off state. The FBX exports do not contain lights or interaction logic.

The source preview uses shade emission0.65 and bulb3.5 with warm emission RGB `(1,0.66,0.36)` in its on state. It adds a preview point light below the opening at source `(0,-0.08,-0.012)` m, corresponding to local UE `(0,8,-1.2)` cm before actor rotation. These are visual reference values, not engine photometric requirements. Recreate the current engine dynamic-material parameter contract and tune the fixture in the apartment lighting.

## Files and checks

- `build_sconce.py`: reads/audits the old blend, builds the corrected assembly and performs source intersection/manifold checks.
- `source-audit.json`: measured old defects and original source hash.
- `manifest.json`: replacement mapping, origins, bounds, materials and toggle contract.
- `models/HA-SCONCE-02.blend`: packed editable scene with preview wall/lights excluded from exports.
- `previews/sconce-off.png`, `sconce-on.png`, `sconce-front.png`, `sconce-side.png`, `sconce-underside.png`: inspected state and clearance views.
- `validate_exports.py` / `validation.json`: FBX reimport verifies all three origins, finite geometry, UVs, bounds, the hardware UCX hull and the original source hash.

Use headless Blender with `-b -t 2 --python-exit-code 1 --python <script>`. Import the hardware through legacy FBX if using its UCX hull; Interchange previously dropped project UCX. Engine visual review and an actual on/off click remain separate acceptance steps.
