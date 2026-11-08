"""Create a reusable painterly surface master without modifying existing materials.

Run in the environment worktree's Unreal Editor, before build_apartment.py:
    python3 Tools/run_in_editor.py Tools/Editor/create_painterly_material.py

M_PainterlySurface exposes BaseColor, Emissive, Roughness, BrushStrength and
BrushScaleCm. Position-projected warm and cool colored brush marks stay approximately the same
world size on differently sized meshes. The material changes color only: it
adds no bump, crust, chips, or damage. Those are separately authored details.
"""
import os
import unreal

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
DEST = '/Game/ICanFixHim/Materials/Environment'
ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SOURCE = os.path.join(ROOT, 'Art Source', 'Environment Textures', 'T_BrushValues.png')


def expression(mat, cls, x, y, **properties):
    node = MEL.create_material_expression(mat, cls, x, y)
    for name, value in properties.items():
        node.set_editor_property(name, value)
    return node


def make_material():
    if not os.path.isfile(SOURCE):
        raise RuntimeError('Missing brush mask: ' + SOURCE)
    task = unreal.AssetImportTask()
    task.filename = SOURCE
    task.destination_path = DEST
    task.destination_name = 'T_BrushValues'
    task.automated = True
    task.replace_existing = True
    task.save = True
    ASSETS.import_asset_tasks([task])
    tex = EAL.load_asset(DEST + '/T_BrushValues')
    if not tex:
        raise RuntimeError('Could not import brush mask')
    # The PNG encodes data in linear space; no gamma conversion.
    tex.set_editor_property('srgb', False)
    EAL.save_loaded_asset(tex)

    path = DEST + '/M_PainterlySurface'
    if EAL.does_asset_exist(path):
        mat = EAL.load_asset(path)
        MEL.delete_all_material_expressions(mat)
    else:
        mat = ASSETS.create_asset('M_PainterlySurface', DEST, unreal.Material,
                                  unreal.MaterialFactoryNew())
    mat.set_editor_property('used_with_static_lighting', True)
    mat.set_editor_property('two_sided', True)
    base = expression(mat, unreal.MaterialExpressionVectorParameter, -800, -400,
                      parameter_name='BaseColor', default_value=unreal.LinearColor(.8, .8, .8, 1))
    emissive = expression(mat, unreal.MaterialExpressionVectorParameter, -800, 450,
                          parameter_name='Emissive', default_value=unreal.LinearColor(0, 0, 0, 1))
    roughness = expression(mat, unreal.MaterialExpressionScalarParameter, -800, 600,
                           parameter_name='Roughness', default_value=.8)
    scale = expression(mat, unreal.MaterialExpressionScalarParameter, -1100, 200,
                       parameter_name='BrushScaleCm', default_value=180.0)
    strength = expression(mat, unreal.MaterialExpressionScalarParameter, -500, 100,
                          parameter_name='BrushStrength', default_value=.7)
    position = expression(mat, unreal.MaterialExpressionWorldPosition, -1100, -100)
    normal = expression(mat, unreal.MaterialExpressionPixelNormalWS, -1100, 50)
    uv = expression(mat, unreal.MaterialExpressionCustom, -800, 0,
                    code='float3 n = abs(N); float2 uv = n.z >= max(n.x,n.y) ? P.xy : (n.x >= n.y ? P.yz : P.xz); return uv / max(Scale, 1.0);',
                    output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT2,
                    description='World-space brush projection')
    inputs = []
    for name in ('P', 'N', 'Scale'):
        inp = unreal.CustomInput()
        inp.set_editor_property('input_name', name)
        inputs.append(inp)
    uv.set_editor_property('inputs', inputs)
    MEL.connect_material_expressions(position, '', uv, 'P')
    MEL.connect_material_expressions(normal, '', uv, 'N')
    MEL.connect_material_expressions(scale, '', uv, 'Scale')
    sample = expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -500, -100,
                        parameter_name='BrushMask', texture=tex,
                        sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    MEL.connect_material_expressions(uv, '', sample, 'UVs')
    subtract = expression(mat, unreal.MaterialExpressionSubtract, -250, -100, const_b=.5)
    MEL.connect_material_expressions(sample, 'RGB', subtract, 'A')
    mult = expression(mat, unreal.MaterialExpressionMultiply, -50, -100)
    MEL.connect_material_expressions(subtract, '', mult, 'A')
    MEL.connect_material_expressions(strength, '', mult, 'B')
    add = expression(mat, unreal.MaterialExpressionAdd, 150, -100, const_b=1.0)
    MEL.connect_material_expressions(mult, '', add, 'A')
    color = expression(mat, unreal.MaterialExpressionMultiply, 350, -250)
    MEL.connect_material_expressions(base, 'RGB', color, 'A')
    MEL.connect_material_expressions(add, '', color, 'B')
    MEL.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(emissive, 'RGB', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(roughness, '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    unreal.log('[FixHim] Created ' + path)
    return mat


if __name__ == '__main__':
    make_material()
