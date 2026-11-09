"""Rev02 step 3: rebuild the shell of L_Apartment_Rev02 for the approved revision 02 plan.

Source of truth: docs/03 Art & Audio/Apartment Design/layout-revision-02/kitchen-dining-study/approved-plan.json and
elevations/elevation-schedule.json (metres, origin at the NW wall centre-line corner, +x east, +y south; Unreal cm
share the same axes). Rebuilds walls (two 6 cm half-boxes per segment, each with the finish of the room it faces),
door/window/portal openings, floors, trim, bath tile, office wainscot (moved from the bedroom), the lead-paint
overlay (moved with it), the living window wall kit, the kitchen counter-height window, the fitted room/entry doors
and the sliding-closet frames. The ceiling grid and hidden floor collision boxes are layout independent and kept.

Openings are rough sizes: room/entry doors 1.05 m (ARC-DOOR-02, 0.99 clear) with heads 2.14 m; sliding closets
0.96 m with heads 2.18 m; the walk-in closet 1.10 m / 2.14 m; kitchen portal 1.20 m / 2.30 m; the living/hall
opening 7.20 m / 2.45 m. Re-runnable on the Rev02 map (run rev02_01 first for a fresh copy).
"""
import unreal
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
R = '/Game/ICanFixHim/Environment/Redesign/'
R2 = '/Game/ICanFixHim/Environment/Rev02/'
F = R + 'Finishes/'
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
load = EAL.load_asset
assert L.load_level(MAP)
cube = load('/Engine/BasicShapes/Cube')
MI = {k: load(F + 'MI_' + k) for k in ('Plaster_Living', 'Plaster_Kitchen', 'Plaster_Bedroom', 'Plaster_Exterior', 'Trim_Cream')}
mesh = lambda p: load(R + p)

REBUILT = ('Redesign/Shell', 'Redesign/Wall Finishes', 'Redesign/Floor Finishes', 'Redesign/Doors')
lead_label = 'Damage_BR_LeadPaint'      # label kept for continuity; the overlay now sits in the office
SUPERSEDED = {'Art_CoatCloset_Frame', 'Art_OfficeCloset_Frame'}   # A+ ARC-SLIDING-CLOSET-01 frames, replaced below
for a in A.get_all_level_actors():
    if str(a.get_folder_path()).startswith(REBUILT) or a.get_actor_label() in SUPERSEDED:
        A.destroy_actor(a)

# ---------------- plan geometry (cm) ----------------
# Openings per wall centre-line: (u0, u1, sill/bottom, head). Rough sizes, see module docstring.
OPEN = {
    ('x', 0):    [(135, 295, 125, 240), (775, 935, 90, 230)],                       # kitchen counter-height window, living window
    ('x', 955):  [(330, 440, 90, 230), (525, 640, 150, 230), (970, 1110, 90, 230)],  # bedroom, bath, office windows
    ('y', 1200): [(400, 505, 0, 214)],                                              # entry door
    ('y', 480):  [(235, 355, 0, 230)],                                              # kitchen portal (no leaf)
    ('x', 380):  [(480, 1200, 0, 245)],                                             # living/dining open to hall, header above
    ('x', 560):  [(55, 165, 0, 214), (300, 405, 0, 214), (625, 730, 0, 214), (945, 1050, 0, 214), (1090, 1186, 0, 218)],
    ('x', 715):  [(1090, 1186, 0, 218)],                                            # guest wardrobe front
}
def openings(axis, fixed, lo=-1e9, hi=1e9):
    return [o for o in OPEN.get((axis, fixed), []) if o[1] > lo and o[0] < hi]

ZONES = [((0, 380, 220, 180), 'Plaster_Living'),        # walk-in mold closet (BC)
         ((1075, 560, 125, 155), 'Plaster_Living'),     # coat closet + guest wardrobe
         ((0, 0, 480, 380), 'Plaster_Kitchen'), ((480, 0, 720, 380), 'Plaster_Living'), ((220, 380, 980, 180), 'Plaster_Living'),
         ((0, 560, 480, 395), 'Plaster_Bedroom'), ((480, 560, 310, 395), 'Plaster_Living'), ((790, 560, 410, 395), 'Plaster_Kitchen')]
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

