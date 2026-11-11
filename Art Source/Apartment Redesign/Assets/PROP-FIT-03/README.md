# Fitted entry hangers and hanging pans

Source release for screenshot feedback. Original assets preserved. Rebuild `model/build_props.py`, then run `model/validate.py` with headless Blender. Both export and validation completed; installed acceptance remains with Unreal integration.

`ARC_ClosetStorage03.fbx` retains original ARC-CLOSET-STORAGE-02 shelf, rail, origin and two UCX hulls, removing the old baked hangers. Place three `HA_Hanger03.fbx` instances per closet using source offsets in assembly.json. Hanger origin is the rail centre, not floor; its plane is YZ and its upper hook internally rests on the 12 mm rail. Follow storage actor yaw and source-Y conversion. Reuse bedroom hanger wood and aged steel materials.

`KI_PanPair03.fbx` contains two differently sized hollow iron pans with wooden handles, actual through-holes and engaged S-hooks. Place at original rail wall-centre/bar-height origin, with the rail yaw. Remove both obsolete body/handle pairs and all old hooks; retain only KI_Pan_Rail_Body, never its full hooked assembly. Hole centres and 2.38 mm minimum radial clearance are recorded in assembly.json/validation.json. Both bores are traversed axially by straight hook segments with clear emerging ends. Keep pan iron and walnut image materials; hook is aged metal.

Exports contain no interaction changes. Verify installed wall clearance, rail contact, full shelf support, materials, dressing footprint and absence of old duplicate props. Source preview is evidence for source appearance only.
