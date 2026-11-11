"""Rev02 step 5m (batch 2 final source releases): PROP-FIT-03, LV-SOFA-03, FEEDBACK-ROOM-03 and ARC-DOOR-03 installed on
the existing placements. Re-runnable; run after rev02_05l, then rev02_05c (pink bullnose) and rev02_05k (base trims).

Source FBXs are never edited. Where a release must be combined with retained art or needs retained collision, an engine
mesh is derived into Rev02/Room03Fit (Geometry Script; positions unchanged, same model space):
  - BR_Bed03_Combined = BR_Bed03_Frame + BR_Bed03_Bedding, the old BR_Bed slot order (walnut, throw, patchwork,
    cotton). The Bed interactable body and its hidden art source keep their transform; complex-as-simple like BR_Bed
    (sleep interaction and bed collision preserved; the hover trace hits one actor).
  - OF_Daybed03_Combined = the retained OF-DAYBED frame (only its Walnut_painted triangles) + OF_Daybed03_Bedding
    (shaped mattress, sewn cushions, projected quilt and hem). Complex-as-simple like the original.
  - ARC_Sliding03_Frame takes ARC_Sliding02_Frame's three UCX hulls (README: reuse prior jamb/head pieces).
  - LV_Book03_Book_NN: each FEEDBACK-ROOM-03 book (covers, rounded spine, pages, page edges, gilt bands imported
    uncombined) merged into one mesh in the LV model space, for the runs laid on the OF bookcase and the :063 shelf.
  - Baseboard_Outside_Start_28: the slim outside-start piece plane-cut to 28 cm (as rev02_03 did for ARC-TRIM-02).
Swaps (materials kept per slot by normalised slot name unless stated):
  - ARC-DOOR-03 frame+leaf on Door_BR/BA/OF (3 frame UCX + 1 leaf UCX from the kit).
  - slim Baseboard_1m on every straight run; Outside End/Start on the hall/living corner.
  - ARC_Sliding03 frame on both closet frames.
  - BA_CurvedL_Rod on the tub rod actor (580,907,0) yaw 180; BA_Curtain03_FixedReturn added there, NoCollision; the
    moving curtain and its slide are untouched.
  - LV_Book03_Books on the LV bookcase; LV_Book03_Plant on both plant copies (two-sided leaves, textured pot).
  - LV_SOFA_03 on Art_LV_Sofa; the woven throw takes MI_Sofa03_WovenThrow (throw-wool x (.58,.49,.36), rough .90, weave).
  - ARC_ClosetStorage03 in both hall closets + three HA_Hanger03 each at the assembly.json rail offsets, storage yaw,
    bedroom hanger wood / aged steel.
  - KI_PanPair03 at the pan rail origin and yaw; both old pan body/handle pairs removed; rail -> KI_Pan_Rail_Body only.
"""
import json, os, re, unreal
G = unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
E = '/Game/ICanFixHim/Environment/'; R2 = E + 'Rev02/'; MATS = R2 + 'Materials/'; FIT = R2 + 'Room03Fit/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
log = []

def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())
def load(p):
    o = EAL.load_asset(p); assert o, p; return o
def lvl_of(a): return a.get_outer().get_outer().get_name()

def swap(owner, comp, sm, override=None):
    """Swap comp's mesh, carrying materials across by normalised slot name (override: {norm slot: material})."""
    old = {norm(s.material_slot_name): comp.get_material(i) for i, s in enumerate(comp.static_mesh.static_materials)} if comp.static_mesh else {}
    owner.modify(); comp.set_static_mesh(sm)
    for i, s in enumerate(sm.static_materials):
        n = norm(s.material_slot_name)
        m = (override or {}).get(n, old.get(n))
        if m is not None: comp.set_material(i, m)
    return old

def actor_swap(label, sm, override=None):
    a = acts[label]; return swap(a, a.static_mesh_component, sm, override)

def to_dm(sm):
    dm = unreal.DynamicMesh()
    G.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(sm, dm, G.GeometryScriptCopyMeshFromAssetOptions(), G.GeometryScriptMeshReadLOD())
    return dm

def remap(dm, mapping):
    """Remap material IDs {from: to} without collisions."""
    for f, t in mapping.items(): G.GeometryScript_Materials.remap_material_i_ds(dm, f, 1000 + t)
    for t in set(mapping.values()): G.GeometryScript_Materials.remap_material_i_ds(dm, 1000 + t, t)

