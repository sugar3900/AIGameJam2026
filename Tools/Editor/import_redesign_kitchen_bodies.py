import os,unreal
root='/Users/davidwallin/Developer/AIGameJam2026-environment/Art Source/Apartment Redesign/Assets'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); tools=unreal.AssetToolsHelpers.get_asset_tools()
assert levels.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for name,src,part,idx,pos in [('Fridge','KI-FRIDGE-01/models','KI_FRIDGE_BODY',6,(599.5,47,0)),('Range','KI-RANGE-01/model','KI_RANGE_Body',7,(687.5,47,0))]:
 folder='/Game/ICanFixHim/Environment/Redesign/KI_'+name
 t=unreal.AssetImportTask();t.filename=os.path.join(root,src,part+'.fbx');t.destination_path=folder;t.destination_name=part;t.automated=True;t.replace_existing=True;t.save=True
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=True;o.import_textures=True;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=True;t.options=o;tools.import_asset_tasks([t]);m=unreal.EditorAssetLibrary.load_asset(folder+'/'+part)
 if not m: raise RuntimeError(part)
 a=actors.spawn_actor_from_object(m,unreal.Vector(*pos),unreal.Rotator(0,0,0));a.set_actor_label('Art_KI_'+name+'_Body');a.set_folder_path('Redesign/Imported Art/Kitchen')
 for old in actors.get_all_level_actors():
  if old.get_actor_label().startswith('Placeholder_%02d_'%idx): actors.destroy_actor(old)
 unreal.log('[Kitchen] %s %s' % (name,m.get_bounds().box_extent))
assert levels.save_current_level()
