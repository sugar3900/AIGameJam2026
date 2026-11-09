# ARC-DOOR-02 — fitted 0.99 m clear door

Rebuilt from ARC-DOOR-01 using the same painted materials and fixed hardware/profile dimensions. New clear width0.99 m, rough width1.05 m, rough head2.14 m, clear head2.11 m. Leaf0.976 m wide and2.094 m tall; 7 mm nominal side gaps. Jamb lining30 mm, partition120 mm; casing extends outside wall cut. Source coordinates Z up, front−Y. FBX uses original default −Z forward/Y up conversion; confirm actual facing in Unreal rather than assuming source yaw.

Frame origin is opening-centre floor. Leaf FBX origin is its hinge; closed source placement relative to frame is (-0.495,-0.035,0). Keep positive unit scale. Source preview opens -80 degrees about Z; engine sign/handing must be confirmed for each doorway. Rotate the whole assembly to put hinge at the approved jamb. Each FBX includes named UCX hulls: separate frame members and one leaf slab. No frame collision crosses the opening. Leaf handle keeps its original physical size.

Build with Blender headless --python model/build_door.py. Closed/open previews and packed .blend included. Original source is unchanged. Parent render and FBX reimport review passed. Independent review found a hinge-axis offset, now corrected in geometry/pivot, collision and preview motion. See assembly.json for exact offsets; engine sweep and trim fit remains required.