def bake(dm, name, slots, complex_collision=False):
    """slots: [(slot name, material)] in material-ID order."""
    path = FIT + name
    if EAL.does_asset_exist(path): sm = load(path)
    else:
        o = G.GeometryScriptCreateNewStaticMeshAssetOptions(); o.set_editor_property('enable_collision', False)
        sm, _ = G.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, path, o)
    co = G.GeometryScriptCopyMeshToAssetOptions()
    co.set_editor_property('replace_materials', True)
    co.set_editor_property('new_materials', [m for _, m in slots])
    co.set_editor_property('new_material_slot_names', [unreal.Name(n) for n, _ in slots])
    G.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, co, G.GeometryScriptMeshWriteLOD())
    if complex_collision:
        bs = sm.get_editor_property('body_setup'); bs.modify()
        bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assert EAL.save_loaded_asset(sm, False), path
    return sm

def spawn(sm, loc, rot, label, level, folder, mats=None, like=None):
    if label in acts: A.destroy_actor(acts.pop(label))
    assert L.set_current_level_by_name(level)
    a = A.spawn_actor_from_object(sm, loc, rot); a.set_actor_label(label); a.set_folder_path(folder); acts[label] = a
    c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
    for i, s in enumerate(sm.static_materials):
        m = (mats or {}).get(norm(s.material_slot_name))
        if m is not None: c.set_material(i, m)
    return a

def bounds(a):
    o, e = a.get_actor_bounds(False); return 'x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z)

# ================= ARC-DOOR-03 =================
DF, DL = load(R2 + 'ARC_Door03/ARC_Door03_Frame'), load(R2 + 'ARC_Door03/ARC_Door03_Leaf')
for room in ('BR', 'BA', 'OF'):
    actor_swap('Door_%s_Frame' % room, DF); actor_swap('Door_%s_Leaf' % room, DL)
log.append('ARC-DOOR-03 on Door_BR/BA/OF frame+leaf')

# ================= slim baseboards =================
BASE = load(R2 + 'Room03/Baseboard_1m'); n = 0
for a in A.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor): continue
    sm = a.static_mesh_component.static_mesh
    if sm and sm.get_path_name().startswith(E + 'Redesign/ARC_Trim/Baseboard_1m.'):
        swap(a, a.static_mesh_component, BASE); n += 1
actor_swap('Trim_HA_N_Base_OutsideEnd', load(R2 + 'Room03/Baseboard_Outside_End'))
trim = acts['Trim_HA_N_Base_OutsideEnd'].static_mesh_component.get_material(0)
dm = to_dm(load(R2 + 'Room03/Baseboard_Outside_Start'))
cut = G.GeometryScriptMeshPlaneCutOptions(); cut.set_editor_property('fill_holes', True)
G.GeometryScript_MeshBooleans.apply_mesh_plane_cut(dm, unreal.Transform(unreal.Vector(28, 0, 0), unreal.Rotator(pitch=-90, yaw=0, roll=0)), cut)
actor_swap('Trim_LV_W_Base_OutsideStart', bake(dm, 'Baseboard_Outside_Start_28', [('AgedIvoryPaint', trim)]))
log.append('slim baseboards: %d straight runs, outside end/start(28 cm) at (486,386)' % n)

# ================= sliding closet frames (frame only, prior UCX) =================
S3, S2 = load(R2 + 'Room03/ARC_Sliding03_Frame'), load(R2 + 'ARC_Sliding02/ARC_Sliding02_Frame')
col = G.GeometryScript_Collision.get_simple_collision_from_static_mesh(S2)
G.GeometryScript_Collision.set_simple_collision_of_static_mesh(col, S3, G.GeometryScriptSetSimpleCollisionOptions())
assert EAL.save_loaded_asset(S3, False)
ncol = len(S3.get_editor_property('body_setup').get_editor_property('agg_geom').get_editor_property('convex_elems'))
for l in ('Art_CoatCloset_Frame', 'Art_OfficeCloset_Frame'): actor_swap(l, S3)
log.append('ARC_Sliding03_Frame on both closet frames, %d UCX hulls from ARC_Sliding02' % ncol)

# ================= tub: curved L rod + fixed return =================
chrome = load(MATS + 'M_Rev02_AgedChrome')
rod = acts['Art_BA_TubFixture02_CurtainRod']
actor_swap('Art_BA_TubFixture02_CurtainRod', load(R2 + 'Room03/BA_CurvedL_Rod'), {'agedchrome': chrome})
cur = acts['Art_BA_Tub_BA_BA_Curtain'].static_mesh_component
floral = next(cur.get_material(i) for i, s in enumerate(cur.static_mesh.static_materials) if norm(s.material_slot_name) == 'floralcotton')
fr = spawn(load(R2 + 'Room03/BA_Curtain03_FixedReturn'), rod.get_actor_location(), rod.get_actor_rotation(), 'Art_BA_Curtain03_FixedReturn',
           lvl_of(rod), str(rod.get_folder_path()), {'floralcotton': floral, 'agedchrome': chrome})
