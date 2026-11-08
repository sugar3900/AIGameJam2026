"""Import and place the remaining furniture kits over their plan placeholders.

All kits: front is Blender -Y (imports as Unreal +Y), floor-centred origin, moving parts
exported in assembly space. yaw maps the front into the room: 0 -> +Y, 180 -> -Y,
90 -> -X, -90 -> +X. Wall pieces are snapped so their rotated bounds touch the finished
wall face; free pieces are centred on the plan rectangle.
"""
import math, os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# label, src dir, parts (first = body with collision), placeholder idx, plan rect (m), yaw, snap (side, face cm) or None
ITEMS = [
    ('LV_TV', 'LV-TV-01/model', ['LV_TV_body', 'LV_TV_left', 'LV_TV_right', 'LV_TV_screen_off'], 1, (4.86, 1.25, .5, 1.1), 90, ('E', 544)),
    ('BR_Nightstand_W', 'BR-NIGHTSTAND-01/models', ['BR_NIGHTSTAND_BODY', 'BR_NIGHTSTAND_DRAWER'], 16, (1.4, 8.95, .45, .45), 180, ('S', 949)),
    ('BR_Nightstand_E', 'BR-NIGHTSTAND-01/models', ['BR_NIGHTSTAND_BODY', 'BR_NIGHTSTAND_DRAWER'], 17, (3.5, 8.95, .45, .45), 180, ('S', 949)),
    ('BA_Linen', 'BA-LINEN-01/model', ['BA_Linen_Body', 'BA_Linen_UpperDoor', 'BA_Linen_LowerDoor'], 22, (7.15, 8.75, .6, .6), 90, ('E', 784)),
    ('OF_Chair', 'OF-CHAIR-01/model', ['OF_CHAIR_01'], 25, (10.1, 8.15, .5, .5), 0, None),
    ('HA_Console', 'HA-CONSOLE-01/model', ['HA_CONSOLE_BODY', 'HA_CONSOLE_DRAWER'], 26, (2.0, 3.86, 1.05, .25), 0, ('N', 386)),
    ('HA_PlantStand', 'LV-PLANT-STAND-01/model', ['LV_Plant_Stand'], 27, (2.05, 5.29, .45, .25), 180, ('S', 554)),
    ('HA_Bench', 'HA-BENCH-01/model', ['HA_BENCH_01'], 28, (11.08, 5.29, .62, .25), 180, ('S', 554)),
    ('HA_EndCabinet', 'HA-CABINET-01/model', ['HA_CABINET_BODY', 'HA_CABINET_DOOR_L', 'HA_CABINET_DOOR_R', 'HA_CABINET_DRAWER'], 29, (.06, 4.18, .25, 1.02), -90, ('W', 6)),
    ('BA_Basket', 'BA-BASKET-01/model', ['BA_Basket', 'BA_Towel_0', 'BA_Towel_1', 'BA_Towel_2'], 30, (4.95, 5.75, .5, .4), 0, ('N', 566)),
    ('BA_Mat', 'BA-MAT-01/model', ['BA_Mat'], 31, (5.45, 8.25, .55, .4), 0, None),
    ('BA_Bin', 'BA-BIN-01/model', ['Bin_body', 'Bin_lid', 'Bin_pedal'], 32, (7.5, 5.75, .25, .3), 0, ('N', 566)),
    ('OF_Bookcase', 'OF-BOOKCASE-01/model', ['OF_BOOKCASE_BODY'], 33, (11.58, 7.05, .3, 1.1), 90, ('E', 1194)),
    ('OF_FloorLamp', 'LV-LAMP-01/model', ['LV_LampBody', 'LV_LampShade', 'LV_LampBulb'], 34, (11.6, 8.2, .28, .28), 0, None),
    ('OF_Cabinet', 'OF-CABINET-01/model', ['OF_CABINET_BODY', 'OF_CABINET_DOOR_L', 'OF_CABINET_DOOR_R', 'OF_CABINET_DRAWER'], 35, (8.05, 5.96, .3, .75), -90, ('W', 796)),
]
NO_COLLISION_BODIES = {'BA_Mat', 'BA_Basket', 'BA_Bin', 'OF_FloorLamp'}

def find_fbx(src, part):
    for d in (src, src.replace('/models', '/model'), src.replace('/model', '/models')):
        p = os.path.join(SRC, d, part + '.fbx')
        if os.path.exists(p): return p
    raise RuntimeError('missing ' + src + '/' + part)

