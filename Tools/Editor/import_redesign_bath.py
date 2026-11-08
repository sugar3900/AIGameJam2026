"""Install provisional bathroom fixture bodies in the A+ review map.
Moving taps, toilet lid, curtain, repair patch and final materials remain pending.
"""
import os
import unreal
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
source = os.path.join(root, 'Art Source/Apartment Redesign/Assets')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
map_path = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
items = [
    ('BA_Tub', 'BA-TUB-01/model', ['BA_Tub', 'BA_TubFixtures'], 19, (580,907,0), 180),
    ('BA_Basin', 'BA-BASIN-01/model', ['BA_BasinBody'], 20, (527.5,727.5,0), -90),
    ('BA_Toilet', 'BA-TOILET-01/model', ['BA_ToiletBody'], 21, (740,792.5,0), 90),
]
if not levels.load_level(map_path):
    raise RuntimeError('Cannot load review map')
for name, directory, parts, index, position, yaw in items:
    folder = '/Game/ICanFixHim/Environment/Redesign/' + name
    imported = []
    for part in parts:
        task = unreal.AssetImportTask()
        task.filename = os.path.join(source, directory, part + '.fbx')
        task.destination_path = folder
        task.destination_name = part
        task.automated = True
        task.replace_existing = True
        task.save = True
        opts = unreal.FbxImportUI()
        opts.import_mesh = True
        opts.import_as_skeletal = False
        opts.import_materials = True
        opts.import_textures = True
        opts.static_mesh_import_data.combine_meshes = True
        opts.static_mesh_import_data.auto_generate_collision = True
        task.options = opts
        tools.import_asset_tasks([task])
        mesh = unreal.EditorAssetLibrary.load_asset(folder + '/' + part)
        if not mesh:
            raise RuntimeError('Missing import ' + part)
        imported.append((part, mesh))
        unreal.log('[Bath] %s half-bounds %s' % (part, mesh.get_bounds().box_extent))
    existing = actors.get_all_level_actors()
    placeholder = next((a for a in existing if a.get_actor_label().startswith('Placeholder_%02d_' % index)), None)
    old = [a for a in existing if a.get_actor_label().startswith('Art_'+name+'_')]
    if not placeholder and not old:
        raise RuntimeError('Missing placeholder for ' + name)
    created = []
    for part, mesh in imported:
        a = actors.spawn_actor_from_object(mesh, unreal.Vector(*position), unreal.Rotator(0,0,yaw))
        if not a:
            raise RuntimeError('Spawn failed: '+part)
        a.set_actor_label('Art_'+name+'_'+part+'_new')
        a.set_folder_path('Redesign/Imported Art/'+name)
        if part != parts[0]:
            a.static_mesh_component.set_collision_profile_name('NoCollision')
        created.append((a,part))
    for a in old + ([placeholder] if placeholder else []):
        actors.destroy_actor(a)
    for a,part in created:
        a.set_actor_label('Art_'+name+'_'+part)
if not levels.save_current_level():
    raise RuntimeError('Save failed')
