"""Rev02 step 2c (round 3): re-import targeted source winding fixes INTO their existing Redesign assets (same asset path,
so every placed actor keeps its transform, pose and material overrides). Legacy FBX importer, combine meshes, the
original Redesign import options; each mesh's prior collision setup (simple-collision count and trace flag) is restored.

ROUND3-BATH-NORMALS-01: BA_Towel_0/1/2 (BA-BASKET-01 rolled towels) and BA_Roll_Paper (BA-ROLL-01 paper roll) were exported
with inward winding (negative signed volume): outer skin, bore and caps faced the wrong way. Re-runnable.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
EAL = unreal.EditorAssetLibrary; G = unreal
SM = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
R = '/Game/ICanFixHim/Environment/Redesign/'
JOBS = [('ROUND3-BATH-NORMALS-01/model/BA_Towel_0.fbx', R + 'BA_BASKET', 'BA_Towel_0'),
        ('ROUND3-BATH-NORMALS-01/model/BA_Towel_1.fbx', R + 'BA_BASKET', 'BA_Towel_1'),
        ('ROUND3-BATH-NORMALS-01/model/BA_Towel_2.fbx', R + 'BA_BASKET', 'BA_Towel_2'),
        ('ROUND3-BATH-NORMALS-01/model/BA_Roll_Paper.fbx', R + 'BA_ROLL', 'BA_Roll_Paper')]
def ncol(m):
    ag = m.get_editor_property('body_setup').get_editor_property('agg_geom')
    return sum(len(ag.get_editor_property(k)) for k in ('convex_elems', 'box_elems', 'sphere_elems', 'sphyl_elems'))
def volume(m):
    dm = unreal.DynamicMesh(); G.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(m, dm, G.GeometryScriptCopyMeshFromAssetOptions(), G.GeometryScriptMeshReadLOD())
    r = G.GeometryScript_MeshQueries.get_mesh_volume_area(dm); v = [x for x in r if isinstance(x, float)]
    return v[1] if len(v) > 1 else float('nan')
CVAR = 'Interchange.FeatureFlags.Import.FBX'
was = unreal.SystemLibrary.get_console_variable_bool_value(CVAR)
unreal.SystemLibrary.execute_console_command(None, CVAR + ' false')
log = []
try:
    for rel, folder, name in JOBS:
        src = os.path.join(SRC, rel); assert os.path.isfile(src), src
        old = EAL.load_asset(folder + '/' + name); assert old, folder + '/' + name
        b0 = old.get_bounding_box(); ctf = old.get_editor_property('body_setup').get_editor_property('collision_trace_flag'); n0 = ncol(old); v0 = volume(old)
        slots0 = [str(s.material_slot_name) for s in old.static_materials]
        t = unreal.AssetImportTask(); t.filename = src; t.destination_path = folder; t.destination_name = name
        t.automated = True; t.replace_existing = True; t.save = True
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = False
        t.options = o; tools.import_asset_tasks([t])
        m = EAL.load_asset(folder + '/' + name)
        ad = m.get_editor_property('asset_import_data')
        assert os.path.normpath(ad.get_first_filename()) == os.path.normpath(src), ad.get_first_filename()
        if ncol(m) and not n0: SM.remove_collisions(m)
        bs = m.get_editor_property('body_setup'); bs.modify(); bs.set_editor_property('collision_trace_flag', ctf)
        assert EAL.save_loaded_asset(m, False), name
        b = m.get_bounding_box()
        log.append('%s: bounds (%.2f,%.2f,%.2f)-(%.2f,%.2f,%.2f) was (%.2f,%.2f,%.2f)-(%.2f,%.2f,%.2f); volume %.2f (was %.2f); slots %s (was %s); collision %d %s' % (
            name, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z, b0.min.x, b0.min.y, b0.min.z, b0.max.x, b0.max.y, b0.max.z, volume(m), v0,
            [str(s.material_slot_name) for s in m.static_materials], slots0, ncol(m), ctf))
finally:
    unreal.SystemLibrary.execute_console_command(None, CVAR + (' true' if was else ' false'))
unreal.log('[Rev02 reimport round3]\n' + '\n'.join(log))