cache = {}
def mesh(src, part, folder):
    key = folder + '/' + part
    if key in cache: return cache[key]
    if EAL.does_asset_exist(R + key):
        cache[key] = EAL.load_asset(R + key); return cache[key]
    t = unreal.AssetImportTask(); t.filename = find_fbx(src, part); t.destination_path = R + folder; t.destination_name = part
    t.automated = True; t.replace_existing = True; t.save = True
    o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
    o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = True; t.options = o
    tools.import_asset_tasks([t]); m = EAL.load_asset(R + key)
    if not m: raise RuntimeError(key)
    b = m.get_bounding_box()
    unreal.log('[Furn] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (part, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
    cache[key] = m; return m

def rotated_aabb(b, yaw):
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    xs, ys = [], []
    for x in (b.min.x, b.max.x):
        for y in (b.min.y, b.max.y):
            xs.append(x * c - y * s); ys.append(x * s + y * c)
    return min(xs), max(xs), min(ys), max(ys)

# Import first (no level held), then edit level.
plans = []
for label, src, parts, idx, rect, yaw, snap in ITEMS:
    folder = src.split('/')[0].replace('-01', '').replace('-', '_')
    plans.append((label, [(p, mesh(src, p, folder)) for p in parts], idx, rect, yaw, snap))
extra = {k: mesh(*v) for k, v in {'riser': ('LV-PLANT-STAND-01/model', 'LV_Plant_Stand_Riser', 'LV_PLANT_STAND'),
                                   'plant': ('LV-PLANT-01/model', 'LV_Plant', 'LV_PLANT'),
                                   'vase': ('HA-VASE-01/model', 'HA_VASE_01', 'HA_VASE'),
                                   'flowers': ('HA-FLOWERS-01/model', 'HA_FLOWERS_01', 'HA_FLOWERS')}.items()}
fuse = {p: mesh('LV-FUSE-01/exports', p, 'LV_FUSE') for p in ['LV_FUSE_01_Shell', 'LV_FUSE_01_Door', 'LV_FUSE_01_Wire_Damaged', 'LV_FUSE_01_Wire_Repaired']}

assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
FOLDER = 'Redesign/Imported Art/Furnishing'
idxs = {p[2] for p in plans} | {5}
for a in A.get_all_level_actors():
    lab = a.get_actor_label()
    if str(a.get_folder_path()) == FOLDER or any(lab.startswith('Placeholder_%02d_' % i) for i in idxs):
        A.destroy_actor(a)

def put(m, loc, yaw, label, collide):
    a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(label); a.set_folder_path(FOLDER)
    if not collide: a.static_mesh_component.set_collision_profile_name('NoCollision')
    return a

tops = {}
for label, parts, idx, rect, yaw, snap in plans:
    x, y, w, d = (v * 100 for v in rect)
    x0, x1, y0, y1 = rotated_aabb(parts[0][1].get_bounding_box(), yaw)
    lx, ly = x + w / 2 - (x0 + x1) / 2, y + d / 2 - (y0 + y1) / 2
    if snap:
        side, face = snap
        if side == 'N': ly = face - y0
        if side == 'S': ly = face - y1
        if side == 'W': lx = face - x0
        if side == 'E': lx = face - x1
    for i, (p, m) in enumerate(parts):
        put(m, (lx, ly, 0), yaw, 'Art_%s_%s' % (label, p), i == 0 and label not in NO_COLLISION_BODIES)
    tops[label] = (lx, ly, parts[0][1].get_bounding_box().max.z)
    unreal.log('[Furn] placed %s at (%.1f,%.1f) yaw %d' % (label, lx, ly, yaw))

# Hall plant on stand (+riser), flowers in vase on the console.
sx, sy, sz = tops['HA_PlantStand']
put(extra['riser'], (sx, sy, sz), 0, 'Art_HA_PlantStand_Riser', False)
put(extra['plant'], (sx, sy, sz + extra['riser'].get_bounding_box().max.z), 0, 'Art_HA_Plant', False)
cx, cy, cz = tops['HA_Console']
put(extra['vase'], (cx - 25, cy, cz), 0, 'Art_HA_Vase', False)
put(extra['flowers'], (cx - 25, cy, cz + 26.0), 0, 'Art_HA_Flowers', False)

# Fusebox (Wyatt): origin at wall, lower box edge; living south wall face y=374, facing north.
for p, m in fuse.items():
    a = put(m, (312.5, 374, 120), 180, 'Art_LV_Fuse_' + p.replace('LV_FUSE_01_', ''), p == 'LV_FUSE_01_Shell')
    if p == 'LV_FUSE_01_Wire_Damaged': a.tags = [unreal.Name('RepairDamage'), unreal.Name('wyatt')]
    if p == 'LV_FUSE_01_Wire_Repaired':
        a.set_actor_hidden_in_game(True); a.static_mesh_component.set_visibility(False)
        a.tags = [unreal.Name('RepairFixed'), unreal.Name('wyatt')]
assert L.save_current_level()
unreal.log('[Furn] saved')
