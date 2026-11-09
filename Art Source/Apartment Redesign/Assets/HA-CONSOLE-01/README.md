# HA-CONSOLE-01 — shallow hall console

Vintage walnut console, 1.05 m wide × 0.25 m deep × 0.785 m high for the A+ gallery hallway. The selected `concepts/console-v1.png` already includes front, back, both sides, perspective and open-drawer views, so it is also the modeling reference. The concept is illustrative; dimensions above follow the floor plan.

`textures/walnut-a.png` and `textures/walnut-b.png` were generated independently. B was chosen for broader warm/cool color variation. They are base-color images, not displacement; the painted character is in color. `model/build_console.py` rebuilds the model and renders the closed and open previews; run it in Blender background mode. Drawer interior, brass pull and wood are separate material slots.

`model/HA_CONSOLE_BODY.fbx` and `model/HA_CONSOLE_DRAWER.fbx` use a shared floor origin, Z up, front facing −Y. Slide the drawer along local −Y; the preview uses 0.13 m travel. The physical pull projects just beyond the stated body depth. The front rail and drawer are modeled independently, with a hollow box and lower shelf.

Validation: both FBXs were reimported in Blender 5.2.3; all positions, polygon normals and UVs were finite and no polygon or triangle had near-zero area. `model/validate_fbx.py` reproduces those checks. Unreal import, material appearance, collision, and passage clearance with the drawer open remain untested.
