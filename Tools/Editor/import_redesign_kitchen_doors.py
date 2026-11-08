import os,unreal
root='/Users/davidwallin/Developer/AIGameJam2026-environment/Art Source/Apartment Redesign/Assets'; A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); T=unreal.AssetToolsHelpers.get_asset_tools()
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for name,src,part,pos in [('Fridge','KI-FRIDGE-01/models','KI_FRIDGE_DOOR',(599.5,47,0)),('Range','KI-RANGE-01/model','KI_RANGE_Door',(687.5,47,0))]:
 folder='/Game/ICanFixHim/Environment/Redesign/KI_'+name;t=unreal.AssetImportTask();t.filename=os.path.join(root,src,part+'.fbx');t.destination_path=folder;t.destination_name=part;t.automated=True;t.replace_existing=True;t.save=True;o=unreal.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=True;o.import_textures=True;o.static_mesh_import_data.combine_meshes=True;t.options=o;T.import_asset_tasks([t]);m=unreal.EditorAssetLibrary.load_asset(folder+'/'+part)
 if not m: raise RuntimeError(part)
 unreal.log('DOOR %s bounds %s' % (name,m.get_bounds()))
 a=A.spawn_actor_from_object(m,unreal.Vector(*pos));a.set_actor_label('Art_KI_'+name+'_Door');a.set_folder_path('Redesign/Imported Art/Kitchen');a.static_mesh_component.set_collision_profile_name('NoCollision')
assert L.save_current_level()
