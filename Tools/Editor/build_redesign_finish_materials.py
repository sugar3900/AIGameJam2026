"""Import selected finish textures and wall-kit meshes; build world-projected finish materials.

The READMEs specify a continuous world-space projection at 320 cm per image with mirrored
repeat, rotation-aware for walls along X or Y. This builds one master and per-room instances.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
BASE = '/Game/ICanFixHim/Environment/Redesign/Finishes'
tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary

def import_file(path, dest, name, mesh=False, collision=True):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = True
    if mesh:
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False
        o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True
        o.static_mesh_import_data.auto_generate_collision = collision
        t.options = o
    tools.import_asset_tasks([t])
    a = EAL.load_asset(dest + '/' + name)
    if not a: raise RuntimeError('import failed ' + path)
    return a


def material_in_place(name, folder):
    """Load-or-create and clear the graph in place. Deleting and recreating would force-delete the
    asset and blank every actor/instance reference to it (EditorAssetLibrary.delete_asset)."""
    path = folder + '/' + name
    if EAL.does_asset_exist(path):
        mat = EAL.load_asset(path); MEL.delete_all_material_expressions(mat); return mat
    return tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())

def instance_in_place(name, folder):
    path = folder + '/' + name
    return EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset(name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())

TEX = {
    'T_Plaster_Living': 'ARC-LIVING-WALL-01/textures/plaster-candidate-d.png',
    'T_Trim_Cream': 'ARC-LIVING-WALL-01/textures/trim-candidate-a.png',
    'T_Plaster_Kitchen': 'ARC-KITCHEN-PLASTER-01/textures/plaster-candidate-b.png',
    'T_Plaster_Bedroom': 'ARC-BEDROOM-PLASTER-01/textures/candidate-b-sage.png',
    'T_Plaster_Ceiling': 'ARC-CEILING-PLASTER-01/textures/plaster-candidate-c.png',
    'T_Wainscot_Ivory': 'BR-WAINSCOT-01/textures/candidate-d-brush-ivory.png',
    'T_Wainscot_Damage': 'BR-WAINSCOT-01/textures/paint-damage-selected.png',
    'T_BathTile_Glaze': 'BA-TILE-01/textures/candidate-b.png',
}
tex = {k: import_file(os.path.join(SRC, v), BASE + '/Textures', k) for k, v in TEX.items()}

# Master: world-projected, mirrored, rotation-aware (X/Z, Y/Z, or X/Y for floors/ceilings).
MPATH = BASE + '/M_Redesign_WorldFinish'
m = material_in_place('M_Redesign_WorldFinish', BASE)
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 0)
nrm = MEL.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -900, 150)
scale = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, 300)
scale.set_editor_property('parameter_name', 'ProjectionCm'); scale.set_editor_property('default_value', 320.0)
cust = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -600, 100)
cust.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT2)
cust.set_editor_property('code', '''float3 n = abs(N);
float2 uv;
if (n.z > 0.7) uv = P.xy;
else if (n.x > n.y) uv = float2(P.y, -P.z);
else uv = float2(P.x, -P.z);
uv /= S;
return 1.0 - abs(1.0 - fmod(abs(uv), 2.0));''')
def _ci(n):
    c = unreal.CustomInput(); c.set_editor_property('input_name', n); return c
cust.set_editor_property('inputs', [_ci(n) for n in ('P', 'N', 'S')])
MEL.connect_material_expressions(wp, '', cust, 'P')
MEL.connect_material_expressions(nrm, '', cust, 'N')
MEL.connect_material_expressions(scale, '', cust, 'S')
samp = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -300, 0)
samp.set_editor_property('parameter_name', 'BaseTexture'); samp.set_editor_property('texture', tex['T_Plaster_Living'])
MEL.connect_material_expressions(cust, '', samp, 'UVs')
tint = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -300, 250)
tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(1, 1, 1, 1))
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -50, 50)
MEL.connect_material_expressions(samp, 'RGB', mul, 'A'); MEL.connect_material_expressions(tint, '', mul, 'B')
MEL.connect_material_property(mul, '', unreal.MaterialProperty.MP_BASE_COLOR)
rough = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -50, 250)
rough.set_editor_property('parameter_name', 'Roughness'); rough.set_editor_property('default_value', 0.9)
MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
MEL.recompile_material(m); EAL.save_asset(MPATH)

def mi(name, texname, roughness=0.9, tint=None, proj=320.0):
    path = BASE + '/' + name
    inst = instance_in_place(name, BASE)
    MEL.set_material_instance_parent(inst, m)
    MEL.set_material_instance_texture_parameter_value(inst, 'BaseTexture', tex[texname])
    MEL.set_material_instance_scalar_parameter_value(inst, 'Roughness', roughness)
    MEL.set_material_instance_scalar_parameter_value(inst, 'ProjectionCm', proj)
    if tint: MEL.set_material_instance_vector_parameter_value(inst, 'Tint', unreal.LinearColor(*tint))
    EAL.save_asset(path); return inst

mi('MI_Plaster_Living', 'T_Plaster_Living')
mi('MI_Plaster_Kitchen', 'T_Plaster_Kitchen')
mi('MI_Plaster_Bedroom', 'T_Plaster_Bedroom')
mi('MI_Plaster_Ceiling', 'T_Plaster_Ceiling', proj=200.0)
mi('MI_Plaster_Exterior', 'T_Plaster_Ceiling', tint=(0.75, 0.73, 0.70, 1))
mi('MI_Trim_Cream', 'T_Trim_Cream', roughness=0.6, proj=100.0)
mi('MI_Wainscot_Ivory', 'T_Wainscot_Ivory', roughness=0.6, proj=150.0)

# Wall kit meshes for inspection/placement.
MESH = [
    ('ARC-LIVING-WALL-01/model', ['ARC_Living_SolidWall_2m', 'ARC_Living_WindowWall_2p4m', 'ARC_Window_Casing_Sash', 'ARC_Window_Glazing'], 'ARC_LivingWall'),
    ('BR-WAINSCOT-01/model', ['BR_Wainscot_Module', 'BR_Wainscot_Damage'], 'BR_Wainscot'),
    ('BA-TILE-01/model', ['BA_Tile_1m_Module', 'BA_Tile_Cap', 'BA_Tile_040_Extension', 'BA_Tile_Damage'], 'BA_Tile'),
    ('ARC-TRIM-01/model', ['Baseboard_1m', 'Crown_1m'], 'ARC_Trim'),
]
for src, parts, folder in MESH:
    for p in parts:
        sm = import_file(os.path.join(SRC, src, p + '.fbx'), '/Game/ICanFixHim/Environment/Redesign/' + folder, p, mesh=True,
                         collision=p in ('ARC_Living_SolidWall_2m',))
        b = sm.get_bounding_box()
        slots = [s.material_slot_name for s in sm.static_materials]
        unreal.log('[Finish] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f) slots=%s' % (p, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z, slots))

# Translucent glass for window glazing (README: low roughness, pale tint, no shadow).
GPATH = BASE + '/M_Redesign_Glass'
g = material_in_place('M_Redesign_Glass', BASE)
g.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
g.set_editor_property('two_sided', True)
gc = MEL.create_material_expression(g, unreal.MaterialExpressionConstant3Vector, -300, 0)
gc.set_editor_property('constant', unreal.LinearColor(0.82, 0.90, 0.92, 1))
MEL.connect_material_property(gc, '', unreal.MaterialProperty.MP_BASE_COLOR)
for prop, val, y in [(unreal.MaterialProperty.MP_OPACITY, 0.05, 120), (unreal.MaterialProperty.MP_ROUGHNESS, 0.08, 220), (unreal.MaterialProperty.MP_SPECULAR, 0.6, 320)]:
    k = MEL.create_material_expression(g, unreal.MaterialExpressionConstant, -300, y); k.set_editor_property('r', val)
    MEL.connect_material_property(k, '', prop)
MEL.recompile_material(g); EAL.save_asset(GPATH)
gi = instance_in_place('MI_Window_Glass', BASE)
MEL.set_material_instance_parent(gi, g); EAL.save_asset(BASE + '/MI_Window_Glass')
