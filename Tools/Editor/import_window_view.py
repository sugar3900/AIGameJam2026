"""Import the painted exterior card used behind apartment windows."""
import os
import unreal
root = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
dest = '/Game/ICanFixHim/Materials/Environment'
assets = unreal.AssetToolsHelpers.get_asset_tools()
e = unreal.EditorAssetLibrary
m = unreal.MaterialEditingLibrary
t = unreal.AssetImportTask()
t.filename = os.path.join(root, 'Art Source', 'Environment Textures', 'T_WindowView.png')
t.destination_path = dest
t.automated = True
t.replace_existing = True
t.save = True
assets.import_asset_tasks([t])
tex = e.load_asset(dest + '/T_WindowView')
if not tex:
    raise RuntimeError('Missing imported window view')
tex.set_editor_property('power_of_two_mode', unreal.TexturePowerOfTwoSetting.STRETCH_TO_POWER_OF_TWO)
e.save_loaded_asset(tex)
path = dest + '/M_WindowView'
mat = e.load_asset(path) if e.does_asset_exist(path) else assets.create_asset('M_WindowView', dest, unreal.Material, unreal.MaterialFactoryNew())
m.delete_all_material_expressions(mat)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
sample = m.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -300, 0)
sample.set_editor_property('texture', tex)
brightness = m.create_material_expression(mat, unreal.MaterialExpressionMultiply, 0, 0)
window_level = m.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -300, 200)
window_level.set_editor_property('parameter_name', 'WindowBrightness')
window_level.set_editor_property('default_value', 12.0)
m.connect_material_expressions(sample, 'RGB', brightness, 'A')
m.connect_material_expressions(window_level, '', brightness, 'B')
m.connect_material_property(brightness, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.recompile_material(mat)
e.save_loaded_asset(mat)
# The same illustrated city provides a small, non-emissive picture print.
art_path = dest + '/M_ArtPrint'
art = e.load_asset(art_path) if e.does_asset_exist(art_path) else assets.create_asset('M_ArtPrint', dest, unreal.Material, unreal.MaterialFactoryNew())
m.delete_all_material_expressions(art)
art_sample = m.create_material_expression(art, unreal.MaterialExpressionTextureSample, -300, 0)
art_sample.set_editor_property('texture', tex)
m.connect_material_property(art_sample, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
m.recompile_material(art)
e.save_loaded_asset(art)
