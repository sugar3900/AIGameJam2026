"""
Builds /Game/ICanFixHim/Maps/L_Apartment from code: a stylized four-room apartment
("12 Heartbreak Lane") made of engine primitives, with lights, rooms, interactables
and the four malady fixtures that hold the hunks.

Coordinates are centimetres, floor at Z=0, north = +X. Layout (top-down):

    X=1400 +-------------------+------------------+
           |  KITCHEN (Lukey)  | BATHROOM (Tyler) |
    X=800  +--------door-------+-------door-------+
           |  LIVING (Wyatt)   | BEDROOM (Malcolm)|
    X=0    +-------------------+------------------+
          Y=0               Y=650              Y=1100

Run inside the editor. Rebuilds the map from scratch each time (idempotent).
"""
import math
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()

MAP = "/Game/ICanFixHim/Maps/L_Apartment"
PALETTE_DIR = "/Game/ICanFixHim/Materials/Palette"

CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
CYL = unreal.load_asset("/Engine/BasicShapes/Cylinder")
SPHERE = unreal.load_asset("/Engine/BasicShapes/Sphere")
FLAT = unreal.load_asset("/Game/ICanFixHim/Materials/M_FlatColor")
TRANS = unreal.load_asset("/Game/ICanFixHim/Materials/M_Translucent")

H = 300.0   # wall height
T = 20.0    # wall thickness

# ---------------------------------------------------------------------------
# Palette (material instances are real assets so they can be tweaked in-editor)

COLORS = {
    "WallCream": (0.93, 0.87, 0.80),
    "WallBlush": (0.96, 0.74, 0.78),
    "WallMint": (0.70, 0.88, 0.78),
    "WallSky": (0.74, 0.84, 0.95),
    "WallLavender": (0.78, 0.71, 0.90),
    "Ceiling": (0.96, 0.95, 0.93),
    "Trim": (0.98, 0.97, 0.95),
    "FloorWood": (0.50, 0.31, 0.18),
    "FloorTile": (0.88, 0.86, 0.80),
    "FloorBath": (0.94, 0.90, 0.92),
    "FloorCarpet": (0.55, 0.45, 0.62),
    "Grass": (0.30, 0.55, 0.25),
    "Rug": (0.95, 0.45, 0.62),
    "RugBlue": (0.40, 0.58, 0.85),
    "Velvet": (0.80, 0.20, 0.38),
    "VelvetDark": (0.62, 0.12, 0.28),
    "Wood": (0.55, 0.35, 0.20),
    "WoodDark": (0.32, 0.19, 0.11),
    "White": (0.95, 0.95, 0.95),
    "Black": (0.04, 0.04, 0.05),
    "Steel": (0.62, 0.64, 0.68),
    "Brass": (0.85, 0.65, 0.30),
    "Mint": (0.45, 0.80, 0.70),
    "Butter": (0.98, 0.88, 0.55),
    "Lilac": (0.70, 0.55, 0.85),
    "Teal": (0.20, 0.55, 0.60),
    "Coral": (0.98, 0.50, 0.42),
    "Leaf": (0.25, 0.60, 0.30),
    "Bark": (0.35, 0.22, 0.12),
    "Plum": (0.30, 0.10, 0.28),
    "PinkTile": (0.98, 0.55, 0.72),
}
EMISSIVE = {
    "LampGlow": ((1.0, 0.92, 0.75), (6.0, 5.0, 3.5)),
    "Mirror": ((0.75, 0.85, 0.92), (0.15, 0.18, 0.22)),
}
_mic_cache = {}


def mic(name):
    if name in _mic_cache:
        return _mic_cache[name]
    path = f"{PALETTE_DIR}/MI_{name}"
    if EAL.does_asset_exist(path):
        mi = EAL.load_asset(path)
    else:
        mi = ASSETS.create_asset(f"MI_{name}", PALETTE_DIR, unreal.MaterialInstanceConstant,
                                 unreal.MaterialInstanceConstantFactoryNew())
    if name == "Glass":
        MEL.set_material_instance_parent(mi, TRANS)
        MEL.set_material_instance_vector_parameter_value(mi, "BaseColor", unreal.LinearColor(0.75, 0.9, 1.0, 1))
        MEL.set_material_instance_scalar_parameter_value(mi, "Opacity", 0.18)
    else:
        MEL.set_material_instance_parent(mi, FLAT)
        if name in EMISSIVE:
            base, emis = EMISSIVE[name]
        else:
            base, emis = COLORS[name], (0, 0, 0)
        MEL.set_material_instance_vector_parameter_value(mi, "BaseColor", unreal.LinearColor(*base, 1))
        MEL.set_material_instance_vector_parameter_value(mi, "Emissive", unreal.LinearColor(*emis, 1))
        rough = 0.35 if name in ("Steel", "Brass", "Black", "PinkTile", "White") else 0.7
        MEL.set_material_instance_scalar_parameter_value(mi, "Roughness", rough)
    EAL.save_loaded_asset(mi)
    _mic_cache[name] = mi
    return mi


