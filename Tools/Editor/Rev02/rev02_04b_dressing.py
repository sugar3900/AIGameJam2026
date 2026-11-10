"""Rev02 step 4b: place the wall-mounted dressing and small children of the revision 02 elevation schedule
(docs/.../layout-revision-02/kitchen-dining-study/elevations/elevation-schedule.json) using existing art.

Each scheduled instance is an existing actor group moved to its rect, or a duplicate of one (same mesh and
materials). Rects are metres: wall-mounted items are positioned by their union bounds centre = rect centre, with the
bottom at the scheduled z. Facing changes are yaw deltas from the source group's current facing. Children sit on
the top of their parent. Run once after rev02_04 on a fresh Rev02 copy (refuses a second run); rev02_08 verifies
every scheduled instance and records intentional omissions.
"""
import math, unreal
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level(MAP)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert 'Rev02_Furnished' in acts and 'Rev02_Dressed' not in acts, 'run once, after rev02_04, on a fresh Rev02 copy'

def actor(label):
    assert label in acts, 'missing actor ' + label
    return acts[label]

def union(labels):
    mn, mx = [1e9] * 3, [-1e9] * 3
    for lab in labels:
        a = actor(lab)
        if isinstance(a, unreal.FixHimInteractable): continue            # lights/radii would inflate the bounds
        o, e = a.get_actor_bounds(False, True)
        for i, (c, h) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
            mn[i] = min(mn[i], c - h); mx[i] = max(mx[i], c + h)
    return mn, mx

def rot2(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

def move(labels, center, dyaw=0.0):
    """Rigidly turn the group by dyaw about its union-bounds centre and put that centre at center (x, y, z)."""
    mn, mx = union(labels); p = [(a + b) / 2 for a, b in zip(mn, mx)]
    for lab in labels:
        a = actor(lab)
        if a.get_attach_parent_actor() and a.get_attach_parent_actor().get_actor_label() in labels: continue
        l, r = a.get_actor_location(), a.get_actor_rotation()
        d = rot2((l.x - p[0], l.y - p[1]), dyaw)
        a.modify()
        a.set_actor_location_and_rotation(unreal.Vector(center[0] + d[0], center[1] + d[1], l.z - p[2] + center[2]),
                                          unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + dyaw), False, True)

def dup(labels, suffix):
    out = []
    for lab in labels:
        a = actor(lab); c = a.static_mesh_component
        b = A.spawn_actor_from_object(c.static_mesh, a.get_actor_location(), a.get_actor_rotation())
        nl = lab + '_' + suffix
        b.set_actor_label(nl); b.set_folder_path(str(a.get_folder_path())); b.set_actor_scale3d(a.get_actor_scale3d())
        for i in range(c.get_num_materials()): b.static_mesh_component.set_material(i, c.get_material(i))
        b.static_mesh_component.set_collision_profile_name(c.get_collision_profile_name())
        b.set_actor_hidden_in_game(False); b.static_mesh_component.set_visibility(True)
        acts[nl] = b; out.append(nl)
    return out

def rect_center(rect, z, h):
    x, y, w, d = rect
    return ((x + w / 2) * 100, (y + d / 2) * 100, (z + h / 2) * 100)

def put_on(labels, parent, at):
    """Stand a child group on top of its parent at plan point at=(x, y) cm."""
    top = union([parent])[1][2]
    mn, mx = union(labels)
    move(labels, (at[0], at[1], top + (mx[2] - mn[2]) / 2 + 0.05))

YAW = {'south': 0, 'east': -90, 'north': 180, 'west': 90}           # imported fronts face +Y
def dyaw_to(labels_anchor, front):
    return (YAW[front] - actor(labels_anchor).get_actor_rotation().yaw + 540) % 360 - 180

