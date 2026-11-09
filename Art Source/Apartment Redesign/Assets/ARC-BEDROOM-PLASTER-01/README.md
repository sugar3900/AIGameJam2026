# ARC-BEDROOM-PLASTER-01 — bedroom upper plaster

A provisional painterly upper-wall finish for the selected A+ bedroom, designed to sit above `BR-WAINSCOT-01` white wainscoting. It is clean aged plaster: lead-paint damage belongs to the separate wainscot damage overlay, while Malcolm's mold belongs inside the closet. This asset has not been imported into Unreal or tested under in-game lighting.

## Texture directions and selection

Three independently generated full-frame color candidates were compared over four metres of the actual intact wainscot under identical lighting:

- A (`candidate-a-ivory.png`, `previews/comparison-a.png`) is warm peach-ivory with delicate sweeping marks.
- B (`candidate-b-sage.png`, `previews/comparison-b.png`) is subdued sage-cream with fine painterly strokes, and is **provisionally selected**: it contrasts with the white wood without competing with the warm furniture or suggesting damage.
- C (`candidate-c-blush.png`, `previews/comparison-c.png`) is more rose/greige with broader strokes.

The comparison uses two adjacent 2 m finish panels and four wainscot bays. The wainscot and floor are contextual preview assets, not part of the exported module. Brushwork is in albedo only, without physical displacement.

## Geometry, material and assembly

`model/ARC_Bedroom_UpperPlaster_2m.fbx` is a **one-sided, nonstructural, zero-thickness** 2.00 m wide surface, extending from Z=1.10 m (chair rail top) to 2.75 m (nominal ceiling). X runs along the wall; its floor-left origin is at `(0,0,0)` and its front faces **−Y**. It has no openings, collision or wainscot. Cut/clip to openings and room width when assembling, or apply the material directly to the structural wall above the wainscot. If overlaying an existing wall, offset very slightly toward the room to avoid z-fighting and do not create duplicate collision. Put crown and openings in their own kits.

The source PNGs are **not proven seamless**. The Blender preview samples the selected image with a mirrored continuous world-position X/Z projection at 3.2 m per image. This removes the hard edge at the adjacent module join, but mirror symmetry can appear over long runs. The FBX UVs alone are local planar coordinates and Blender's position/mirror nodes do **not** transfer as a finished Unreal shader. In Unreal, reconstruct a continuous wall-tangent/height projection at 320 cm per image with mirrored repeat; preserve continuity between modules and rotate the projection correctly on perpendicular walls. A fixed world X/Z projection is unsuitable for walls perpendicular to X. Check corners, seams, scale and repeated pattern in the assembled bedroom and introduce independent local variation if necessary.

## Rebuild and verification

Run from the repository root with Blender 5.2.3 LTS:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/ARC-BEDROOM-PLASTER-01/model/build_plaster.py'
/Applications/Blender.app/Contents/MacOS/Blender -b --python 'Art Source/Apartment Redesign/Assets/ARC-BEDROOM-PLASTER-01/model/validate_fbx.py'
```

The exported FBX reimport passed geometry, finite coordinate and UV tests, nonzero triangle and UV area, 2.00 × 1.65 m bounds and −Y normal orientation. The 4 m contextual test has no obvious vertical seam at the 2 m join in the Blender render; it does not prove all corner rotations or full-room repetition. Recreate the material and test in Unreal with the bedroom lighting, structural walls, trim, windows and real camera before accepting it.
