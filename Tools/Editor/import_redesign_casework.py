"""Place provisional closed desk and dresser assemblies in the review map.

Parts remain separate for future interaction work. This does not implement drawer
motion or functional mirror reflection; imported materials need visual review.
"""
import os
import unreal
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
assets = os.path.join(root, 'Art Source/Apartment Redesign/Assets')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
map_path = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
assemblies = [
    ('OF_Desk', 'OF-DESK-01/model', ['OF_DESK_BODY', 'OF_DESK_DRAWER_1', 'OF_DESK_DRAWER_2', 'OF_DESK_DRAWER_3'], 24, (1057.5,910,0), 180),
    ('BR_Dresser', 'BR-DRESSER-01/model', ['BR_Dresser_body', 'BR_Dresser_drawer1', 'BR_Dresser_drawer2', 'BR_Dresser_drawer3', 'BR_Dresser_mirror'], 18, (450,772.5,0), 90),
]
if not levels.load_level(map_path):
    raise RuntimeError('Could not load map')
for name, source, parts, index, position, yaw in assemblies:
    folder = '/Game/ICanFixHim/Environment/Redesign/' + name
    imported = []
    for part in parts:
        task = unreal.AssetImportTask()
        task.filename = os.path.join(assets, source, part + '.fbx')
        task.destination_path = folder
        task.destination_name = part
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
        mesh = unreal.EditorAssetLibrary.load_asset(folder + '/' + part)
        if not mesh:
            raise RuntimeError('Import failed: ' + part)
        imported.append((part, mesh))
        unreal.log('[Casework] %s bounds %s' % (part, mesh.get_bounds().box_extent))
    existing = actors.get_all_level_actors()
    placeholder = next((a for a in existing if a.get_actor_label().startswith('Placeholder_%02d_' % index)), None)
    old = [a for a in existing if a.get_actor_label().startswith('Art_'+name+'_')]
    if not placeholder and not old:
        raise RuntimeError('No previous object for ' + name)
    created = []
    for part, mesh in imported:
        actor = actors.spawn_actor_from_object(mesh, unreal.Vector(*position), unreal.Rotator(0,0,yaw))
        if not actor:
            raise RuntimeError('Failed to spawn ' + part)
        actor.set_actor_label('Art_'+name+'_'+part+'_new')
        actor.set_folder_path('Redesign/Imported Art/'+name)
        if part != parts[0]:
            actor.static_mesh_component.set_collision_profile_name('NoCollision')
        created.append((actor, part))
    for actor in old + ([placeholder] if placeholder else []):
        actors.destroy_actor(actor)
    for actor, part in created:
        actor.set_actor_label('Art_'+name+'_'+part)
if not levels.save_current_level():
    raise RuntimeError('Could not save')
