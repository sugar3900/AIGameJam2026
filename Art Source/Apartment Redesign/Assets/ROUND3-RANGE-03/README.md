# ROUND3-RANGE-03 — vintage controls, oven construction and recessed base

Additive source revision for the body and moving oven door. Original KI-RANGE-01/02 files are unchanged. `model/build_range03.py` reuses the established cooktop/casing/oven-rack construction, develops the controls/door/base and exports two FBXs, the editable blend and closed/open previews. Run `model/validate_range03.py` for independent fresh-import checks.

## Design changes

Four larger 44 mm fluted bakelite grips sit on stepped steel escutcheons, with ceramic centers, dark pointers, an off mark and graduated fan scales. They project **14.65 mm farther forward** than the old tiny steel cylinders; this deliberate change gives the knobs a believable grip. Centers remain in the existing control strip.

The oven door is a continuous pressed enamel frame surrounding a real window aperture, replacing the old solid slab hidden behind the pane. The recessed pane has outer gasket/steel trim, a separate inner frame, inner screws and heat seals. Bowed handles sit on small plates and short supports; the oven pull has a dark heat-safe central grip. The full-depth black floor block is replaced by a recessed support frame and adjustable metal feet.

The four-burner arrangement, grates, burner wells and kettle support are retained because their spacing and construction already work with this stove. That is a design choice; controls, the window and base received the larger changes. All upper-body geometry above z .9 m is checked byte-position-equivalent after fresh FBX import against KI-RANGE-02.

## Import and interaction contract

| Part | FBX | Source origin |
| --- | --- | --- |
| Fixed body | `model/KI_RANGE03_Body.fbx` | `(0,0,0)` m |
| Moving door | `model/KI_RANGE03_Door.fbx` | physical hinge `(0,-.363,.23)` m |

Both export with **forward -Z / up Y**, metres, matching KI-RANGE-02. Import each combined, use the same component-local transforms and replace both body and door. Exact bounds/slots are in `assembly.json`.

- Body actor stays `(382.5,50.03,0)` cm. Body X `±.375` m, back Y `.35`, height `1.07` remain unchanged; front Y changes from `-.3815` to `-.39615` m at the knob pointers.
- Oven interaction root stays `(382.5,88.03,22)` cm with the existing attachment offset. The source door hinge is unchanged. Door outer bounds remain X `±.330`, Z `.216… .720` m; its front Y `-.425897` is within the old `-.426` envelope.
- The installed rig rotates the floor/assembly-space imported mesh about source `(0,−.38,.22)` m, **not** the FBX object's authored `(0,−.363,.23)` origin. Its root is `(382.5,88.025,22)` cm, pivot-relative transform is identity, Body relative location is `(0,−38,−22)` cm and rotation is zero. Keep that rig unchanged; UE roll +85° corresponds to source +X rotation. Source→engine positions are `(x,−y,z) × 100`.
- Existing burner click root `(400.5,65.03,93.1)`, flame, light and kettle origin `(367,61.03,91)` cm stay where they are. No burner, kettle, lid or flame geometry is included here.
- Reuse existing fixed-body and moving-door collision and interactive settings. No new UCX or blocking collision is supplied. Recheck the real oven click/open/close, neighbouring doors, burner and kettle after integration.

## Material contract

The flat grey FBX material is not the authored steel finish. Bind each slot by its exact name and wire the image/tint below. All images use explicit UV0 and sRGB. Copied textures are self-contained: range enamel from KI-RANGE-02, brushed steel from KI-KETTLE-01, fine iron grain from KI-PAN-01.

| Slot | Appearance | Metallic | Roughness |
| --- | --- | --- | --- |
| `Enamel_Painted` | `range-enamel.png`, existing cream palette, no old orange Phong multiplier | 0 | .49 |
| `Range03_AgedSteel` | `aged-steel.png` × `(.72,.76,.78)` | .78 | .34 |
| `Range03_Bakelite` | `iron-grain.png` × `(.42,.34,.28)` | .04 | .36 |
| `Range03_CeramicMarkings` | `range-enamel.png` × `(1.05,1.05,1.01)` | 0 | .40 |
| `Range03_OvenGlass` | dark tint `(.085,.075,.061)`, IOR 1.46, source transmission .38 | .13 | .23 |
| `Oven_Dark` | dark interior `(.082,.065,.052)` | 0 | .50 |
| `Burner_Cast_Iron` | existing dark cast iron `(.075,.067,.060)` | .25 | .80 |
| `Gasket` | dark heat seal `(.13,.115,.09)` | 0 | .80 |