def lc(rgb):
    return unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0)


# ---------------------------------------------------------------------------
# Spawning helpers

def rot(yaw=0.0, pitch=0.0, roll=0.0):
    return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)


def prim(label, center, size, color, folder, mesh=CUBE, yaw=0.0, pitch=0.0, roll=0.0, collide=True):
    """Static mesh primitive. Engine basic shapes are 100cm and centred."""
    a = EAS.spawn_actor_from_object(mesh, unreal.Vector(*center), rot(yaw, pitch, roll))
    a.set_actor_label(label)
    a.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    a.set_folder_path(folder)
    smc = a.static_mesh_component
    smc.set_material(0, mic(color))
    if not collide:
        smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return a


def box_minmax(label, lo, hi, color, folder, collide=True):
    c = [(lo[i] + hi[i]) / 2.0 for i in range(3)]
    s = [abs(hi[i] - lo[i]) for i in range(3)]
    return prim(label, c, s, color, folder, collide=collide)


def wall(label, axis, fixed, a0, a1, color, openings=(), folder="Structure/Walls"):
    """
    Wall running along `axis` ('x' or 'y') at the fixed other coordinate, from a0 to a1.
    openings: (start, end, z_bottom, z_top) along the wall; doors use z_bottom = 0.
    """
    ops = sorted(openings)
    pieces = []
    cur = a0
    for (s, e, zb, zt) in ops:
        if s > cur:
            pieces.append((cur, s, 0.0, H))
        if zb > 0:
            pieces.append((s, e, 0.0, zb))
        if zt < H:
            pieces.append((s, e, zt, H))
        cur = e
    if cur < a1:
        pieces.append((cur, a1, 0.0, H))
    for i, (s, e, zb, zt) in enumerate(pieces):
        if axis == "x":
            lo, hi = (s, fixed - T / 2, zb), (e, fixed + T / 2, zt)
        else:
            lo, hi = (fixed - T / 2, s, zb), (fixed + T / 2, e, zt)
        box_minmax(f"{label}_{i}", lo, hi, color, folder)
    # Trim around openings so doors and windows read clearly.
    for j, (s, e, zb, zt) in enumerate(ops):
        trims = [(s - 4, s + 4, zb, zt), (e - 4, e + 4, zb, zt), (s - 4, e + 4, zt - 4, zt + 4)]
        if zb > 0:
            trims.append((s - 4, e + 4, zb - 6, zb + 2))
        for k, (ts, te, tz0, tz1) in enumerate(trims):
            if axis == "x":
                lo, hi = (ts, fixed - T / 2 - 2, tz0), (te, fixed + T / 2 + 2, tz1)
            else:
                lo, hi = (fixed - T / 2 - 2, ts, tz0), (fixed + T / 2 + 2, te, tz1)
            box_minmax(f"{label}_Trim{j}_{k}", lo, hi, "Trim", folder + "/Trim")
        if zb > 0:  # window glass
            if axis == "x":
                lo, hi = (s, fixed - 1, zb), (e, fixed + 1, zt)
            else:
                lo, hi = (fixed - 1, s, zb), (fixed + 1, e, zt)
            g = box_minmax(f"{label}_Glass{j}", lo, hi, "Glass", folder + "/Glass", collide=True)
            g.static_mesh_component.set_material(0, mic("Glass"))
            g.static_mesh_component.set_cast_shadow(False)


