"""Wall art, lamps and dressing from the elevation sheets (positions converted from
docs/.../elevations at 125 px/m). Fronts import as +Y (Blender -Y); wall pieces are snapped by
their combined rotated bounds to the finished wall face and centred at the given height.
Lamps use tabletop origins and are set on the measured top of the placed furniture.
"""
import math, os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
YAW = {'N': 0, 'S': 180, 'W': -90, 'E': 90}
# label, asset dir, parts, mode, args
#  wall: (side, face, along, z_centre)   floor: (x, y, yaw)   top: (x, y, z, yaw)   ontop: (anchor label prefix, dx, dy, yaw)
ITEMS = [
    ('LV_Art04', 'LV-ART-04', ['LV-ART-04'], 'wall', ('W', 6, 161, 165)),
    ('LV_SideTable', 'LV-SIDE-TABLE-01', ['LV_SIDE_TABLE_BODY', 'LV_SIDE_TABLE_DRAWER'], 'wallfloor', ('W', 6, 40)),
    ('LV_TableLamp', 'LV-TABLE-LAMP-01', ['LV_TableLampBody', 'LV_TableLampShade', 'LV_TableLampBulb'], 'ontop', ('Art_LV_SideTable_LV_SIDE_TABLE_BODY', 0, 0, 0)),
    ('LV_Chest', 'LV-CHEST-01', ['LV_CHEST_BODY', 'LV_CHEST_LID'], 'wallfloor', ('S', 374, 167)),
    ('HA_Art02', 'HA-ART-02', ['HA-ART-02'], 'wall', ('N', 386, 139, 160)),
    ('HA_Art03', 'HA-ART-03', ['HA-ART-03'], 'wall', ('N', 386, 817, 160)),
    ('HA_Art09', 'HA-ART-09', ['HA-ART-09'], 'wall', ('W', 6, 469, 165)),
    ('HA_Sconce01', 'HA-SCONCE-01', ['HA_Sconce_Hardware', 'HA_Sconce_Shade', 'HA_Sconce_Bulb'], 'wall', ('N', 386, 330, 185)),
    ('HA_Sconce02', 'HA-SCONCE-01', ['HA_Sconce_Hardware', 'HA_Sconce_Shade', 'HA_Sconce_Bulb'], 'wall', ('N', 386, 750, 185)),
    ('HA_Hooks', 'HA-HOOKS-01', ['HA_Hooks'], 'wall', ('N', 386, 982, 160)),
    ('HA_Coat', 'HA-COAT-01', ['HA_Coat'], 'wall', ('N', 390, 960, 118)),
    ('HA_Runner', 'HA-RUNNER-01', ['HA_RUNNER_01'], 'floor', (480, 470, 0)),
    ('BA_Mirror', 'BA-MIRROR-01', ['BA_Mirror_mirror', 'BA_Mirror_sconce', 'BA_Mirror_globe'], 'wall', ('W', 486, 727, 160)),
    ('BA_TowelRail', 'BA-TOWEL-RAIL-01', ['BA_Towel_Rail', 'BA_Towel_Ivory', 'BA_Towel_Rose'], 'wall', ('E', 784, 690, 95)),
    ('BA_Art01', 'BA-ART-01', ['BA-ART-01'], 'wall', ('N', 566, 580, 165)),
    ('BR_ArtFloral', 'BR-ART-FLORAL-01', ['BR-ART-FLORAL-01'], 'wall', ('N', 566, 250, 165)),
    ('BR_Lamp_W', 'BR-LAMP-01', ['BR_LampBody', 'BR_LampShade', 'BR_LampBulb'], 'ontop', ('Art_BR_Nightstand_W_BR_NIGHTSTAND_BODY', 0, 0, 180)),
    ('BR_Lamp_E', 'BR-LAMP-01', ['BR_LampBody', 'BR_LampShade', 'BR_LampBulb'], 'ontop', ('Art_BR_Nightstand_E_BR_NIGHTSTAND_BODY', 0, 0, 180)),
    ('OF_ArtBotanical', 'OF-ART-BOTANICAL-01', ['OF-ART-BOTANICAL-01'], 'wall', ('E', 1194, 760, 150)),
    ('OF_ArtLandscape', 'OF-ART-LANDSCAPE-01', ['OF-ART-LANDSCAPE-01'], 'wall', ('W', 796, 820, 150)),
    ('OF_DeskLamp', 'OF-DESK-LAMP-01', ['OF_DeskLamp_Body', 'OF_DeskLamp_Shade', 'OF_DeskLamp_Bulb'], 'top', (1000, 905, 76, 180)),
    ('KI_Art01', 'KI-ART-01', ['KI-ART-01'], 'wall', ('E', 1194, 185, 165)),
    ('KI_PanRail', 'KI-PAN-RAIL-01', ['KI_Pan_Rail_Assembly'], 'wall', ('N', 6, 740, 190)),
    ('KI_Kettle', 'KI-KETTLE-01', ['KI_Kettle_Body', 'KI_Kettle_Lid'], 'top', (672, 58, 91, 0)),
]
COLLIDE = {'LV_SIDE_TABLE_BODY', 'LV_CHEST_BODY'}

