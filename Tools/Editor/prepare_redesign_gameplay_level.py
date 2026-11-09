"""Prepare the redesign map for gameplay: place the bath moving parts (toilet lid, tub taps) with
their bodies' transforms, and create/attach the always-loaded gameplay sublevel
L_Apartment_Redesign_Gameplay so gameplay actors live in their own .umap."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
PERSIST = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
GAMEPLAY = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Gameplay'

def mesh(src, part, folder):
    path = R + folder + '/' + part
    t = unreal.AssetImportTask(); t.filename = os.path.join(SRC, src, part + '.fbx'); t.destination_path = R + folder
    t.destination_name = part; t.automated = True; t.replace_existing = True; t.save = True
    o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
    o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = True; t.options = o
    tools.import_asset_tasks([t]); m = EAL.load_asset(path)
    b = m.get_bounding_box()
    unreal.log('[Prep] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (part, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
    return m

assert L.load_level(PERSIST)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
for label in ('Art_BA_Toilet_BA_ToiletLid', 'Art_BA_Tub_BA_TapLeft', 'Art_BA_Tub_BA_TapRight'):
    if label in acts: A.destroy_actor(acts[label])
for src, part, folder, body_label in [('BA-TOILET-01/model', 'BA_ToiletLid', 'BA_Toilet', 'Art_BA_Toilet_BA_ToiletBody'),
                                      ('BA-TUB-01/model', 'BA_TapLeft', 'BA_Tub', 'Art_BA_Tub_BA_Tub'),
                                      ('BA-TUB-01/model', 'BA_TapRight', 'BA_Tub', 'Art_BA_Tub_BA_Tub')]:
    body = acts[body_label]
    a = A.spawn_actor_from_object(mesh(src, part, folder), body.get_actor_location(), body.get_actor_rotation())
    a.set_actor_label(body_label.rsplit('_', 2)[0] + '_' + part); a.set_folder_path(str(body.get_folder_path()))
    a.static_mesh_component.set_collision_profile_name('NoCollision')
    o, e = a.get_actor_bounds(False)
    unreal.log('[Prep] placed %s world min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (a.get_actor_label(), o.x-e.x, o.y-e.y, o.z-e.z, o.x+e.x, o.y+e.y, o.z+e.z))

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
names = [l.get_outermost().get_name() for l in unreal.EditorLevelUtils.get_levels(world)]
if not any(n.endswith('L_Apartment_Redesign_Gameplay') for n in names):
    if EAL.does_asset_exist(GAMEPLAY):
        unreal.EditorLevelUtils.add_level_to_world(world, GAMEPLAY, unreal.LevelStreamingAlwaysLoaded)
    else:
        unreal.EditorLevelUtils.create_new_streaming_level(unreal.LevelStreamingAlwaysLoaded, GAMEPLAY, False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.log('[Prep] levels: %s' % [l.get_outermost().get_name() for l in unreal.EditorLevelUtils.get_levels(world)])
L.save_all_dirty_levels()
unreal.log('[Prep] saved; gameplay map exists=%s' % EAL.does_asset_exist(GAMEPLAY))
