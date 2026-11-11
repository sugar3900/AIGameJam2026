# Fitted kitchen backsplash and counter infills

Replace all stretched old backsplash modules/end caps with four fitted bands. Every FBX uses native metre dimensions and scale1; place each at assembly.json world_origin_cm with yaw0. Source fronts face-Y; established Unreal import flips Y so room-facing tiles project to increasing worldY from wall faceY6. Do not place source review blend world transforms on the FBX again.

Top line117.5cm is 5mm below apron118cm. Tile grid is10cm square, aligned in worldX/Z with cropped boundary tiles. Top uses a rounded ceramic bullnose; only exposed fridge-side end also has bullnose. No lower trim and no caps against sink/range/right wall. Range strip rises from107 to117.5cm.

Runs A112.1–162.5, B267.5–345, Range345–420, C420–474cm. Main runs bottom91cm. Five separate ivory-enamel infills close rear and east9cm gaps and support fridge-side extension112.1–120. Fillers spanZ87–91cm matching existing counter-edge thickness. Review render shows the complete assembly without appliances for fit visibility.

Tiles are static decoration without blocking collision; fillers may use simple box collision. No interaction changes. Backsplash materials retain old glaze texture names; new counter fillers use Counter_Ivory/ivory-enamel.png. Blender texture graphs do not transfer directly: use established Unreal tile/counter materials on named slots. Fresh FBX dimensions/UV validation passes. Engine still must inspect aperture clearance, side joints and real cabinet/appliance motions.