def find_fbx(d, part):
    for root, _, files in os.walk(os.path.join(SRC, d)):
        if part + '.fbx' in files: return os.path.join(root, part + '.fbx')
    raise RuntimeError('missing %s/%s' % (d, part))
def mesh(d, part):
    folder = d.replace('-01', '').replace('-', '_')
    path = R + folder + '/' + part.replace('-', '_')
    if EAL.does_asset_exist(path): return EAL.load_asset(path)
    t = unreal.AssetImportTask(); t.filename = find_fbx(d, part); t.destination_path = R + folder; t.destination_name = part.replace('-', '_')
    t.automated = True; t.replace_existing = True; t.save = True
    o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
    o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = part in COLLIDE; t.options = o
    tools.import_asset_tasks([t]); m = EAL.load_asset(path)
    if not m: raise RuntimeError(path)
    b = m.get_bounding_box()
    unreal.log('[Dress] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (part, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
    return m
def aabb(meshes, yaw):
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    xs, ys, zs = [], [], []
    for m in meshes:
        b = m.get_bounding_box()
        for x in (b.min.x, b.max.x):
            for y in (b.min.y, b.max.y):
                xs.append(x * c - y * s); ys.append(x * s + y * c)
        zs += [b.min.z, b.max.z]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

plans = [(lab, [(p, mesh(d, p)) for p in parts], mode, args) for lab, d, parts, mode, args in ITEMS]
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
FOLDER = 'Redesign/Imported Art/Dressing'
for a in A.get_all_level_actors():
    if str(a.get_folder_path()) == FOLDER: A.destroy_actor(a)
def tops():
    return {a.get_actor_label(): a for a in A.get_all_level_actors()}
for lab, parts, mode, args in plans:
    ms = [m for _, m in parts]
    if mode in ('wall', 'wallfloor'):
        side, face, along = args[0], args[1], args[2]; yaw = YAW[side]
        x0, x1, y0, y1, z0, z1 = aabb(ms, yaw)
        z = (args[3] - (z0 + z1) / 2) if mode == 'wall' else -z0
        if side in 'NS':
            lx = along - (x0 + x1) / 2; ly = face - y0 if side == 'N' else face - y1
        else:
            ly = along - (y0 + y1) / 2; lx = face - x0 if side == 'W' else face - x1
        loc = (lx, ly, z)
    elif mode == 'floor':
        x, y, yaw = args; x0, x1, y0, y1, z0, z1 = aabb(ms, yaw); loc = (x - (x0 + x1) / 2, y - (y0 + y1) / 2, -z0 + 0.2)
    elif mode == 'top':
        x, y, z, yaw = args; loc = (x, y, z)
    else:  # ontop
        anchor = tops()[args[0]]; o, e = anchor.get_actor_bounds(False); yaw = args[3]
        loc = (o.x + args[1], o.y + args[2], o.z + e.z)
    for i, (p, m) in enumerate(parts):
        a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
        a.set_actor_label('Art_%s_%s' % (lab, p.replace('-', '_'))); a.set_folder_path(FOLDER)
        if p not in COLLIDE: a.static_mesh_component.set_collision_profile_name('NoCollision')
    unreal.log('[Dress] placed %s at (%.1f,%.1f,%.1f) yaw %d' % (lab, loc[0], loc[1], loc[2], yaw))
assert L.save_current_level()
unreal.log('[Dress] saved')
