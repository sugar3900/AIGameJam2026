"""Import floor, ceiling and door kits; build one UV-mapped master finish material.

BaseColor = lerp(Texture * Mult, LerpColor, LerpAmount); Roughness/Metallic params.
Material instances reproduce each README's Blender multipliers/mixes.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
F = R + 'Finishes/'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()

def imp(path, dest, name, mesh=False, collision=False):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = True
    if mesh:
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = collision; t.options = o
    tools.import_asset_tasks([t]); a = EAL.load_asset(dest + '/' + name)
    if not a: raise RuntimeError(path)
    return a

TEX = {'T_Wood_Honey': 'ARC-FLOOR-WOOD-01/textures/wood-candidate-c.png',
       'T_KitchenChecker': 'KI-TILE-01/textures/checker-selected.png',
       'T_BathGlaze': 'BA-FLOOR-01/textures/ivory-glaze.png',
       'T_Door_Paint': 'ARC-DOOR-01/textures/paint-selected.png',
       'T_Walnut_Aged': 'ARC-ENTRY-DOOR-01/textures/walnut-aged.png'}
tex = {k: imp(os.path.join(SRC, v), F + 'Textures', k) for k, v in TEX.items()}
tex['T_Plaster_Ceiling'] = EAL.load_asset(F + 'Textures/T_Plaster_Ceiling')
white = EAL.load_asset('/Engine/EngineResources/WhiteSquareTexture')

MP = F + 'M_Redesign_UVFinish'
if not EAL.does_asset_exist(MP):
    m = tools.create_asset('M_Redesign_UVFinish', F[:-1], unreal.Material, unreal.MaterialFactoryNew())
    def p(cls, name, x, y, val):
        e = MEL.create_material_expression(m, cls, x, y); e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', val); return e
    s = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, 0)
    s.set_editor_property('parameter_name', 'BaseTexture'); s.set_editor_property('texture', white)
    mult = p(unreal.MaterialExpressionVectorParameter, 'Mult', -700, 250, unreal.LinearColor(1, 1, 1, 1))
    lc = p(unreal.MaterialExpressionVectorParameter, 'LerpColor', -450, 250, unreal.LinearColor(1, 1, 1, 1))
    la = p(unreal.MaterialExpressionScalarParameter, 'LerpAmount', -450, 400, 0.0)
    mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, 50)
    MEL.connect_material_expressions(s, 'RGB', mul, 'A'); MEL.connect_material_expressions(mult, '', mul, 'B')
    lp = MEL.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -200, 50)
    MEL.connect_material_expressions(mul, '', lp, 'A'); MEL.connect_material_expressions(lc, '', lp, 'B'); MEL.connect_material_expressions(la, '', lp, 'Alpha')
    MEL.connect_material_property(lp, '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(p(unreal.MaterialExpressionScalarParameter, 'Roughness', -200, 300, 0.85), '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(p(unreal.MaterialExpressionScalarParameter, 'Metallic', -200, 400, 0.0), '', unreal.MaterialProperty.MP_METALLIC)
    MEL.recompile_material(m); EAL.save_asset(MP)
m = EAL.load_asset(MP)

def mi(name, t=None, mult=None, lerpc=None, lerpa=0.0, rough=0.85, metal=0.0):
    path = F + name
    inst = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset(name, F[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(inst, m)
    MEL.set_material_instance_texture_parameter_value(inst, 'BaseTexture', tex[t] if t else white)
    if mult: MEL.set_material_instance_vector_parameter_value(inst, 'Mult', unreal.LinearColor(*mult, 1))
    if lerpc: MEL.set_material_instance_vector_parameter_value(inst, 'LerpColor', unreal.LinearColor(*lerpc, 1))
    MEL.set_material_instance_scalar_parameter_value(inst, 'LerpAmount', lerpa)
    MEL.set_material_instance_scalar_parameter_value(inst, 'Roughness', rough)
    MEL.set_material_instance_scalar_parameter_value(inst, 'Metallic', metal)
    EAL.save_asset(path)

for i, c in enumerate([(1.03, 1.00, .96), (.72, .75, .76), (.90, .84, .77), (.79, .83, .85), (.98, .88, .77), (.84, .86, .82)]):
    mi('MI_FloorWood_%d' % i, 'T_Wood_Honey', mult=c, rough=0.88)
mi('MI_FloorWood_Subfloor', mult=(0.035, 0.025, 0.018), rough=0.95)
mi('MI_KitchenChecker', 'T_KitchenChecker', rough=0.72)
mi('MI_KitchenSubstrate', mult=(0.16, 0.10, 0.07), rough=0.9)
mi('MI_BathHex_Ivory', 'T_BathGlaze', lerpc=(0.79, 0.66, 0.57), lerpa=0.30, rough=0.79)
mi('MI_BathHex_Rose', 'T_BathGlaze', lerpc=(0.56, 0.28, 0.27), lerpa=0.80, rough=0.79)
mi('MI_BathGrout', mult=(0.78, 0.72, 0.62), rough=0.9)
mi('MI_Ceiling_UV', 'T_Plaster_Ceiling', rough=0.9)
mi('MI_Door_Paint', 'T_Door_Paint', lerpc=(0.80, 0.74, 0.62), lerpa=0.35, rough=0.75)
mi('MI_Door_Brass', mult=(0.55, 0.42, 0.22), rough=0.42, metal=1.0)
mi('MI_Door_EdgeWood', mult=(0.30, 0.19, 0.11), rough=0.8)
mi('MI_Entry_Walnut', 'T_Walnut_Aged', rough=0.65)

MESH = [('ARC-FLOOR-WOOD-01/model', ['ARC_Floor_Wood_2m'], 'ARC_FloorWood'),
        ('KI-TILE-01/model', ['KI_TILE_TOP', 'KI_TILE_SUBSTRATE'], 'KI_Tile'),
        ('BA-FLOOR-01/model', ['BA_FLOOR_MODULE'], 'BA_Floor'),
        ('ARC-CEILING-PLASTER-01/model', ['ARC_Ceiling_Module_2m'], 'ARC_Ceiling'),
        ('ARC-DOOR-01/model', ['ARC_Door_Frame', 'ARC_Door_Leaf'], 'ARC_Door'),
        ('ARC-ENTRY-DOOR-01/model', ['ARC_Entry_Door_Frame', 'ARC_Entry_Door_Leaf'], 'ARC_EntryDoor')]
for src, parts, folder in MESH:
    for prt in parts:
        sm = imp(os.path.join(SRC, src, prt + '.fbx'), R + folder, prt, mesh=True, collision=(prt == 'ARC_Entry_Door_Leaf'))
        b = sm.get_bounding_box()
        unreal.log('[FD] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f) slots=%s' % (prt, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z,
                   [str(s.material_slot_name) for s in sm.static_materials]))