BOUNDS = {'x': [220, 480, 790, 1075], 'y': [380, 560, 640, 715]}
def wall(name, axis, fixed, start, end, hide=None):
    ops = openings(axis, fixed, start, end)
    pts = sorted(set([start, end] + [min(max(v, start), end) for o in ops for v in o[:2]] + [v for v in BOUNDS[axis] if start < v < end]))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        op = next((o for o in ops if a >= o[0] - .001 and b <= o[1] + .001), None)
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

WALLS = [('North', 'x', 0, 0, 1200), ('South', 'x', 955, 0, 1200), ('West', 'y', 0, 0, 955), ('East', 'y', 1200, 0, 955),
         ('HallNorth', 'x', 380, 0, 1200), ('HallSouth', 'x', 560, 0, 1200), ('KitchenLiving', 'y', 480, 0, 380),
         ('ClosetEast', 'y', 220, 380, 560), ('BedroomBath', 'y', 480, 560, 955), ('BathOffice', 'y', 790, 560, 955),
         ('ClosetSide', 'y', 1075, 560, 715), ('CoatBack', 'x', 640, 1075, 1200), ('WardrobeFront', 'x', 715, 1075, 1200)]
for name, axis, fixed, start, end in WALLS:
    wall(name, axis, fixed, start, end, hide=(480, 1200) if name == 'North' else None)   # living window wall kit replaces visuals
# The entry leaf never opens and is narrower than its jambs; this panel outside the east wall (behind the outer
# casing) keeps exterior sky from showing through the gap.
box('EntryBacker', (1214, 452.5, 112.5), (4, 125, 225), 'Plaster_Exterior')

def spawn(m, loc, yaw=0.0, label='', folder='', mats=(), scale=(1, 1, 1), collision=False):
    a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(label); a.set_folder_path(folder); a.set_actor_scale3d(unreal.Vector(*scale))
    c = a.static_mesh_component
    if not collision: c.set_collision_profile_name('NoCollision')
    for i, mt in enumerate(mats):
        if mt: c.set_material(i, mt)
    return a

# ---------------- living window wall kit (north wall x 480-1200, window centred x=855) ----------------
KIT = 'Redesign/Wall Finishes/Living'
solid, win = mesh('ARC_LivingWall/ARC_Living_SolidWall_2m'), mesh('ARC_LivingWall/ARC_Living_WindowWall_2p4m')
wm = [MI['Plaster_Living'], MI['Trim_Cream']]
for label, m, x0, x1 in [('Kit_LV_N_End_W', solid, 480, 495), ('Kit_LV_N_Solid_W', solid, 495, 735),
                         ('Kit_LV_N_Solid_E', solid, 975, 1175), ('Kit_LV_N_End_E', solid, 1175, 1200)]:
    spawn(m, ((x0 + x1) / 2, 0, 0), 0, label, KIT, wm, ((x1 - x0) / 200.0, 1, 1))
spawn(win, (855, 0, 0), 0, 'Kit_LV_N_Window', KIT, wm)
spawn(mesh('ARC_LivingWall/ARC_Window_Casing_Sash'), (855, 0, 0), 0, 'Kit_LV_N_Casing', KIT, [MI['Trim_Cream']])
glass_mi = load(F + 'MI_Window_Glass')
g = spawn(mesh('ARC_LivingWall/ARC_Window_Glazing'), (855, 0, 0), 0, 'Kit_LV_N_Glazing', KIT, [glass_mi])
g.static_mesh_component.set_cast_shadow(False)

# ---------------- windows ----------------
WIN = 'Redesign/Wall Finishes/Windows'
frosted = load(F + 'M_Redesign_GlassFrosted')
for room, folder, x in [('BR', 'ARC_WindowNarrow', 385), ('BA', 'ARC_WindowBath', 582.5), ('OF', 'ARC_WindowOffice', 1040)]:
    for p in ('frame', 'upper_sash', 'lower_sash', 'upper_glass', 'lower_glass'):
        a = spawn(mesh('%s/ARC_Window_%s' % (folder, p)), (x, 955, 0), 180, 'Win_%s_%s' % (room, p), WIN)
        c = a.static_mesh_component
        if 'glass' in p:
            c.set_material(0, frosted if room == 'BA' else glass_mi); c.set_cast_shadow(False)
        else:
            for i in range(c.get_num_materials()): c.set_material(i, MI['Trim_Cream'])