log.append('BA_CurvedL_Rod on the tub rod; fixed return %s' % bounds(fr))

# ================= bed (frame + sewn bedding) =================
bed_body = acts['Bed'].get_editor_property('body')
old = {norm(s.material_slot_name): bed_body.get_material(i) for i, s in enumerate(bed_body.static_mesh.static_materials)}
dm = to_dm(load(R2 + 'Room03/BR_Bed03_Frame'))
bd = to_dm(load(R2 + 'Room03/BR_Bed03_Bedding')); remap(bd, {0: 1, 1: 2, 2: 3})   # throw, patchwork, cotton
G.GeometryScript_MeshEdits.append_mesh(dm, bd, unreal.Transform())
old['paintedwalnut'] = load(MATS + 'MI_Bed03_Walnut')     # README walnut image (installed slot was flat white Phong)
BED = bake(dm, 'BR_Bed03_Combined', [(n_, old[norm(n_)]) for n_ in ('Painted_Walnut', 'Dusty_Rose_Throw', 'Floral_Patchwork', 'Ivory_Cotton')], True)
swap(acts['Bed'], bed_body, BED, {'paintedwalnut': old['paintedwalnut']}); actor_swap('Art_BR_Bed', BED, {'paintedwalnut': old['paintedwalnut']})
# hover outline: the inverted hull showed broad shell faces through the throw's folds -> outline the rigid frame only
acts['Bed'].modify(); acts['Bed'].set_editor_property('outline_mesh_override', load(R2 + 'Room03/BR_Bed03_Frame'))
log.append('BR_Bed03_Combined on Bed body + Art_BR_Bed (complex-as-simple, walnut frame, frame-only hover outline)')

# ================= daybed (retained frame + new bedding) =================
db = acts['Art_OF_Daybed_23']; dc = db.static_mesh_component
OLD_DAYBED = load(E + 'Redesign/OF_Daybed/OF_Daybed')
names = [str(s.material_slot_name) for s in OLD_DAYBED.static_materials]
assert names == ['Walnut_painted', 'Floral_quilt', 'Ivory_linen', 'Rose_knit', 'Sage_cloth'], names
mats = {norm(s.material_slot_name): (dc.get_material(i) if dc.static_mesh == OLD_DAYBED else None) for i, s in enumerate(OLD_DAYBED.static_materials)}
if dc.static_mesh != OLD_DAYBED:   # re-run: materials from the installed combined mesh
    mats = {norm(s.material_slot_name): dc.get_material(i) for i, s in enumerate(dc.static_mesh.static_materials)}
dm = to_dm(OLD_DAYBED)
for k in (1, 2, 3, 4): G.GeometryScript_Materials.delete_triangles_by_material_id(dm, k)
bd = to_dm(load(R2 + 'Room03/OF_Daybed03_Bedding'))
bnames = [norm(s.material_slot_name) for s in load(R2 + 'Room03/OF_Daybed03_Bedding').static_materials]
remap(bd, {i: [norm(x) for x in names].index(n_) for i, n_ in enumerate(bnames)})
G.GeometryScript_MeshEdits.append_mesh(dm, bd, unreal.Transform())
DAYBED = bake(dm, 'OF_Daybed03_Combined', [(n_, mats[norm(n_)]) for n_ in names], True)
swap(db, dc, DAYBED)
log.append('OF_Daybed03_Combined (retained walnut frame + new bedding) on Art_OF_Daybed_23 %s' % bounds(db))

# ================= LV books + plant =================
lvb = acts['Art_LV_Book_LV_BOOK_BOOKS'].static_mesh_component
SLOTMAT = {norm(s.material_slot_name): lvb.get_material(i) for i, s in enumerate(lvb.static_mesh.static_materials)}
actor_swap('Art_LV_Book_LV_BOOK_BOOKS', load(R2 + 'Room03/LV_Book03_Books'), SLOTMAT)
PLANT = load(R2 + 'Room03/LV_Book03_Plant')
PM = {'plantleaf': load(MATS + 'MI_Plant03_Leaf'), 'plantleaflight': load(MATS + 'MI_Plant03_LeafLight'), 'ceramicpot': load(MATS + 'MI_Plant03_CeramicPot'),
      'potbotanical': load(MATS + 'MI_Plant03_PotBotanical'), 'potsoil': load(MATS + 'MI_Plant03_PotSoil')}