# ---------------- wall shelves (ARC-WALL-SHELF-01) ----------------
SHELF = 'Art_BA_WallShelf_ARC_WALL_SHELF_01'
basin_kids = ['Art_BA_Bottle_BA_Bottle_Body', 'Art_BA_Bottle_BA_Bottle_Stopper', 'Art_BA_Cup_BA_Cup', 'Art_BA_Cup_BA_Brush_Ivory',
              'Art_BA_Cup_BA_Brush_Sage', 'Art_BA_Soap_BA_SoapBar', 'Art_BA_Soap_BA_SoapDish']
SHELVES = {   # instance: (rect, z, front)
    '046': ([5.45, 0.06, 0.65, 0.15], 1.55, 'south'), '063': ([4.59, 8.7, 0.15, 0.65], 1.62, 'west'),
    '065': ([0.06, 7.98, 0.15, 0.65], 1.65, 'east'), '072': ([7.96, 6.6, 0.15, 0.65], 1.65, 'east'),
    '074': ([11.79, 7.22, 0.15, 0.65], 1.45, 'west'), '080': ([5.25, 5.66, 0.65, 0.15], 1.55, 'south'),
    '083': ([3.35, 3.59, 0.65, 0.15], 1.65, 'north'), '085': ([7.69, 7.15, 0.15, 0.65], 1.65, 'west')}
shelf_of = {}
for inst, (rect, z, front) in SHELVES.items():
    lab = dup([SHELF], 'S' + inst)[0]
    move([lab], rect_center(rect, z, 0.145), dyaw_to(lab, front)); shelf_of[inst] = lab