# ARC-WINDOW-KITCHEN-02: all five parts share a sill-local origin at world (215, 0, 125) cm, room side +Y.
for p in ('frame', 'upper_sash', 'lower_sash', 'upper_glass', 'lower_glass'):
    a = spawn(load(R2 + 'ARC_WindowKitchen02/ARC_Window_Kitchen_' + p), (215, 0, 125), 0, 'Win_KI_' + p, WIN)
    c = a.static_mesh_component
    if 'glass' in p:
        c.set_material(0, glass_mi); c.set_cast_shadow(False)
    else:
        for i in range(c.get_num_materials()): c.set_material(i, MI['Trim_Cream'])

# ---------------- trim, tile, wainscot ----------------
def strip(tag, folder, m, axis, plane, s, span, z, h, mats=None, zscale=1.0, under_sill=False):
    """Tile 1 m modules (origin left, front +Y) along a room face. s=+1: room on + side of plane.
    under_sill: below a window whose sill is above z, fill the opening's width with modules squashed to the
    sill height (fitted apron panels; their rail stops under the sill instead of crossing the window)."""
    ops = [o for o in openings(axis, plane - 6 * s) if o[2] < z + h and o[3] > z]
    pieces, cur = [], span[0]
    for o0, o1, sill, _ in sorted(ops):
        if o1 <= span[0] or o0 >= span[1]: continue
        if o0 > cur: pieces.append((cur, o0, zscale))
        if under_sill and sill > z:
            pieces.append((max(o0, span[0]), min(o1, span[1]), zscale * (sill - z) / h))
        cur = max(cur, o1)
    if cur < span[1]: pieces.append((cur, span[1], zscale))
    out = []
    for a0, a1, zs in pieces:
        n = max(1, int(round((a1 - a0) / 100.0)))
        step = (a1 - a0) / n
        for k in range(n):
            u0, u1 = a0 + k * step, a0 + (k + 1) * step
            if axis == 'x':
                yaw, loc = (0, (u0, plane, z)) if s > 0 else (180, (u1, plane, z))
            else:
                yaw, loc = (-90, (plane, u1, z)) if s > 0 else (90, (plane, u0, z))
            act = spawn(m, loc, yaw, '%s_%d' % (tag, len(out)), folder, mats or [], (step / 100.0, 1, zs))
            out.append((act, u0, u1))
    return out

TR = 'Redesign/Wall Finishes/Trim'
base, crown, trim = mesh('ARC_Trim/Baseboard_1m'), mesh('ARC_Trim/Crown_1m'), [MI['Trim_Cream']]
def trims(room, faces, skip_base=(), skip_crown=()):
    for k, (axis, plane, s, span) in faces:
        if k not in skip_base: strip('Trim_%s_%s_Base' % (room, k), TR, base, axis, plane, s, span, 0, 13, trim)
        if k not in skip_crown: strip('Trim_%s_%s_Crown' % (room, k), TR, crown, axis, plane, s, span, 265, 10, trim)

# Room faces: (key, (axis, face plane, side, span)). Face planes sit 6 cm off the wall centre-lines.
trims('KI', [('N', ('x', 6, 1, (6, 474))), ('W', ('y', 6, 1, (6, 374))), ('E', ('y', 474, -1, (6, 374))), ('S', ('x', 374, -1, (6, 474)))])
# Living/dining + entry share one open volume: the kit carries the north wall's base/crown; the 7.2 m opening's
# header gets crown on both faces; the east wall runs past the opening to the hall end.
trims('LV', [('W', ('y', 486, 1, (6, 374))), ('E', ('y', 1194, -1, (6, 554))), ('HDR', ('x', 374, -1, (480, 1194)))], skip_base=('HDR',))
trims('HA', [('N', ('x', 386, 1, (226, 474))), ('W', ('y', 226, 1, (386, 554))), ('S', ('x', 554, -1, (226, 1194))),
             ('HDR', ('x', 386, 1, (486, 1194)))], skip_base=('HDR',))
trims('BC', [('N', ('x', 386, 1, (6, 214))), ('W', ('y', 6, 1, (386, 554))), ('E', ('y', 214, -1, (386, 554))), ('S', ('x', 554, -1, (6, 214)))])
trims('BR', [('N', ('x', 566, 1, (6, 474))), ('W', ('y', 6, 1, (566, 949))), ('E', ('y', 474, -1, (566, 949))), ('S', ('x', 949, -1, (6, 474)))])

