"""Rev02 step 5d: source-free placement/interaction fixes from the feedback batch (no new art).

FIX-011  bedroom shelf :063 (east wall, x 459-474, y 870-935, top z 176.5): the lying stack overhung the shelf's north
         end by 6.8 cm and floated 1.1 cm, the standing run floated 2.1 cm, the tin overlapped the last two standing
         books, and spines touched the wall. Each group is reseated on the shelf top (+1 mm), 1 cm off the wall, in
         three supported runs along the shelf: lying stack, standing books, tin.
FIX-015  office geranium on shelf :072 (west wall face x 796, shelf to x 811): foliage pierced the wall. The plant
         moves out until its foliage clears the wall by 5 mm, provided the pot footprint (measured by cutting the mesh
         above the pot rim) stays fully on the shelf; it is checked, not assumed.
FIX-017  desk lamp: turned about its base so arm and shade reach over the desk's work area instead of the window, and
         the DeskLamp click body becomes ONE merged mesh of base/arm + shade + bulb (Geometry Script), so every
         visible part toggles the same light; no invisible catch-all.
Run after rev02_05c (re-runnable: positions are absolute).
"""
import math, unreal
G = unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}

def union(labels):
    mn, mx = [1e9] * 3, [-1e9] * 3
    for lab in labels:
        o, e = acts[lab].get_actor_bounds(False)
        for i, (c, h) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
            mn[i] = min(mn[i], c - h); mx[i] = max(mx[i], c + h)
    return mn, mx

def shift(labels, dx, dy, dz):
    for lab in labels:
        a = acts[lab]; l = a.get_actor_location(); a.modify()
        a.set_actor_location(unreal.Vector(l.x + dx, l.y + dy, l.z + dz), False, True)

def mesh_dm(sm):
    dm = unreal.DynamicMesh()
    G.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(sm, dm, G.GeometryScriptCopyMeshFromAssetOptions(), G.GeometryScriptMeshReadLOD())
    return dm

def footprint_below(actor, height):
    """World XY bounds of the part of the actor's mesh lying within `height` cm of its lowest point."""
    dm = mesh_dm(actor.static_mesh_component.static_mesh)
    G.GeometryScript_MeshTransforms.transform_mesh(dm, actor.get_actor_transform())
    b = G.GeometryScript_MeshQueries.get_mesh_bounding_box(dm)
    o = G.GeometryScriptMeshPlaneCutOptions(); o.set_editor_property('fill_holes', False)
    G.GeometryScript_MeshBooleans.apply_mesh_plane_cut(dm, unreal.Transform(unreal.Vector(0, 0, b.min.z + height), unreal.Rotator(0, 0, 0)), o)
    f = G.GeometryScript_MeshQueries.get_mesh_bounding_box(dm)
    return f.min, f.max

log = []
# ---------------- FIX-011 ----------------
SHELF_TOP, WALL, Y0, Y1 = 176.5, 474.0, 870.0, 935.0
lying = [l for l in acts if l.startswith('Art_Book_S063_lying')]
standing = [l for l in acts if l.startswith('Art_Book_S063_') and 'lying' not in l]
tin = ['Art_LV_Book_LV_BOOK_TIN_063']
cursor = Y0 + 2.0
# wall gaps: the tin and the standing books are as deep as the 15 cm shelf, so they keep 3 mm off the wall to stay
# over the shelf front; the shorter lying stack keeps 1 cm.
for grp, gap, wgap in ((lying, 3.0, 1.0), (standing, 2.5, 0.3), (tin, 0.0, 0.3)):
    mn, mx = union(grp)
    shift(grp, (WALL - wgap) - mx[0], cursor - mn[1], (SHELF_TOP + 0.1) - mn[2])
    mn, mx = union(grp); cursor = mx[1] + gap
    log.append('FIX-011 group %s: x %.1f-%.1f y %.1f-%.1f z %.1f-%.1f' % (grp[0], mn[0], mx[0], mn[1], mx[1], mn[2], mx[2]))
assert cursor <= Y1 + 0.01, 'shelf :063 run does not fit (%.1f > %.1f)' % (cursor, Y1)

