# OF-BOOKCASE-01 — office low bookcase

Low open walnut bookcase with two shelf bays and period stepped cap and plinth. The generated concept `concepts/bookcase-multiview-v1.png` shows five views of the empty case. Books, plant and storage box are separate planned dressing: none are baked into this model.

The design measures **1.10 m wide × 0.30 m deep × 0.90 m high**, with Z up and front toward local −Y, floor-centred origin. Plan footprint is `[11.58, 7.05, 0.30, 1.10]` metres; the front faces west into the office. Under the proposed direct plan-to-Unreal XY mapping, locate the case centre at `(11.73, 7.60)` m, and rotate local −Y to plan −X (a −90° yaw for conventional XY rotations). Verify actual world axes, asset import transforms, wall collision, baseboard and clearance before final placement.

`textures/walnut-muted-b.png` is the independently generated muted walnut selected for the revised living-room chest. The Blender material applies saturation 0.68, value 1.35, and roughness 0.88; sparse modeled edge rubs use a separate material. The prior daybed and living-bookcase walnut candidates are retained. Recreate the selected texture and color adjustment in Unreal because FBX does not reproduce Blender's shader graph. `model/OF-BOOKCASE-01.blend` is editable; `model/OF_BOOKCASE_BODY.fbx` is the single case export. Rebuild and render using `Blender -b --python model/build_bookcase.py`; validate using `Blender -b --python model/validate_bookcase.py`.

An independent Blender FBX reimport passed finite vertex/UV, nonzero-area triangle and bounding checks: 1 mesh, 2,304 vertices, 4,512 triangles, 1.10 × 0.3008 × 0.90 m including edge-rub geometry. The studio preview is not an Unreal screenshot. In-engine texture/lighting, collision and shelf dressing remain untested.