# Office / guest: white wainscot (BR-WAINSCOT-01, own base + rail) plus crown; coat closet and wardrobe in the NE.
OFF = [('N', ('x', 566, 1, (796, 1069))), ('CS', ('y', 1069, -1, (566, 721))), ('WF', ('x', 721, 1, (1069, 1194))),
       ('E', ('y', 1194, -1, (721, 949))), ('S', ('x', 949, -1, (796, 1194))), ('W', ('y', 796, 1, (566, 949)))]
wain = mesh('BR_Wainscot/BR_Wainscot_Module')
north_mods = []
for k, (axis, plane, s, span) in OFF:
    mods = strip('Wainscot_OF_%s' % k, 'Redesign/Wall Finishes/Office', wain, axis, plane, s, span, 0, 110, under_sill=True)
    if k == 'N': north_mods = mods
    strip('Trim_OF_%s_Crown' % k, TR, crown, axis, plane, s, span, 265, 10, trim)
# Lead-paint condition: office north wall x 8.65-9.20 m (elevation schedule BR-WAINSCOT-01:069), on the module there.
lead_mi = load(F + 'MI_Decal_LeadPaint')
src = next((m for m, u0, u1 in north_mods if u0 <= 892.5 <= u1 and abs(m.get_actor_scale3d().z - 1) < 1e-3), None)
assert src, 'no office north wainscot module at x=892.5'
d = A.spawn_actor_from_object(mesh('BR_Wainscot/BR_Wainscot_Damage'), src.get_actor_location(), src.get_actor_rotation())
d.set_actor_scale3d(src.get_actor_scale3d()); d.set_actor_label(lead_label); d.set_folder_path('Redesign/Wall Finishes/Office')
d.static_mesh_component.set_collision_profile_name('NoCollision'); d.static_mesh_component.set_cast_shadow(False)
d.tags = [unreal.Name('RepairDamage'), unreal.Name('LeadPaint')]
if lead_mi: d.static_mesh_component.set_material(0, lead_mi)
# The overlay mesh is the damaged patch itself; centre it on the scheduled patch (x 8.65-9.20, z 0.55-0.85 m).
o, _ = d.get_actor_bounds(False); l = d.get_actor_location()
d.set_actor_location(unreal.Vector(l.x + 892.5 - o.x, l.y, l.z + 70 - o.z), False, True)

# Bath (unchanged room): 1.10 m tile wainscot, 1.50 m tub surround on the south wall. Tyler's crack overlay
# lives in the gameplay sublevel, attached to his malady, and is not touched here.
tile, cap, ext = mesh('BA_Tile/BA_Tile_1m_Module'), mesh('BA_Tile/BA_Tile_Cap'), mesh('BA_Tile/BA_Tile_040_Extension')
BAF = [('N', ('x', 566, 1, (486, 784))), ('S', ('x', 949, -1, (486, 784))), ('W', ('y', 486, 1, (566, 949))), ('E', ('y', 784, -1, (566, 949)))]
for k, (axis, plane, s, span) in BAF:
    strip('Tile_BA_%s' % k, 'Redesign/Wall Finishes/Bath', tile, axis, plane, s, span, 0, 110)
    if k == 'S':
        strip('Tile_BA_%s_Ext' % k, 'Redesign/Wall Finishes/Bath', ext, axis, plane, s, span, 110, 40)
        strip('Tile_BA_%s_Cap' % k, 'Redesign/Wall Finishes/Bath', cap, axis, plane, s, span, 150, 5)
    else:
        strip('Tile_BA_%s_Cap' % k, 'Redesign/Wall Finishes/Bath', cap, axis, plane, s, span, 110, 5)
    strip('Trim_BA_%s_Crown' % k, TR, crown, axis, plane, s, span, 265, 10, trim)

# ---------------- floors ----------------
def best(Lc, w):
    return min(range(1, 20), key=lambda n: abs(Lc / (n * w) - 1))
def grid(tag, m, rect, w, h, mats, origin='center'):
    x0, y0, W, D = rect
    nx, ny = best(W, w), best(D, h)
    sx, sy = W / (nx * w), D / (ny * h)
    for i in range(nx):
        for j in range(ny):
            loc = (x0 + (i + .5) * w * sx, y0 + (j + .5) * h * sy, 0) if origin == 'center' else (x0 + i * w * sx, y0 + (j + 1) * h * sy, 0)
            spawn(m, loc, 0, '%s_%d_%d' % (tag, i, j), 'Redesign/Floor Finishes', mats, (sx, sy, 1))
