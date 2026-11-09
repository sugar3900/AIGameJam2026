"""Place moving parts that the furniture passes left out: BA-BASIN-01 taps and the BA-TUB-01 shower
curtain. Both kits export in assembly space, so each part shares its body's transform. Re-runnable."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def mesh(src, part, folder):
    path = R + folder + '/' + part
    if not EAL.does_asset_exist(path):
        f = os.path.join(SRC, src, part + '.fbx')
        if not os.path.isfile(f): raise RuntimeError('missing ' + f)
        t = unreal.AssetImportTask(); t.filename = f; t.destination_path = R + folder; t.destination_name = part
        t.automated = True; t.replace_existing = True; t.save = True
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = False; t.options = o
        tools.import_asset_tasks([t])
        if not t.get_editor_property('imported_object_paths'): raise RuntimeError('import produced nothing: ' + f)
    return EAL.load_asset(path)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
for src, part, folder, body in [('BA-BASIN-01/model', 'BA_BasinTap_L', 'BA_Basin', 'Art_BA_Basin_BA_BasinBody'),
                                ('BA-BASIN-01/model', 'BA_BasinTap_R', 'BA_Basin', 'Art_BA_Basin_BA_BasinBody'),
                                ('BA-TUB-01/model', 'BA_Curtain', 'BA_Tub', 'Art_BA_Tub_BA_Tub')]:
    label = body.rsplit('_', 1)[0].replace('BasinBody', '').rstrip('_') + '_' + part
    m = mesh(src, part, folder)
    b = acts[body]
    a = acts.get(label)
    if a:   # update in place (it may be a hidden gameplay body source)
        a.static_mesh_component.set_static_mesh(m); a.set_actor_transform(b.get_actor_transform(), False, True)
    else:
        a = A.spawn_actor_from_object(m, b.get_actor_location(), b.get_actor_rotation())
        a.set_actor_label(label); a.set_folder_path(str(b.get_folder_path()))
        a.static_mesh_component.set_collision_profile_name('NoCollision')
    o, e = a.get_actor_bounds(False)
    unreal.log('[Extra] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (label, o.x-e.x, o.y-e.y, o.z-e.z, o.x+e.x, o.y+e.y, o.z+e.z))
assert L.save_current_level()
