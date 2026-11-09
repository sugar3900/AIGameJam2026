"""Import KI-FRIDGE-01 / KI-RANGE-01 bodies and place them in the redesign map (re-runnable)."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()

def import_mesh(src, part, folder, collision):
    path = os.path.join(SRC, src, part + '.fbx')
    if not os.path.isfile(path): raise RuntimeError('Missing source FBX: ' + path)
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = folder; t.destination_name = part
    t.automated = True; t.replace_existing = True; t.save = True
    o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
    o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = collision; t.options = o
    tools.import_asset_tasks([t])
    if not t.get_editor_property('imported_object_paths'): raise RuntimeError('Import produced nothing: ' + path)
    return unreal.EditorAssetLibrary.load_asset(folder + '/' + part)

def place(label, mesh, loc, folder, collision=True):
    """Update the existing actor with this label in place (keeps tags/hidden state), else spawn it."""
    a = next((x for x in A.get_all_level_actors() if x.get_actor_label() == label), None)
    if a:
        a.static_mesh_component.set_static_mesh(mesh); a.set_actor_location_and_rotation(unreal.Vector(*loc), unreal.Rotator(0, 0, 0), False, True)
    else:
        a = A.spawn_actor_from_object(mesh, unreal.Vector(*loc), unreal.Rotator(0, 0, 0)); a.set_actor_label(label); a.set_folder_path(folder)
        if not collision: a.static_mesh_component.set_collision_profile_name('NoCollision')
    return a

if __name__ == '__main__':
    assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
    for name, src, part, idx, pos in [('Fridge', 'KI-FRIDGE-01/models', 'KI_FRIDGE_BODY', 6, (599.5, 47, 0)),
                                      ('Range', 'KI-RANGE-01/model', 'KI_RANGE_Body', 7, (687.5, 47, 0))]:
        m = import_mesh(src, part, '/Game/ICanFixHim/Environment/Redesign/KI_' + name, True)
        place('Art_KI_' + name + '_Body', m, pos, 'Redesign/Imported Art/Kitchen')
        for old in A.get_all_level_actors():
            if old.get_actor_label().startswith('Placeholder_%02d_' % idx): A.destroy_actor(old)
        unreal.log('[Kitchen] %s %s' % (name, m.get_bounds().box_extent))
    assert L.save_current_level()
