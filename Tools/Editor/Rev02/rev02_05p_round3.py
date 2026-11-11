"""Rev02 step 5p (user feedback round 3). Re-runnable; run after rev02_05o.

Living-room north base: the four ARC-LIVING-WALL-01 kit pieces on the north wall (and the rev02_05e fuse-niche variant
of the solid wall) carry the old 21.5 cm, 57 mm-deep base as part of their 'Trim_Ivory' slot, so rev02_05m's swap of the
standalone Baseboard_1m runs never reached it. Each kit mesh used there is copied into Rev02/LivingWallFit with every
Trim_Ivory triangle that lies entirely at or below z 22 cm deleted (the crown at z 262-275 and the full-height plaster
slab, which already runs to the floor behind the old base, are untouched; simple collision and trace flag are copied).
The north wall then gets the same slim FEEDBACK-ROOM-03 Baseboard_1m runs as every other room (front +Y on the y 6 cm
plaster face, x 4.874 -> 11.926 m, butted against the W and E runs' front faces at both inside corners, NoCollision like the
other trims).

Towel rail (BA-TOWEL-RAIL-01): the rail/bracket/finial slot 'Aged_Brass' was flat FBX Phong (white) -> the README's
aged-brass image (MI_TowelRail_AgedBrass, metallic .68, roughness .45). The towel slots (terry, border) are unchanged.
"""
import unreal
G = unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'; FIT = R2 + 'LivingWallFit/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
_missing = [l for l in ['Kit_LV_N_Window', 'Trim_KI_N_Base_0', 'Trim_LV_W_Base0_0', 'Trim_LV_E_Base_0'] if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
log = []
BASE_TOP = 22.0

def no_base(src):
    """Engine copy of a living-wall kit mesh without its embedded base (Trim_Ivory triangles below BASE_TOP)."""
    name = src.get_name() + '_NoBase'
    if src.get_path_name().startswith(FIT): return src            # already derived (re-run)
    names = [str(s.material_slot_name) for s in src.static_materials]
    trim = names.index('Trim_Ivory')
    dm = unreal.DynamicMesh()
    G.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(src, dm, G.GeometryScriptCopyMeshFromAssetOptions(), G.GeometryScriptMeshReadLOD())
    _, tl = G.GeometryScript_Materials.get_triangles_by_material_id(dm, trim)
    low = []
    for i in range(G.GeometryScript_List.get_index_list_length(tl)):
        t = G.GeometryScript_List.get_index_list_item(tl, i); t = t[0] if isinstance(t, tuple) else t
        vs = [v for v in G.GeometryScript_MeshQueries.get_triangle_positions(dm, t) if hasattr(v, 'z')][:3]
        if max(v.z for v in vs) <= BASE_TOP: low.append(t)
    if not low: return src                                        # e.g. the window casing: no embedded base
    removed = 0
    for t in sorted(low, reverse=True):
        ok = G.GeometryScript_MeshEdits.delete_triangle_from_mesh(dm, t, True)
        removed += int(ok[1] if isinstance(ok, tuple) else bool(ok))
    path = FIT + name
    if EAL.does_asset_exist(path): sm = EAL.load_asset(path)
    else:
        o = G.GeometryScriptCreateNewStaticMeshAssetOptions(); o.set_editor_property('enable_collision', False)
        sm, _ = G.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, path, o)
    co = G.GeometryScriptCopyMeshToAssetOptions(); co.set_editor_property('replace_materials', True)
    co.set_editor_property('new_materials', [s.material_interface for s in src.static_materials])
    co.set_editor_property('new_material_slot_names', [s.material_slot_name for s in src.static_materials])
    G.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, co, G.GeometryScriptMeshWriteLOD())
    col = G.GeometryScript_Collision.get_simple_collision_from_static_mesh(src)
    G.GeometryScript_Collision.set_simple_collision_of_static_mesh(col, sm, G.GeometryScriptSetSimpleCollisionOptions())
    bs = sm.get_editor_property('body_setup'); bs.modify()
    bs.set_editor_property('collision_trace_flag', src.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))
    assert EAL.save_loaded_asset(sm, False), path
    b = sm.get_bounding_box()
    log.append('%s: removed %d/%d low Trim_Ivory tris; bounds z %.1f..%.1f' % (name, removed, len(low), b.min.z, b.max.z))
    return sm

done = {}
for lab in sorted(l for l in acts if l.startswith('Kit_LV_N_')):
    c = acts[lab].static_mesh_component; sm = c.static_mesh
    if 'Trim_Ivory' not in [str(s.material_slot_name) for s in sm.static_materials]: continue
    key = sm.get_path_name()
    if key not in done: done[key] = no_base(sm)
    mats = [c.get_material(i) for i in range(c.get_num_materials())]
    acts[lab].modify(); c.set_static_mesh(done[key])
    for i, m in enumerate(mats): c.set_material(i, m)
    log.append('%s -> %s' % (lab, done[key].get_name()))

# slim base runs on the north plaster face (y 6), x 486 -> 1194, ~1 m pieces
ref = acts['Trim_KI_N_Base_0']; rc = ref.static_mesh_component
for l in [l for l in acts if l.startswith('Trim_LV_N_Base_')]: A.destroy_actor(acts.pop(l))
assert L.set_current_level_by_name(ref.get_outer().get_outer().get_name())
# butt joins at both inside corners: the run stops at the front faces of the existing W (x 486-487.4) and E (x 1192.6-1194)
# runs instead of overlapping their ends (coplanar top faces would shimmer)
_w, _e = acts['Trim_LV_W_Base0_0'], acts['Trim_LV_E_Base_0']
x0 = _w.get_actor_bounds(False)[0].x + _w.get_actor_bounds(False)[1].x
x1 = _e.get_actor_bounds(False)[0].x - _e.get_actor_bounds(False)[1].x
y = 6.0
n = max(1, int(round((x1 - x0) / 100.0))); step = (x1 - x0) / n
for k in range(n):
    a = A.spawn_actor_from_object(rc.static_mesh, unreal.Vector(x0 + k * step, y, 0), unreal.Rotator(0, 0, 0))
    a.set_actor_label('Trim_LV_N_Base_%d' % k); a.set_folder_path(str(ref.get_folder_path()))
    a.set_actor_scale3d(unreal.Vector(step / 100.0, 1, 1))
    c = a.static_mesh_component; c.set_collision_profile_name(rc.get_collision_profile_name()); c.set_material(0, rc.get_material(0))
    acts[a.get_actor_label()] = a
log.append('Trim_LV_N_Base_0..%d: %d x %.1f cm on y %.0f, x %.0f..%.0f (%s)' % (n - 1, n, step, y, x0, x1, rc.static_mesh.get_name()))

# towel rail hardware
mi = EAL.load_asset(MATS + 'MI_TowelRail_AgedBrass'); nrail = 0
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name() == 'BA_Towel_Rail':
            for i, s in enumerate(c.static_mesh.static_materials):
                if str(s.material_slot_name) == 'Aged_Brass': a.modify(); c.set_material(i, mi); nrail += 1
log.append('towel rail Aged_Brass -> MI_TowelRail_AgedBrass on %d slot(s)' % nrail)
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 round3]\n' + '\n'.join(log))
