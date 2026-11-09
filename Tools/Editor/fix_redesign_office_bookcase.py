"""OF-BOOKCASE-01: muted walnut (walnut-muted-b, Blender sat 0.68 / value 1.35, rough 0.88)."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
F = '/Game/ICanFixHim/Environment/Redesign/Finishes/'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
t = unreal.AssetImportTask(); t.filename = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/OF-BOOKCASE-01/textures/walnut-muted-b.png')
t.destination_path = F + 'Textures'; t.destination_name = 'T_Walnut_MutedB'; t.automated = True; t.replace_existing = True; t.save = True
tools.import_asset_tasks([t])
path = F + 'MI_Walnut_MutedB'
mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset('MI_Walnut_MutedB', F[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, EAL.load_asset(F + 'M_Redesign_UVFinish'))
MEL.set_material_instance_texture_parameter_value(mi, 'BaseTexture', EAL.load_asset(F + 'Textures/T_Walnut_MutedB'))
MEL.set_material_instance_vector_parameter_value(mi, 'Mult', unreal.LinearColor(1.35, 1.35, 1.35, 1))
MEL.set_material_instance_vector_parameter_value(mi, 'LerpColor', unreal.LinearColor(0.30, 0.24, 0.19, 1))
MEL.set_material_instance_scalar_parameter_value(mi, 'LerpAmount', 0.32)
MEL.set_material_instance_scalar_parameter_value(mi, 'Roughness', 0.88)
EAL.save_asset(path)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
n = 0
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith('Art_OF_Bookcase_'): a.static_mesh_component.set_material(0, mi); n += 1
assert L.save_current_level()
unreal.log('[Bookcase] updated %d' % n)