# ---------------- FIX-015 ----------------
ger = acts['Art_KI_Geranium_KI_Geranium']; WALL_X, SHELF_X1 = 796.0, 811.0
o, e = ger.get_actor_bounds(False)
need = (WALL_X + 0.5) - (o.x - e.x)                         # move until foliage is 5 mm off the wall
pmn, pmx = footprint_below(ger, 9.0)                         # pot body below the rim
assert pmx.x + max(need, 0) <= SHELF_X1 + 0.01, 'pot would overhang shelf :072 (%.1f > %.1f)' % (pmx.x + need, SHELF_X1)
shift(['Art_KI_Geranium_KI_Geranium'], max(need, 0), 0, 0)
o, e = ger.get_actor_bounds(False); pmn, pmx = footprint_below(ger, 9.0)
log.append('FIX-015 geranium: foliage x %.1f-%.1f (wall 796); pot x %.1f-%.1f y %.1f-%.1f (shelf x 796-811)' % (o.x - e.x, o.x + e.x, pmn.x, pmx.x, pmn.y, pmx.y))

# ---------------- FIX-014 contact ----------------
# rev02_04b seats the riser on the stand and keeps the plant's old origin-on-riser offset; LV-PLANT-02's pot base is
# 0.5 cm above its origin, so the plant is lowered until the measured pot bottom meets the measured riser top.
pl, rs = acts['Art_HA_Plant'], acts['Art_HA_PlantStand_Riser']
ro, re_ = rs.get_actor_bounds(False); riser_top = ro.z + re_.z
pmn, pmx = footprint_below(pl, 1.0)
dm_ = mesh_dm(pl.static_mesh_component.static_mesh); G.GeometryScript_MeshTransforms.transform_mesh(dm_, pl.get_actor_transform())
pot_min = G.GeometryScript_MeshQueries.get_mesh_bounding_box(dm_).min.z
shift(['Art_HA_Plant'], 0, 0, riser_top - pot_min)
dm_ = mesh_dm(pl.static_mesh_component.static_mesh); G.GeometryScript_MeshTransforms.transform_mesh(dm_, pl.get_actor_transform())
log.append('FIX-014 plant: riser top z %.2f; pot min z %.2f -> %.2f (origin z %.2f)' % (riser_top, pot_min,
           G.GeometryScript_MeshQueries.get_mesh_bounding_box(dm_).min.z, pl.get_actor_location().z))

# ---------------- FIX-017 ----------------
PARTS = ['Art_OF_DeskLamp_OF_DeskLamp_Body', 'Art_OF_DeskLamp_OF_DeskLamp_Shade', 'Art_OF_DeskLamp_OF_DeskLamp_Bulb']
lamp = acts['DeskLamp']; body_art = acts[PARTS[0]]
bmn, bmx = footprint_below(body_art, 3.0)                   # the base disc
base = unreal.Vector((bmn.x + bmx.x) / 2, (bmn.y + bmx.y) / 2, 0)
YAW_NOW = body_art.get_actor_rotation().yaw; TARGET_YAW = -20.0  # arm/shade toward the work area in front of the chair (desk centre, front edge), not the window
d = TARGET_YAW - YAW_NOW
def turn(a):
    l, r = a.get_actor_location(), a.get_actor_rotation(); c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    dx, dy = l.x - base.x, l.y - base.y; a.modify()
    a.set_actor_location_and_rotation(unreal.Vector(base.x + dx * c - dy * s, base.y + dx * s + dy * c, l.z),
                                      unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + d), False, True)
if abs(((d + 180) % 360) - 180) > 0.5:
    for lab in PARTS + ['DeskLamp']: turn(acts[lab])
# one clickable body: all three parts share the lamp's assembly origin, so they merge without per-part offsets
dm, mats = unreal.DynamicMesh(), []
for lab in PARTS:
    c = acts[lab].static_mesh_component; part = mesh_dm(c.static_mesh)
    pm = [c.get_material(i) for i in range(c.get_num_materials())]
    dm, mats = G.GeometryScript_MeshEdits.append_mesh_with_materials(dm, mats, part, pm, unreal.Transform())