# The existing shelf and its toiletries become the basin shelf (077).
move([SHELF] + basin_kids, rect_center([4.86, 7.8, 0.15, 0.65], 1.28, 0.145), dyaw_to(SHELF, 'east'))
shelf_of['077'] = SHELF
def on_shelf(labels, inst, frac):
    """Children along the shelf: frac 0..1 from one end of its long axis."""
    s = shelf_of[inst]; mn, mx = union([s])
    along_x = (mx[0] - mn[0]) > (mx[1] - mn[1])
    c = ((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2)
    at = (mn[0] + 8 + (mx[0] - mn[0] - 16) * frac, c[1]) if along_x else (c[0], mn[1] + 8 + (mx[1] - mn[1] - 16) * frac)
    put_on(labels, s, at)
on_shelf(['Art_BA_Jar_BA_Jar_Body', 'Art_BA_Jar_BA_Jar_Lid'], '080', 0.3)                       # north toiletries shelf
on_shelf(dup(['Art_BA_Soap_BA_SoapDish', 'Art_BA_Soap_BA_SoapBar'], '080'), '080', 0.75)
on_shelf(['Art_BA_FoldedTowel_BA_Folded_Towel'], '085', 0.35)                                     # folded towel + tin
on_shelf(['Art_BA_Tin_BA_Tin_Body', 'Art_BA_Tin_BA_Tin_Lid'], '085', 0.8)
on_shelf(dup(['Art_KI_Pottery_KI_Pottery_01'], '046'), '046', 0.5)                               # living display shelf
on_shelf(dup(['Art_HA_Vase'], '065'), '065', 0.7)                                                # bedroom books + vase
on_shelf(['Art_KI_Geranium_KI_Geranium'], '072', 0.5)                                            # daybed shelf plant
on_shelf(dup(['Art_KI_Pottery_KI_Pottery_01'], '074'), '074', 0.5)                               # office east: small pot
on_shelf(dup(['Art_KI_Mug_KI_Mug_01'], '083'), '083', 0.3)                                       # breakfast mugs / pottery
on_shelf(dup(['Art_KI_Pottery_KI_Pottery_01'], '083'), '083', 0.75)

# ---------------- switches (BA-SWITCH-01) ----------------
SW = ['Art_BA_Switch_BA_Switch_Plate', 'Art_BA_Switch_BA_Switch_Toggle']
for inst, rect, z, front in [('068', [2.76, 5.66, 0.1, 0.035], 1.08, 'south'), ('075', [9.22, 5.66, 0.1, 0.035], 1.08, 'south'),
                             # 086 (FIX-009): centred on the 19 cm jamb face y 3.55-3.74 between the portal and the
                             # hall-wall corner; the schedule rect y 3.65-3.75 put the plate into the corner wall.
                             ('086', [4.705, 3.61, 0.035, 0.1], 1.08, 'west')]:
    labs = dup(SW, 'S' + inst); move(labs, rect_center(rect, z, 0.12), dyaw_to(labs[0], front))
move(SW, rect_center([4.86, 5.75, 0.035, 0.1], 1.18, 0.12), dyaw_to(SW[0], 'east'))             # 079 bath switch

# ---------------- bath wall fittings ----------------
RAIL = ['Art_BA_TowelRail_BA_Towel_Rail', 'Art_BA_TowelRail_BA_Towel_Ivory', 'Art_BA_TowelRail_BA_Towel_Rose']
hand = dup(['Art_BA_TowelRail_BA_Towel_Rail', 'Art_BA_TowelRail_BA_Towel_Ivory'], 'S078')        # hand towel rail by the basin
move(hand, rect_center([4.86, 6.05, 0.08, 0.55], 1.02, 0.5), dyaw_to(hand[0], 'east'))
move(RAIL, rect_center([7.76, 5.98, 0.08, 0.65], 1.12, 0.6), dyaw_to(RAIL[0], 'west'))           # 084 bath towel rail
move(['Art_BA_Hook_BA_Hook_01', 'Art_BA_HandTowel_BA_Hand_Towel'], rect_center([7.45, 5.66, 0.22, 0.08], 1.1, 0.55),
     dyaw_to('Art_BA_Hook_BA_Hook_01', 'south'))                                                  # 082 hook + hand towel
move(['Art_BA_Roll_BA_Roll_Holder', 'Art_BA_Roll_BA_Roll_Paper'], rect_center([7.805, 6.88, 0.035, 0.18], 0.66, 0.18),
     dyaw_to('Art_BA_Roll_BA_Roll_Holder', 'west'))                                               # 083 toilet roll
move(['Art_BA_Art01_BA_ART_01'], rect_center([5.35, 5.66, 0.46, 0.035], 1.95, 0.5))               # 081 small botanical

# ---------------- sconces (HA-SCONCE-01): scheduled heights; breakfast sconce added ----------------
S1 = ['Art_HA_Sconce01_HA_Sconce_Bulb', 'Art_HA_Sconce01_HA_Sconce_Hardware', 'Art_HA_Sconce01_HA_Sconce_Shade']
S2 = [l.replace('Sconce01', 'Sconce02') for l in S1]
move(S1 + ['Sconce_Hall_1'], rect_center([4.45, 3.86, 0.16, 0.18], 1.85, 0.3))                   # 059 hall warm sconce
move(S2 + ['Sconce_Hall_2'], rect_center([11.76, 5.22, 0.18, 0.16], 1.82, 0.3))                  # 044 entry sconce
S3 = dup(S1, 'Kitchen')                                                                           # 084 breakfast sconce
move(S3, rect_center([1.5, 3.56, 0.16, 0.18], 1.75, 0.3), dyaw_to(S3[1], 'north'))

# ---------------- table / counter children ----------------
put_on(dup(['Art_KI_Mug_KI_Mug_01'], 'Coffee'), 'Art_LV_Coffee_04', (962, 262))                  # coffee table mug
put_on(dup(['Art_KI_Mug_KI_Mug_01'], 'Prep'), 'Art_KI_Cab0450_body', (430, 42))                   # prep / uppers mug
put_on(dup(['Art_KI_Bowl_KI_Bowl'], 'Counter'), 'Art_KI_Cab0775_body', (300, 42))                 # counter bowl

# ---------------- closet storage boxes (BR-CLOSET-BOX-01) ----------------
BOX = ['Art_BR_ClosetBox_BR_BOX_BODY', 'Art_BR_ClosetBox_BR_BOX_LID']
for inst, rect in [('095', [10.95, 6.087, 0.3, 0.253]), ('097', [10.95, 6.46, 0.3, 0.253])]:
    labs = dup(BOX, 'S' + inst); mn, mx = union(labs)
    move(labs, rect_center(rect, 0.08, (mx[2] - mn[2]) / 100.0), dyaw_to(labs[0], 'south'))
mn, mx = union(BOX)
move(BOX, rect_center([0.084, 4.2, 0.253, 0.3], 0.0, (mx[2] - mn[2]) / 100.0))                    # 091 low west box (BC)

# ---------------- books (LV-BOOK-01 parts, imported uncombined by rev02_02) ----------------
# Each LV shelf book is five meshes (cover, pages, page top, two spine gilts) in the LV bookcase's model space; the
# three lying books are two. Books keep their LV materials (by slot name). Runs are laid out in another piece's
# local frame: rows keep their authored spacing, with a few books left out and the run shifted for variety.
BOOKS = '/Game/ICanFixHim/Environment/Rev02/LV_BookParts'
lvmesh = actor('Art_LV_Book_LV_BOOK_BOOKS').static_mesh_component
SLOTMAT = {str(sl.material_slot_name): lvmesh.get_material(i) for i, sl in enumerate(lvmesh.static_mesh.static_materials)}
parts = []
for path in unreal.EditorAssetLibrary.list_assets(BOOKS, False, False):
    m = unreal.EditorAssetLibrary.load_asset(path)
    if isinstance(m, unreal.StaticMesh):
        b = m.get_bounding_box(); parts.append((m, b.min, b.max))
def row_of(mn): return 'A' if mn.z < 95 else 'B' if mn.z < 145 else 'C'
books = {}                                   # (row, cover x0) -> parts of one book
covers = [(mn, mx) for m, mn, mx in parts if 'book_cover' in m.get_name() or 'lying_book' in m.get_name()]
for m, mn, mx in parts:
    cx = (mn.x + mx.x) / 2
    owner = next(((row_of(c0), round(c0.x, 1)) for c0, c1 in covers if row_of(c0) == row_of(mn) and c0.x - 0.5 <= cx <= c1.x + 0.5), None)
    if owner: books.setdefault(owner, []).append(m)
BASE = {'A': 54.8, 'B': 101.8, 'C': 148.8}   # LV shelf tops under each row (local z)
def lay_books(row, host, shelf_z, skip=(), dx=0.0, scale=1.0, keep=None, y_front=None, tag='B'):
    """Stand one LV row on host's shelf at local height shelf_z (host frame: front +Y), dropping `skip`ped books."""
    t = actor(host).get_actor_transform(); rot = actor(host).get_actor_rotation()
    keys = sorted(k for k in books if k[0] == row)
    keys = [k for i, k in enumerate(keys) if i not in skip][:keep] if keep else [k for i, k in enumerate(keys) if i not in skip]
    if not keys: return []
    mins = [p.get_bounding_box().min for k in keys for p in books[k]]; maxs = [p.get_bounding_box().max for k in keys for p in books[k]]
    x0, x1 = min(v.x for v in mins), max(v.x for v in maxs); y1 = max(v.y for v in maxs)
    out = []
    for k in keys:
        for m in books[k]:
            # local placement: centre the run in x (plus dx), front of the books at y_front, bottoms on shelf_z
            off = unreal.Vector(-(x0 + x1) / 2 * scale + dx, (y_front - y1 * scale) if y_front is not None else 0, shelf_z - BASE[row] * scale)
            a = A.spawn_actor_from_object(m, t.transform_location(off), rot)
            a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            a.set_actor_label('Art_Book_%s_%s_%d' % (tag, m.get_name().replace('LV_BOOK_BOOKS_', ''), len(out)))
            a.set_folder_path('Redesign/Imported Art/Rev02 Books')
            c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
            for i, sl in enumerate(m.static_materials):
                mt = SLOTMAT.get(str(sl.material_slot_name))
                if mt: c.set_material(i, mt)
            acts[a.get_actor_label()] = a; out.append(a.get_actor_label())
    return out
# Bedroom bookcase (OF-BOOKCASE-01:015): shelves at world z 11.9 and 47.9; its front faces local +Y.
ofc = actor('Art_OF_Bookcase_OF_BOOKCASE_BODY'); olo, ohi = ofc.static_mesh_component.get_local_bounds()
lay_books('A', 'Art_OF_Bookcase_OF_BOOKCASE_BODY', 11.9, skip=(2, 6), dx=4, y_front=ohi.y - 3, tag='OFLow')
lay_books('C', 'Art_OF_Bookcase_OF_BOOKCASE_BODY', 47.9, skip=(0, 4), dx=-6, y_front=ohi.y - 3, tag='OFHigh')
# The plant's trailing foliage hangs below its pot, so anchor by the pot base: in the LV bookcase's model space the
# pot stands on the top shelf at z 148.8 cm.
plant = dup(['Art_LV_Book_LV_BOOK_PLANT'], 'OFTop')
put_on(plant, 'Art_OF_Bookcase_OF_BOOKCASE_BODY', (30, 728))
pa = actor(plant[0]); pl = pa.get_actor_location()
pa.set_actor_location(unreal.Vector(pl.x, pl.y, union(['Art_OF_Bookcase_OF_BOOKCASE_BODY'])[1][2] - 148.8 * pa.get_actor_scale3d().z), False, True)
put_on(dup(['Art_BR_ClosetBox_BR_BOX_BODY', 'Art_BR_ClosetBox_BR_BOX_LID'], 'OFTop'), 'Art_OF_Bookcase_OF_BOOKCASE_BODY', (30, 668))
# Bedroom display shelf (:063): a short run of small books (70 %) and a tin as the keepsake.
s063 = shelf_of['063']; slo, shi = actor(s063).static_mesh_component.get_local_bounds()
lay_books('B', s063, shi.z, keep=5, dx=-12, scale=0.7, y_front=shi.y - 1, tag='S063')
on_shelf(dup(['Art_LV_Book_LV_BOOK_TIN'], '063'), '063', 0.82)

# ---------------- height / position corrections against the schedule ----------------
# Living plant (LV-PLANT-01:026): stand top 0.48 m + riser 0.036 m -> plant origin 0.516 m. The A+ placement
# left the riser and plant 45 cm above the stand.
rmn, rmx = union(['Art_HA_PlantStand_Riser']); smx = union(['Art_HA_PlantStand_LV_Plant_Stand'])[1]
pmn, pmx = union(['Art_HA_PlantStand_Riser', 'Art_HA_Plant'])
move(['Art_HA_PlantStand_Riser', 'Art_HA_Plant'], ((pmn[0] + pmx[0]) / 2, (pmn[1] + pmx[1]) / 2, (pmn[2] + pmx[2]) / 2 + smx[2] - rmn[2]))
# Pan rail with its pans (KI-PAN-RAIL-01:085): assembly from 1.65 m (rail at the top, pans hanging below).
PR = ['Art_KI_PanRail_KI_Pan_Rail_Assembly', 'Art_KI_Pan_A_KI_Pan_Body', 'Art_KI_Pan_A_KI_Pan_Handle', 'Art_KI_Pan_B_KI_Pan_Body', 'Art_KI_Pan_B_KI_Pan_Handle']
mn, mx = union(PR); move(PR, ((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, 165 + (mx[2] - mn[2]) / 2))
# Tyler's cracked tile (BA-TILE-01:086) is centred over the tub at x 5.845 m; his malady (with the attached crack
# overlay, hunk spawn and talk spot) moves with it.
o, _ = actor('Damage_BA_CrackedTile').get_actor_bounds(False)
mt = actor('Malady_PinkTile'); l = mt.get_actor_location(); mt.modify()
mt.set_actor_location(unreal.Vector(l.x + 584.5 - o.x, l.y, l.z), False, True)

m = A.spawn_actor_from_class(unreal.Note, unreal.Vector(0, 0, -510)); m.set_actor_label('Rev02_Dressed'); m.set_folder_path('Redesign/Imported Art/Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 dressing] saved')
