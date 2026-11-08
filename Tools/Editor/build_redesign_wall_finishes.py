"""Replace gray blockout walls with per-room finished wall skins and place wall kits.

Run after build_redesign_finish_materials.py. Rebuilds Redesign/Shell walls as two
half-thickness boxes per segment (each gets the plaster of the room it faces), then
places ARC-LIVING-WALL-01 on the living north wall, BR-WAINSCOT-01 around the bedroom,
BA-TILE-01 around the bath, and ARC-TRIM-01 baseboard/crown elsewhere.
Imported kit fronts face local +Y in Unreal; origin at the module's left end.
"""
import json, os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
plan = json.load(open(os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/A-plus-candidate.json')))
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
R = '/Game/ICanFixHim/Environment/Redesign/'
F = R + 'Finishes/'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level(MAP)
load = unreal.EditorAssetLibrary.load_asset
cube = load('/Engine/BasicShapes/Cube')
MI = {k: load(F + 'MI_' + k) for k in ('Plaster_Living', 'Plaster_Kitchen', 'Plaster_Bedroom', 'Plaster_Exterior', 'Trim_Cream')}
mesh = lambda p: load(R + p)

for a in A.get_all_level_actors():
    fp = str(a.get_folder_path())
    if fp.startswith('Redesign/Shell') or fp.startswith('Redesign/Wall Finishes'):
        A.destroy_actor(a)

# ---------- room lookup (closets first) ----------
ZONES = [((0, 560, 180, 145), 'Plaster_Living'),        # bedroom mold closet
         ((1070, 300, 130, 80), 'Plaster_Living'),       # coat closet
         ((1075, 560, 125, 120), 'Plaster_Kitchen'),     # office closet
         ((0, 0, 550, 380), 'Plaster_Living'), ((550, 0, 650, 380), 'Plaster_Kitchen'),
         ((0, 380, 1200, 180), 'Plaster_Living'), ((0, 560, 480, 395), 'Plaster_Bedroom'),
         ((480, 560, 310, 395), 'Plaster_Living'), ((790, 560, 410, 395), 'Plaster_Kitchen')]
def zone(x, y):
    for (x0, y0, w, d), m in ZONES:
        if x0 < x < x0 + w and y0 < y < y0 + d: return m
    return 'Plaster_Exterior'

def box(label, center, size, mat, folder='Redesign/Shell'):
    a = A.spawn_actor_from_object(cube, unreal.Vector(*center))
    a.set_actor_label(label); a.set_folder_path(folder)
    a.set_actor_scale3d(unreal.Vector(*(v / 100.0 for v in size)))
    a.static_mesh_component.set_material(0, MI[mat])
    return a

def plan_openings(axis, fixed):
    out = []
    for d in plan['swing_doors'] + plan['windows']:
        if d['axis'] != ('h' if axis == 'x' else 'v'): continue
        if abs(100 * d['y' if axis == 'x' else 'x'] - fixed) > .01: continue
        s = 100 * d['x' if axis == 'x' else 'y']
        out.append((s, s + 100 * d['width'], 100 * d.get('sill_height', 0), 100 * d.get('head_height', 2.1)))
    if axis == 'x' and abs(fixed - 380) < .01: out.append((1090, 1180, 0, 210))
    return out

BOUNDS = {'x': [180, 480, 550, 790, 1070, 1075], 'y': [300, 380, 560, 680, 705]}
HIDE = []  # (axis, fixed, a, b): keep collision, hide visuals (kit geometry replaces them)
def wall(name, axis, fixed, start, end, openings=(), hide=None):
    pts = sorted(set([start, end] + [v for o in openings for v in o[:2]] + [v for v in BOUNDS[axis] if start < v < end]))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        op = next((o for o in openings if a >= o[0] - .001 and b <= o[1] + .001), None)
        spans = [(0, 275)] if op is None else [(0, op[2]), (op[3], 275)]
        for j, (z0, z1) in enumerate(spans):
            if z1 <= z0: continue
            for side in (-1, 1):
                off = fixed + side * 3
                if axis == 'x':
                    c, s, probe = ((a + b) / 2, off, (z0 + z1) / 2), (b - a, 6, z1 - z0), ((a + b) / 2, fixed + side * 6.5)
                else:
                    c, s, probe = (off, (a + b) / 2, (z0 + z1) / 2), (6, b - a, z1 - z0), (fixed + side * 6.5, (a + b) / 2)
                act = box('%s_%d_%d_%s' % (name, i, j, 'P' if side > 0 else 'N'), c, s, zone(*probe))
                if hide and hide[0] <= a and b <= hide[1]:
                    act.static_mesh_component.set_visibility(False)
                    act.set_actor_label(act.get_actor_label() + '_CollisionOnly')

for name, axis, fixed, start, end in [
        ('North', 'x', 0, 0, 1200), ('South', 'x', 955, 0, 1200), ('West', 'y', 0, 0, 955), ('East', 'y', 1200, 0, 955),
        ('HallNorth', 'x', 380, 0, 1200), ('HallSouth', 'x', 560, 0, 1200),
        ('LivingKitchen', 'y', 550, 0, 380), ('BedroomBath', 'y', 480, 560, 955), ('BathOffice', 'y', 790, 560, 955)]:
    wall(name, axis, fixed, start, end, plan_openings(axis, fixed), hide=(0, 550) if name == 'North' else None)
wall('BedroomClosetFront', 'x', 705, 0, 180, [(45, 135, 0, 210)])
wall('BedroomClosetSide', 'y', 180, 560, 705)
wall('OfficeClosetFront', 'x', 680, 1075, 1200, [(1093, 1183, 0, 210)])
wall('OfficeClosetSide', 'y', 1075, 560, 680)
wall('CoatClosetBack', 'x', 300, 1070, 1200)
wall('CoatClosetSide', 'y', 1070, 300, 380)

# ---------- living-room wall kit on the north exterior wall ----------
KIT = 'Redesign/Wall Finishes/Living'
def kit(label, m, x, sx=1.0, mats=None):
    a = A.spawn_actor_from_object(m, unreal.Vector(x, 0, 0), unreal.Rotator(0, 0, 0))
    a.set_actor_label(label); a.set_folder_path(KIT); a.set_actor_scale3d(unreal.Vector(sx, 1, 1))
    c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
    for i, mt in enumerate(mats or []):
        if mt: c.set_material(i, mt)
    return a
solid, win = mesh('ARC_LivingWall/ARC_Living_SolidWall_2m'), mesh('ARC_LivingWall/ARC_Living_WindowWall_2p4m')
wm = [MI['Plaster_Living'], MI['Trim_Cream']]
kit('Kit_LV_N_Solid_W', solid, 47.5, 0.95, wm)              # 0-95
kit('Kit_LV_N_Window', win, 215, 1.0, wm)                   # 95-335, opening 135-295
kit('Kit_LV_N_Solid_E', solid, 435, 1.0, wm)                # 335-535
kit('Kit_LV_N_Solid_End', solid, 542.5, 0.075, wm)          # 535-550 (ends inside partition)
kit('Kit_LV_N_Casing', mesh('ARC_LivingWall/ARC_Window_Casing_Sash'), 215, 1.0, [MI['Trim_Cream']])
glass = kit('Kit_LV_N_Glazing', mesh('ARC_LivingWall/ARC_Window_Glazing'), 215)
gm = unreal.EditorAssetLibrary.load_asset(F + 'MI_Window_Glass')
if gm: glass.static_mesh_component.set_material(0, gm)
glass.static_mesh_component.set_cast_shadow(False)

# ---------- strip placement for wainscot / tile / trim ----------
def room_openings(axis, plane, s):
    fixed = plane - 6 * s
    out = plan_openings(axis, fixed)
    if axis == 'x' and abs(fixed - 705) < .1: out.append((45, 135, 0, 210))
    if axis == 'x' and abs(fixed - 680) < .1: out.append((1093, 1183, 0, 210))
    return out

def strip(tag, folder, m, axis, plane, s, span, z, h, mats=None, collision=False, zscale=1.0, keep=None):
    """Tile 1 m modules (origin left, front +Y) along a room face. s=+1: room on + side of plane."""
    ops = [o for o in room_openings(axis, plane, s) if o[2] < z + h and o[3] > z]
    pieces, cur = [], span[0]
    for o0, o1, _, _ in sorted(ops):
        if o1 <= span[0] or o0 >= span[1]: continue
        if o0 > cur: pieces.append((cur, o0))
        cur = max(cur, o1)
    if cur < span[1]: pieces.append((cur, span[1]))
    out = []
    for a0, a1 in pieces:
        n = max(1, int(round((a1 - a0) / 100.0)))
        step = (a1 - a0) / n
        for k in range(n):
            u0, u1 = a0 + k * step, a0 + (k + 1) * step
            if axis == 'x':
                yaw, loc = (0, (u0, plane, z)) if s > 0 else (180, (u1, plane, z))
            else:
                yaw, loc = (-90, (plane, u1, z)) if s > 0 else (90, (plane, u0, z))
            act = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
            act.set_actor_scale3d(unreal.Vector(step / 100.0, 1, zscale))
            act.set_actor_label('%s_%d' % (tag, len(out))); act.set_folder_path(folder)
            c = act.static_mesh_component
            if not collision: c.set_collision_profile_name('NoCollision')
            for i, mt in enumerate(mats or []):
                if mt: c.set_material(i, mt)
            out.append((act, u0, u1))
    return out

def faces(rect, skip=()):
    x0, y0, w, d = rect
    f = {'N': ('x', y0 + 6, 1, (x0 + 6, x0 + w - 6)), 'S': ('x', y0 + d - 6, -1, (x0 + 6, x0 + w - 6)),
         'W': ('y', x0 + 6, 1, (y0 + 6, y0 + d - 6)), 'E': ('y', x0 + w - 6, -1, (y0 + 6, y0 + d - 6))}
    return {k: v for k, v in f.items() if k not in skip}

base, crown = mesh('ARC_Trim/Baseboard_1m'), mesh('ARC_Trim/Crown_1m')
trim = [MI['Trim_Cream']]
def trims(room, rect, skip_base=(), skip_crown=(), extra=()):
    fl = list(faces(rect).items()) + list(extra)
    for k, (axis, plane, s, span) in fl:
        if k not in skip_base:
            strip('Trim_%s_%s_Base' % (room, k), 'Redesign/Wall Finishes/Trim', base, axis, plane, s, span, 0, 13, trim)
        if k not in skip_crown:
            strip('Trim_%s_%s_Crown' % (room, k), 'Redesign/Wall Finishes/Trim', crown, axis, plane, s, span, 265, 10, trim)

# Living: kit already has base/crown on N.
trims('LV', (0, 0, 550, 380), skip_base=('N',), skip_crown=('N',))
# Kitchen: coat closet notches the SE corner.
trims('KI', (550, 0, 650, 380), skip_base=('S', 'E'), skip_crown=('S', 'E'),
      extra=[('S1', ('x', 374, -1, (556, 1064))), ('E1', ('y', 1194, -1, (6, 294))),
             ('CB', ('x', 294, -1, (1064, 1194))), ('CS', ('y', 1064, -1, (306, 374)))])
trims('HA', (0, 380, 1200, 180))
# Office: closet in NE corner.
trims('OF', (790, 560, 410, 395), skip_base=('N', 'E'), skip_crown=('N', 'E'),
      extra=[('N1', ('x', 566, 1, (796, 1069))), ('E1', ('y', 1194, -1, (686, 949))),
             ('CF', ('x', 686, 1, (1069, 1194))), ('CS', ('y', 1069, -1, (566, 686)))])

# Bedroom: wainscot (has its own baseboard and rail) + crown; closet in NW corner.
BRF = [('N', ('x', 566, 1, (186, 474))), ('CS', ('y', 186, 1, (566, 699))), ('CF', ('x', 711, 1, (6, 186))),
       ('W', ('y', 6, 1, (711, 949))), ('S', ('x', 949, -1, (6, 474))), ('E', ('y', 474, -1, (566, 949)))]
wain = mesh('BR_Wainscot/BR_Wainscot_Module')
east_mods = []
for k, (axis, plane, s, span) in BRF:
    mods = strip('Wainscot_BR_%s' % k, 'Redesign/Wall Finishes/Bedroom', wain, axis, plane, s, span, 0, 110)
    if k == 'E': east_mods = mods
    strip('Trim_BR_%s_Crown' % k, 'Redesign/Wall Finishes/Trim', crown, axis, plane, s, span, 265, 10, trim)
# Localized lead-paint state on the east wall (separate repair; no gameplay wired yet).
if east_mods:
    src = east_mods[len(east_mods) // 2][0]
    d = A.spawn_actor_from_object(mesh('BR_Wainscot/BR_Wainscot_Damage'), src.get_actor_location(), src.get_actor_rotation())
    d.set_actor_scale3d(src.get_actor_scale3d()); d.set_actor_label('Damage_BR_LeadPaint'); d.set_folder_path('Redesign/Wall Finishes/Bedroom')
    d.static_mesh_component.set_collision_profile_name('NoCollision'); d.static_mesh_component.set_cast_shadow(False)
    d.tags = [unreal.Name('RepairDamage'), unreal.Name('LeadPaint')]

# Bath: 1.15 m tile wainscot, 1.55 m tub surround on south wall, crack above tub.
tile, cap, ext = mesh('BA_Tile/BA_Tile_1m_Module'), mesh('BA_Tile/BA_Tile_Cap'), mesh('BA_Tile/BA_Tile_040_Extension')
BAF = faces((480, 560, 310, 395))
south_mods = []
for k, (axis, plane, s, span) in BAF.items():
    mods = strip('Tile_BA_%s' % k, 'Redesign/Wall Finishes/Bath', tile, axis, plane, s, span, 0, 110)
    if k == 'S':
        south_mods = mods
        strip('Tile_BA_%s_Ext' % k, 'Redesign/Wall Finishes/Bath', ext, axis, plane, s, span, 110, 40)
        strip('Tile_BA_%s_Cap' % k, 'Redesign/Wall Finishes/Bath', cap, axis, plane, s, span, 150, 5)
    else:
        strip('Tile_BA_%s_Cap' % k, 'Redesign/Wall Finishes/Bath', cap, axis, plane, s, span, 110, 5)
    strip('Trim_BA_%s_Crown' % k, 'Redesign/Wall Finishes/Trim', crown, axis, plane, s, span, 265, 10, trim)
if south_mods:
    src = south_mods[len(south_mods) // 2][0]
    loc = src.get_actor_location(); loc.z += 45
    d = A.spawn_actor_from_object(mesh('BA_Tile/BA_Tile_Damage'), loc, src.get_actor_rotation())
    d.set_actor_scale3d(src.get_actor_scale3d()); d.set_actor_label('Damage_BA_CrackedTile'); d.set_folder_path('Redesign/Wall Finishes/Bath')
    d.static_mesh_component.set_collision_profile_name('NoCollision')
    d.tags = [unreal.Name('RepairDamage'), unreal.Name('tyler')]

assert L.save_current_level()
n = sum(1 for a in A.get_all_level_actors() if str(a.get_folder_path()).startswith(('Redesign/Shell', 'Redesign/Wall Finishes')))
unreal.log('[Walls] saved; shell+finish actors=%d' % n)
