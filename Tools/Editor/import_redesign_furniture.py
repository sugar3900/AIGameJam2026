"""Import first reviewed furniture exports into the separate redesign blockout."""
import os
import unreal
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
asset_root = '/Game/ICanFixHim/Environment/Redesign'
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
if not levels.load_level(level):
    raise RuntimeError('Could not load redesign blockout')
tools = unreal.AssetToolsHelpers.get_asset_tools()
items = [
    ('LV_Sofa', 'LV-SOFA-01/model/LV-SOFA-01.fbx', 'Placeholder_00_Sofa', (54.5,180,0), 90),
    ('BR_Bed', 'BR-BED-01/model/BR_Bed_Complete.fbx', 'Placeholder_15_Bed', (265,850,0), 180),
]
for name, source, placeholder, location, yaw in items:
    src_path = os.path.join(root, 'Art Source/Apartment Redesign/Assets', source)
    if not os.path.isfile(src_path):
        raise RuntimeError('Missing source FBX: ' + src_path)
    task = unreal.AssetImportTask()
    task.filename = src_path
    task.destination_path = asset_root
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = False
    options.import_materials = True
    options.import_textures = True
    options.static_mesh_import_data.combine_meshes = True
    options.static_mesh_import_data.auto_generate_collision = True
    task.options = options
    tools.import_asset_tasks([task])
    # Only trust this run's import, not a stale asset that already exists at the destination.
    if not task.get_editor_property('imported_object_paths'):
        raise RuntimeError('Import produced nothing: ' + src_path)
    mesh = unreal.EditorAssetLibrary.load_asset(asset_root + '/' + name)
    if not isinstance(mesh, unreal.StaticMesh):
        raise RuntimeError('Import failed: ' + name)
    label = 'Art_' + name
    existing = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == label), None)
    if existing:   # re-run: update in place (keeps tags/hidden state if it is a gameplay body source)
        existing.static_mesh_component.set_static_mesh(mesh)
        existing.set_actor_location_and_rotation(unreal.Vector(*location), unreal.Rotator(0, 0, yaw), False, True)
    else:
        a = actors.spawn_actor_from_object(mesh, unreal.Vector(*location), unreal.Rotator(0, 0, yaw))
        if not a:
            raise RuntimeError('Spawn failed: ' + name)
        a.set_actor_label(label)
        a.set_folder_path('Redesign/Imported Art')
    old = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == placeholder), None)
    if old:
        actors.destroy_actor(old)
    unreal.log('[Redesign] %s bounds %s' % (name, mesh.get_bounds().box_extent))
if not levels.save_current_level():
    raise RuntimeError('Failed to save redesign')
