# Cabinet front fit revision

Release replaces only four lower doors and four drawers from JOINERY-02/03. Body carcasses, range fillers, sink-side stationary filler and all functional pivots remain installed. Use assembly.json replacement mapping; KI_Cab05 files export pivot-local identity using the established -Z-forward/Y-up convention. Source X remains engine X and source Y flips in engine.

Door painted-frame tops are 67.2cm, giving 3mm clearance beneath drawer bottom67.5cm. Drawer painted-front widths and centers exactly match their corresponding lower painted frames. Drawer boxes remain their original dimensions/positions. Knobs/pulls, finishes, lower-door bottoms and hinge positions retained. The narrower sink-side leaf from JOINERY-03 remains narrow, and its drawer now matches it. Keep its stationary filler attached to the body.

Fresh FBX import confirms eight visual meshes with UVs and authored UCX. Source101-pose sweep per door clears own carcass, existing sink and stationary filler where applicable. These tests do not replace engine neighbouring-range/full-scene sweeps, drawer clicks or appearance review. Source renders show closed/open assemblies; no claim of engine acceptance.

Run validate_kitchen.py in headless Blender after rebuilding all three kitchen kits. It checks this release plus KI-BACKSPLASH-02 and KI-RANGE-02.