def interactable(label, loc, yaw, room, body_mesh, body_loc, body_size, color, toggle,
                 prompt_off, prompt_on, body_rot=(0, 0, 0), offset=None, rotation=None,
                 on_emissive=None, light_loc=None, light_color=None, light_intensity=None,
                 reveal=None, cls=None, folder=None):
    cls = cls or unreal.FixHimInteractable
    a = EAS.spawn_actor_from_class(cls, unreal.Vector(*loc), rot(yaw))
    a.set_actor_label(label)
    a.set_folder_path(folder or f"Interactables/{room}")
    a.set_editor_property("room_id", room)
    body = a.get_editor_property("body")
    body.set_static_mesh(body_mesh)
    body.set_relative_location(unreal.Vector(*body_loc), False, False)
    body.set_relative_rotation(rot(*body_rot), False, False)
    body.set_relative_scale3d(unreal.Vector(body_size[0] / 100.0, body_size[1] / 100.0, body_size[2] / 100.0))
    a.set_editor_property("body_color", lc(COLORS[color]))
    a.set_editor_property("toggle", toggle)
    a.set_editor_property("prompt_off", prompt_off)
    a.set_editor_property("prompt_on", prompt_on)
    if offset:
        a.set_editor_property("toggle_offset", unreal.Vector(*offset))
    if rotation:
        a.set_editor_property("toggle_rotation", rot(*rotation))
    if on_emissive:
        a.set_editor_property("on_emissive", unreal.LinearColor(*on_emissive, 1))
    light = a.get_editor_property("light")
    if light_loc:
        light.set_relative_location(unreal.Vector(*light_loc), False, False)
    if light_color:
        light.set_editor_property("light_color", unreal.Color(*light_color, 255))
    if light_intensity:
        a.set_editor_property("light_intensity_on", light_intensity)
    if reveal:
        rp = a.get_editor_property("reveal_part")
        rp.set_static_mesh(reveal["mesh"])
        rp.set_relative_location(unreal.Vector(*reveal["loc"]), False, False)
        rp.set_relative_scale3d(unreal.Vector(*[v / 100.0 for v in reveal["size"]]))
    return a


def malady(label, hunk_id, style, loc, yaw, room, body_mesh, body_loc, body_size, color,
           fx_offset=(0, 0, 0), hunk_spawn=(140, 0, 0), talk_spot=(300, 0, 0)):
    a = interactable(label, loc, yaw, room, body_mesh, body_loc, body_size, color,
                     unreal.InteractToggle.NONE, "Inspect", "Inspect", cls=unreal.FixHimMalady,
                     folder=f"Maladies")
    a.set_editor_property("hunk_id", hunk_id)
    a.set_editor_property("style", style)
    a.set_editor_property("fx_offset", unreal.Vector(*fx_offset))
    a.get_editor_property("hunk_spawn").set_relative_location(unreal.Vector(*hunk_spawn), False, False)
    a.get_editor_property("hunk_spawn").set_relative_rotation(rot(0), False, False)
    a.get_editor_property("talk_spot").set_relative_location(unreal.Vector(*talk_spot), False, False)
    a.get_editor_property("talk_spot").set_relative_rotation(rot(180), False, False)
    return a


def room(room_id, name, x0, x1, y0, y1, color, entry, entry_yaw):
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    a = EAS.spawn_actor_from_class(unreal.FixHimRoom, unreal.Vector(cx, cy, 150), rot())
    a.set_actor_label(f"Room_{room_id}")
    a.set_folder_path("Rooms")
    a.set_editor_property("room_id", room_id)
    a.set_editor_property("display_name", name)
    a.set_editor_property("map_color", lc(COLORS[color]))
    a.get_editor_property("bounds").set_box_extent(unreal.Vector((x1 - x0) / 2.0, (y1 - y0) / 2.0, 150), True)
    ep = a.get_editor_property("entry_point")
    ep.set_world_location(unreal.Vector(entry[0], entry[1], 100), False, False)
    ep.set_world_rotation(rot(entry_yaw), False, False)
    return a


