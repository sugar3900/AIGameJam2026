"""Rev02 step 5j: second user-feedback batch, engine-owned material and placement corrections. Re-runnable.

Materials (every placed component, including interactable bodies and their hidden art sources):
  - every 'Aged_Chrome'/'Aged_chrome' slot (fridge body/door, KI-FAUCET-02 sink body/taps incl. drain and exposed trap,
    bath basin taps, BA-TUB-FIXTURES-02 plumbing/rod/drain, tub taps) -> M_Rev02_AgedChrome (metallic, restrained
    roughness variation). Enamel/porcelain slot indices untouched.
  - mirror glass slots (BR_Dresser 'Mirror', BA_Mirror 'Mirror_Glass') -> M_Rev02_MirrorAged: softly blurred Lumen room
    reflections (roughness ~.22), faint aged tint. No scene captures, no global reflection change.
  - HA-HOOKS-01 coat rack: board 'Warm_muted_walnut' -> MI_Rev02_WhitePaintGrain (bench finish), 'Aged_brass' hooks ->
    MI_Joinery_AgedBrass (aged metallic).
  - KI-WALL-TABLE-02 / KI-STOOL-02 sage apron/stretchers -> the set's own walnut material.
Placement:
  - bedroom shelf :065 vase (HA_VASE_01, 24 cm belly on a 15 cm shelf, through the wall) scaled to fit the shelf with
    its whole base supported and 1 cm wall clearance.
  - shoe bench centred under the full coat rack (hooks board centre y 330), slippers directly in front of it.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
log = []

def comps():
    for a in A.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.static_mesh: yield a, c

def by_slot(pred, mat_path, mesh_filter=None):
    mat = EAL.load_asset(mat_path); n = 0
    for a, c in comps():
        if mesh_filter and mesh_filter not in c.static_mesh.get_path_name(): continue
        for i, s in enumerate(c.static_mesh.static_materials):
            if pred(str(s.material_slot_name)):
                a.modify(); c.set_material(i, mat); n += 1
    log.append('%s -> %s on %d slots' % (mesh_filter or 'all', mat_path.split('/')[-1], n))

# ---- materials ----
by_slot(lambda n: n.lower() == 'aged_chrome', MATS + 'M_Rev02_AgedChrome')
by_slot(lambda n: n == 'Mirror', MATS + 'M_Rev02_MirrorAged', '/BR_Dresser/BR_Dresser_mirror')
by_slot(lambda n: n == 'Mirror_Glass', MATS + 'M_Rev02_MirrorAged', '/BA_MIRROR/BA_Mirror_mirror')
by_slot(lambda n: n == 'Warm_muted_walnut', MATS + 'MI_Rev02_WhitePaintGrain', '/HA_HOOKS/HA_Hooks')
by_slot(lambda n: n == 'Aged_brass', MATS + 'MI_Joinery_AgedBrass', '/HA_HOOKS/HA_Hooks')
for mesh, sage, walnut in (('/KI_WallTable02/KI_WALL_TABLE_02', 'PaintedSage', 'PaintedWalnut'), ('/KI_Stool02/KI_STOOL_02', 'PaintedSage_001', 'PaintedWalnut_001')):
    for a, c in comps():
        if mesh not in c.static_mesh.get_path_name(): continue
        names = [str(s.material_slot_name) for s in c.static_mesh.static_materials]
        wood = c.get_material(names.index(walnut))
        a.modify(); c.set_material(names.index(sage), wood)
        log.append('%s %s -> %s' % (a.get_actor_label(), sage, wood.get_name()))

# ---- vase on bedroom shelf :065 ----
shelf, vase = acts['Art_BA_WallShelf_ARC_WALL_SHELF_01_S065'], acts['Art_HA_Vase_065']
so, se = shelf.get_actor_bounds(False); top = so.z + se.z; wall_x = so.x - se.x; front_x = so.x + se.x
vase.modify(); vase.set_actor_scale3d(unreal.Vector(1, 1, 1))
vo, ve = vase.get_actor_bounds(False)
depth_room = (front_x - wall_x) - 1.0 - 0.5          # 1 cm wall clearance, 0.5 cm front lip
k = min(1.0, depth_room / (2 * ve.x), (2 * se.y - 4) / (2 * ve.y))
vase.set_actor_scale3d(unreal.Vector(k, k, k))
vo, ve = vase.get_actor_bounds(False); vl = vase.get_actor_location()
# seat: bottom on the shelf top, back 1 cm off the wall, centred along the shelf
vase.set_actor_location(unreal.Vector(vl.x + (wall_x + 1.0 + ve.x) - vo.x, vl.y + so.y - vo.y, vl.z + top - (vo.z - ve.z)), False, True)
vo, ve = vase.get_actor_bounds(False)
log.append('vase :065 scale %.3f -> x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f (shelf x%.1f-%.1f top %.1f)' % (k, vo.x-ve.x, vo.x+ve.x, vo.y-ve.y, vo.y+ve.y, vo.z-ve.z, vo.z+ve.z, wall_x, front_x, top))

# ---- entry: bench centred under the full coat rack, slippers in front ----
hooks, bench, slip = acts['Art_HA_Hooks_HA_Hooks'], acts['Art_HA_Bench_HA_BENCH_01'], acts['Art_HA_Slippers01']
ho, he = hooks.get_actor_bounds(False)
bo, be = bench.get_actor_bounds(False); bl = bench.get_actor_location()
bench.modify(); bench.set_actor_location(unreal.Vector(bl.x, bl.y + ho.y - bo.y, bl.z), False, True)
bo, be = bench.get_actor_bounds(False)
po, pe = slip.get_actor_bounds(False); pl = slip.get_actor_location()
gap = 3.0                                              # slippers 3 cm in front of the bench's front (room-side) edge
slip.modify(); slip.set_actor_location(unreal.Vector(pl.x + (bo.x - be.x - gap - pe.x) - po.x, pl.y + ho.y - po.y, pl.z), False, True)
po, pe = slip.get_actor_bounds(False)
log.append('rack centre y %.1f; bench x%.1f-%.1f y%.1f-%.1f; slippers x%.1f-%.1f y%.1f-%.1f' % (ho.y, bo.x-be.x, bo.x+be.x, bo.y-be.y, bo.y+be.y, po.x-pe.x, po.x+pe.x, po.y-pe.y, po.y+pe.y))

assert L.save_all_dirty_levels()
unreal.log('[Rev02 batch2]\n' + '\n'.join(log))
