# PR-OUTLET-01 — separate painterly wall outlet

A cream duplex wall outlet for the dehumidifier storyline. Concept art was generated in the selected B style and shown before modeling. The revised proportions use broad 38 × 35 mm receptacle faces, taller blade slots, D-shaped ground openings, a raised inset plate border and a cream-painted domed fixing screw with a diagonal slot. The matching plug has a smaller tapered brown bakelite body and molded grip ridges. It is a standalone wall asset, separate from the movable appliance and plug.

## Files

- `model/PR_Outlet01.fbx`: combined outlet with `UCX_PR_Outlet01_00` simple collision. The collision is an authoring convenience; configure its trace/collision profile for the intended interaction.
- `model/PR-OUTLET-01.blend`: editable plate, socket faces, shadow backing, screw, source anchors and studio setup. Saved unplugged, without a plug permanently joined to the outlet.
- `model/build_outlet.py`, `model/validate_outlet.py`: headless build and independent fresh-FBX topology, UV, socket-hole and plug-fit checks.
- `previews/outlet-unplugged.png` and `previews/outlet-plugged.png`: neutral studio appearance references. The inserted plug and short cable in the second preview illustrate assembly only.
- `concepts/outlet-and-plug.png` and `concepts/prompts.json`: concept and complete built-in imagegen prompt.
- `interaction-anchors.json`: exact socket poses, insertion axis and matching plug reference.
- `textures/`: self-contained unchanged copies of the established painterly enamel and aged-metal maps.

The matching plug is the single authoritative `PR-DEHUMIDIFIER-01/model/DH_Plug01.fbx`. This kit's plugged preview and validator reference that file; rebuild the dehumidifier first if starting from scripts alone. No duplicate or joined plug is exported with the outlet.

## Dimensions, pivots and connection

Blender metres, Z up, front **−Y**. Mounting origin is at the centre of the plate on its wall datum, **Y=0**. Plate is **7 × 11.5 cm**, with 1.15 cm plate depth projecting into the room. FBX forward −Z/up Y, unit scale applied. A shallow dark backing extends behind the wall datum to make the slots read as deep holes.

The grounded plug points along **+Y into the outlet**. Set its translation to either socket anchor with identity rotation in Blender assembly space:

| Anchor | XYZ, metres |
| --- | --- |
| Upper socket | `(0, −.0147, .022)` |
| Lower socket | `(0, −.0147, −.022)` |

The plug's own pivot is on its seating face; the outlet anchor leaves a 0.2 mm seating seam. Its cable exits at local `(0,−.043,0)`. The blades and ground pin fit the authored openings on either socket; neither plug nor cable is permanently part of the outlet geometry.

The dehumidifier's selected movement behavior is **choose a destination room**. Gameplay will be implemented in a separate thread. Keep outlets fixed in their rooms; runtime code can manage occupancy, power, plug visibility, cable spline and relocation using these anchors. This kit adds no gameplay code, UI, save fields, room placement or runtime wiring.

## Authored material contract

Recreate the PBR materials in Unreal rather than relying on imported FBX Phong materials. All slots use UV0, are opaque/single-sided, and all maps are sRGB. `E = lerp(enamel-albedo.png, enamel-brush.png, .52)`.

| Slot | Albedo | Metallic | Roughness |
| --- | --- | --- | --- |
| `Outlet_Ivory_Painted` | `E × (1.06,1.04,1)` | 0 | .46 |
| `Outlet_Aged_Receptacle` | `E × (.76,.74,.67)` | 0 | .59 |
| `Outlet_Aged_Screw` | `E × (1,.91,.75)` | .12 | .45 |
| `Outlet_Socket_Shadow` | `(.023,.019,.014)` | 0 | .95 |

The preview plug uses PR-DEHUMIDIFIER-01's rubber and aged-hardware contract. Its short lead is illustrative; use `DH_CableSegment01.fbx` with a runtime spline or cable component for arbitrary appliance/outlet separation.

The revised plug housing uses `DH_Plug_Bakelite`: aged-metal image × `(.22,.15,.09)`, metallic 0, roughness .58. The image supplies painterly variation; it does not make the housing metallic. `previews/plug-close.png` shows the taper, grip ridges, punched blades and ground pin independently.

## Validation

Run from repository root with `/Applications/Blender.app/Contents/MacOS/Blender -b --threads 2 --python-exit-code 1 --python`, followed by either script path. The two builders serialize against `/tmp/apartment_blender.lock`.

`validation.json` records a fresh import: finite positions/UV0 with coverage per material, closed outward components, no degenerate triangles/nonmanifold edges, mounting pivot, dimensions, collision identity, six rays passing through the actual socket openings to their deep backing, and zero triangle contacts with the matching plug seated at either socket. Geometry validation does not constitute Unreal or gameplay acceptance.