def point_light(label, loc, intensity_lm, color=(255, 236, 214), radius=900, shadows=True, folder="Lighting"):
    a = EAS.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), rot())
    a.set_actor_label(label)
    a.set_folder_path(folder)
    c = a.get_component_by_class(unreal.PointLightComponent)
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_editor_property("intensity", intensity_lm)
    c.set_editor_property("light_color", unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    c.set_editor_property("attenuation_radius", radius)
    c.set_editor_property("cast_shadows", shadows)
    c.set_editor_property("source_radius", 8.0)
    return a


# ---------------------------------------------------------------------------
# Build

def reset_level():
    if EAL.does_asset_exist(MAP):
        LES.load_level(MAP)
        for a in EAS.get_all_level_actors():
            if isinstance(a, (unreal.WorldSettings,)) or a.get_class().get_name() in ("Brush", "DefaultPhysicsVolume", "GameplayDebuggerPlayerManager"):
                continue
            EAS.destroy_actor(a)
    else:
        LES.new_level(MAP)


def build_structure():
    # Floors (top at Z=0) and ceilings, one per room so each can have its own finish.
    rooms = {
        "living": (0, 800, 0, 650, "FloorWood"),
        "kitchen": (800, 1400, 0, 650, "FloorTile"),
        "bedroom": (0, 800, 650, 1100, "FloorCarpet"),
        "bathroom": (800, 1400, 650, 1100, "FloorBath"),
    }
    for rid, (x0, x1, y0, y1, floor) in rooms.items():
        box_minmax(f"Floor_{rid}", (x0, y0, -10), (x1, y1, 0), floor, "Structure/Floors")
        box_minmax(f"Ceiling_{rid}", (x0 - 10, y0 - 10, H), (x1 + 10, y1 + 10, H + 12), "Ceiling", "Structure/Ceilings")
    prim("Ground", (700, 550, -16), (8000, 8000, 10), "Grass", "Structure")

    # Kitchen floor checkerboard accents.
    for i in range(6):
        for j in range(6):
            if (i + j) % 2 == 0:
                box_minmax(f"KitchenTile_{i}_{j}", (810 + i * 97, 10 + j * 105, 0), (810 + (i + 1) * 97, 10 + (j + 1) * 105, 0.4),
                           "Coral", "Structure/Floors/KitchenTiles", collide=False)

    # Exterior walls (pastel per room) - X-running walls span the corners.
    wall("Wall_W_Living", "x", 0, -10, 800, "WallBlush", [(130, 250, 0, 220)])  # front door (decorative)
    wall("Wall_W_Kitchen", "x", 0, 800, 1410, "WallMint", [(1000, 1200, 110, 230)])
    wall("Wall_E_Bedroom", "x", 1100, -10, 800, "WallLavender", [(250, 450, 95, 230)])
    wall("Wall_E_Bath", "x", 1100, 800, 1410, "WallSky")
    wall("Wall_S_Living", "y", 0, 10, 650, "WallBlush", [(120, 370, 95, 230)])
    wall("Wall_S_Bedroom", "y", 0, 650, 1090, "WallLavender", [(780, 1000, 95, 230)])
    wall("Wall_N_Kitchen", "y", 1400, 10, 650, "WallMint", [(200, 440, 110, 230)])
    wall("Wall_N_Bath", "y", 1400, 650, 1090, "WallSky", [(950, 1060, 170, 240)])

    # Interior walls with doorways.
    wall("Wall_Mid_X800", "y", 800, 10, 1090, "WallCream", [(480, 600, 0, 225), (860, 960, 0, 225)])
    wall("Wall_Mid_Y650_West", "x", 650, 10, 790, "WallCream", [(560, 680, 0, 225)])
    wall("Wall_Mid_Y650_East", "x", 650, 810, 1390, "WallCream", [(1040, 1150, 0, 225)])

    # The decorative front door, firmly closed: nobody leaves until he's fixed.
    box_minmax("FrontDoor", (132, 2, 0), (248, 14, 218), "Velvet", "Structure")
    prim("FrontDoorKnob", (230, 18, 100), (6, 6, 6), "Brass", "Structure", mesh=SPHERE, collide=False)


def build_living():
    f = "Furniture/Living"
    prim("Rug", (240, 260, 0.6), (330, 300, 1.2), "Rug", f, collide=False)
    # Sofa against the south wall under the window, facing the TV.
    prim("Sofa_Base", (72, 245, 24), (95, 250, 48), "Velvet", f)
    prim("Sofa_Back", (34, 245, 70), (22, 250, 55), "VelvetDark", f)
    prim("Sofa_ArmL", (72, 112, 40), (95, 22, 62), "VelvetDark", f)
    prim("Sofa_ArmR", (72, 378, 40), (95, 22, 62), "VelvetDark", f)
    prim("Sofa_Cushion1", (80, 185, 55), (72, 112, 16), "Velvet", f)
    prim("Sofa_Cushion2", (80, 305, 55), (72, 112, 16), "Velvet", f)
    prim("Sofa_Pillow", (52, 140, 80), (16, 40, 34), "Butter", f, yaw=-10, roll=8)
    # Coffee table
    prim("CoffeeTable_Top", (230, 245, 40), (75, 140, 6), "Wood", f)
    for i, (dx, dy) in enumerate(((-30, -60), (30, -60), (-30, 60), (30, 60))):
        prim(f"CoffeeTable_Leg{i}", (230 + dx, 245 + dy, 18), (5, 5, 37), "WoodDark", f, mesh=CYL)
    prim("CoffeeTable_Mug", (220, 220, 49), (9, 9, 12), "Mint", f, mesh=CYL, collide=False)
    # TV stand and TV on the east (kitchen) wall
    prim("TVStand", (762, 245, 26), (50, 180, 52), "WoodDark", f)
    prim("TVFrame", (782, 245, 115), (6, 140, 84), "Black", f)
    # Bookshelf on the west wall
    prim("Bookshelf", (680, 30, 95), (150, 38, 190), "Wood", f)
    book_colors = ["Coral", "Mint", "Butter", "Lilac", "Teal", "Velvet"]
    for shelf in range(3):
        for b in range(7):
            prim(f"Book_{shelf}_{b}", (620 + b * 18, 42, 30 + shelf * 58), (14, 22, 34 + (b % 3) * 5),
                 book_colors[(b + shelf) % len(book_colors)], f + "/Books", collide=False)
    # Plant
    prim("Plant_Pot", (740, 600, 22), (40, 40, 44), "Coral", f, mesh=CYL)
    prim("Plant_Leaves", (740, 600, 80), (70, 70, 80), "Leaf", f, mesh=SPHERE, collide=False)
    # Floor lamp pole (shade is interactable)
    prim("FloorLamp_Base", (60, 430, 2), (34, 34, 4), "Brass", f, mesh=CYL)
    prim("FloorLamp_Pole", (60, 430, 75), (4, 4, 146), "Brass", f, mesh=CYL)
    # Fuse box surround
    prim("FuseBox_Conduit", (420, 14, 230), (6, 6, 130), "Steel", f, mesh=CYL, collide=False)

    interactable("FloorLamp", (60, 430, 0), 0, "living", CYL, (0, 0, 158), (46, 46, 34), "Butter",
                 unreal.InteractToggle.LIGHT, "Turn on lamp", "Turn off lamp",
                 on_emissive=(5, 4, 2.5), light_loc=(0, 0, 150), light_intensity=5000)
    interactable("TV", (778, 245, 115), 180, "living", CUBE, (0, 0, 0), (4, 128, 72), "Black",
                 unreal.InteractToggle.LIGHT, "Turn on TV", "Turn off TV",
                 on_emissive=(0.6, 1.2, 3.0), light_loc=(60, 0, 0), light_color=(120, 170, 255), light_intensity=1500)

    malady("Malady_FuseBox", "wyatt", unreal.MaladyStyle.WIRING, (420, 10, 150), 90, "living",
           CUBE, (8, 0, 0), (16, 56, 74), "Steel", fx_offset=(18, 0, -20),
           hunk_spawn=(150, 0, 0), talk_spot=(310, 0, 0))


def build_kitchen():
    f = "Furniture/Kitchen"
    # Counter run along the north wall (y 120..640), fridge at the west end.
    prim("Counter_Base", (1360, 380, 43), (60, 520, 86), "Mint", f)
    prim("Counter_Top", (1357, 380, 89), (68, 524, 5), "White", f)
    prim("Counter_Kick", (1331, 380, 5), (4, 520, 10), "Teal", f, collide=False)
    for i, y in enumerate((170, 260, 520, 600)):
        prim(f"Cabinet_Knob{i}", (1328, y, 60), (4, 4, 4), "Brass", f, mesh=SPHERE, collide=False)
    # Faucet behind the sink (sink basin is the malady body)
    prim("Faucet_Stem", (1382, 320, 105), (5, 5, 30), "Steel", f, mesh=CYL, collide=False)
    prim("Faucet_Spout", (1370, 320, 118), (26, 5, 5), "Steel", f, collide=False)
    # Stove
    prim("Stove_Top", (1360, 560, 90), (58, 90, 3), "Black", f, collide=False)
    # Fridge
    prim("Fridge", (1357, 65, 95), (66, 90, 190), "Butter", f)
    prim("Fridge_Handle", (1318, 95, 120), (3, 3, 40), "Steel", f, mesh=CYL, collide=False)
    # Upper shelf + jars
    prim("Shelf", (1385, 560, 185), (28, 100, 4), "Wood", f, collide=False)
    for i in range(4):
        prim(f"Jar{i}", (1385, 525 + i * 24, 197), (12, 12, 20), ["Coral", "Butter", "Lilac", "Mint"][i], f, mesh=CYL, collide=False)
    # Table & chairs
    prim("Table_Top", (1010, 120, 74), (90, 130, 5), "Wood", f)
    prim("Table_Leg", (1010, 120, 36), (10, 10, 72), "WoodDark", f, mesh=CYL)
    prim("Table_Foot", (1010, 120, 2), (50, 50, 4), "WoodDark", f, mesh=CYL)
    for i, dy in enumerate((-80, 80)):
        prim(f"Chair{i}_Seat", (1010, 120 + dy, 45), (42, 42, 6), "Coral", f)
        prim(f"Chair{i}_Back", (1010, 120 + dy * 1.25, 75), (42, 5, 55), "Coral", f)
        prim(f"Chair{i}_Leg", (1010, 120 + dy, 22), (6, 6, 44), "WoodDark", f, mesh=CYL)
    prim("FruitBowl", (1010, 110, 82), (36, 36, 10), "White", f, mesh=SPHERE, collide=False)
    for i, c in enumerate(("Coral", "Butter", "Leaf")):
        prim(f"Fruit{i}", (1000 + i * 10, 105 + (i % 2) * 12, 88), (11, 11, 11), c, f, mesh=SPHERE, collide=False)

    interactable("Fridge_Door", (1322, 20, 0), 180, "kitchen", CUBE, (3, -45, 95), (6, 88, 186), "Butter",
                 unreal.InteractToggle.ROTATE, "Open fridge", "Close fridge", rotation=(100, 0, 0))
    interactable("Stove_Burner", (1352, 560, 92), 180, "kitchen", CYL, (0, 0, 0), (26, 26, 2), "WoodDark",
                 unreal.InteractToggle.LIGHT, "Turn on stove", "Turn off stove",
                 on_emissive=(8, 1.2, 0.2), light_loc=(0, 0, 15), light_color=(255, 90, 40), light_intensity=800)
    interactable("Kitchen_Drawer", (1328, 450, 70), 180, "kitchen", CUBE, (2, 0, 0), (5, 80, 24), "Teal",
                 unreal.InteractToggle.SLIDE, "Open drawer", "Close drawer", offset=(38, 0, 0))

    malady("Malady_Sink", "lukey", unreal.MaladyStyle.LEAK, (1358, 320, 92), 180, "kitchen",
           CUBE, (0, 0, 2), (46, 74, 8), "Steel", fx_offset=(32, 0, -14),
           hunk_spawn=(160, 0, 0), talk_spot=(320, 0, 0))


def build_bathroom():
    f = "Furniture/Bathroom"
    # Tub along the north wall
    prim("Tub_Outer", (1345, 790, 28), (80, 180, 56), "White", f)
    prim("Tub_Water", (1345, 790, 50), (62, 160, 4), "Glass", f, collide=False)
    prim("Tub_Foot0", (1310, 715, 4), (10, 10, 8), "Brass", f, mesh=SPHERE, collide=False)
    prim("Tub_Foot1", (1310, 865, 4), (10, 10, 8), "Brass", f, mesh=SPHERE, collide=False)
    prim("Tub_FaucetStem", (1388, 790, 70), (5, 5, 30), "Brass", f, mesh=CYL, collide=False)
    # Toilet against the east wall
    prim("Toilet_Base", (900, 1050, 20), (40, 50, 40), "White", f, mesh=CYL)
    prim("Toilet_Tank", (900, 1080, 62), (44, 18, 44), "White", f)
    # Pedestal sink + mirror on the west (bedroom) wall
    prim("Sink_Pedestal", (832, 720, 40), (16, 16, 80), "White", f, mesh=CYL)
    prim("Sink_Bowl", (835, 720, 84), (44, 56, 14), "White", f)
    prim("Mirror", (812, 720, 160), (3, 60, 80), "Mirror", f, collide=False)
    prim("BathMat", (1240, 790, 0.6), (60, 120, 1.2), "RugBlue", f, collide=False)
    prim("Towel", (1210, 1088, 140), (4, 50, 70), "Mint", f, collide=False)

    interactable("Tub_Faucet", (1386, 790, 82), 180, "bathroom", CYL, (9, 0, 0), (5, 5, 18), "Brass",
                 unreal.InteractToggle.REVEAL, "Run the bath", "Turn off the water", body_rot=(0, 90, 0),
                 reveal={"mesh": CYL, "loc": (18, 0, -16), "size": (4, 4, 32)})
    interactable("Toilet_Lid", (900, 1068, 41), -90, "bathroom", CUBE, (22, 0, 1), (44, 38, 3), "White",
                 unreal.InteractToggle.ROTATE, "Lift the lid", "Put the lid down", rotation=(0, 85, 0))

    # The pink tile wall: the bathroom's original 1957 "feature".
    malady("Malady_PinkTile", "tyler", unreal.MaladyStyle.TILE, (1100, 1090, 150), -90, "bathroom",
           CUBE, (2, 0, 0), (4, 220, 180), "PinkTile",
           hunk_spawn=(130, 0, 0), talk_spot=(290, 0, 0))
    for i in range(10):
        for j in range(8):
            box_minmax(f"Grout_{i}_{j}", (990 + i * 22, 1084, 60 + j * 22.5), (990 + i * 22 + 1.5, 1086, 60 + j * 22.5 + 1.5),
                       "White", f + "/Grout", collide=False)


def build_bedroom():
    f = "Furniture/Bedroom"
    prim("Rug", (420, 850, 0.6), (240, 160, 1.2), "Butter", f, collide=False)
    # Bed against the east wall
    prim("Bed_Frame", (350, 985, 18), (170, 210, 36), "WoodDark", f)
    prim("Bed_Mattress", (350, 985, 45), (160, 200, 18), "White", f)
    prim("Bed_Blanket", (350, 955, 56), (164, 140, 6), "Plum", f, collide=False)
    prim("Bed_Headboard", (350, 1086, 65), (175, 8, 130), "WoodDark", f)
    for i, dx in enumerate((-38, 38)):
        prim(f"Bed_Pillow{i}", (350 + dx, 1055, 60), (62, 30, 14), "Lilac", f, collide=False)
    # Nightstand
    prim("Nightstand", (480, 1060, 28), (46, 44, 56), "Wood", f)
    prim("BedLamp_Base", (480, 1060, 66), (12, 12, 20), "Brass", f, mesh=CYL, collide=False)
    # Wardrobe on the south wall
    prim("Wardrobe", (42, 720, 100), (64, 112, 200), "Wood", f)
    # Dresser on the north (living) wall
    prim("Dresser", (225, 685, 40), (150, 50, 80), "Wood", f)
    prim("Dresser_Mirror", (225, 664, 130), (90, 3, 70), "Mirror", f, collide=False)
    prim("Plant_Pot", (740, 1050, 18), (34, 34, 36), "Teal", f, mesh=CYL)
    prim("Plant_Leaves", (740, 1050, 65), (56, 56, 70), "Leaf", f, mesh=SPHERE, collide=False)

    interactable("BedLamp", (480, 1060, 56), 0, "bedroom", CYL, (0, 0, 32), (30, 30, 22), "Lilac",
                 unreal.InteractToggle.LIGHT, "Turn on lamp", "Turn off lamp",
                 on_emissive=(5, 3.5, 5), light_loc=(0, 0, 28), light_color=(255, 200, 230), light_intensity=2500)
    interactable("Wardrobe_Door", (76, 666, 0), 0, "bedroom", CUBE, (0, 54, 100), (5, 106, 196), "WoodDark",
                 unreal.InteractToggle.ROTATE, "Open wardrobe", "Close wardrobe", rotation=(-100, 0, 0))
    interactable("Dresser_Drawer", (225, 713, 55), 90, "bedroom", CUBE, (0, 0, 0), (5, 130, 24), "WoodDark",
                 unreal.InteractToggle.SLIDE, "Open drawer", "Close drawer", offset=(35, 0, 0))

    malady("Malady_Mold", "malcolm", unreal.MaladyStyle.MOLD, (790, 760, 140), 180, "bedroom",
           CUBE, (1, 0, 0), (3, 150, 170), "WallCream", fx_offset=(2, 0, 0),
           hunk_spawn=(140, 0, 0), talk_spot=(300, 0, 0))


def build_lighting():
    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 800), rot(yaw=200, pitch=-38))
    sun.set_actor_label("Sun")
    sun.set_folder_path("Lighting")
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_editor_property("intensity", 450.0)
    sc.set_editor_property("light_color", unreal.Color(r=255, g=236, b=214, a=255))
    sc.set_editor_property("atmosphere_sun_light", True)

    sky = EAS.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), rot())
    sky.set_actor_label("SkyAtmosphere")
    sky.set_folder_path("Lighting")
    skylight = EAS.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500), rot())
    skylight.set_actor_label("SkyLight")
    skylight.set_folder_path("Lighting")
    slc = skylight.get_component_by_class(unreal.SkyLightComponent)
    slc.set_editor_property("real_time_capture", True)
    slc.set_editor_property("intensity", 1.0)
    fog = EAS.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, -100), rot())
    fog.set_actor_label("HeightFog")
    fog.set_folder_path("Lighting")

    # Warm ceiling fixtures, one per room.
    for rid, (cx, cy) in {"living": (400, 325), "kitchen": (1100, 325), "bedroom": (400, 875), "bathroom": (1100, 875)}.items():
        prim(f"CeilingFixture_{rid}", (cx, cy, H - 4), (50, 50, 8), "LampGlow", "Lighting/Fixtures", mesh=CYL, collide=False)
        point_light(f"CeilingLight_{rid}", (cx, cy, H - 40), 4500)
    # Fill lights so corners aren't murky.
    point_light("Fill_Living", (150, 500, 200), 1200, radius=600, shadows=False)
    point_light("Fill_Kitchen", (1250, 150, 200), 1200, radius=600, shadows=False)

    ppv = EAS.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(700, 550, 150), rot())
    ppv.set_actor_label("PostProcess")
    ppv.set_folder_path("Lighting")
    ppv.set_editor_property("unbound", True)
    s = ppv.get_editor_property("settings")
    s.set_editor_property("override_auto_exposure_min_brightness", True)
    s.set_editor_property("auto_exposure_min_brightness", 3.0)
    s.set_editor_property("override_auto_exposure_max_brightness", True)
    s.set_editor_property("auto_exposure_max_brightness", 6.5)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 0.6)
    s.set_editor_property("override_bloom_intensity", True)
    s.set_editor_property("bloom_intensity", 0.9)
    s.set_editor_property("override_vignette_intensity", True)
    s.set_editor_property("vignette_intensity", 0.35)
    s.set_editor_property("override_color_saturation", True)
    s.set_editor_property("color_saturation", unreal.Vector4(1.12, 1.12, 1.12, 1.0))
    s.set_editor_property("override_film_toe", True)
    s.set_editor_property("film_toe", 0.5)
    ppv.set_editor_property("settings", s)


