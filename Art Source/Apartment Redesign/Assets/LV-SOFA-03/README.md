# Sofa throw contact correction

Replacement `model/LV-SOFA-03.fbx` preserves actor floor-centre origin, axis convention, all upholstery/frame/feet and 13 UCX hulls from LV-SOFA-02. Cloth is shifted forward of the rear cushions and supports queried against both seat/arm and back/decorative cushions. The fresh FBX import validator checks finite mesh/UVs, hulls, previous footprint and BVH intersections against arm, seat, back and decorative pillows; all pass.

Use existing sofa material mappings by slot. For `Sofa02_WovenThrow`, bind the existing LV-SOFA-02 `textures/throw-wool.png`, multiply base colour by linear (.58,.49,.36), roughness .90 and retain modest weave bump. This is essential: FBX does not transfer the Blender multiply node, and plain white material does not meet the request. The new `assembly.json` includes this contract.

Rebuild `model/build_sofa.py`, then `model/validate.py` with headless Blender. Source preview `previews/sofa-context.png` demonstrates revised drape and oatmeal colour. Final installed material/clearance acceptance remains with integration.

Final installed-review correction: the rear cloth edge now remains ahead of the rear cushion, preventing the support ray from lifting a free corner onto the tall back. Throw maximum height is 0.8535 m; validation rejects unsupported lifting above 0.88 m. All six cushion/arm intersection checks still return zero. Same 13 hulls, actor root and material slots.

Export UV correction: every source member now uses the same first UV layer name before joining. This prevents the cloth UVs from ending up only in a secondary channel while UV0 collapses. Fresh FBX validation explicitly requires both throw UV0 axes to span more than 0.9; the corrected export passes.
