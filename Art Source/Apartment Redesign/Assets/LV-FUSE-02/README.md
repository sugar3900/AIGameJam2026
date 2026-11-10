# LV-FUSE-02 — FIX-030 aged interior

Replace **only the shell** with models/LV_Fuse02_Shell.fbx. Same back/bottom-centre origin, source metres, -Y front. At the approved north-wall recess place (1105.7,-4,152.2)cm yaw0. Original non-wire case, fuse, gasket and fixed hinge geometry and UVs are preserved exactly; the separate original door and damaged/repaired wires stay unchanged. New source removes external wire stubs and clamps; no slot hiding is required.

Eight irregular cloth/dark insulated loops now occupy the top, bottom and side cavities. Four ceramic fuses remain readable; new wiring stays behind the original fuse fronts and door plane. Cloth weave, darkened bakelite, stained ceramic rims and mottled interior metal supply localized ageing. This is separate from engine-owned plaster soot decals and the per-instance wall niche.

## Geometry and acceptance

Fresh FBX validation compares **7477 retained original face position/UV keys** within10 micrometres against LV-FUSE-01. New shell27207 triangles, finite nondegenerate polygons/UVs. New interior bounds x[-.19326,.19432], y[-.09256,-.03974], z[.01972,.56376]m: behind gasket/door and not crossing the four fuse sightlines. Entire shell including original knuckles is x[-.239,.225], y[-.140,0], z[0,.58]. Small original flat wear patches remain; a closed-whole-shell test would be inappropriate for those legacy decorative faces. See fbx-validation.json.

Do not replace LV_FUSE_01_Door, LV_FUSE_01_Wire_Damaged or LV_FUSE_01_Wire_Repaired. The blend retains them for fit previews only, not as new releases. Keep their approved -10cm worldY shift, hinge/pivots/toggle/repair tags. Old assembly and footprint remain valid for the niche and collision split. Shell uses existing complex collision policy. Real door/inspect/Wyatt/repair tests and lit Lumen front/oblique review are required after import.

## Slot mapping — use explicit materials

Do not accept auto Phong defaults or accidentally update unrelated shared materials. Original slot names are retained to make mapping explicit; the three aged interior slots below intentionally get new local material instances.

| Slot | Albedo / linear constant | Metal | Roughness |
|---|---|---|---|
| Painted_Olive_Metal | T_Fusebox_GrayGreen_Painterly_v2.png, existing material | .15 | .83 |
| Interior_Dark_Brown | T_Fuse02_Interior.png | .10 | .88 |
| Inset_Gasket | .075,.070,.055 | 0 | .83 |
| Patinated_Brass | T_Fusebox_AgedBrass.png, existing material | .55 | .45 |
| Edge_Wear_Ochre | .35,.235,.12 | .18 | .80 |
| Bakelite_Dark_Brown | T_Fuse02_Bakelite.png | .06 | .83 |
| Ivory_Ceramic | T_Fuse02_AgedCeramic.png | 0 | .56 |
| Fuse02_AgedCloth | T_Fuse02_Cloth.png | 0 | .80 |
| Fuse02_DarkCloth | .12,.105,.08 | 0 | .80 |
| Fuse02_TarnishedTerminal | .22,.17,.085 | .55 | .65 |

Wire_Brick_Red, Wire_Navy, Wire_Cloth legacy slots remain in the FBX but have no visible replacement-shell polygons. Leave their separate repair-actor materials as already installed. Texture PNGs are sRGB albedos; use directly without extra tint. New materials are opaque, no emissive. Geometry preview uses neutral light; judge overall darkness against actual room lighting.

Build build_fuse.py loads original LV-FUSE-01 blend, modifies a copy in memory and writes only LV-FUSE-02. validate_fbx.py compares fresh old/new FBX imports. No original source, engine or git writes.