path = '/Game/ICanFixHim/Environment/Rev02/OF_DeskLamp/SM_OF_DeskLamp_Merged'
if EAL.does_asset_exist(path): sm = EAL.load_asset(path)
else:
    co = G.GeometryScriptCreateNewStaticMeshAssetOptions(); co.set_editor_property('enable_collision', False)
    sm, _ = G.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, path, co)
cp = G.GeometryScriptCopyMeshToAssetOptions(); cp.set_editor_property('replace_materials', True); cp.set_editor_property('new_materials', mats)
G.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, cp, G.GeometryScriptMeshWriteLOD())
bs = sm.get_editor_property('body_setup'); bs.modify()
bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)   # click hits the real shape
assert EAL.save_loaded_asset(sm, False)
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
b = lamp.get_editor_property('body'); lamp.modify()
b.set_static_mesh(sm); b.set_world_location_and_rotation(body_art.get_actor_location(), body_art.get_actor_rotation(), False, False)
b.set_world_scale3d(unreal.Vector(1, 1, 1))
for i, m in enumerate(mats): b.set_material(i, m)
lamp.set_editor_property('use_authored_body_materials', True)
bo, be, _ = unreal.SystemLibrary.get_component_bounds(acts['Art_OF_DeskLamp_OF_DeskLamp_Bulb'].static_mesh_component)
lamp.get_editor_property('light').set_world_location(bo, False, False)
assert L.set_current_level_by_name('L_Apartment_Rev02')
for lab in PARTS:                                        # the merged body draws the lamp; source parts stay as hidden sources
    a = acts[lab]; a.modify(); a.set_actor_hidden_in_game(True); a.static_mesh_component.set_visibility(False)
    a.static_mesh_component.set_collision_profile_name('NoCollision'); a.tags = [unreal.Name('GameplayBodySource')]
o, e, _ = unreal.SystemLibrary.get_component_bounds(b)
log.append('FIX-017 lamp: base centre (%.1f,%.1f), merged body x %.1f-%.1f y %.1f-%.1f z %.1f-%.1f, %d material slots' % (
    base.x, base.y, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z, len(mats)))
# ---------------- FIX-026 / FIX-028 untextured walnut furniture (material-only) ----------------
# LV-SIDE-TABLE-01 and BR-NIGHTSTAND-01 FBXs carry no texture (walnut image routed through shader nodes the FBX
# exporter drops). Every visible user of those meshes - art actors AND drawer interactable bodies, which hold their
# own material copies - gets the slot finishes. LV-CHEST-01 is not placed in Rev02. Placement/actions unchanged.
R2M = '/Game/ICanFixHim/Environment/Rev02/Materials/'
SLOT = {'aged_painterly_walnut': '/Game/ICanFixHim/Environment/Redesign/Finishes/MI_Walnut_MutedB',
        'fine_worn_wood_edges': R2M + 'MI_Rev02_WoodEdges', 'drawer_interior': R2M + 'MI_Rev02_DrawerInterior',
        'aged_brass': R2M + 'MI_Rev02_TableBrass'}
MESHES = ('LV_SIDE_TABLE_BODY', 'LV_SIDE_TABLE_DRAWER', 'BR_NIGHTSTAND_BODY', 'BR_NIGHTSTAND_DRAWER')
norm = lambda n: ''.join(ch if ch.isalnum() else '_' for ch in n.lower()).strip('_')
fixed = []
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        sm = c.static_mesh
        if not sm or sm.get_name() not in MESHES: continue
        a.modify()
        for i, sl in enumerate(sm.static_materials):
            c.set_material(i, EAL.load_asset(SLOT[norm(str(sl.material_slot_name))]))
        fixed.append('%s/%s' % (a.get_actor_label(), c.get_name()))
log.append('FIX-026/028 walnut slots on %d components: %s' % (len(fixed), ', '.join(fixed)))
assert L.save_all_dirty_levels()
unreal.log('[Rev02 feedback placement] saved\n' + '\n'.join(log))
