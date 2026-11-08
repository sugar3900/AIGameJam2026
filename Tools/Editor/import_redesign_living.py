"""Place reviewed rug and bookcase assembly in the redesign review map."""
import os, unreal
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
base=os.path.join(root,'Art Source/Apartment Redesign/Assets')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools=unreal.AssetToolsHelpers.get_asset_tools()
assert levels.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
items=[('LV_Rug','LV-RUG-01/model',['LV_RUG_01'],None,(260,195,0),0),('LV_Book','LV-BOOK-01/model',['LV_BOOK_CASE','LV_BOOK_BOOKS','LV_BOOK_PLANT','LV_BOOK_TIN'],2,(417.5,32,0),0)]
for name,src,parts,idx,pos,yaw in items:
 folder='/Game/ICanFixHim/Environment/Redesign/'+name
 meshes=[]
 for part in parts:
  task=unreal.AssetImportTask(); task.filename=os.path.join(base,src,part+'.fbx'); task.destination_path=folder; task.destination_name=part; task.automated=True; task.replace_existing=True; task.save=True
  opt=unreal.FbxImportUI(); opt.import_mesh=True; opt.import_as_skeletal=False; opt.import_materials=True; opt.import_textures=True; opt.static_mesh_import_data.combine_meshes=True; opt.static_mesh_import_data.auto_generate_collision=True; task.options=opt
  tools.import_asset_tasks([task]); mesh=unreal.EditorAssetLibrary.load_asset(folder+'/'+part)
  if not mesh: raise RuntimeError(part)
  meshes.append((part,mesh)); unreal.log('[Living] %s %s' % (part,mesh.get_bounds().box_extent))
 existing=actors.get_all_level_actors(); old=[a for a in existing if a.get_actor_label().startswith('Art_'+name+'_') or (idx is not None and a.get_actor_label().startswith('Placeholder_%02d_'%idx))]
 for a in old: actors.destroy_actor(a)
 for part,mesh in meshes:
  a=actors.spawn_actor_from_object(mesh,unreal.Vector(*pos),unreal.Rotator(0,0,yaw)); a.set_actor_label('Art_'+name+'_'+part); a.set_folder_path('Redesign/Imported Art/'+name)
  if name=='LV_Rug' or part!='LV_BOOK_CASE': a.static_mesh_component.set_collision_profile_name('NoCollision')
assert levels.save_current_level()
