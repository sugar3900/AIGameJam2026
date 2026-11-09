"""Place reviewed static furniture into the A+ blockout. Run in its editor.

Imports each source into its own folder to prevent FBX material-name collisions.
The imported materials and simple collision require an in-game art review.
"""
import os
import unreal

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
source_root = os.path.join(root, 'Art Source/Apartment Redesign/Assets')
asset_root = '/Game/ICanFixHim/Environment/Redesign'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
level = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
# source, name, placements: placeholder index, centre in cm, yaw (front is -Y)
items = [
    ('LV-COFFEE-01/model/LV_COFFEE_01.fbx', 'LV_Coffee', [(4, (265,195,0), 0)]),
    ('LV-CHAIR-01/model/LV-CHAIR-01.fbx', 'LV_Chair', [(3, (157.5,47,0), 0)]),
    ('KI-TABLE-01/model/KI_TABLE_01.fbx', 'KI_Table', [(12, (895,227.5,0), 0)]),
    ('KI-CHAIR-01/model/KI_CHAIR_01.fbx', 'KI_Chair', [(13, (787.5,230,0), -90), (14, (1007.5,230,0), 90)]),
    ('OF-DAYBED-01/model/OF_DAYBED_Assembly.fbx', 'OF_Daybed', [(23, (845,820,0), -90)]),
]
if not levels.load_level(level):
    raise RuntimeError('Could not load ' + level)
for source, name, placements in items:
    folder = asset_root + '/' + name
    task = unreal.AssetImportTask()
    task.filename = os.path.join(source_root, source)
    task.destination_path = folder
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
    mesh = unreal.EditorAssetLibrary.load_asset(folder + '/' + name)
    if not mesh:
        raise RuntimeError('Missing imported mesh ' + name)
    for index, location, yaw in placements:
        label = 'Art_%s_%02d' % (name, index)
        all_actors = actors.get_all_level_actors()
        old = next((a for a in all_actors if a.get_actor_label().startswith('Placeholder_%02d_' % index) or a.get_actor_label() == label), None)
        if not old:
            raise RuntimeError('Missing placeholder or existing art for index %d' % index)
        a = actors.spawn_actor_from_object(mesh, unreal.Vector(*location), unreal.Rotator(0, 0, yaw))
        if not a:
            raise RuntimeError('Could not spawn ' + name)
        a.set_actor_label(label + '_new')
        a.set_folder_path('Redesign/Imported Art')
        actors.destroy_actor(old)
        a.set_actor_label(label)
    unreal.log('[Redesign] %s half-bounds %s' % (name, mesh.get_bounds().box_extent))
if not levels.save_current_level():
    raise RuntimeError('Could not save ' + level)
