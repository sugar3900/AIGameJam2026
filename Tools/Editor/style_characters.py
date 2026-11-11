"""Build character-only scene-lit illustrated/matte alternatives, retaining the original M_Hunk.

Run with Tools/run_in_editor.py. Defaults to matte for all five characters.
Stop PIE before comparing:
  -c "import runpy; runpy.run_path('.../Tools/Editor/style_characters.py', init_globals={'STYLE': 'matte'})"
STYLE: original | illustrated | matte (cel is a legacy alias).
BUILD=False switches existing variants only.
No level, lighting, texture, mesh or environment assets are modified.
"""
import unreal

L = unreal.MaterialEditingLibrary
E = unreal.EditorAssetLibrary
ROOT = '/Game/ICanFixHim'
ORIGINAL = ROOT + '/Materials/M_Hunk'
FOLDERS = ('BlackMold', 'FaultyWiring', 'LeadPaint', 'LeakyPipes', 'PinkTile')
STYLES = {'original': ORIGINAL,
          'illustrated': ORIGINAL + '_Illustrated', 'cel': ORIGINAL + '_Cel', 'matte': ORIGINAL + '_Cel'}
STYLE = globals().get('STYLE', 'matte')
BUILD = globals().get('BUILD', True)


def node(mat, cls, **props):
    n = L.create_material_expression(mat, cls, 0, 0)
    for k, v in props.items():
        n.set_editor_property(k, v)
    return n


def connect(src, output, dst, input_name):
    assert L.connect_material_expressions(src, output, dst, input_name), input_name


def build(style):
    path = STYLES[style]
    mat = E.load_asset(path) if E.does_asset_exist(path) else E.duplicate_asset(ORIGINAL, path)
    assert mat, path
    style_parameters = {'StyleNormalStrength', 'StyleRoughness', 'StyleRoughnessWeight',
                        'StyleMetallicWeight', 'StyleSpecular'}
    existing = set(map(str, L.get_scalar_parameter_names(mat)))
    if style_parameters <= existing:
        assert mat.get_editor_property('shading_model') == unreal.MaterialShadingModel.MSM_DEFAULT_LIT
        assert mat.get_editor_property('blend_mode') == unreal.BlendMode.BLEND_MASKED
        return mat
    assert not style_parameters.intersection(existing), 'Incomplete style graph: ' + path
    assert {'Dissolve', 'FormHeight', 'EdgeGlow', 'ArcAmount', 'EdgeDark'} <= existing, 'Add the reveal effect to M_Hunk before building styles'
    assert mat.get_editor_property('shading_model') == unreal.MaterialShadingModel.MSM_DEFAULT_LIT
    # Keep the complete original graph, including the opacity mask and reveal glow.
    for n in L.get_material_expressions(mat):
        if isinstance(n, unreal.MaterialExpressionScalarParameter) and str(n.get_editor_property('parameter_name')) == 'Rim':
            n.set_editor_property('default_value', 0.035)

    def scalar(name, value):
        return node(mat, unreal.MaterialExpressionScalarParameter, parameter_name=name, default_value=value)

    # Real scene lighting, GI, exposure and cast shadows supply all the shading.
    # Stylization comes from quieter material response, not replacement lighting.
    normal_prop = unreal.MaterialProperty.MP_NORMAL
    normal = L.get_material_property_input_node(mat, normal_prop)
    normal_out = L.get_material_property_input_node_output_name(mat, normal_prop)
    flat = node(mat, unreal.MaterialExpressionConstant3Vector, constant=unreal.LinearColor(0,0,1,1))
    softened = node(mat, unreal.MaterialExpressionLinearInterpolate)
    connect(flat, '', softened, 'A')
    connect(normal, normal_out, softened, 'B')
    connect(scalar('StyleNormalStrength', 0.22 if style == 'illustrated' else 0.0), '', softened, 'Alpha')
    assert L.connect_material_property(softened, '', normal_prop)

    rough_prop = unreal.MaterialProperty.MP_ROUGHNESS
    rough = L.get_material_property_input_node(mat, rough_prop)
    rough_out = L.get_material_property_input_node_output_name(mat, rough_prop)
    matte = node(mat, unreal.MaterialExpressionLinearInterpolate)
    connect(rough, rough_out, matte, 'A')
    connect(scalar('StyleRoughness', 0.82 if style == 'illustrated' else 0.98), '', matte, 'B')
    connect(scalar('StyleRoughnessWeight', 0.85 if style == 'illustrated' else 1.0), '', matte, 'Alpha')
    assert L.connect_material_property(matte, '', rough_prop)

    metal_prop = unreal.MaterialProperty.MP_METALLIC
    metal = L.get_material_property_input_node(mat, metal_prop)
    metal_out = L.get_material_property_input_node_output_name(mat, metal_prop)
    muted = node(mat, unreal.MaterialExpressionMultiply)
    connect(metal, metal_out, muted, 'A')
    connect(scalar('StyleMetallicWeight', 0.12 if style == 'illustrated' else 0.0), '', muted, 'B')
    assert L.connect_material_property(muted, '', metal_prop)
    assert L.connect_material_property(scalar('StyleSpecular', 0.20 if style == 'illustrated' else 0.08), '', unreal.MaterialProperty.MP_SPECULAR)
    L.layout_material_expressions(mat)
    L.recompile_material(mat)
    assert E.save_loaded_asset(mat, only_if_is_dirty=False), 'Could not save ' + path
    return mat


def apply(style):
    assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), 'Stop PIE before switching character styles'
    assert style in STYLES, 'STYLE must be original, illustrated or matte (cel is an alias)'
    parent = E.load_asset(STYLES[style])
    assert parent, 'Build style variants first'
    # Resolve every instance before changing any, so missing imports do not leave
    # the game with a mixture of old and new character styles.
    instances = [E.load_asset(f'{ROOT}/Characters/{folder}/MI_{folder}') for folder in FOLDERS]
    assert all(instances), 'Import all five character materials before switching styles'
    for mi in instances:
        L.set_material_instance_parent(mi, parent)
        L.update_material_instance(mi)
        assert E.save_loaded_asset(mi, only_if_is_dirty=False), 'Could not save ' + mi.get_path_name()
    unreal.log(f'[Character style] {style}: all {len(instances)} character instances saved')


assert STYLE in STYLES, 'STYLE must be original, illustrated or matte (cel is an alias)'
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), 'Stop PIE before changing character materials'

if BUILD:
    assert E.load_asset(ORIGINAL), 'Import characters first'
    for alternative in ('illustrated', 'cel'):
        build(alternative)
apply(STYLE)