for l in ('Art_LV_Book_LV_BOOK_PLANT', 'Art_LV_Book_LV_BOOK_PLANT_OFTop'): actor_swap(l, PLANT, PM)
log.append('LV_Book03_Books + LV_Book03_Plant (x2, two-sided leaves) installed')

# keepsake tin (every alias): painted enamel body/lid + aged brass hardware, instead of flat cream Phong
TINM = {'ceramicpot': load(MATS + 'MI_Tin_PaintedEnamel'), 'hardwareagedbrass': load(MATS + 'MI_Joinery_AgedBrass')}
tins = [a for a in A.get_all_level_actors() if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh
        and a.static_mesh_component.static_mesh.get_name() == 'LV_BOOK_TIN']
for a in tins: swap(a, a.static_mesh_component, a.static_mesh_component.static_mesh, TINM)
log.append('LV_BOOK_TIN enamel/brass on %d aliases: %s' % (len(tins), [a.get_actor_label() for a in tins]))

# split shelf runs (rev02_04b lay_books) rebuilt from merged FEEDBACK-ROOM-03 books
parts = []
for p in EAL.list_assets(R2 + 'LV_Book03Parts', False, False):
    m = EAL.load_asset(p)
    if isinstance(m, unreal.StaticMesh):
        b = m.get_bounding_box(); parts.append((m, b.min, b.max))
