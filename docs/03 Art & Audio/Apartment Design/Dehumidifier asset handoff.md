# Dehumidifier and outlet asset handoff

Selected design: **B — cream and blue-gray workhorse**. Planned movement: **choose a destination room**. Gameplay is explicitly reserved for a separate thread; this release supplies art and attachment contracts only.

## Source kits

- `Art Source/Apartment Redesign/Assets/PR-DEHUMIDIFIER-01/`: editable Blender source, selected concept B, PBR textures/material values, six FBX exports, attachment metadata, seven studio previews and fresh-import validation.
- `Art Source/Apartment Redesign/Assets/PR-OUTLET-01/`: separate wall outlet, concept generated before modeling, editable source, FBX, texture copies, socket metadata, unplugged/plugged previews and plug-fit validation.

The dehumidifier's full parked assembly is approximately **43 × 37.5 × 53.35 cm**, including folded handle and stored lead. The outlet plate is **7 × 11.5 cm**. Both use the apartment's existing painterly enamel and aged-hardware sources.

## Suggested component assembly

For gameplay, use `DH_Dehumidifier01_Body`, `DH_Dehumidifier01_Tank`, `DH_Dehumidifier01_CordStowed`, and the separate `DH_Plug01`. The combined `DH_Dehumidifier01` is a convenient static preview alternative; do not place it on top of the separate components. Only that combined FBX supplies the simple appliance UCX hull. Configure collision on the gameplay assembly separately.

Body, tank and stored cord have a common floor pivot. The plug has an insertion-face pivot. Use `interaction-anchors.json` for its stored transform. A separate `DH_CableSegment01` is 1 m long along X, with 32 longitudinal subdivisions and 6 mm diameter for spline deformation.

The outlet is `PR_Outlet01`, with a wall-centred mounting pivot and independent upper/lower socket anchors. Its matching plug is the same `DH_Plug01`; no duplicate plug is baked into the outlet.

For an unplugged/relocated state, show the stored lead and plug on the appliance. For a plugged-in state, hide the stored coil, put the plug at the chosen outlet anchor, and connect the appliance's `CordExit` to the plug's cord exit with a runtime spline or cable component. The fixed outlet remains in its room when the appliance relocates. Do not deform the coiled stored-lead mesh into the running cable.

## Import notes

All source coordinates/anchors are **Blender metres, Z up, front −Y**. FBX exports use forward −Z/up Y with applied unit scale. Anchor JSON is in source space; convert units and axes before applying it as Unreal component/world coordinates. Verify the floor/wall pivot and dimensions on import. The plug's source insertion axis is +Y; its seating face is local Y=0.

Recreate the documented PBR materials in Unreal using explicit slot names; default FBX Phong materials do not reproduce the painterly blend. PR-DEHUMIDIFIER-01's blue finish is now `DH_BlueGray_Painted`, replacing the initial working A model's sage slot. The tank window and collected water need renderer-appropriate translucent materials. Disable collision on decorative running cable, plug detail and transparent water where appropriate to the gameplay actor.

No `.uasset`, map placement, runtime interaction, destination selector, occupancy logic, save schema or storyline flags are included. Those belong to the separate gameplay integration.

## Validation

- Dehumidifier: 37,696 triangles, 150 individually closed positive-volume components, all ten material slots have finite nonzero UV0 coverage; zero degenerate triangles/nonmanifold edges. All split exports reconstruct the combined parked bounds, including the plug transform. Bucket pull is clear at 11 positions over 24.5 cm. The spline cable export has verified length/diameter and closed topology.
- Outlet: 4,806 triangles, seven closed positive-volume components, four material slots; zero degenerate triangles/nonmanifold edges. Rays pass through all six actual socket openings to recessed backing. The matching grounded plug seats in either socket with zero triangle contacts at the authored clearance.
- Front, rear, bucket-pulled, handle-raised, unplugged-outlet and plugged-outlet studio views inspected. Validation is source-side; it does not claim in-engine acceptance.

## Concept-fit revision

The outlet now has broader receptacle faces, larger blade slots, D-shaped ground throats, a raised plate field, and a cream-painted domed screw with a diagonal slot. The plug uses a smaller tapered brown bakelite housing, top grip ridges and punched blades; slot/pin spacing changed together and both sockets pass the fit test.

The dehumidifier has a flat angled control area united with its casing. Mounting rings/bezels embed by 0.25 mm, and the switch by 0.75 mm; the source checks reject hovering mounts. Front slats are recessed 10 mm and extend into both ends of the frame. Top vents are unchanged. Side, low and overhead close-ups are included in the source previews.

The front and top grilles share the side panels’ existing `DH_BlueGray_Painted` material: the painterly enamel blend tinted `(.26,.38,.49)`, metallic 0, roughness .56. This replaces the front ivory and top aged-hardware assignments; grille geometry is unchanged.