wood = mesh('ARC_FloorWood/ARC_Floor_Wood_2m')
wmats = [load(F + 'MI_FloorWood_Subfloor')] + [load(F + 'MI_FloorWood_%d' % i) for i in range(6)]
for tag, rect in [('LV', (480, 0, 720, 380)), ('HA', (220, 380, 980, 180)), ('BC', (0, 380, 220, 180)),
                  ('BR', (0, 560, 480, 395)), ('OF', (790, 560, 410, 395))]:
    grid('Floor_Wood_' + tag, wood, rect, 200, 200, wmats)
grid('Floor_KI_Top', mesh('KI_Tile/KI_TILE_TOP'), (0, 0, 480, 380), 100, 100, [load(F + 'MI_KitchenChecker')])
grid('Floor_KI_Sub', mesh('KI_Tile/KI_TILE_SUBSTRATE'), (0, 0, 480, 380), 100, 100, [load(F + 'MI_KitchenSubstrate')])
grid('Floor_BA_Hex', mesh('BA_Floor/BA_FLOOR_MODULE'), (480, 560, 310, 395), 90, 103.923,
     [load(F + 'MI_BathGrout'), load(F + 'MI_BathHex_Ivory'), load(F + 'MI_BathHex_Rose')], origin='corner')

# ---------------- doors (ARC-DOOR-02 / ARC-ENTRY-DOOR-02, 0.99 clear in 1.05 rough) ----------------
# Imported fronts face +Y; leaves are hinge-local and extend +X; hinge axis at frame-local (-49.5, +3.5).
paint, brass, edge, walnut = (load(F + n) for n in ('MI_Door_Paint', 'MI_Door_Brass', 'MI_Door_EdgeWood', 'MI_Entry_Walnut'))
DF, DL = load(R2 + 'ARC_Door02/ARC_Door02_Frame'), load(R2 + 'ARC_Door02/ARC_Door02_Leaf')
for room, cx, hinge in [('BR', 352.5, 'E'), ('BA', 677.5, 'W'), ('OF', 997.5, 'W')]:
    spawn(DF, (cx, 560, 0), 0, 'Door_%s_Frame' % room, 'Redesign/Doors', [paint, brass], collision=True)
    # Static open leaves collide (UCX slab). They stand at 90 deg, flat beside their jamb: at the source's 80 deg
    # reference pose the free end leans ~17 cm back into the opening and blocks the 76 cm player capsule on the
    # plan routes (measured with capsule traces); at 90 deg the routes keep 42-47 cm to the leaf.
    if hinge == 'W':      # opened into the room (south)
        spawn(DL, (cx - 49.5, 563.5, 0), 90, 'Door_%s_Leaf' % room, 'Redesign/Doors', [paint, brass, edge], collision=True)
    else:                 # plan: bedroom door hinged east; the leaf turned 180 so it extends west, opened south
        spawn(DL, (cx + 49.5, 556.5, 0), 90, 'Door_%s_Leaf' % room, 'Redesign/Doors', [paint, brass, edge], collision=True)
EF, EL = load(R2 + 'ARC_EntryDoor02/ARC_Entry_Door02_Frame'), load(R2 + 'ARC_EntryDoor02/ARC_Entry_Door02_Leaf')
spawn(EF, (1200, 452.5, 0), 90, 'Door_Entry_Frame', 'Redesign/Doors', [paint, brass], collision=True)
spawn(EL, (1196.5, 403.0, 0), 90, 'Door_Entry_Leaf', 'Redesign/Doors', [walnut, brass, edge], collision=True)

# Sliding-closet frames (ARC-SLIDING-CLOSET-02). Coat closet opens north into the entry; guest wardrobe south.
for room, y, yaw in [('Coat', 560, 180), ('Office', 715, 0)]:
    spawn(load(R2 + 'ARC_Sliding02/ARC_Sliding02_Frame'), (1138, y, 0), yaw, 'Art_%sCloset_Frame' % room, 'Redesign/Doors', collision=True)

assert L.save_current_level()
n = sum(1 for a in A.get_all_level_actors() if str(a.get_folder_path()).startswith(REBUILT))
unreal.log('[Rev02 shell] saved; actors=%d' % n)