The pane can use a dark translucent Unreal glass material to reveal the real aperture/oven cavity subtly; evaluate tint/reflection in the installed scene. It has no emissive. Keep enamel/metal/bakelite/marking/gasket surfaces single-sided. Imported Blender node graphs require explicit Unreal materials.

## Verification

Fresh FBXs are checked for finite vertices, no degenerate triangles, one meaningful finite UV0 across every slot, and positive signed volume for **each** closed connected component. A front ray through the window center hits its pane rather than an enamel slab. Twenty-one samples through the full 82° opening preserve the 45 mm lateral gap to adjacent cabinet envelopes and keep the door above the floor. These source checks complement engine click/door-neighbour/flame/kettle regressions; they do not claim runtime acceptance.

## Rear hinge clearance correction

The initial RANGE03 frame's 3 mm edge bevel left more material at its lower rear than the old slab's 12 mm bevel. Fresh FBXs reproduced the engine result exactly on the actual rig: RANGE01/02 contacted the fixed hinge mounts at 6/21 poses (0…21.25°); initial RANGE03 extended to 8/21 (0…29.75°). The extra 25.5° and 29.75° intersections were exclusively `Enamel_Painted` pressed-frame triangles against the two retained `Burner_Cast_Iron` hinge mounting plates. They were not caused by the lower drawer, handle supports, gasket or glass.

The plates occupy X `±(.2575….3225)`, Y `−.351…−.333`, Z `.2075….2525` m. For example, at 29.75° initial body triangle 8216 intersected door triangle 612 around X `.31950….32093`, Y `−.35013…−.34981`, Z `.25115….25210` m. `contact-audit-before.json` retains the full pre-correction triangle/island evidence and RANGE01/02 comparison; hashes identify the audited initial RANGE03 exports. Moving the rig to the authored origin was also tested and increased contact to 21/21 poses, so that change was rejected.

Two concealed rear-bottom hinge pockets now remove that unwanted frame penetration. Each cutter is 70 × 40 × 38 mm, centered at X `±.29`, Y `−.337`, Z `.239` m. The pockets retain a **31 mm front skin**, 2.5 mm lateral clearance on either side of each hinge plate, and the original front silhouette/aperture. The builder initializes the original frame UVs before cutting and asserts that all **896 visible front UV corners remain identical**. Fresh FBX comparison independently confirms those same front UV/geometry corners, all non-enamel moving-door positions/materials, and all fixed-body positions/materials. Rebuilt UVs outside the frame differ by at most 0.0000001 per component, within the 0.0000002 comparison tolerance (`hinge-relief-fbx-invariants.json`).

Run `model/audit_hinge_contacts.py` in a fresh Blender process after the regular validator. On the unchanged installed pivot, corrected RANGE03 contacts only **3/21 poses**: 0°, 4.25° and 8.5°. These are the retained barrel/plate intersection and, only when closed, the compressible lower gasket touching the mount; the pressed frame never intersects either plate. Every sample **12.75°…85°** is clear, including both regression angles. An additional half-degree sweep is clear from **10°…85°** (last contact at 9.5°). Exact remaining island bounds, material identities, triangle pairs and all dense samples are in `contact-validation.json`. The open preview uses the same actual hinge at 85°.

`model/verify_hinge_relief_invariants.py` can repeat the before/after invariant comparison when given retained initial FBXs via Blender arguments `-- --before-body <file> --before-door <file>`. The audited initial file hashes are recorded in `contact-audit-before-hashes.json`.

The two replacement FBXs keep their names, source origins, material slots and actor/component contracts. No engine hinge/offset change is required. Reimport `KI_RANGE03_Door.fbx` (the fixed body's geometry is unchanged), then repeat the engine sweep and real open/close click.
