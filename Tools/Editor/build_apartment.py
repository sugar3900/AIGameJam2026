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
import os
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
FLAT = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_PainterlySurface")
if not FLAT:
    raise RuntimeError("Run create_painterly_material.py before building the apartment")
TRANS = unreal.load_asset("/Game/ICanFixHim/Materials/M_Translucent")

H = 300.0   # wall height
T = 20.0    # wall thickness

# ---------------------------------------------------------------------------
# Palette (material instances are real assets so they can be tweaked in-editor)

COLORS = {
    "WallCream": (0.68, 0.58, 0.44),
    "WallBlush": (0.69, 0.53, 0.45),
    "WallMint": (0.57, 0.62, 0.48),
    "WallSky": (0.70, 0.61, 0.53),
    "WallLavender": (0.53, 0.56, 0.43),
    "Ceiling": (0.96, 0.95, 0.93),
    "Trim": (0.98, 0.97, 0.95),
    "FloorWood": (0.50, 0.31, 0.18),
    "FloorTile": (0.88, 0.86, 0.80),
    "FloorBath": (0.94, 0.90, 0.92),
    "FloorCarpet": (0.43, 0.27, 0.16),
    "Grass": (0.30, 0.55, 0.25),
    "Rug": (0.52, 0.25, 0.20),
    "RugBlue": (0.40, 0.58, 0.85),
    "Velvet": (0.43, 0.25, 0.18),
    "VelvetDark": (0.25, 0.16, 0.12),
    "Wood": (0.55, 0.35, 0.20),
    "WoodDark": (0.32, 0.19, 0.11),
    "White": (0.95, 0.95, 0.95),
    "Black": (0.04, 0.04, 0.05),
    "Steel": (0.62, 0.64, 0.68),
    "Brass": (0.85, 0.65, 0.30),
    "Mint": (0.36, 0.47, 0.35),
    "Butter": (0.98, 0.88, 0.55),
    "Lilac": (0.70, 0.55, 0.85),
    "Teal": (0.20, 0.55, 0.60),
    "Coral": (0.98, 0.50, 0.42),
    "Leaf": (0.28, 0.34, 0.22),
    "FabricOlive": (0.27, 0.31, 0.22),
    "FabricShade": (0.18, 0.22, 0.15),
    "OldRose": (0.48, 0.25, 0.24),
    "Paper": (0.67, 0.56, 0.40),
    "Mildew": (0.06, 0.11, 0.06),
    "Damp": (0.31, 0.32, 0.20),
    "Bark": (0.35, 0.22, 0.12),
    "Plum": (0.30, 0.10, 0.28),
    "PinkTile": (0.76, 0.40, 0.47),
}
EMISSIVE = {
    "LampGlow": ((1.0, 0.92, 0.75), (6.0, 5.0, 3.5)),
    "Mirror": ((0.75, 0.85, 0.92), (0.15, 0.18, 0.22)),
    "WindowDaylight": ((0.65, 0.78, 0.77), (0.4, 0.50, 0.48)),
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
    if name in ("Glass", "Invisible"):
        MEL.set_material_instance_parent(mi, TRANS)
        MEL.set_material_instance_vector_parameter_value(mi, "BaseColor", unreal.LinearColor(0.75, 0.9, 1.0, 1))
        MEL.set_material_instance_scalar_parameter_value(mi, "Opacity", 0.0 if name == "Invisible" else 0.18)
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
    surface = mic(color)
    overrides = {"Floor_living": "M_Floorboards", "Floor_bedroom": "M_Floorboards",
                 "Counter_Base": "M_AgedSagePaint", "Floor_kitchen": "M_KitchenChecker", "Floor_bathroom": "M_BathMosaic"}
    if "_Outside" in label:
        surface = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_WindowView")
        if not surface:
            raise RuntimeError("Run import_window_view.py first")
    if label.startswith("Wall_S_Living_") and folder == "Structure/Walls":
        surface = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_FloralWallpaperWorn")
        if not surface:
            raise RuntimeError("Run import_environment_textures.py first")
    if label in overrides:
        surface = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/" + overrides[label])
        if not surface:
            raise RuntimeError("Run import_environment_textures.py first")
    smc.set_material(0, surface)
    if "_Outside" in label:
        smc.set_cast_shadow(False)
        a.tags = [unreal.Name("WindowView")]
    if not collide:
        smc.set_collision_profile_name("NoCollision")
    return a



def authored(label, asset, location, folder, yaw=0):
    mesh = unreal.load_asset("/Game/ICanFixHim/Environment/Meshes/" + asset)
    if not mesh:
        raise RuntimeError("Missing environment mesh: " + asset)
    a = EAS.spawn_actor_from_object(mesh, unreal.Vector(*location), rot(yaw))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    apply_authored_materials(a.static_mesh_component, mesh)
    return a


def apply_authored_materials(component, mesh):
    slots = {"Enamel_Cream": "Butter", "Paint_Sage": "Mint", "Iron": "Black",
             "Aged_Metal": "Steel", "Rust": "WoodDark", "Upholstery": "FabricOlive",
             "Upholstery_Shadow": "FabricShade", "Wood": "WoodDark",
             "Porcelain": "White", "Burner": "Black", "Plaid_Rose": "OldRose", "Plaid_Gold": "Butter", "Plaid_Cream": "Trim", "Wire_Red": "Velvet", "Wire_Ochre": "Butter", "Wire_Blue": "Teal", "Exposed_Plaster": "Paper", "Old_Paint": "WallCream", "Damp_Edge": "Wood", "Quilt_Rose": "OldRose", "Quilt_Sage": "FabricOlive", "Quilt_Ivory": "Trim", "Mildew": "Mildew", "Damp": "Damp", "Pot_Terracotta": "Coral", "Leaf_Green": "Leaf", "Leaf_Light": "Mint", "Fruit_Red": "Velvet", "Fruit_Gold": "Butter", "Fruit_Green": "Leaf"}
    for index, slot in enumerate(mesh.get_editor_property("static_materials")):
        name = str(slot.get_editor_property("material_slot_name"))
        special = {"Quilt_Rose": "M_RoseQuilt", "Quilt_Ivory": "M_IvoryPillow", "Paint_Sage": "M_CabinetSage", "Enamel_Cream": "M_IvoryEnamel", "Wood": "M_WarmWood"}
        if name in special:
            material = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/" + special[name])
            if not material:
                raise RuntimeError("Missing quilt material " + special[name])
        else:
            material = mic(slots.get(name, "Wood"))
        component.set_material(index, material)


def moving_mesh(actor, name, local_location, yaw=0):
    mesh = unreal.load_asset("/Game/ICanFixHim/Environment/Meshes/" + name)
    if not mesh:
        raise RuntimeError("Missing moving mesh " + name)
    actor.set_editor_property("use_authored_body_materials", True)
    body = actor.get_editor_property("body")
    body.set_static_mesh(mesh)
    body.set_relative_location(unreal.Vector(*local_location), False, False)
    body.set_relative_rotation(rot(yaw), False, False)
    body.set_relative_scale3d(unreal.Vector(1, 1, 1))
    apply_authored_materials(body, mesh)


def solid_proxy(label, center, size, folder):
    a = prim(label, center, size, "Wood", folder)
    a.set_actor_hidden_in_game(True)
    a.static_mesh_component.set_collision_profile_name("EnvironmentBlocking")
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
            # A softly lit exterior card prevents empty black windows in an
            # enclosed level. Mullions make the period windows legible.
            if axis == "x":
                prim(f"{label}_Outside{j}", ((s+e)/2, fixed-20 if fixed < 100 else fixed+20, (zb+zt)/2),
                     (e-s, 2, zt-zb), "WindowDaylight", folder+"/Glass", collide=False)
                prim(f"{label}_Mullion{j}", ((s+e)/2, fixed, (zb+zt)/2),
                     (5, 5, zt-zb), "Trim", folder+"/Trim", collide=False)
            else:
                prim(f"{label}_Outside{j}", (fixed-20 if fixed < 100 else fixed+20, (s+e)/2, (zb+zt)/2),
                     (2, e-s, zt-zb), "WindowDaylight", folder+"/Glass", collide=False)
                prim(f"{label}_Mullion{j}", (fixed, (s+e)/2, (zb+zt)/2),
                     (5, 5, zt-zb), "Trim", folder+"/Trim", collide=False)


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

    # Period baseboards and crown rails are non-blocking and preserve doorway gaps.
    for name, axis, fixed, start, end in (
        ("LivingSouth", "y", 12, 10, 650), ("KitchenNorth", "y", 1388, 10, 650),
        ("BedroomSouth", "y", 12, 660, 1090), ("BathNorth", "y", 1388, 660, 1090)):
        if axis == "y":
            prim("Baseboard_" + name, (fixed, (start+end)/2, 9), (3, end-start, 18), "Trim", "Structure/Trim", collide=False)
            prim("Crown_" + name, (fixed, (start+end)/2, 286), (3, end-start, 12), "Trim", "Structure/Trim", collide=False)
    # Localized old plaster loss keeps the house in need of repair without
    # turning the painterly shader into physical surface relief.
    for label, loc, yaw, scale in (
        ("KitchenOldPlaster", (920, 11, 220), -90, (0.8,0.8,0.8)),
        ("BedroomOldPlaster", (11, 710, 220), 180, (0.75,0.75,0.75))):
        patch = authored(label, "SM_PlasterDamage", loc, "Structure/Age", yaw=yaw)
        patch.set_actor_scale3d(unreal.Vector(*scale))
        patch.static_mesh_component.set_collision_profile_name("NoCollision")
    # The decorative front door, firmly closed: nobody leaves until he's fixed.
    front_door = authored("MoldedFrontDoor", "SM_MoldedFrontDoor", (190,8,0), "Structure", yaw=-90)
    front_door.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("FrontDoorCollision", (190,8,109), (116,12,218), "Structure")


def build_living():
    f = "Furniture/Living"
    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    rug = prim("FloralRug", (240,260,1), (330,300,1), "Rug", f, mesh=plane, collide=False)
    rug.static_mesh_component.set_material(0, unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_FloralRug"))
    sofa = authored("VintageSofa", "SM_VintageSofa", (72, 245, 0), f, yaw=180)
    for y in (172, 315):
        cushion = authored("PlaidCushion", "SM_PlaidCushion", (93,y,50), f, yaw=180)
        cushion.static_mesh_component.set_collision_profile_name("NoCollision")
    throw = authored("FoldedThrow", "SM_FoldedThrow", (72,345,66), f)
    throw.static_mesh_component.set_collision_profile_name("NoCollision")
    # Coffee table
    authored("VintageCoffeeTable", "SM_VintageCoffeeTable", (230,245,0), f)
    prim("CoffeeTable_Mug", (220, 220, 49), (9, 9, 12), "Mint", f, mesh=CYL, collide=False)
    books = authored("StackedBooks", "SM_StackedBooks", (230,270,44), f)
    books.static_mesh_component.set_collision_profile_name("NoCollision")
    caddy = authored("RepairCaddy", "SM_RepairCaddy", (370,58,0), f)
    caddy.static_mesh_component.set_collision_profile_name("NoCollision")
    # TV stand and TV on the east (kitchen) wall
    authored("VintageTVStand", "SM_VintageTVStand", (762,245,0), f)
    tv_frame = authored("VintageTVFrame", "SM_VintageTVFrame", (782,245,115), f)
    tv_frame.static_mesh_component.set_collision_profile_name("NoCollision")
    # Bookshelf on the west wall
    bookshelf = authored("OldBookshelf", "SM_OldBookshelf", (680, 30, 0), f, yaw=-90)
    # Plant
    living_plant = authored("LivingPlant", "SM_LeafyPottedPlant", (740,600,0), f)
    living_plant.static_mesh_component.set_collision_profile_name("NoCollision")
    # Floor lamp pole (shade is interactable)
    lamp_base = authored("FloorLampBase", "SM_FloorLampBase", (60,430,0), f)
    lamp_base.static_mesh_component.set_collision_profile_name("NoCollision")
    # Window dressing and old framed pictures keep the room lived-in.
    curtains = authored("GatheredCurtains", "SM_GatheredCurtains", (19,245,5), f, yaw=180)
    curtains.static_mesh_component.set_collision_profile_name("NoCollision")
    for y,z,w,h in ((470,190,75,58),(550,175,48,62)):
        prim("PictureFrame", (13,y,z), (5,w,h), "WoodDark", f, collide=False)
        picture = prim("PicturePrint", (17,y,z), (2,w-10,h-10), "Paper", f, collide=False)
        picture.static_mesh_component.set_material(0, unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_ArtPrint"))
    # Fuse box surround
    prim("FuseBox_Conduit", (420, 14, 230), (6, 6, 130), "Steel", f, mesh=CYL, collide=False)

    # The localized stain is a flat color overlay, not physical relief.
    overlay = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_WaterStain_Overlay")
    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    age_overlay = None
    if overlay and plane:
        a = EAS.spawn_actor_from_object(plane, unreal.Vector(420, 11.5, 150), rot(0, 0, 90))
        age_overlay = a
        a.set_actor_label("FuseWallAge")
        a.set_folder_path(f)
        a.set_actor_scale3d(unreal.Vector(2.5, 1.7, 1))
        a.static_mesh_component.set_material(0, overlay)
        a.static_mesh_component.set_collision_profile_name("NoCollision")
    lamp = interactable("FloorLamp", (60, 430, 0), 0, "living", CYL, (0, 0, 158), (46, 46, 34), "Butter",
                 unreal.InteractToggle.LIGHT, "Turn on lamp", "Turn off lamp",
                 on_emissive=(5, 4, 2.5), light_loc=(0, 0, 150), light_intensity=5000)
    lamp_body = lamp.get_editor_property("body")
    lamp_body.set_static_mesh(unreal.load_asset("/Game/ICanFixHim/Environment/Meshes/SM_FloorLampShade"))
    lamp_body.set_relative_scale3d(unreal.Vector(1,1,1))
    for index in range(lamp_body.get_num_materials()):
        lamp_body.set_material(index, mic("Butter"))
    interactable("TV", (778, 245, 115), 180, "living", CUBE, (0, 0, 0), (4, 128, 72), "Black",
                 unreal.InteractToggle.LIGHT, "Turn on TV", "Turn off TV",
                 on_emissive=(0.6, 1.2, 3.0), light_loc=(60, 0, 0), light_color=(120, 170, 255), light_intensity=1500)

    fuse = malady("Malady_FuseBox", "wyatt", unreal.MaladyStyle.WIRING, (420, 10, 150), 90, "living",
           CUBE, (8, 0, 0), (16, 56, 74), "Steel", fx_offset=(18, 0, -20),
           hunk_spawn=(150, 0, 0), talk_spot=(310, 0, 0))
    for name, mesh, location in (("BrokenFuseDetails", "SM_DamagedFuseboxOverlay", (420,29,150)),
                                 ("FusePlasterDamage", "SM_PlasterDamage", (420,11,150))):
        detail = authored(name, mesh, location, f, yaw=-90)
        detail.static_mesh_component.set_collision_profile_name("NoCollision")
        detail.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        detail.tags = [unreal.Name("RepairDamage")]
        detail.attach_to_actor(fuse, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    if age_overlay:
        age_overlay.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        age_overlay.tags = [unreal.Name("RepairDamage")]
        age_overlay.attach_to_actor(fuse, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)


def build_kitchen():
    f = "Furniture/Kitchen"
    # Counter run along the north wall (y 120..640), fridge at the west end.
    for label, mesh, y, width in (("BaseCabinet96", "SM_BaseCabinet96", 168, 96), ("BaseCabinet86", "SM_BaseCabinet86", 467, 86)):
        cabinet = authored(label, mesh, (1360,y,0), f)
        cabinet.static_mesh_component.set_collision_profile_name("NoCollision")
        solid_proxy(label + "Collision", (1368,y,42), (44,width,84), f)
    sink_cabinet = authored("VintageSinkCabinet", "SM_KitchenSinkCabinet", (1360, 320, 0), f)
    sink_cabinet.static_mesh_component.set_collision_profile_name("NoCollision")
    prim("Counter_Top", (1357, 168, 89), (68, 96, 5), "White", f)
    prim("Counter_Top", (1357, 467, 89), (68, 86, 5), "White", f)
    prim("Counter_Kick", (1331, 315, 5), (4, 390, 10), "Teal", f, collide=False)
    for i, y in enumerate((170, 260, 520, 600)):
        prim(f"Cabinet_Knob{i}", (1328, y, 60), (4, 4, 4), "Brass", f, mesh=SPHERE, collide=False)
    # Faucet behind the sink (sink basin is the malady body)
    # Stove
    range_actor = authored("VintageRange", "SM_VintageRange", (1360, 560, 0), f)
    range_actor.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("RangeCollision", (1360,560,42), (60,76,84), f)
    # Fridge
    fridge = authored("VintageFridge", "SM_VintageFridgeBody", (1357, 65, 0), f)
    fridge.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("FridgeCollision", (1367,65,91), (44,82,182), f)
    # Backsplash panels respect the window opening above the sink.
    backsplash = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_KitchenBacksplash")
    for y, width, z, height in ((160,80,120,60), (320,240,100,20), (475,70,120,60)):
        tile = prim("KitchenBacksplash", (1388,y,z), (2,width,height), "White", f, collide=False)
        tile.static_mesh_component.set_material(0, backsplash)
    upper = authored("UpperKitchenCabinet", "SM_UpperKitchenCabinet", (1380,510,160), f)
    upper.static_mesh_component.set_collision_profile_name("NoCollision")
    pans = authored("HangingPans", "SM_HangingPans", (1385,590,154), f)
    pans.static_mesh_component.set_collision_profile_name("NoCollision")
    kettle = authored("OldKettle", "SM_EnamelKettle", (1358, 560, 94), f)
    kettle.static_mesh_component.set_collision_profile_name("NoCollision")
    bucket = authored("RepairBucket", "SM_RepairBucket", (1260, 245, 0), f)
    bucket.static_mesh_component.set_collision_profile_name("NoCollision")
    # Table & chairs
    authored("VintageDiningTable", "SM_VintageDiningTable", (1010,120,0), f)
    authored("DiningChairA", "SM_VintageDiningChair", (1010,40,0), f, yaw=-90)
    authored("DiningChairB", "SM_VintageDiningChair", (1010,200,0), f, yaw=90)
    fruit = authored("FruitBowl", "SM_FruitBowl", (1010,110,74), f)
    fruit.static_mesh_component.set_collision_profile_name("NoCollision")

    fridge_door = interactable("Fridge_Door", (1322, 20, 0), 180, "kitchen", CUBE, (3, -45, 95), (6, 88, 186), "Butter",
                 unreal.InteractToggle.ROTATE, "Open fridge", "Close fridge", rotation=(100, 0, 0))
    moving_mesh(fridge_door, "SM_RetroFridgeDoor", (3,-45,0), yaw=180)
    interactable("Stove_Burner", (1352, 560, 92), 180, "kitchen", CYL, (0, 0, 0), (26, 26, 2), "WoodDark",
                 unreal.InteractToggle.LIGHT, "Turn on stove", "Turn off stove",
                 on_emissive=(8, 1.2, 0.2), light_loc=(0, 0, 15), light_color=(255, 90, 40), light_intensity=800)
    kitchen_drawer = interactable("Kitchen_Drawer", (1328, 467, 70), 180, "kitchen", CUBE, (2, 0, 0), (5, 80, 24), "Teal",
                 unreal.InteractToggle.SLIDE, "Open drawer", "Close drawer", offset=(38, 0, 0))
    moving_mesh(kitchen_drawer, "SM_KitchenDrawer", (-17,0,0), yaw=180)

    sink = malady("Malady_Sink", "lukey", unreal.MaladyStyle.LEAK, (1358, 320, 92), 180, "kitchen",
           CUBE, (0, 0, 2), (46, 74, 8), "Steel", fx_offset=(32, 0, -14),
           hunk_spawn=(160, 0, 0), talk_spot=(320, 0, 0))
    # Keep the original collision target while letting the authored basin show.
    sink.set_editor_property("use_authored_body_materials", True)
    sink.get_editor_property("body").set_material(0, mic("Invisible"))
    sink.get_editor_property("body").set_cast_shadow(False)
    wear = prim("SinkFloorWear", (1280,320,0.8), (150,130,1), "Wood", f,
                mesh=unreal.load_asset("/Engine/BasicShapes/Plane"), collide=False)
    wear.static_mesh_component.set_material(0, unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_LinoleumWear_Overlay"))
    wear.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    wear.tags = [unreal.Name("RepairDamage")]
    wear.attach_to_actor(sink, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    stain = prim("SinkWallStain", (1386,320,102), (110,24,1), "Wood", f,
                 mesh=unreal.load_asset("/Engine/BasicShapes/Plane"), yaw=90, roll=90, collide=False)
    stain.static_mesh_component.set_material(0, unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_SinkStain_Overlay"))
    stain.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    stain.tags = [unreal.Name("RepairDamage")]
    stain.attach_to_actor(sink, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)


def build_bathroom():
    f = "Furniture/Bathroom"
    # Tub along the north wall
    authored("VintageTub", "SM_ClawfootTub", (1345, 790, 0), f)

    prim("Tub_FaucetStem", (1388, 790, 70), (5, 5, 30), "Brass", f, mesh=CYL, collide=False)
    # Toilet against the east wall
    toilet = authored("VintageToilet", "SM_VintageToiletBody", (900, 1050, 0), f, yaw=90)
    toilet.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("ToiletCollision", (900,1050,19), (40,50,38), f)
    # Pedestal sink + mirror on the west (bedroom) wall
    authored("PedestalSink", "SM_PedestalSink", (835, 720, 0), f, yaw=180)
    mirror = authored("BathMirror", "SM_BathMirror", (813,720,108), f, yaw=180)
    mirror.static_mesh_component.set_collision_profile_name("NoCollision")
    prim("BathMat", (1240, 790, 0.6), (60, 120, 1.2), "RugBlue", f, collide=False)
    towel_rail = authored("TowelRail", "SM_TowelRail", (1210,1088,90), f, yaw=90)
    towel_rail.static_mesh_component.set_collision_profile_name("NoCollision")
    basket = authored("TowelBasket", "SM_TowelBasket", (1270,1035,0), f)
    basket.static_mesh_component.set_collision_profile_name("NoCollision")

    tub_faucet = interactable("Tub_Faucet", (1386, 790, 82), 180, "bathroom", CYL, (9, 0, 0), (5, 5, 18), "Brass",
                 unreal.InteractToggle.REVEAL, "Run the bath", "Turn off the water", body_rot=(0, 90, 0),
                 reveal={"mesh": CYL, "loc": (18, 0, -16), "size": (4, 4, 32)})
    moving_mesh(tub_faucet, "SM_TubFaucet", (0,0,0))
    lid = interactable("Toilet_Lid", (900, 1068, 41), -90, "bathroom", CUBE, (22, 0, 1), (44, 38, 3), "White",
                 unreal.InteractToggle.ROTATE, "Lift the lid", "Put the lid down", rotation=(0, 85, 0))
    moving_mesh(lid, "SM_ToiletLid", (22,0,1))

    # Original wall tile surrounds the interactive feature wall.
    tile_mat = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_PinkTile")
    if not tile_mat:
        raise RuntimeError("Run import_environment_textures.py first")
    # Continuous wainscot wraps the room, with door openings left clear.
    for label, center, size in (
        ("BathTileEast", (1100,1087,75), (580,2,150)),
        ("BathTileNorth", (1388,870,75), (2,440,150)),
        ("BathTileWestA", (925,662,75), (230,2,150)),
        ("BathTileWestB", (1270,662,75), (240,2,150)),
        ("BathTileSouthA", (812,755,75), (2,210,150)),
        ("BathTileSouthB", (812,1025,75), (2,130,150))):
        tile = prim(label, center, size, "PinkTile", f, collide=False)
        tile.static_mesh_component.set_material(0, tile_mat)
    # Tile surface remains visible before and after repair; the crack overlay
    # is attached separately and follows the malady's repaired state.
    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    tile_surface = prim("PinkTileSurface", (1100,1085,150), (220,180,1), "PinkTile", f, mesh=plane, roll=90, collide=False)
    tile_surface.static_mesh_component.set_material(0, tile_mat)
    # The pink tile wall: the bathroom's original 1957 "feature".
    tile_malady = malady("Malady_PinkTile", "tyler", unreal.MaladyStyle.TILE, (1100, 1090, 150), -90, "bathroom",
           CUBE, (2, 0, 0), (4, 220, 180), "PinkTile",
           hunk_spawn=(130, 0, 0), talk_spot=(290, 0, 0))
    crack_mat = unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_TileCrack_Overlay")
    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    if crack_mat and plane:
        crack = EAS.spawn_actor_from_object(plane, unreal.Vector(1100,1084,150), rot(0,0,90))
        crack.set_actor_label("DamagedPinkTile")
        crack.set_folder_path(f)
        crack.set_actor_scale3d(unreal.Vector(2.2,1.8,1))
        crack.static_mesh_component.set_material(0, crack_mat)
        crack.static_mesh_component.set_collision_profile_name("NoCollision")
        crack.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        crack.tags = [unreal.Name("RepairDamage")]
        crack.attach_to_actor(tile_malady, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)


def build_bedroom():
    f = "Furniture/Bedroom"
    prim("Rug", (420, 850, 0.6), (240, 160, 1.2), "Butter", f, collide=False)
    # Bed against the east wall
    bed_mesh = authored("VintageBed", "SM_VintageBed", (350, 985, 0), f, yaw=180)
    bed_mesh.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("BedCollision", (350,985,25), (165,200,50), f)
    # The blanket is the clickable bed: "Go to bed (end the day)".
    bed = interactable("Bed", (350, 955, 56), 0, "bedroom", CUBE, (0, 0, 0), (164, 140, 6), "Plum",
                       unreal.InteractToggle.NONE, "Go to bed", "Go to bed", cls=unreal.FixHimBed)
    moving_mesh(bed, "SM_RumpledQuilt", (0,0,12), yaw=180)
    # Nightstand
    authored("VintageNightstand", "SM_VintageNightstand", (480,1060,0), f, yaw=180)
    prim("BedLamp_Base", (480, 1060, 66), (12, 12, 20), "Brass", f, mesh=CYL, collide=False)
    # Wardrobe on the south wall
    wardrobe = authored("VintageWardrobe", "SM_VintageWardrobe", (42, 720, 0), f, yaw=180)
    wardrobe.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("WardrobeCollision", (33,720,100), (45,108,200), f)
    # Dresser on the north (living) wall
    dresser = authored("VintageDresser", "SM_VintageDresser", (225, 685, 0), f, yaw=-90)
    dresser.static_mesh_component.set_collision_profile_name("NoCollision")
    solid_proxy("DresserCollision", (225,677,40), (145,35,80), f)
    dresser_mirror = authored("DresserMirror", "SM_BathMirror", (225,713,94), f, yaw=-90)
    dresser_mirror.static_mesh_component.set_collision_profile_name("NoCollision")
    bedroom_curtains = authored("BedroomCurtains", "SM_GatheredCurtains", (350,1090,0), f, yaw=90)
    bedroom_curtains.set_actor_scale3d(unreal.Vector(.8,.8,1))
    bedroom_curtains.static_mesh_component.set_collision_profile_name("NoCollision")
    bedroom_plant = authored("BedroomPlant", "SM_LeafyPottedPlant", (740,1050,0), f)
    bedroom_plant.set_actor_scale3d(unreal.Vector(.8,.8,.8))
    bedroom_plant.static_mesh_component.set_collision_profile_name("NoCollision")

    bed_lamp = interactable("BedLamp", (480, 1060, 56), 0, "bedroom", CYL, (0, 0, 32), (30, 30, 22), "Lilac",
                 unreal.InteractToggle.LIGHT, "Turn on lamp", "Turn off lamp",
                 on_emissive=(5, 3.5, 5), light_loc=(0, 0, 28), light_color=(255, 200, 230), light_intensity=2500)
    bed_lamp_body = bed_lamp.get_editor_property("body")
    bed_lamp_body.set_static_mesh(unreal.load_asset("/Game/ICanFixHim/Environment/Meshes/SM_FloorLampShade"))
    bed_lamp_body.set_relative_scale3d(unreal.Vector(.65,.65,.65))
    for index in range(bed_lamp_body.get_num_materials()):
        bed_lamp_body.set_material(index, mic("Lilac"))
    wardrobe_door = interactable("Wardrobe_Door", (76, 666, 0), 0, "bedroom", CUBE, (0, 54, 100), (5, 106, 196), "WoodDark",
                 unreal.InteractToggle.ROTATE, "Open wardrobe", "Close wardrobe", rotation=(-100, 0, 0))
    moving_mesh(wardrobe_door, "SM_WardrobeDoor", (0,54,0), yaw=180)
    drawer = interactable("Dresser_Drawer", (225, 713, 55), 90, "bedroom", CUBE, (0, 0, 0), (5, 130, 24), "WoodDark",
                 unreal.InteractToggle.SLIDE, "Open drawer", "Close drawer", offset=(35, 0, 0))
    moving_mesh(drawer, "SM_DresserDrawer", (-14,0,0), yaw=180)

    mold = malady("Malady_Mold", "malcolm", unreal.MaladyStyle.MOLD, (790, 760, 140), 180, "bedroom",
           CUBE, (1, 0, 0), (3, 150, 170), "WallCream", fx_offset=(2, 0, 0),
           hunk_spawn=(140, 0, 0), talk_spot=(300, 0, 0))
    mold.set_editor_property("use_authored_body_materials", True)
    mold.get_editor_property("body").set_material(0, mic("Invisible"))
    mold.get_editor_property("body").set_cast_shadow(False)
    mold_plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    mold_detail = prim("MoldDamage", (786,760,150), (160,160,1), "Mildew", f, mesh=mold_plane, yaw=90, roll=90, collide=False)
    mold_detail.static_mesh_component.set_material(0, unreal.load_asset("/Game/ICanFixHim/Materials/Environment/M_Mold_Overlay"))
    mold_detail.static_mesh_component.set_collision_profile_name("NoCollision")
    mold_detail.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    mold_detail.tags = [unreal.Name("RepairDamage"), unreal.Name("AuthoredMoldDamage")]
    mold_detail.attach_to_actor(mold, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)


def build_lighting():
    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 800), rot(yaw=200, pitch=-38))
    sun.set_actor_label("Sun")
    sun.set_folder_path("Lighting")
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_editor_property("intensity", 8.0)
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
        point_light(f"CeilingLight_{rid}", (cx, cy, H - 40), 3400)
    # Fill lights so corners aren't murky.
    point_light("Fill_Living", (150, 500, 200), 850, radius=600, shadows=False)
    point_light("Fill_Kitchen", (1250, 150, 200), 850, radius=600, shadows=False)

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
    s.set_editor_property("bloom_intensity", 0.25)
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
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        raise RuntimeError("Stop PIE before rebuilding the apartment")
    expected = os.path.realpath(os.path.join(os.path.dirname(__file__), "../.."))
    actual = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
    if actual != expected:
        raise RuntimeError("Refusing to rebuild a different project: " + actual)
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