def build_outdoors():
    f = "Outdoors"
    for i, (x, y, s) in enumerate(((-350, 300, 1.0), (-300, 900, 1.3), (1800, 200, 1.1), (1750, 950, 0.9), (600, -400, 1.2), (500, 1500, 1.0))):
        prim(f"Tree{i}_Trunk", (x, y, 120 * s), (30 * s, 30 * s, 240 * s), "Bark", f, mesh=CYL)
        prim(f"Tree{i}_Crown", (x, y, 300 * s), (220 * s, 220 * s, 200 * s), "Leaf", f, mesh=SPHERE)
    prim("Path", (-150, 190, -10.5), (300, 130, 1), "FloorTile", f, collide=False)


def build_gameplay():
    room("living", "Living Room", 0, 800, 0, 650, "Rug", (420, 420), 0)
    room("kitchen", "Kitchen", 800, 1400, 0, 650, "Mint", (1080, 420), 0)
    room("bedroom", "Bedroom", 0, 800, 650, 1100, "Lilac", (520, 820), 90)
    room("bathroom", "Bathroom", 800, 1400, 650, 1100, "WallSky", (1000, 790), 90)

    start = EAS.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(420, 420, 100), rot(yaw=0))
    start.set_actor_label("PlayerStart")
    start.set_folder_path("Gameplay")

    cam = EAS.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(745, 590, 205), rot(yaw=-145, pitch=-13))
    cam.set_actor_label("TitleCamera")
    cam.set_folder_path("Gameplay")
    cam.tags = [unreal.Name("TitleCamera")]
    cam.camera_component.set_editor_property("field_of_view", 70.0)


def main():
    reset_level()
    build_structure()
    build_living()
    build_kitchen()
    build_bathroom()
    build_bedroom()
    build_lighting()
    build_outdoors()
    build_gameplay()
    LES.save_current_level()
    unreal.log("[FixHim] build_apartment done")


main()
