# BA-TUB-WATER-01 — revealable bath-water surface

Status: **provisional visual pass; Unreal integration and gameplay tests pending**. This is a separate, non-colliding water surface for the existing `BA-TUB-01` bathtub and its **Run the bath** reveal. `concepts/empty-filled.png` is the generated before/after visual goal; `previews/tub-empty.png` and `previews/tub-filled.png` render the actual exported geometry in the imported original tub. `textures/water-cool-b.png` is the selected painterly blue-green water color texture. `water-cool-a.png` is an independently generated greener alternative, and `water-painterly.png` is the original warmer candidate; all are color maps, not simulations or displacement maps.

## Export and precise placement

- `model/BA_TUB_WATER_Surface.fbx` is the **water-only** mesh. The tub shown in previews and included as an inspection reference in the `.blend` is not part of this FBX. `model/BA-TUB-WATER-01.blend` is the editable source and `model/build_water.py` regenerates the FBX and before/after previews.
- The source uses Blender metres, Z up and the same **floor-centred assembly origin** as `BA-TUB-01`; tub length is local X and its front faces local −Y. Place the water and tub with the same transform and scale, after checking the Unreal FBX axis/unit conversion and imported origin. The exported water origin is `(0,0,0)` at the tub floor datum, **not** at the water surface. Do not add the waterline height twice.
- The perimeter is sampled using 128 radial ray casts against the **imported `BA_Tub.fbx` interior shell** at local Z=0.430 m. It is inset 0.018 m from the sampled interior wall; the rim is at 0.570 m. The surface bounds are approximately **X −0.7181 to +0.7181 m, Y −0.2292 to +0.2292 m, Z 0.4289 to 0.4311 m**. Tiny interior ripples taper to zero at the perimeter. This is a fixed partial fill; no rising-water animation is authored.
- `model/validate_water.py` reimports both FBXs and checks finite geometry/UVs, triangle area and every water vertex against the actual basin shell. `model/validation.txt` records 2,561 vertices, 4,992 triangles and minimum sampled radial wall clearance 0.018 m. The check is in Blender's imported assembly space and does **not** prove Unreal transforms, water depth sorting, interaction or collision.

## Unreal setup

1. Import the water FBX as a separate static mesh component/actor. Put it at exactly the tub assembly transform, verify orientation and units, and disable collision and shadow casting unless explicitly needed. Keep it hidden while the bath is empty; reveal it for **Run the bath**, and hide it again on reset. Persistence and any faucet linkage are game-code concerns, not contained in the FBX.
2. Recreate the material: assign `water-cool-b.png` as an sRGB color texture using the included UVs. The Blender preview uses Principled roughness 0.19, metallic 0.03, transmission 0.08 and alpha 0.92 under warm light; these are visual reference values, **not** calibrated Unreal shader parameters. Start with a lightly tinted translucent surface and restrained specular highlights; tune opacity and exposure against the real room. A subtle opaque/masked fallback may be preferable if translucency sorting or performance fails. Do not interpret alpha or Blender shader nodes as automatically imported gameplay-ready material.
3. Inspect at oblique and top-down camera angles. The 18 mm perimeter inset avoids intersecting the sloped enamel basin, but may leave a visible gap depending on camera and material. Adjust with the actual tub if needed; do not widen blindly or overlap the rim. Check against the drain, shower curtain and player camera. Confirm no z-fighting, visible exterior spill, or unwanted translucent depth sorting. The texture is one full-surface map and is not asserted seamless or tileable.
4. Exercise the reveal with empty/filled states, any on/off control, save/load/reset as appropriate and actual camera lighting. Capture evidence in-engine; none of these have been tested here.

## Generation and reproduction

The concept was generated with the built-in image tool using the approved painterly fixer-upper and existing tub preview as references: same empty and partially filled tub, calm clear water below the rim and no people. The first water texture was generated separately from the approved environment reference. After review found the filled preview too beige, two independent blue-green alternatives were generated; B was selected for stronger cool-water readability with gentle warm reflections. The Blender preview lowered transmission and raised alpha to preserve that contrast under warm lighting.

From the repository root run:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python 'Art Source/Apartment Redesign/Assets/BA-TUB-WATER-01/model/build_water.py'
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python 'Art Source/Apartment Redesign/Assets/BA-TUB-WATER-01/model/validate_water.py'
```
