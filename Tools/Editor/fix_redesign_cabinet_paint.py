"""Apply sage paint per READMEs: KI-CABINET-01 uses sage-D at HSV value 0.75;
KI-UPPER-01 reuses the pantry's sage material ("matching pantry")."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
R = '/Game/ICanFixHim/Environment/Redesign/'
F = R + 'Finishes/'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
t = unreal.AssetImportTask(); t.filename = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/KI-CABINET-01/textures/sage-D.png')
t.destination_path = F + 'Textures'; t.destination_name = 'T_Cabinet_SageD'; t.automated = True; t.replace_existing = True; t.save = True
tools.import_asset_tasks([t])
path = F + 'MI_Cabinet_Sage'
mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset('MI_Cabinet_Sage', F[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, EAL.load_asset(F + 'M_Redesign_UVFinish'))
MEL.set_material_instance_texture_parameter_value(mi, 'BaseTexture', EAL.load_asset(F + 'Textures/T_Cabinet_SageD'))
MEL.set_material_instance_vector_parameter_value(mi, 'Mult', unreal.LinearColor(0.75, 0.75, 0.75, 1))
MEL.set_material_instance_scalar_parameter_value(mi, 'Roughness', 0.7)
EAL.save_asset(path)
pantry_sage = EAL.load_asset(R + 'KI_Pantry/Sage_painted_wood')
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
n = 0
for a in A.get_all_level_actors():
    lab = a.get_actor_label()
    if lab.startswith('Art_KI_Cabinet_'): a.static_mesh_component.set_material(0, mi); n += 1
    elif lab.startswith('Art_KI_Upper_') and pantry_sage: a.static_mesh_component.set_material(0, pantry_sage); n += 1
assert L.save_current_level()
unreal.log('[Paint] updated %d actors, pantry material found=%s' % (n, bool(pantry_sage)))
