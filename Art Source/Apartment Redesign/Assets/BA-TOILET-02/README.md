# BA-TOILET-02 — fitted vintage toilet (FIX-023)

Additive replacement for BA-TOILET-01. Metres, Z up, front −Y, common floor datum `(0,0,0)`. The old asset is untouched. Retain the approved FIX-007 toilet placement; this is a construction/appearance revision, not another bathroom layout change.

## Construction

The cover follows the fixed seat's oval profile with a flat rear hinge edge and underside bumpers. Brass fixed cheeks, moving barrels and connecting leaves meet on a forward hinge axis. The rear pedestal reaches the floor beneath the cistern, and the tank has a front-mounted brass/ivory paddle lever and a plain removable lid without a top button. A continuous inner bowl descends into a trap throat; the front pedestal is annular so it does not cap that opening. A separate static water surface sits inside the cavity.

The existing independently generated painted-ivory texture is reused directly, without extra colour multiplication. Aged brass, dark trap interior and matte ivory rubber are separate material slots. This retains the cream ceramic look while avoiding a geometry rewrite of the whole apartment style.

## Exact exports and placement

- `model/BA_Toilet02_Body.fbx`: assembled body at floor origin, **21 UCX hulls**. Import through the legacy FBX importer with one convex hull per UCX. Do not combine collision into visible geometry. Body includes the fixed seat, fixed hinge supports and front lever. No flush interaction is added.
- `model/BA_Toilet02_Lid.fbx`: closed cover, moving barrels/leaves and bumpers; pivot **`(0,0.110,0.516)`**, source-local X hinge axis, **1 UCX hull**. This replaces the old `(0,0.125,0.505)` pivot. Preserve the existing `Toilet_Lid` action label and rebind it to this pivot and mesh.
- `model/BA_Toilet02_Water.fbx`: static standing water, origin `(0,0,0)`, top **Z=0.275 m**, elliptical surface radii 0.088/0.109 m centred at source `(0,-0.075)`. No collision or click action. Water stays in the toilet and does not follow lid rotation or repair-hide tags.

Existing FIX-007 assembly transform: body and water at **UE `(555,603,0)` cm, yaw 0**. Source-to-plan `(5.55+sourceX, 6.03-sourceY, sourceZ)`. Lid hinge therefore lands at **UE `(555,592,51.6)` cm**. Use source-assembly geometry correctly: the FBX stores the pivot and an assembled location; do not apply that offset twice when binding the interactive body.

Closed lid rotation is zero. Opening is **−85° about source-local X**. The imported sign must be chosen by the required motion (front edge rises toward the tank), not copied blindly from the old action. The source front-centre hinge-height test point `(0,-0.366,0.516)` moves to approximately `(0,0.06851,0.99019)` at −85°. In plan this is `(5.55,5.96149,0.99019)`. This gives an unambiguous end-pose reference independent of engine Euler conventions. Do not exceed 85° without a new sweep test.

New visual envelope is about 0.510 × 0.713 × 0.921 m. It is inside the former footprint (the removed side lever accounted for extra width). The floor underside now reaches Z=0 rather than leaving the old 8 mm source gap. Re-run exact bounds from `validation/fbx-roundtrip.json`; do not centre the new body by its bounds, which would move the approved assembly origin.

## Material contract

1. `Painted_Ivory_Enamel`: `textures/painted-ivory.png`, sRGB on, direct base colour, roughness 0.36, metallic 0; opaque.
2. `Aged_Brass`: linear base colour `(0.40,0.25,0.11)`, roughness 0.32, metallic 0.72; opaque.
3. `Trap_Interior`: `(0.10,0.087,0.065)`, roughness 0.60, metallic 0; opaque. Only the deep passage termination is dark.
4. `Ivory_Rubber_Bumpers`: `(0.57,0.54,0.46)`, roughness 0.80, metallic 0; opaque.
5. `Toilet_Standing_Water`: use a proper Unreal water material, preferably the existing bucket's still-water treatment, not the FBX Phong fallback. Roughness around 0.09, IOR 1.333, no emissive, restrained opacity and clear refraction so the bowl/trap remain readable. No moving stream, flush effect, decal or large floor puddle is requested. Blender preview uses transmissive water only as an appearance guide; Unreal appearance needs review.

Material names/slot order per mesh are recorded in `validation/fbx-roundtrip.json`; bind by name, not guessed slot numbers.

## Build and validation

Run `/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 --python model/build_toilet.py` from any directory (full script path if necessary). `-- --no-render` skips the four 720×800 CPU previews. Build saves the closed editable blend, three FBXs and analytical report. `model/validate_fbx.py` performs a fresh FBX roundtrip, collision count, finite geometry/UV and zero-area triangle checks. It also casts a centreline ray: body hit must be below Z=0.16, while water is at Z=0.275, proving no hidden pedestal cap fills the visible bowl.

The lid is sampled every degree through 0–85° against the conservative tank-front region; zero tank hits. Open/closed, side and top previews were reviewed. This is source validation, **not Unreal acceptance**: the engine owner must verify real `Toilet_Lid` clicks/open-close, correct hinge sign, full sweep against the body/tank/room door, approved bathroom routes, water appearance under Lumen, and no wall clipping in the north-wall location.