pages = sorted([x for x in parts if re.search(r'_pages(_\d+)?$', x[0].get_name())], key=lambda x: (x[1].z, x[1].x))
groups = {i: [] for i in range(len(pages))}
for m, mn, mx in parts:
    c = ((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2)
    def dist(pg):
        _, a0, a1 = pg
        return sum(max(a0_ - 4 - v, 0, v - a1_ - 4) for v, a0_, a1_ in zip(c, (a0.x, a0.y, a0.z), (a1.x, a1.y, a1.z)))
    i = min(range(len(pages)), key=lambda k: (dist(pages[k]), abs(c[0] - (pages[k][1].x + pages[k][2].x) / 2)))
    groups[i].append(m)
merged = {}   # row -> [(sm, min, max)]
for i, pg in enumerate(pages):
    dm, slots = unreal.DynamicMesh(), []
    for m in groups[i]:
        pd = to_dm(m); mp = {}
        for k, s in enumerate(m.static_materials):
            n_ = norm(s.material_slot_name)
            if n_ not in [x for x, _ in slots]: slots.append((n_, SLOTMAT.get(n_)))
            mp[k] = [x for x, _ in slots].index(n_)
        remap(pd, mp); G.GeometryScript_MeshEdits.append_mesh(dm, pd, unreal.Transform())
    sm = bake(dm, 'LV_Book03_Book_%02d' % i, slots)
    b = sm.get_bounding_box(); row = 'A' if b.min.z < 95 else 'B' if b.min.z < 145 else 'C'
    merged.setdefault(row, []).append((sm, b.min, b.max))
for r in merged: merged[r].sort(key=lambda x: x[1].x)
log.append('merged books per row: %s (parts %d)' % ({r: len(v) for r, v in sorted(merged.items())}, len(parts)))

for l in [l for l in acts if l.startswith(('Art_Book_', 'Art_Book03_'))]: A.destroy_actor(acts.pop(l))
def lay(row, host, shelf_z, skip=(), dx=0.0, scale=1.0, keep=None, y_front=None, tag='B'):
    h = acts[host]; t = h.get_actor_transform(); rot = h.get_actor_rotation()
    run = [x for k, x in enumerate(merged[row]) if k not in skip]
    if keep: run = run[:keep]
    x0, x1 = min(b[1].x for b in run), max(b[2].x for b in run); y1 = max(b[2].y for b in run); z0 = min(b[1].z for b in run)
    out = []
    assert L.set_current_level_by_name(lvl_of(h))
    for sm, mn, mx in run:
        off = unreal.Vector(-(x0 + x1) / 2 * scale + dx, (y_front - y1 * scale) if y_front is not None else 0, shelf_z - z0 * scale)
        a = A.spawn_actor_from_object(sm, t.transform_location(off), rot)
        a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        a.set_actor_label('Art_Book03_%s_%d' % (tag, len(out))); a.set_folder_path('Redesign/Imported Art/Rev02 Books')
        a.static_mesh_component.set_collision_profile_name('NoCollision'); acts[a.get_actor_label()] = a; out.append(a)
    return out
ofc = acts['Art_OF_Bookcase_OF_BOOKCASE_BODY']; olo, ohi = ofc.static_mesh_component.get_local_bounds()
r1 = lay('A', 'Art_OF_Bookcase_OF_BOOKCASE_BODY', 11.9, skip=(2, 6), dx=4, y_front=ohi.y - 3, tag='OFLow')
r2 = lay('C', 'Art_OF_Bookcase_OF_BOOKCASE_BODY', 47.9, skip=(0, 4), dx=-6, y_front=ohi.y - 3, tag='OFHigh')
s063 = 'Art_BA_WallShelf_ARC_WALL_SHELF_01_S063'; slo, shi = acts[s063].static_mesh_component.get_local_bounds()
r3 = lay('B', s063, shi.z, keep=5, dx=-12, scale=0.7, y_front=shi.y - 1, tag='S063')
log.append('book runs: OFLow %d, OFHigh %d, S063 %d books' % (len(r1), len(r2), len(r3)))

# ================= LV-SOFA-03 =================
actor_swap('Art_LV_Sofa', load(R2 + 'LV_Sofa03/LV_SOFA_03'), {'sofa02woventhrow': load(MATS + 'MI_Sofa03_WovenThrow')})
log.append('LV_SOFA_03 on Art_LV_Sofa (woven throw MI_Sofa03_WovenThrow)')

# ================= PROP-FIT-03: hall closet storage + hangers =================
ST3, HG = load(R2 + 'PropFit03/ARC_ClosetStorage03'), load(R2 + 'PropFit03/HA_Hanger03')
brs = load(R2 + 'BR_ClosetStorage03/BR_ClosetStorage03_West')
HM = {norm(s.material_slot_name): s.material_interface for s in brs.static_materials}
asm = json.load(open(os.path.join(SRC, 'PROP-FIT-03/assembly.json')))['entry_hangers']['rail_datum_offsets']
for l in [l for l in acts if l.startswith('Art_HA_Hanger03_')]: A.destroy_actor(acts.pop(l))
for st, tag in (('Art_CoatCloset_Storage', 'Coat'), ('Art_OfficeCloset_Storage', 'Office')):
    a = acts[st]; c = a.static_mesh_component
    a.modify(); c.set_static_mesh(ST3)
    for i, s_ in enumerate(ST3.static_materials): c.set_material(i, s_.material_interface)
    t = a.get_actor_transform()
    for k, (x, y, z) in enumerate(asm):
        h = spawn(HG, t.transform_location(unreal.Vector(x * 100, -y * 100, z * 100)), a.get_actor_rotation(), 'Art_HA_Hanger03_%s_%d' % (tag, k),
                  lvl_of(a), str(a.get_folder_path()), HM)
    log.append('%s -> ARC_ClosetStorage03 + 3 HA_Hanger03, last %s' % (st, bounds(h)))

# ================= PROP-FIT-03: pans on the rail body =================
pan = acts.get('Art_KI_Pan_A_KI_Pan_Body')
PANM = {}
if pan:
    PANM['seasonediron'] = pan.static_mesh_component.get_material(0)
    PANM['agedwalnut'] = acts['Art_KI_Pan_A_KI_Pan_Handle'].static_mesh_component.get_material(0)
else:
    PANM['seasonediron'] = load(E + 'Redesign/KI_PAN/Seasoned_iron'); PANM['agedwalnut'] = load(E + 'Redesign/KI_PAN/Aged_walnut')
for l in ('Art_KI_Pan_A_KI_Pan_Body', 'Art_KI_Pan_A_KI_Pan_Handle', 'Art_KI_Pan_B_KI_Pan_Body', 'Art_KI_Pan_B_KI_Pan_Handle'):
    if l in acts: A.destroy_actor(acts.pop(l))
rail = acts['Art_KI_PanRail_KI_Pan_Rail_Assembly']
actor_swap('Art_KI_PanRail_KI_Pan_Rail_Assembly', load(R2 + 'KI_PanRail01/KI_Pan_Rail_Body'))
pp = spawn(load(R2 + 'PropFit03/KI_PanPair03'), rail.get_actor_location(), rail.get_actor_rotation(), 'Art_KI_PanPair03', lvl_of(rail), str(rail.get_folder_path()), PANM)
log.append('pan rail -> KI_Pan_Rail_Body; KI_PanPair03 at rail origin %s' % bounds(pp))

assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 room source]\n' + '\n'.join(log))
