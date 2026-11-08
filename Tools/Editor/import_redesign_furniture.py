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
    task = unreal.AssetImportTask()
    task.filename = os.path.join(root, 'Art Source/Apartment Redesign/Assets', source)
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
    mesh = unreal.EditorAssetLibrary.load_asset(asset_root + '/' + name)
    if not mesh:
        raise RuntimeError('Import failed: ' + name)
    old = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == placeholder), None)
    if not old:
        raise RuntimeError('Placeholder missing: ' + placeholder)
    a = actors.spawn_actor_from_object(mesh, unreal.Vector(*location), unreal.Rotator(0, 0, yaw))
    if not a:
        raise RuntimeError('Spawn failed: ' + name)
    a.set_actor_label('Art_' + name)
    a.set_folder_path('Redesign/Imported Art')
    actors.destroy_actor(old)
    unreal.log('[Redesign] %s bounds %s' % (name, mesh.get_bounds().box_extent))
if not levels.save_current_level():
    raise RuntimeError('Failed to save redesign')
