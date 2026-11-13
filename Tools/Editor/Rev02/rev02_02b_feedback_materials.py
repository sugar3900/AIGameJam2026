"""Rev02 step 2b: engine materials for feedback source release 001-003 (run after rev02_02 imports those kits).

FIX-001 BR-MOLD-02  M_Rev02_Mold02: neutral charcoal, matte, two-sided masked + DitherTemporalAA, coverage from the
                    README formula (vertex alpha x texture alpha x pigment darkness). No inherited olive tint.
FIX-003 KI-LEAK-02  M_Rev02_Water (+ MI_Rev02_BucketWater, MI_Rev02_LeakDrop): lit translucent water, so the pail
                    water and the falling drop pick up the scene's light instead of glowing.
                    M_Rev02_LeakRipple: one expanding ring on a unit plane, driven by the scalar "Phase" (0..1) that
                    AFixHimMalady animates on an authored leak.
                    M_Rev02_LeakPuddleDecal: deferred decal, Modulate (stain) blend - darkens the tile under the mask
                    and makes it glossy, but keeps the tile's own colour, grout and normals readable.
                    MI_Rev02_Zinc / MI_Rev02_ZincSeams / MI_Rev02_IronBail: pail slots per the KI-LEAK-02 README.
Re-runnable: existing materials are cleared and rebuilt in place (instances keep their references).
"""
import unreal
R2 = '/Game/ICanFixHim/Environment/Rev02/'
MATS = R2 + 'Materials/'
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
MP = unreal.MaterialProperty

def material(name):
    path = MATS + name
    if EAL.does_asset_exist(path):
        m = EAL.load_asset(path); MEL.delete_all_material_expressions(m)
    else:
        m = tools.create_asset(name, MATS[:-1], unreal.Material, unreal.MaterialFactoryNew())
    return m

def instance(name, parent, scalars=None, vectors=None, textures=None):
    path = MATS + name
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset(
        name, MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (scalars or {}).items(): MEL.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (vectors or {}).items(): MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
    for k, v in (textures or {}).items(): MEL.set_material_instance_texture_parameter_value(mi, k, v)
    EAL.save_asset(path)
    return mi

def const(m, v, x, y):
    if isinstance(v, (int, float)):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, x, y); e.set_editor_property('r', float(v))
    else:
        e = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, x, y)
        e.set_editor_property('constant', unreal.LinearColor(v[0], v[1], v[2], 1))
    return e

def sparam(m, name, default, x, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', float(default)); return e

def vparam(m, name, default, x, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, x, y)
    e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', unreal.LinearColor(*default)); return e

def tex(m, texture, x, y, param=None, linear=True):
    cls = unreal.MaterialExpressionTextureSampleParameter2D if param else unreal.MaterialExpressionTextureSample
    e = MEL.create_material_expression(m, cls, x, y)
    if param: e.set_editor_property('parameter_name', param)
    e.set_editor_property('texture', texture)
    e.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR if linear else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    return e

def custom(m, code, inputs, x, y, out=unreal.CustomMaterialOutputType.CMOT_FLOAT1):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
    e.set_editor_property('code', code); e.set_editor_property('output_type', out)
    ins = []
    for n in inputs:
        ci = unreal.CustomInput(); ci.set_editor_property('input_name', n); ins.append(ci)
    e.set_editor_property('inputs', ins)
    return e

def finish(m, path):
    MEL.recompile_material(m); assert EAL.save_asset(path), path

# ---------------- FIX-001 mold ----------------
m = material('M_Rev02_Mold02')
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
m.set_editor_property('two_sided', True)
m.set_editor_property('opacity_mask_clip_value', 0.5)          # DitherTemporalAA output is centred on the clip value
t = tex(m, EAL.load_asset(R2 + 'BR_Mold02/mold_colonies_rgba'), -900, 200, param='MoldTexture')
vc = MEL.create_material_expression(m, unreal.MaterialExpressionVertexColor, -900, 450)
cov = custom(m, 'float g = dot(RGB, float3(0.2126, 0.7152, 0.0722));\nreturn VA * TA * pow(saturate((0.56 - g) / 0.38), 1.35);',
             ['RGB', 'TA', 'VA'], -550, 300)
MEL.connect_material_expressions(t, 'RGB', cov, 'RGB'); MEL.connect_material_expressions(t, 'A', cov, 'TA')
MEL.connect_material_expressions(vc, 'A', cov, 'VA')
dither = MEL.create_material_expression(m, unreal.MaterialExpressionMaterialFunctionCall, -300, 300)
dither.set_editor_property('material_function', EAL.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'))
MEL.connect_material_expressions(cov, '', dither, 'Alpha Threshold')
MEL.connect_material_property(dither, '', MP.MP_OPACITY_MASK)
MEL.connect_material_property(vparam(m, 'BaseColor', (0.022, 0.021, 0.020, 1), -300, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(const(m, 1.0, -300, 120), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.0, -300, 170), '', MP.MP_METALLIC)
MEL.connect_material_property(const(m, 0.0, -300, 220), '', MP.MP_SPECULAR)
finish(m, MATS + 'M_Rev02_Mold02')

# ---------------- FIX-003 water, drop, ripple ----------------
def lit_translucent(m):
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property('translucency_lighting_mode', unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    m.set_editor_property('two_sided', False)

m = material('M_Rev02_Water'); lit_translucent(m)
MEL.connect_material_property(vparam(m, 'BaseColor', (0.020, 0.028, 0.032, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Opacity', 0.35, -400, 120), '', MP.MP_OPACITY)
MEL.connect_material_property(sparam(m, 'Roughness', 0.05, -400, 180), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(sparam(m, 'Specular', 0.5, -400, 240), '', MP.MP_SPECULAR)
MEL.connect_material_property(const(m, 0.0, -400, 300), '', MP.MP_METALLIC)
# MI_Rev02_LeakDrop draws the leak spray as instanced drops (FixHimMalady BuildSpray).
MEL.set_material_usage(m, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
finish(m, MATS + 'M_Rev02_Water')
water = EAL.load_asset(MATS + 'M_Rev02_Water')
instance('MI_Rev02_BucketWater', water, {'Opacity': 0.55, 'Roughness': 0.04})
instance('MI_Rev02_LeakDrop', water, {'Opacity': 0.5, 'Roughness': 0.03}, {'BaseColor': (0.06, 0.07, 0.075, 1)})

m = material('M_Rev02_LeakRipple'); lit_translucent(m)
uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, 200)
ring = custom(m, 'float d = length(UV - 0.5) * 2.0;\nfloat r = lerp(0.12, 0.95, Phase);\n'
                 'float w = lerp(0.07, 0.16, Phase);\n'
                 'return saturate(1.0 - abs(d - r) / w) * (1.0 - Phase) * (1.0 - Phase) * step(d, 1.0) * Strength;',
              ['UV', 'Phase', 'Strength'], -550, 200)
MEL.connect_material_expressions(uv, '', ring, 'UV')
MEL.connect_material_expressions(sparam(m, 'Phase', 0.3, -900, 320), '', ring, 'Phase')
MEL.connect_material_expressions(sparam(m, 'Strength', 0.6, -900, 400), '', ring, 'Strength')
MEL.connect_material_property(ring, '', MP.MP_OPACITY)
MEL.connect_material_property(vparam(m, 'BaseColor', (0.35, 0.38, 0.40, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(const(m, 0.03, -400, 300), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.8, -400, 360), '', MP.MP_SPECULAR)
finish(m, MATS + 'M_Rev02_LeakRipple')

# ---------------- FIX-003 residual floor spill (decal) ----------------
# Translucent (DBuffer colour + roughness) decal; the mask alpha drives coverage. A Modulate (stain) decal was tried
# first: in this project it ignored the mask opacity and darkened the whole decal box as a hard rectangle. Here the
# wet film darkens the tile a little and makes it glossy where the mask is set; normal is left unconnected, so tile
# relief and grout stay readable through the water.
m = material('M_Rev02_LeakPuddleDecal')
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property('material_domain', unreal.MaterialDomain.MD_DEFERRED_DECAL)
mask = tex(m, EAL.load_asset(R2 + 'KI_Leak02/T_Leak_Puddle_Mask'), -900, 200, param='PuddleMask')
# Mask basis (README): image right = UE +X, image up = UE -Y. FlipU/FlipV (0/1) match the decal's UV basis to that;
# set from a top-down capture of the installed decal.
duv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1500, 200)
flip = custom(m, 'return float2(lerp(UV.x, 1.0 - UV.x, FU), lerp(UV.y, 1.0 - UV.y, FV));', ['UV', 'FU', 'FV'], -1200, 200,
              out=unreal.CustomMaterialOutputType.CMOT_FLOAT2)
MEL.connect_material_expressions(duv, '', flip, 'UV')
MEL.connect_material_expressions(sparam(m, 'FlipU', 0.0, -1500, 320), '', flip, 'FU')
MEL.connect_material_expressions(sparam(m, 'FlipV', 0.0, -1500, 400), '', flip, 'FV')
MEL.connect_material_expressions(flip, '', mask, 'UVs')
op = custom(m, 'return saturate(A * Strength);', ['A', 'Strength'], -550, 200)
MEL.connect_material_expressions(mask, 'A', op, 'A')
MEL.connect_material_expressions(sparam(m, 'Strength', 0.22, -900, 420), '', op, 'Strength')
MEL.connect_material_property(op, '', MP.MP_OPACITY)
MEL.connect_material_property(vparam(m, 'WetTint', (0.07, 0.05, 0.035, 1), -400, 0), '', MP.MP_BASE_COLOR)
finish(m, MATS + 'M_Rev02_LeakPuddleDecal')
# DBuffer channels share one opacity, so a modest darkening would also dilute the gloss. The wet sheen is a second,
# roughness-only decal on the same mask (only connected outputs are written): strong gloss, no colour change.
m = material('M_Rev02_LeakPuddleWet')
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property('material_domain', unreal.MaterialDomain.MD_DEFERRED_DECAL)
mask = tex(m, EAL.load_asset(R2 + 'KI_Leak02/T_Leak_Puddle_Mask'), -900, 200, param='PuddleMask')
op = custom(m, 'return saturate(A * Strength);', ['A', 'Strength'], -550, 200)
MEL.connect_material_expressions(mask, 'A', op, 'A')
MEL.connect_material_expressions(sparam(m, 'Strength', 0.9, -900, 420), '', op, 'Strength')
MEL.connect_material_property(op, '', MP.MP_OPACITY)
MEL.connect_material_property(sparam(m, 'WetRoughness', 0.03, -400, 120), '', MP.MP_ROUGHNESS)
finish(m, MATS + 'M_Rev02_LeakPuddleWet')

# ---------------- FIX-003 pail (KI-LEAK-02 README material contract) ----------------
m = material('M_Rev02_Zinc')
bc = tex(m, EAL.load_asset(R2 + 'KI_Leak02/T_Bucket_Zinc_BaseColor'), -700, 0, param='BaseColorMap', linear=False)
mt = tex(m, EAL.load_asset(R2 + 'KI_Leak02/T_Bucket_Zinc_Metallic'), -700, 250, param='MetallicMap')
rg = tex(m, EAL.load_asset(R2 + 'KI_Leak02/T_Bucket_Zinc_Roughness'), -700, 500, param='RoughnessMap')
MEL.connect_material_property(bc, 'RGB', MP.MP_BASE_COLOR)
MEL.connect_material_property(mt, 'R', MP.MP_METALLIC)
MEL.connect_material_property(rg, 'R', MP.MP_ROUGHNESS)
finish(m, MATS + 'M_Rev02_Zinc')
instance('MI_Rev02_Zinc', EAL.load_asset(MATS + 'M_Rev02_Zinc'))

m = material('M_Rev02_ConstPBR')
MEL.connect_material_property(vparam(m, 'BaseColor', (0.5, 0.5, 0.5, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Metallic', 0.0, -400, 120), '', MP.MP_METALLIC)
MEL.connect_material_property(sparam(m, 'Roughness', 0.5, -400, 180), '', MP.MP_ROUGHNESS)
finish(m, MATS + 'M_Rev02_ConstPBR')
cpbr = EAL.load_asset(MATS + 'M_Rev02_ConstPBR')
instance('MI_Rev02_ZincSeams', cpbr, {'Metallic': 0.64, 'Roughness': 0.55}, {'BaseColor': (0.21, 0.235, 0.245, 1)})
instance('MI_Rev02_IronBail', cpbr, {'Metallic': 0.74, 'Roughness': 0.42}, {'BaseColor': (0.16, 0.175, 0.18, 1)})

# ---------------- FIX-005 LV-SOFA-02 (README material contract; base colour texture replaces the constant) ----------------
m = material('M_Rev02_TexPBR')
t = tex(m, EAL.load_asset(R2 + 'LV_Sofa02/sofa_floral'), -700, 0, param='BaseColorMap', linear=False)
# Tint defaults to white: direct-texture kits (sofa, paintings, runner, slippers) use the texture alone; kits whose
# contract says texture x multiplier (FIX-013 armchair) set it.
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 0)
MEL.connect_material_expressions(t, 'RGB', mul, 'A')
MEL.connect_material_expressions(vparam(m, 'Tint', (1, 1, 1, 1), -700, 250), '', mul, 'B')
MEL.connect_material_property(mul, '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Roughness', 0.85, -400, 200), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(sparam(m, 'Metallic', 0.0, -400, 260), '', MP.MP_METALLIC)
finish(m, MATS + 'M_Rev02_TexPBR')
texpbr = EAL.load_asset(MATS + 'M_Rev02_TexPBR')
for name, texname in (('MI_Sofa02_PaintedFloral', 'sofa_floral'), ('MI_Sofa02_TealNeedlepoint', 'pillow_teal_needlepoint'),
                      ('MI_Sofa02_CoralEmbroidery', 'pillow_coral_embroidery'), ('MI_Sofa02_WovenThrow', 'throw_wool')):
    instance(name, texpbr, {'Roughness': 0.85}, textures={'BaseColorMap': EAL.load_asset(R2 + 'LV_Sofa02/' + texname)})
for name, rgb, rough in (('MI_Sofa02_OliveWelt', (0.18, 0.155, 0.085), 0.85), ('MI_Sofa02_WornWalnut', (0.18, 0.075, 0.025), 0.62),
                         ('MI_Sofa02_AgedGoldCord', (0.43, 0.31, 0.13), 0.85)):
    instance(name, cpbr, {'Metallic': 0.0, 'Roughness': rough}, {'BaseColor': rgb + (1,)})

# ---------------- FIX-006 framed paintings: one instance per material slot (82), per the asset manifests ----------------
# A slot with base_color_texture uses the texture alone (it REPLACES base_color_linear; no multiply).
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
inv = json.load(open(os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json')))
n = 0
for it in inv['items']:
    sa = it['source_art']; kit = sa['asset'].replace('-', '_')
    for mt in sa['materials']:
        name = 'MI_' + mt['name'].replace('-', '_')
        if mt.get('base_color_texture'):
            tx = EAL.load_asset(R2 + kit + '/' + os.path.splitext(os.path.basename(mt['base_color_texture']))[0])
            assert tx, (kit, mt['base_color_texture'])
            instance(name, texpbr, {'Roughness': mt['roughness']}, textures={'BaseColorMap': tx})
        else:
            instance(name, cpbr, {'Metallic': mt['metallic'], 'Roughness': mt['roughness']}, {'BaseColor': tuple(mt['base_color_linear']) + (1,)})
        n += 1
unreal.log('[Rev02 feedback materials] FIX-006 slot instances: %d' % n)

# ---------------- FIX-020 HA-RUNNER-02 (assembly.json material contract) ----------------
if EAL.does_asset_exist(R2 + 'HA_Runner02/runner_albedo'):          # only once the FIX-020 kit has been imported
    instance('MI_Runner02_Painterly', texpbr, {'Roughness': 0.96}, textures={'BaseColorMap': EAL.load_asset(R2 + 'HA_Runner02/runner_albedo')})
    for name, rgb in (('MI_Runner02_LinenBacking', (0.29, 0.23, 0.16)), ('MI_Runner02_FadedRoseBinding', (0.27, 0.14, 0.105)),
                      ('MI_Runner02_FlaxFringe', (0.55, 0.46, 0.31))):
        instance(name, cpbr, {'Metallic': 0.0, 'Roughness': 0.96}, {'BaseColor': rgb + (1,)})
# ---------------- FIX-008 HA-SCONCE-02 / FIX-016 HA-SLIPPERS-01 (manifest material contracts), once imported ----------------
if EAL.does_asset_exist(R2 + 'HA_Sconce02/aged_brass'):
    instance('MI_HA_Sconce02_AgedBrass', texpbr, {'Roughness': 0.54, 'Metallic': 0.6}, textures={'BaseColorMap': EAL.load_asset(R2 + 'HA_Sconce02/aged_brass')})
    instance('MI_HA_Sconce02_OpalOpaque', texpbr, {'Roughness': 0.43, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'HA_Sconce02/opal_glass')})
    instance('MI_HA_Sconce02_PorcelainHolder', cpbr, {'Metallic': 0.0, 'Roughness': 0.57}, {'BaseColor': (0.74, 0.69, 0.58, 1)})
    instance('MI_HA_Sconce02_BulbIvory', cpbr, {'Metallic': 0.0, 'Roughness': 0.40}, {'BaseColor': (0.92, 0.82, 0.68, 1)})
if EAL.does_asset_exist(R2 + 'HA_Slippers01/T_Slipper_Quilt'):
    asm = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/HA-SLIPPERS-01/assembly.json')))
    for name, mt in asm['materials'].items():
        if mt['base_color_texture']:
            tx = EAL.load_asset(R2 + 'HA_Slippers01/' + os.path.splitext(os.path.basename(mt['base_color_texture']))[0])
            instance('MI_' + name, texpbr, {'Roughness': mt['roughness'], 'Metallic': 0.0}, textures={'BaseColorMap': tx})
        else:
            instance('MI_' + name, cpbr, {'Metallic': 0.0, 'Roughness': mt['roughness']}, {'BaseColor': tuple(mt['base_color_linear']) + (1,)})
# ---------------- FIX-010 entry door: new dark latch/bolt recess slot (frame slot 2, leaf slot 3) ----------------
instance('MI_Rev02_DarkRecess', cpbr, {'Metallic': 0.0, 'Roughness': 0.95}, {'BaseColor': (0.025, 0.018, 0.012, 1)})
# ---------------- FIX-013 LV-ARMCHAIR-02: texture x multiplier where the contract gives one ----------------
if EAL.does_asset_exist(R2 + 'LV_Armchair02/rust_jacquard'):
    asm = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/LV-ARMCHAIR-02/assembly.json')))
    for mt in asm['materials']:
        if mt['albedo_texture']:
            tx = EAL.load_asset(R2 + 'LV_Armchair02/' + os.path.splitext(os.path.basename(mt['albedo_texture']))[0].replace('-', '_'))
            instance('MI_' + mt['name'], texpbr, {'Roughness': mt['roughness'], 'Metallic': 0.0},
                     {'Tint': tuple(mt['base_color_multiplier']) + (1,)}, textures={'BaseColorMap': tx})
        else:
            instance('MI_' + mt['name'], cpbr, {'Metallic': 0.0, 'Roughness': mt['roughness']}, {'BaseColor': tuple(mt['base_color_linear']) + (1,)})
# ---------------- FIX-014 LV-PLANT-02: five material groups per manifest (texture direct, else constant) ----------------
def slot_mi(prefix, name): return 'MI_' + prefix + '_' + ''.join(ch if ch.isalnum() else '_' for ch in name)
if EAL.does_asset_exist(R2 + 'LV_Plant02/terracotta'):
    pm = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/LV-PLANT-02/manifest.json')))
    for part in pm['parts']:
        if part['base_color_texture']:
            tx = EAL.load_asset(R2 + 'LV_Plant02/' + os.path.splitext(os.path.basename(part['base_color_texture']))[0].replace('-', '_'))
            instance(slot_mi('LVPlant02', part['material']), texpbr, {'Roughness': part['roughness'], 'Metallic': 0.0}, textures={'BaseColorMap': tx})
        else:
            instance(slot_mi('LVPlant02', part['material']), cpbr, {'Metallic': 0.0, 'Roughness': part['roughness']}, {'BaseColor': tuple(part['base_color_linear'][:3]) + (1,)})
# ---------------- FIX-018 KI-CHAIR-02 (materials.json: textures direct, piping constant; roughness .65) ----------------
if EAL.does_asset_exist(R2 + 'KI_Chair02/vinyl'):
    instance('MI_Chair_Walnut', texpbr, {'Roughness': 0.65, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'KI_Chair02/wood_selected_v2')})
    instance('MI_Chair_Rust_Vinyl', texpbr, {'Roughness': 0.65, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'KI_Chair02/vinyl')})
    instance('MI_Chair_Piping', cpbr, {'Metallic': 0.0, 'Roughness': 0.65}, {'BaseColor': (0.25, 0.075, 0.035, 1)})
# ---------------- FIX-019 OF-WAINSCOT-02: painted ivory, texture direct, roughness .80 ----------------
if EAL.does_asset_exist(R2 + 'OF_Wainscot02/painted_ivory'):
    instance('MI_OF02_Painterly_Ivory', texpbr, {'Roughness': 0.80, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'OF_Wainscot02/painted_ivory')})
# ---------------- FIX-007 BA-HAND-TOWEL-RING-02 (assembly.json: texture x multiply) ----------------
if EAL.does_asset_exist(R2 + 'BA_Ring02/terry'):
    ra = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/BA-HAND-TOWEL-RING-02/assembly.json')))
    for name, mt in ra['materials'].items():
        tx = EAL.load_asset(R2 + 'BA_Ring02/' + os.path.splitext(os.path.basename(mt['texture']))[0].replace('-', '_'))
        instance('MI_' + name, texpbr, {'Roughness': mt['roughness'], 'Metallic': mt.get('metallic', 0.0)},
                 {'Tint': tuple(mt['multiply']) + (1,)}, textures={'BaseColorMap': tx})
# ---------------- FIX-012 clear window glass ----------------
# The shared M_Redesign_Glass (lit translucent, two-sided, volumetric translucency lighting) veils the painted view
# cards: on the sunlit south windows the panes pick up so much indirect light they wash the scenery out (verified: with
# only the bedroom panes hidden the view reads in full colour). Per-pixel surface lighting, low opacity and a dark
# tint keep a clear pane with reflections and no milky film. Assigned to all clear windows by rev02_06.
m = material('M_Rev02_WindowGlass'); lit_translucent(m)
m.set_editor_property('two_sided', True)
MEL.connect_material_property(vparam(m, 'BaseColor', (0.015, 0.018, 0.02, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Opacity', 0.1, -400, 120), '', MP.MP_OPACITY)
MEL.connect_material_property(sparam(m, 'Roughness', 0.04, -400, 180), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(sparam(m, 'Specular', 0.5, -400, 240), '', MP.MP_SPECULAR)
MEL.connect_material_property(const(m, 0.0, -400, 300), '', MP.MP_METALLIC)
finish(m, MATS + 'M_Rev02_WindowGlass')
# ---------------- FIX-026 side table (source FBX carries no texture; slot repair) ----------------
_wal = EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/Finishes/MI_Walnut_MutedB')
_di = EAL.load_asset(MATS + 'MI_Rev02_DrawerInterior') if EAL.does_asset_exist(MATS + 'MI_Rev02_DrawerInterior') else tools.create_asset(
    'MI_Rev02_DrawerInterior', MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(_di, _wal.get_editor_property('parent'))
MEL.set_material_instance_texture_parameter_value(_di, 'BaseTexture', MEL.get_material_instance_texture_parameter_value(_wal, 'BaseTexture'))
MEL.set_material_instance_vector_parameter_value(_di, 'Mult', MEL.get_material_instance_vector_parameter_value(_wal, 'Mult'))
MEL.set_material_instance_vector_parameter_value(_di, 'LerpColor', unreal.LinearColor(0.42, 0.26, 0.15, 1))
MEL.set_material_instance_scalar_parameter_value(_di, 'LerpAmount', 0.60)
MEL.set_material_instance_scalar_parameter_value(_di, 'Roughness', 0.86)
EAL.save_asset(MATS + 'MI_Rev02_DrawerInterior')
instance('MI_Rev02_WoodEdges', cpbr, {'Metallic': 0.0, 'Roughness': 0.93}, {'BaseColor': (0.39, 0.27, 0.15, 1)})
instance('MI_Rev02_TableBrass', cpbr, {'Metallic': 0.65, 'Roughness': 0.60}, {'BaseColor': (0.34, 0.22, 0.09, 1)})
# ---------------- FIX-023 BA-TOILET-02 (assembly.json recipes; texture direct, unmultiplied) ----------------
if EAL.does_asset_exist(R2 + 'BA_Toilet02/painted_ivory'):
    instance('MI_Toilet02_Painted_Ivory_Enamel', texpbr, {'Roughness': 0.36, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'BA_Toilet02/painted_ivory')})
    for n, rgb, r, mt in (('Aged_Brass', (0.4, 0.25, 0.11), 0.32, 0.72), ('Trap_Interior', (0.1, 0.087, 0.065), 0.6, 0.0),
                          ('Ivory_Rubber_Bumpers', (0.57, 0.54, 0.46), 0.8, 0.0)):
        instance('MI_Toilet02_' + n, cpbr, {'Metallic': mt, 'Roughness': r}, {'BaseColor': rgb + (1,)})
# ---------------- closet bulb: dim warm incandescent glow (user request, FIX-021 follow-up) ----------------
m = material('M_Rev02_BulbGlow')
MEL.connect_material_property(vparam(m, 'BaseColor', (0.95, 0.78, 0.55, 1), -500, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(const(m, 0.3, -500, 120), '', MP.MP_ROUGHNESS)
glow = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 260)
MEL.connect_material_expressions(vparam(m, 'GlowColor', (1.0, 0.52, 0.18, 1), -500, 220), '', glow, 'A')
MEL.connect_material_expressions(sparam(m, 'GlowStrength', 3.0, -500, 360), '', glow, 'B')
MEL.connect_material_property(glow, '', MP.MP_EMISSIVE_COLOR)
finish(m, MATS + 'M_Rev02_BulbGlow')

# ---------------- FIX-030 fuse-box soot (deferred decal) ----------------
# Subtle feathered charcoal soot on the wallpaper where the (now concealed) wires leave the box. Procedural, in world
# space so no UV basis has to be guessed: CX = plume centre x, BZ = the box edge it starts from, Dir = +1 up / -1 down,
# HW = half width at the base, H = plume length (cm). Coverage widens and fades away from the box edge; anisotropic
# value noise breaks it into soft vertical tongues. Darkens and mattes only (one DBuffer opacity, no normal).
m = material('M_Rev02_FuseSoot')
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property('material_domain', unreal.MaterialDomain.MD_DEFERRED_DECAL)
SOOT = '''
float u = (W.x - CX) / HW;
float v = (W.z - BZ) * Dir / H;
if (v < 0.0 || v > 1.0) return 0.0;
float2 q = float2(W.x * 0.21, W.z * 0.065) + Seed;
float n = 0.0; float amp = 0.5;
for (int k = 0; k < 4; k++) {
  float2 i = floor(q); float2 f = frac(q); f = f * f * (3.0 - 2.0 * f);
  float a = frac(sin(dot(i, float2(127.1, 311.7))) * 43758.5453);
  float b = frac(sin(dot(i + float2(1, 0), float2(127.1, 311.7))) * 43758.5453);
  float c = frac(sin(dot(i + float2(0, 1), float2(127.1, 311.7))) * 43758.5453);
  float d = frac(sin(dot(i + float2(1, 1), float2(127.1, 311.7))) * 43758.5453);
  n += amp * lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y);
  q = q * 2.03 + float2(1.7, 9.2); amp *= 0.5;
}
float w = 0.8 + 0.35 * v;
float side = smoothstep(0.0, 1.0, saturate(1.0 - abs(u) / w));
float fall = pow(saturate(1.0 - v), 1.25);
return saturate(side * fall * saturate(0.25 + 1.4 * (n - 0.25)) * Strength);
'''
op = custom(m, SOOT, ['W', 'CX', 'BZ', 'Dir', 'HW', 'H', 'Seed', 'Strength'], -550, 200)
MEL.connect_material_expressions(MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1100, 100), '', op, 'W')
for k, (n_, d_) in enumerate((('CX', 1106.0), ('BZ', 210.2), ('Dir', 1.0), ('HW', 13.0), ('H', 30.0), ('Seed', 0.0), ('Strength', 0.5))):
    MEL.connect_material_expressions(sparam(m, n_, d_, -1100, 200 + 70 * k), '', op, n_)
MEL.connect_material_property(op, '', MP.MP_OPACITY)
MEL.connect_material_property(vparam(m, 'SootColor', (0.022, 0.018, 0.015, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'SootRoughness', 0.95, -400, 120), '', MP.MP_ROUGHNESS)
finish(m, MATS + 'M_Rev02_FuseSoot')
instance('MI_Rev02_FuseSoot_Above', m, scalars={'CX': 1106.0, 'BZ': 210.2, 'Dir': 1.0, 'HW': 24.0, 'H': 34.0, 'Seed': 3.1, 'Strength': 0.85})
instance('MI_Rev02_FuseSoot_Below', m, scalars={'CX': 1106.0, 'BZ': 152.2, 'Dir': -1.0, 'HW': 18.0, 'H': 24.0, 'Seed': 7.7, 'Strength': 0.6})
# ---------------- FIX-030 LV-FUSE-02 shell (README slot table; textures sRGB albedo, no extra tint) ----------------
if EAL.does_asset_exist(R2 + 'LV_Fuse02/T_Fuse02_Interior'):
    for n, t, mt, r in (('Interior_Dark_Brown', 'T_Fuse02_Interior', 0.10, 0.88), ('Bakelite_Dark_Brown', 'T_Fuse02_Bakelite', 0.06, 0.83),
                        ('Ivory_Ceramic', 'T_Fuse02_AgedCeramic', 0.0, 0.56), ('Fuse02_AgedCloth', 'T_Fuse02_Cloth', 0.0, 0.80)):
        instance('MI_Fuse02_' + n, texpbr, {'Roughness': r, 'Metallic': mt}, textures={'BaseColorMap': EAL.load_asset(R2 + 'LV_Fuse02/' + t)})
    for n, rgb, mt, r in (('Inset_Gasket', (0.075, 0.070, 0.055), 0.0, 0.83), ('Edge_Wear_Ochre', (0.35, 0.235, 0.12), 0.18, 0.80),
                          ('Fuse02_DarkCloth', (0.12, 0.105, 0.08), 0.0, 0.80), ('Fuse02_TarnishedTerminal', (0.22, 0.17, 0.085), 0.55, 0.65)):
        instance('MI_Fuse02_' + n, cpbr, {'Metallic': mt, 'Roughness': r}, {'BaseColor': rgb + (1,)})
# ---------------- FIX-029 BR-CLOSET-LIGHT-01 (README material contract) ----------------
# GlowStrength defaults are the ON values; AFixHimInteractable (GlowActors) scales them by the Light toggle alpha.
for n, rgb, mt, r in (('Closet_AgedBrass', (0.17, 0.105, 0.046), 0.75, 0.40), ('Closet_BrassEdge', (0.31, 0.20, 0.085), 0.72, 0.36),
                      ('Closet_BraidedCord', (0.022, 0.017, 0.012), 0.0, 0.85), ('Closet_Ceramic', (0.50, 0.43, 0.31), 0.0, 0.60),
                      ('Closet_SupportWire', (0.09, 0.075, 0.055), 0.70, 0.48)):
    instance('MI_ClosetLight01_' + n, cpbr, {'Metallic': mt, 'Roughness': r}, {'BaseColor': rgb + (1,)})
m = material('M_Rev02_ClosetFilament')
MEL.connect_material_property(vparam(m, 'BaseColor', (0.25, 0.08, 0.012, 1), -500, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(const(m, 0.10, -500, 80), '', MP.MP_METALLIC)
MEL.connect_material_property(const(m, 0.50, -500, 140), '', MP.MP_ROUGHNESS)
glow = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 260)
MEL.connect_material_expressions(vparam(m, 'GlowColor', (1.0, 0.36, 0.075, 1), -500, 220), '', glow, 'A')
MEL.connect_material_expressions(sparam(m, 'GlowStrength', 6.0, -500, 360), '', glow, 'B')
MEL.connect_material_property(glow, '', MP.MP_EMISSIVE_COLOR)
finish(m, MATS + 'M_Rev02_ClosetFilament')
# clear, lightly warm envelope (lit translucent like the window glass, so the filament reads through it); a faint glow
m = material('M_Rev02_ClosetGlass'); lit_translucent(m)
MEL.connect_material_property(vparam(m, 'BaseColor', (0.94, 0.86, 0.70, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Opacity', 0.18, -400, 120), '', MP.MP_OPACITY)
MEL.connect_material_property(sparam(m, 'Roughness', 0.16, -400, 180), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(sparam(m, 'Specular', 0.5, -400, 240), '', MP.MP_SPECULAR)
MEL.connect_material_property(const(m, 0.0, -400, 300), '', MP.MP_METALLIC)
glow = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 420)
MEL.connect_material_expressions(vparam(m, 'GlowColor', (1.0, 0.62, 0.30, 1), -500, 400), '', glow, 'A')
MEL.connect_material_expressions(sparam(m, 'GlowStrength', 0.25, -500, 520), '', glow, 'B')
MEL.connect_material_property(glow, '', MP.MP_EMISSIVE_COLOR)
finish(m, MATS + 'M_Rev02_ClosetGlass')
# ---------------- FIX-031/032 LV-TV-02 (README slot table) + LV-TV-01 stand/doors (LV-TV-01 README / build_tv.py) ----------------
if EAL.does_asset_exist(R2 + 'LV_TV02/T_TV02_Walnut'):
    _w2 = EAL.load_asset(R2 + 'LV_TV02/T_TV02_Walnut')
    instance('MI_TV02_WalnutVeneer', texpbr, {'Roughness': 0.55, 'Metallic': 0.0}, textures={'BaseColorMap': _w2})
    instance('MI_TV02_EndGrainTrim', texpbr, {'Roughness': 0.59, 'Metallic': 0.0}, textures={'BaseColorMap': _w2})
    instance('MI_TV02_SpeakerCloth', texpbr, {'Roughness': 0.95, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'LV_TV02/T_TV02_SpeakerWeave')})
    for n, rgb, r, mt in (('Bakelite', (0.029, 0.026, 0.022), 0.50, 0.0), ('CRTSeal', (0.012, 0.015, 0.012), 0.85, 0.0),
                          ('AgedChampagneMetal', (0.39, 0.30, 0.17), 0.40, 0.65), ('DialIvory', (0.64, 0.60, 0.46), 0.58, 0.0),
                          ('BackBoard', (0.065, 0.044, 0.027), 0.90, 0.0), ('VentDark', (0.009, 0.010, 0.008), 0.95, 0.0)):
        instance('MI_TV02_' + n, cpbr, {'Metallic': mt, 'Roughness': r}, {'BaseColor': rgb + (1,)})
    # original stand + cabinet doors: painted walnut = image x linear (0.25,0.23,0.14), roughness .78 (build_tv.py)
    instance('MI_TV01_Walnut_Painted', texpbr, {'Roughness': 0.78, 'Metallic': 0.0}, {'Tint': (0.25, 0.23, 0.14, 1)},
             textures={'BaseColorMap': EAL.load_asset(R2 + 'LV_TV02/T_TV01_WalnutPainted')})
    for n, rgb, r, mt in (('Walnut_Shadow', (0.19, 0.075, 0.035), 0.65, 0.0), ('Warm_Wood_Trim', (0.18, 0.085, 0.03), 0.65, 0.0),
                          ('Aged_Brass', (0.56, 0.35, 0.10), 0.38, 0.6), ('Back_Panel', (0.14, 0.065, 0.035), 0.65, 0.0)):
        instance('MI_TV01_' + n, cpbr, {'Metallic': mt, 'Roughness': r}, {'BaseColor': rgb + (1,)})
    # CRT: one opaque glass; GlowStrength (ON value; the TV interactable fades it with its Light toggle) drives a soft
    # warm-white radial phosphor ramp on the screen UV (centre (1,.90,.74) inside r .10, edge (.16,.19,.15) by r .65).
    m = material('M_Rev02_TVScreen')
    MEL.connect_material_property(vparam(m, 'BaseColor', (0.035, 0.048, 0.042, 1), -500, 0), '', MP.MP_BASE_COLOR)
    MEL.connect_material_property(const(m, 0.08, -500, 80), '', MP.MP_METALLIC)
    MEL.connect_material_property(const(m, 0.19, -500, 140), '', MP.MP_ROUGHNESS)
    ramp = custom(m, 'float r = distance(UV, float2(0.5, 0.5)); float t = smoothstep(0.10, 0.65, r); return lerp(C, E, t) * G;',
                  ['UV', 'C', 'E', 'G'], -250, 300, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    MEL.connect_material_expressions(MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -700, 260), '', ramp, 'UV')
    MEL.connect_material_expressions(vparam(m, 'CentreColor', (1.0, 0.90, 0.74, 1), -700, 330), '', ramp, 'C')
    MEL.connect_material_expressions(vparam(m, 'EdgeColor', (0.16, 0.19, 0.15, 1), -700, 450), '', ramp, 'E')
    MEL.connect_material_expressions(sparam(m, 'GlowStrength', 0.7, -700, 570), '', ramp, 'G')
    MEL.connect_material_property(ramp, '', MP.MP_EMISSIVE_COLOR)
    finish(m, MATS + 'M_Rev02_TVScreen')
    # in-room strength: README preview .7 read as a pale wash at the room's exposure; .3 keeps it restrained (paired captures)
    instance('MI_TV02_Screen', m, {'GlowStrength': 0.3})
# ---------------- FIX-035 dining-table apron: same wood as the top, grain along the rails ----------------
# KI-TABLE-01 apron UVs (Table_Sage_Painted): rail length runs along V (~4.99 m per UV on the long rails, ~2.35 m on the
# end rails) and height along U (~0.35 m per UV); the top's grain runs along U at ~2.87 m per UV. Swap U/V and rescale
# so the wood grain runs lengthwise at about the top's density (compromise 1.5 for long/end rails).
m = material('M_Rev02_TexPBR_UV')
uvx = custom(m, 'float2 q = lerp(UV, UV.yx, Swap); return q * float2(SU, SV);', ['UV', 'Swap', 'SU', 'SV'], -1000, 0,
             out=unreal.CustomMaterialOutputType.CMOT_FLOAT2)
MEL.connect_material_expressions(MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1300, 0), '', uvx, 'UV')
for k_, (n_, d_) in enumerate((('Swap', 1.0), ('SU', 1.5), ('SV', 0.215))):
    MEL.connect_material_expressions(sparam(m, n_, d_, -1300, 80 + 70 * k_), '', uvx, n_)
t = tex(m, EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/KI_Table/table-wood-v2'), -700, 0, param='BaseColorMap', linear=False)
MEL.connect_material_expressions(uvx, '', t, 'UVs')
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 0)
MEL.connect_material_expressions(t, 'RGB', mul, 'A')
MEL.connect_material_expressions(vparam(m, 'Tint', (1, 1, 1, 1), -700, 250), '', mul, 'B')
MEL.connect_material_property(mul, '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Roughness', 0.75, -400, 200), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(sparam(m, 'Metallic', 0.0, -400, 260), '', MP.MP_METALLIC)
finish(m, MATS + 'M_Rev02_TexPBR_UV')
# KI-TABLE-02 (UV-only source fix) gives the apron continuous lengthwise boards at the top's density on IDENTITY UV0:
# the interim swap/rescale is retired (Swap 0, scale 1); texture, tint and roughness unchanged.
instance('MI_Table_ApronWood', EAL.load_asset(MATS + 'M_Rev02_TexPBR_UV'), {'Swap': 0.0, 'SU': 1.0, 'SV': 1.0, 'Roughness': 0.75})
# ---------------- FIX-037 untextured furniture (Redesign UV finish family, same as FIX-028 nightstands) ----------------
_uvf = EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/Finishes/M_Redesign_UVFinish')
def uvfinish(name, texture, mult, lerp_color, lerp_amount, rough):
    path = MATS + name
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset(
        name, MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, _uvf)
    MEL.set_material_instance_texture_parameter_value(mi, 'BaseTexture', EAL.load_asset(texture))
    MEL.set_material_instance_vector_parameter_value(mi, 'Mult', unreal.LinearColor(mult, mult, mult, 1))
    MEL.set_material_instance_vector_parameter_value(mi, 'LerpColor', unreal.LinearColor(*lerp_color, 1))
    MEL.set_material_instance_scalar_parameter_value(mi, 'LerpAmount', lerp_amount)
    MEL.set_material_instance_scalar_parameter_value(mi, 'Roughness', rough)
    EAL.save_asset(path)
# HA-CONSOLE-01 README: walnut-b chosen (plain colour image, no adjustment), roughness .84
uvfinish('MI_Rev02_ConsoleWalnutB', '/Game/ICanFixHim/Environment/Redesign/HA_CONSOLE/walnut-b', 1.0, (0.3, 0.24, 0.19), 0.0, 0.84)
# white painted bench / plant stand (user: keep them white): ivory paint over a faint walnut grain, matte
uvfinish('MI_Rev02_WhitePaintWood', '/Game/ICanFixHim/Environment/Redesign/Finishes/Textures/T_Walnut_MutedB', 1.35, (0.80, 0.78, 0.72), 0.86, 0.72)
# ---------------- FIX-033/034/036 CABINET-JOINERY-02 (material-contract.json; textures sRGB, tint baked -> unity) ----------------
if EAL.does_asset_exist(R2 + 'Joinery02/T_Joinery_Sage'):
    for n, t, r in (('Sage', 'T_Joinery_Sage', 0.78), ('Ivory', 'T_Joinery_Ivory', 0.72), ('Interior', 'T_Joinery_Interior', 0.80),
                    ('ToeDark', 'T_Joinery_ToeDark', 0.78)):
        instance('MI_Joinery_' + n, texpbr, {'Roughness': r, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, textures={'BaseColorMap': EAL.load_asset(R2 + 'Joinery02/' + t)})
    instance('MI_Joinery_AgedBrass', cpbr, {'Metallic': 0.65, 'Roughness': 0.42}, {'BaseColor': (0.32, 0.22, 0.085, 1)})
    instance('MI_Joinery_KnobIvory', cpbr, {'Metallic': 0.0, 'Roughness': 0.32}, {'BaseColor': (0.63, 0.59, 0.48, 1)})
# ---------------- FIX-038 BA-TILE-GLAZE-02 pink glaze (README): installed pink kept, subtle glaze normal/roughness ----------------
# The eight installed Pink_glaze_0x slots were flat FBX Phong (0.65,0.34,0.37); candidate-b was never bound. Colour =
# installed pink x a restrained per-slot tint (half the BA-TILE-01 palette's relative spread, so the 8-slot mean stays
# the installed pink) x a restrained candidate-b luminance variation normalised by its measured mean (linear lum
# .3183), so each slot's mean stays its pink. Normal: DirectX tangent-space glaze map on the existing UV0 (UE is DX: no
# green flip), strength 1. Roughness: map R (.3745-.4663) + bias. No height/displacement; grout/cap untouched.
if EAL.does_asset_exist(R2 + 'BA_TileGlaze02/T_BathGlaze_NormalDX'):
    m = material('M_Rev02_TileGlaze')
    cb = tex(m, EAL.load_asset(R2 + 'BA_TileGlaze02/T_BathTile_GlazeB'), -1000, 0, param='GlazeColour', linear=False)
    col = custom(m, 'float l = dot(C, float3(0.2126, 0.7152, 0.0722)) / MeanLum; return Pink * Tint * lerp(1.0, l, Var);',
                 ['C', 'Pink', 'Tint', 'MeanLum', 'Var'], -500, 0, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    MEL.connect_material_expressions(cb, 'RGB', col, 'C')
    MEL.connect_material_expressions(vparam(m, 'Pink', (0.65, 0.34, 0.37, 1), -1000, 250), '', col, 'Pink')
    MEL.connect_material_expressions(vparam(m, 'Tint', (1, 1, 1, 1), -1000, 380), '', col, 'Tint')
    MEL.connect_material_expressions(sparam(m, 'MeanLum', 0.3183, -1000, 500), '', col, 'MeanLum')
    MEL.connect_material_expressions(sparam(m, 'Var', 0.3, -1000, 570), '', col, 'Var')
    MEL.connect_material_property(col, '', MP.MP_BASE_COLOR)
    nm = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, 650)
    nm.set_editor_property('parameter_name', 'GlazeNormal'); nm.set_editor_property('texture', EAL.load_asset(R2 + 'BA_TileGlaze02/T_BathGlaze_NormalDX'))
    nm.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    MEL.connect_material_property(nm, 'RGB', MP.MP_NORMAL)
    rg = tex(m, EAL.load_asset(R2 + 'BA_TileGlaze02/T_BathGlaze_Roughness'), -1000, 800, param='GlazeRoughness', linear=True)
    rgo = custom(m, 'return saturate(R + Bias);', ['R', 'Bias'], -500, 800)
    MEL.connect_material_expressions(rg, 'R', rgo, 'R'); MEL.connect_material_expressions(sparam(m, 'RoughnessBias', 0.0, -1000, 950), '', rgo, 'Bias')
    MEL.connect_material_property(rgo, '', MP.MP_ROUGHNESS)
    MEL.connect_material_property(const(m, 0.0, -500, 950), '', MP.MP_METALLIC)
    finish(m, MATS + 'M_Rev02_TileGlaze')
    _pal = [(.92, .48, .49), (.78, .37, .41), (.90, .50, .48), (.75, .36, .40), (.86, .43, .47), (.89, .44, .42), (.80, .42, .46), (.92, .52, .51)]
    _mean = [sum(c[k] for c in _pal) / 8 for k in range(3)]
    for i, c in enumerate(_pal):
        tint = tuple(1 + 0.5 * (c[k] / _mean[k] - 1) for k in range(3))
        instance('MI_Rev02_PinkGlaze_%02d' % i, m, {}, {'Tint': tint + (1,)})
# FIX-037 follow-up: white bench / plant stand read nearly flat. Same mean colour as MI_Rev02_WhitePaintWood
# (0.713,0.679,0.622 = 14% walnut x1.35 + 86% ivory paint), but the grain now modulates luminance around that mean
# (walnut-muted-b mean linear lum .0613) so it reads at play distance without browning, plus a small matching
# roughness variation (grain slightly rougher).
m = material('M_Rev02_PaintedGrain')
g = tex(m, EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/Finishes/Textures/T_Walnut_MutedB'), -1000, 0, param='Grain', linear=False)
col = custom(m, 'float l = dot(C, float3(0.2126, 0.7152, 0.0722)) / MeanLum; return Paint * lerp(1.0, l, Var);',
             ['C', 'Paint', 'MeanLum', 'Var'], -500, 0, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
MEL.connect_material_expressions(g, 'RGB', col, 'C')
MEL.connect_material_expressions(vparam(m, 'Paint', (0.713, 0.679, 0.622, 1), -1000, 250), '', col, 'Paint')
MEL.connect_material_expressions(sparam(m, 'MeanLum', 0.0613, -1000, 380), '', col, 'MeanLum')
MEL.connect_material_expressions(sparam(m, 'Var', 0.22, -1000, 450), '', col, 'Var')
MEL.connect_material_property(col, '', MP.MP_BASE_COLOR)
rgh = custom(m, 'float l = dot(C, float3(0.2126, 0.7152, 0.0722)) / MeanLum; return saturate(R0 - RV * (l - 1.0));',
             ['C', 'R0', 'RV', 'MeanLum'], -500, 300)
MEL.connect_material_expressions(g, 'RGB', rgh, 'C')
MEL.connect_material_expressions(sparam(m, 'Roughness', 0.72, -1000, 560), '', rgh, 'R0')
MEL.connect_material_expressions(sparam(m, 'RoughVar', 0.10, -1000, 630), '', rgh, 'RV')
MEL.connect_material_expressions(sparam(m, 'MeanLum2', 0.0613, -1000, 700), '', rgh, 'MeanLum')
MEL.connect_material_property(rgh, '', MP.MP_ROUGHNESS)
finish(m, MATS + 'M_Rev02_PaintedGrain')
instance('MI_Rev02_WhitePaintGrain', EAL.load_asset(MATS + 'M_Rev02_PaintedGrain'), {'Var': 0.22, 'RoughVar': 0.10})
# ---------------- batch 2: aged chrome hardware and aged mirror glass ----------------
# Shared world-space value noise (low frequency) for restrained roughness/tint variation; no textures needed.
NOISE = """
float2 q = (W.xy + W.z * 0.37) * Freq; float n = 0.0; float amp = 0.5;
for (int k = 0; k < 3; k++) {
  float2 i = floor(q); float2 f = frac(q); f = f * f * (3.0 - 2.0 * f);
  float a = frac(sin(dot(i, float2(127.1, 311.7))) * 43758.5453);
  float b = frac(sin(dot(i + float2(1, 0), float2(127.1, 311.7))) * 43758.5453);
  float c = frac(sin(dot(i + float2(0, 1), float2(127.1, 311.7))) * 43758.5453);
  float d = frac(sin(dot(i + float2(1, 1), float2(127.1, 311.7))) * 43758.5453);
  n += amp * lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y); q = q * 2.07 + 3.1; amp *= 0.5;
}
return n / 0.875;
"""
def aged_metal(name, base, rough, rvar, tvar, freq, metallic=1.0):
    m = material(name)
    nz = custom(m, NOISE, ['W', 'Freq'], -900, 300)
    MEL.connect_material_expressions(MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1200, 300), '', nz, 'W')
    MEL.connect_material_expressions(sparam(m, 'NoiseFreq', freq, -1200, 400), '', nz, 'Freq')
    col = custom(m, 'return Base * (1.0 + TVar * (N - 0.5));', ['Base', 'TVar', 'N'], -500, 0, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    MEL.connect_material_expressions(vparam(m, 'BaseColor', base + (1,), -900, 0), '', col, 'Base')
    MEL.connect_material_expressions(sparam(m, 'TintVar', tvar, -900, 120), '', col, 'TVar')
    MEL.connect_material_expressions(nz, '', col, 'N')
    MEL.connect_material_property(col, '', MP.MP_BASE_COLOR)
    rg = custom(m, 'return saturate(R0 + RV * (N - 0.5));', ['R0', 'RV', 'N'], -500, 300)
    MEL.connect_material_expressions(sparam(m, 'Roughness', rough, -900, 480), '', rg, 'R0')
    MEL.connect_material_expressions(sparam(m, 'RoughVar', rvar, -900, 550), '', rg, 'RV')
    MEL.connect_material_expressions(nz, '', rg, 'N')
    MEL.connect_material_property(rg, '', MP.MP_ROUGHNESS)
    MEL.connect_material_property(sparam(m, 'Metallic', metallic, -500, 500), '', MP.MP_METALLIC)
    finish(m, MATS + name)
# aged chrome: slightly warm nickel-chrome, restrained roughness breakup (fridge/sink/tap hardware)
aged_metal('M_Rev02_AgedChrome', (0.62, 0.60, 0.56), 0.24, 0.16, 0.10, 0.35)
# aged mirror: silvered glass with Lumen's existing reflections softened by roughness (~.22) and a faint warm,
# uneven tint (old silvering); low-frequency variation so the blur reads as age, not noise
aged_metal('M_Rev02_MirrorAged', (0.80, 0.77, 0.70), 0.30, 0.08, 0.08, 0.08)   # .30: user wants an indistinct low-pass room reflection (do not sharpen)
# ---------------- batch 2: wide exterior view cards (no exposed card edges at oblique/downward window views) ----------------
# Same unlit look and the controller-driven 'WindowBrightness' x 'BrightnessScale' as M_Redesign_WindowView. The card is
# enlarged K-fold (CoverageU/V) by rev02_06; UVs are remapped (uv-0.5)*K+0.5 so the painted view keeps its exact world size and
# position, and T_WindowView's mirror addressing fills only the outer band that oblique/downward views can reach.
_tv = EAL.load_asset('/Game/ICanFixHim/Materials/Environment/T_WindowView')
_tv.set_editor_property('address_x', unreal.TextureAddress.TA_MIRROR); _tv.set_editor_property('address_y', unreal.TextureAddress.TA_MIRROR)
EAL.save_loaded_asset(_tv, False)
m = material('M_Rev02_WindowViewWide')
m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
uvk = custom(m, 'return (UV - 0.5) * float2(KU, KV) + 0.5;', ['UV', 'KU', 'KV'], -900, 0, out=unreal.CustomMaterialOutputType.CMOT_FLOAT2)
MEL.connect_material_expressions(MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1200, 0), '', uvk, 'UV')
MEL.connect_material_expressions(sparam(m, 'CoverageU', 1.4, -1200, 80), '', uvk, 'KU')
MEL.connect_material_expressions(sparam(m, 'CoverageV', 1.6, -1200, 150), '', uvk, 'KV')
smp = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -600, 0); smp.set_editor_property('texture', _tv)
MEL.connect_material_expressions(uvk, '', smp, 'UVs')
br = custom(m, 'return C * WB * BS;', ['C', 'WB', 'BS'], -300, 0, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
MEL.connect_material_expressions(smp, 'RGB', br, 'C')
MEL.connect_material_expressions(sparam(m, 'WindowBrightness', 12.0, -600, 250), '', br, 'WB')
MEL.connect_material_expressions(sparam(m, 'BrightnessScale', 0.0750, -600, 320), '', br, 'BS')
MEL.connect_material_property(br, '', MP.MP_EMISSIVE_COLOR)
finish(m, MATS + 'M_Rev02_WindowViewWide')
_old = EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/Finishes/MI_WindowView')
instance('MI_Rev02_WindowViewWide', m, {'WindowBrightness': 12.0, 'BrightnessScale': MEL.get_material_instance_scalar_parameter_value(_old, 'BrightnessScale'),
                                        'CoverageU': 1.4, 'CoverageV': 1.6})
# ---------------- batch 2 sources: LV-BOOK-03 plant, LV-SOFA-03 throw, sink water (authored reveal) ----------------
# Pothos leaves: thin single-sheet leaves need a two-sided lit material (README: keep double-sided in engine).
m = material('M_Rev02_LeafTwoSided'); m.set_editor_property('two_sided', True)
t = tex(m, EAL.load_asset(R2 + 'Room03/pothos-leaf'), -700, 0, param='BaseColorMap', linear=False)
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 0)
MEL.connect_material_expressions(t, 'RGB', mul, 'A')
MEL.connect_material_expressions(vparam(m, 'Tint', (1, 1, 1, 1), -700, 250), '', mul, 'B')
MEL.connect_material_property(mul, '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Roughness', 0.55, -400, 200), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.0, -400, 260), '', MP.MP_METALLIC)
finish(m, MATS + 'M_Rev02_LeafTwoSided')
leaf = EAL.load_asset(MATS + 'M_Rev02_LeafTwoSided')
instance('MI_Plant03_Leaf', leaf, {'Roughness': 0.55}, textures={'BaseColorMap': EAL.load_asset(R2 + 'Room03/pothos-leaf')})
instance('MI_Plant03_LeafLight', leaf, {'Roughness': 0.5}, textures={'BaseColorMap': EAL.load_asset(R2 + 'Room03/pothos-leaf_ncl1_1')})
# pot: textured terracotta ceramic (the imported graph binds terracotta; built as PBR like the other kits), glaze band/soil
instance('MI_Plant03_CeramicPot', texpbr, {'Roughness': 0.62, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'Room03/terracotta')})
instance('MI_Plant03_PotBotanical', cpbr, {'Metallic': 0.0, 'Roughness': 0.45}, {'BaseColor': (0.42, 0.24, 0.12, 1)})
instance('MI_Plant03_PotSoil', cpbr, {'Metallic': 0.0, 'Roughness': 0.95}, {'BaseColor': (0.10, 0.07, 0.035, 1)})

# LV-SOFA-03 woven throw: throw-wool x linear (.58,.49,.36), roughness .90 and a fine over-under weave bump (procedural
# tangent normal on the throw's UVs; WeaveFreq = threads per UV unit, WeaveStrength small so it reads as cloth, not ribs).
m = material('M_Rev02_TexPBR_Weave')
# LV-SOFA-03 (UV0 fixed at source: the throw shares the joined 'UVMap'): throw-wool on UV0 x UVScale, multiplied by Tint,
# with a fine procedural over-under weave normal on the same UVs (WeaveFreq = threads per UV unit).
uv0 = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1500, 0)
uvs = custom(m, 'return UV * K;', ['UV', 'K'], -1200, 0, out=unreal.CustomMaterialOutputType.CMOT_FLOAT2)
assert MEL.connect_material_expressions(uv0, '', uvs, 'UV')
assert MEL.connect_material_expressions(sparam(m, 'UVScale', 1.0, -1500, 100), '', uvs, 'K')
t = tex(m, EAL.load_asset(R2 + 'LV_Sofa02/throw_wool'), -900, 0, param='BaseColorMap', linear=False)
assert MEL.connect_material_expressions(uvs, '', t, 'UVs')
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -500, 0)
assert MEL.connect_material_expressions(t, 'RGB', mul, 'A')
assert MEL.connect_material_expressions(vparam(m, 'Tint', (1, 1, 1, 1), -900, 250), '', mul, 'B')
MEL.connect_material_property(mul, '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Roughness', 0.9, -400, 200), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.0, -400, 260), '', MP.MP_METALLIC)
wv = custom(m, 'float2 p = UV * F * 6.28318;\n'
               'float over = sign(sin(p.y * 0.5)) * sign(sin(p.x * 0.5));\n'
               'float dx = cos(p.x) * (0.5 + 0.5 * over);\nfloat dy = cos(p.y) * (0.5 - 0.5 * over);\n'
               'return normalize(float3(dx * S, dy * S, 1.0));',
            ['UV', 'F', 'S'], -800, 500, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
assert MEL.connect_material_expressions(uvs, '', wv, 'UV')
assert MEL.connect_material_expressions(sparam(m, 'WeaveFreq', 120.0, -1300, 600), '', wv, 'F')
assert MEL.connect_material_expressions(sparam(m, 'WeaveStrength', 0.2, -1300, 680), '', wv, 'S')
MEL.connect_material_property(wv, '', MP.MP_NORMAL)
finish(m, MATS + 'M_Rev02_TexPBR_Weave')
instance('MI_Sofa03_WovenThrow', EAL.load_asset(MATS + 'M_Rev02_TexPBR_Weave'), {'Roughness': 0.90, 'WeaveFreq': 120.0, 'WeaveStrength': 0.2, 'UVScale': 1.0},
         {'Tint': (0.58, 0.49, 0.36, 1)}, {'BaseColorMap': EAL.load_asset(R2 + 'LV_Sofa02/throw_wool')})

# Sink tap water (batch 2): authored reveal (FixHimInteractable bUseAuthoredRevealMaterial) - the stream keeps this lit
# translucent water instead of the generic tinted reveal; 'RevealAlpha' (0..1) is driven by the tap's toggle fade.
m = material('M_Rev02_WaterStream'); lit_translucent(m)
# Review: a uniform cylinder read as a straight glass rod. Now: falling streaks (value noise panned down), Fresnel-weighted
# opacity (thin bright edges, clearer core), a streak-driven normal breakup and a small time wobble that grows below the
# spout (world position offset, max ~WobbleAmp cm), so the column shimmers instead of standing still.
uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1300, 200)
tm = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -1300, 300)
fr = MEL.create_material_expression(m, unreal.MaterialExpressionFresnel, -1300, 700)
NOISE = ('float vn(float2 q) { float2 i = floor(q); float2 f = frac(q); f = f * f * (3.0 - 2.0 * f);\n'
         ' float a = frac(sin(dot(i, float2(127.1, 311.7))) * 43758.5); float b = frac(sin(dot(i + float2(1, 0), float2(127.1, 311.7))) * 43758.5);\n'
         ' float c = frac(sin(dot(i + float2(0, 1), float2(127.1, 311.7))) * 43758.5); float d = frac(sin(dot(i + float2(1, 1), float2(127.1, 311.7))) * 43758.5);\n'
         ' return lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y); }\n')
st = custom(m, 'float2 q = float2(UV.x * 8.0, UV.y * 7.0 - T * Speed);\n'
               'float n = frac(sin(dot(floor(q), float2(127.1, 311.7))) * 43758.5);\n'
               'float2 f = frac(q); f = f * f * (3.0 - 2.0 * f);\n'
               'float n1 = lerp(lerp(frac(sin(dot(floor(q), float2(127.1,311.7)))*43758.5), frac(sin(dot(floor(q)+float2(1,0), float2(127.1,311.7)))*43758.5), f.x),\n'
               '                lerp(frac(sin(dot(floor(q)+float2(0,1), float2(127.1,311.7)))*43758.5), frac(sin(dot(floor(q)+float2(1,1), float2(127.1,311.7)))*43758.5), f.x), f.y);\n'
               'return saturate((Base * (0.45 + 1.1 * F) + Streak * (n1 - 0.5)) * RevealAlpha);',
            ['UV', 'T', 'Speed', 'Base', 'Streak', 'RevealAlpha', 'F'], -700, 200)
MEL.connect_material_expressions(uv, '', st, 'UV'); MEL.connect_material_expressions(tm, '', st, 'T'); MEL.connect_material_expressions(fr, '', st, 'F')
spd = sparam(m, 'Speed', 2.2, -1300, 400)
MEL.connect_material_expressions(spd, '', st, 'Speed')
MEL.connect_material_expressions(sparam(m, 'Opacity', 0.42, -1300, 470), '', st, 'Base')
MEL.connect_material_expressions(sparam(m, 'Streak', 0.35, -1300, 540), '', st, 'Streak')
MEL.connect_material_expressions(sparam(m, 'RevealAlpha', 1.0, -1300, 610), '', st, 'RevealAlpha')
MEL.connect_material_property(st, '', MP.MP_OPACITY)
nb = custom(m, 'float2 q = float2(UV.x * 8.0, UV.y * 7.0 - T * Speed);\n'
               'float s = sin(q.x * 6.2831 + sin(q.y * 1.7) * 2.0);\n'
               'return normalize(float3(s * S, cos(q.y * 2.3) * S * 0.5, 1.0));',
            ['UV', 'T', 'Speed', 'S'], -700, 800, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
MEL.connect_material_expressions(uv, '', nb, 'UV'); MEL.connect_material_expressions(tm, '', nb, 'T'); MEL.connect_material_expressions(spd, '', nb, 'Speed')
MEL.connect_material_expressions(sparam(m, 'NormalBreakup', 0.45, -1300, 900), '', nb, 'S')
MEL.connect_material_property(nb, '', MP.MP_NORMAL)
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1300, 1000)
wo = custom(m, 'float k = saturate((TopZ - WP.z) / 40.0);\n'
               'return float3(sin(WP.z * 0.45 + T * 13.0) * A * k, cos(WP.z * 0.37 + T * 11.0) * A * k, 0.0);',
            ['WP', 'T', 'A', 'TopZ'], -700, 1000, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
MEL.connect_material_expressions(wp, '', wo, 'WP'); MEL.connect_material_expressions(tm, '', wo, 'T')
MEL.connect_material_expressions(sparam(m, 'WobbleAmp', 0.12, -1300, 1100), '', wo, 'A')
MEL.connect_material_expressions(sparam(m, 'TopZ', 123.0, -1300, 1170), '', wo, 'TopZ')
MEL.connect_material_property(wo, '', MP.MP_WORLD_POSITION_OFFSET)
MEL.connect_material_property(vparam(m, 'BaseColor', (0.05, 0.065, 0.07, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(const(m, 0.03, -400, 320), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.6, -400, 380), '', MP.MP_SPECULAR)
MEL.connect_material_property(const(m, 0.0, -400, 440), '', MP.MP_METALLIC)
finish(m, MATS + 'M_Rev02_WaterStream')
instance('MI_Rev02_TapStream', EAL.load_asset(MATS + 'M_Rev02_WaterStream'), {'Opacity': 0.55, 'Streak': 0.55, 'Speed': 2.6, 'NormalBreakup': 0.45, 'WobbleAmp': 0.12, 'TopZ': 123.0},
         {'BaseColor': (0.16, 0.2, 0.22, 1)})
# splash where the stream lands: two continuously expanding rings (time-driven), faded by RevealAlpha
m = material('M_Rev02_TapSplash'); lit_translucent(m)
uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1100, 200)
tm = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -1100, 300)
ring = custom(m, 'float d = length(UV - 0.5) * 2.0; float o = 0.0;\n'
                 'for (int k = 0; k < 3; k++) { float ph = frac(T * Rate + k / 3.0);\n'
                 '  float r = lerp(0.10, 0.95, ph); float w = lerp(0.10, 0.22, ph);\n'
                 '  o += saturate(1.0 - abs(d - r) / w) * (1.0 - ph) * (1.0 - ph); }\n'
                 'o += saturate(1.0 - d / 0.38) * 0.75;\n'
                 'return saturate(o * step(d, 1.0) * Strength * RevealAlpha);',
              ['UV', 'T', 'Rate', 'Strength', 'RevealAlpha'], -600, 200)
MEL.connect_material_expressions(uv, '', ring, 'UV'); MEL.connect_material_expressions(tm, '', ring, 'T')
MEL.connect_material_expressions(sparam(m, 'Rate', 2.6, -1100, 400), '', ring, 'Rate')
MEL.connect_material_expressions(sparam(m, 'Strength', 0.55, -1100, 470), '', ring, 'Strength')
MEL.connect_material_expressions(sparam(m, 'RevealAlpha', 1.0, -1100, 540), '', ring, 'RevealAlpha')
MEL.connect_material_property(ring, '', MP.MP_OPACITY)
spc = vparam(m, 'BaseColor', (0.30, 0.33, 0.35, 1), -400, 0)
MEL.connect_material_property(spc, '', MP.MP_BASE_COLOR)
gl = custom(m, 'return C * O * Glow;', ['C', 'O', 'Glow'], -300, 500, out=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
MEL.connect_material_expressions(spc, '', gl, 'C'); MEL.connect_material_expressions(ring, '', gl, 'O')
MEL.connect_material_expressions(sparam(m, 'Glow', 0.6, -600, 560), '', gl, 'Glow')
MEL.connect_material_property(gl, '', MP.MP_EMISSIVE_COLOR)
MEL.connect_material_property(const(m, 0.03, -400, 300), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.8, -400, 360), '', MP.MP_SPECULAR)
finish(m, MATS + 'M_Rev02_TapSplash')
instance('MI_Rev02_TapSplash', EAL.load_asset(MATS + 'M_Rev02_TapSplash'), {'Strength': 1.0, 'Rate': 2.4, 'Glow': 0.6}, {'BaseColor': (0.8, 0.85, 0.9, 1)})
# ---------------- batch 2 leak puddle: dielectric wet film ----------------
# The roughness-only DBuffer decal gave no visible sheen. A thin lit film on the floor carries the actual reflection:
# masked + DitherTemporalAA (soft mask edges, partial coverage lets the tile show through), near-mirror roughness, dark
# water colour. Its UVs come from world XY so it registers exactly with the stain decal's mask basis (README: image
# right = +X, image up = -Y): u = (x - CX)/SX + .5, v = (y - CY)/SY + .5, with FlipU/FlipV for calibration.
m = material('M_Rev02_PuddleFilm')
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
m.set_editor_property('dither_opacity_mask', True)
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1500, 200)
wuv = custom(m, 'float2 uv = float2((WP.x - CX) / SX, (WP.y - CY) / SY) + 0.5;\n'
                'return float2(lerp(uv.x, 1.0 - uv.x, FU), lerp(uv.y, 1.0 - uv.y, FV));',
             ['WP', 'CX', 'CY', 'SX', 'SY', 'FU', 'FV'], -1200, 200, out=unreal.CustomMaterialOutputType.CMOT_FLOAT2)
MEL.connect_material_expressions(wp, '', wuv, 'WP')
for k, (n_, v) in enumerate((('CX', 206.7), ('CY', 75.9), ('SX', 68.2221), ('SY', 86.1652), ('FlipU', 0.0), ('FlipV', 0.0))):
    MEL.connect_material_expressions(sparam(m, n_, v, -1500, 320 + 70 * k), '', wuv, {'FlipU': 'FU', 'FlipV': 'FV'}.get(n_, n_))
mask = tex(m, EAL.load_asset(R2 + 'KI_Leak02/T_Leak_Puddle_Mask'), -900, 200, param='PuddleMask')
MEL.connect_material_expressions(wuv, '', mask, 'UVs')
# soft wet edge: 5x5 box blur of the mask alpha (R = UV step), eased; Strength caps coverage so the tile stays readable
tob = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -900, 500)
tob.set_editor_property('parameter_name', 'PuddleMaskObj'); tob.set_editor_property('texture', EAL.load_asset(R2 + 'KI_Leak02/T_Leak_Puddle_Mask'))
op = custom(m, 'float a = 0.0;\nfor (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++)\n'
               '  a += Texture2DSample(Tex, TexSampler, U + float2(i, j) * R).a;\na /= 25.0;\n'
               'float inside = (U.x > 0 && U.x < 1 && U.y > 0 && U.y < 1) ? 1.0 : 0.0;\n'
               'return saturate(smoothstep(0.05, 0.95, a) * Strength) * inside;', ['Tex', 'U', 'R', 'Strength'], -550, 200)
MEL.connect_material_expressions(tob, '', op, 'Tex'); MEL.connect_material_expressions(wuv, '', op, 'U')
MEL.connect_material_expressions(sparam(m, 'EdgeBlur', 0.014, -900, 700), '', op, 'R')
MEL.connect_material_expressions(sparam(m, 'Strength', 0.42, -900, 800), '', op, 'Strength')
MEL.connect_material_property(op, '', MP.MP_OPACITY_MASK)
MEL.connect_material_property(vparam(m, 'WaterColor', (0.10, 0.085, 0.07, 1), -400, 0), '', MP.MP_BASE_COLOR)
MEL.connect_material_property(sparam(m, 'Roughness', 0.04, -400, 120), '', MP.MP_ROUGHNESS)
MEL.connect_material_property(const(m, 0.5, -400, 180), '', MP.MP_SPECULAR)
MEL.connect_material_property(const(m, 0.0, -400, 240), '', MP.MP_METALLIC)
finish(m, MATS + 'M_Rev02_PuddleFilm')
instance('MI_Rev02_PuddleFilm', EAL.load_asset(MATS + 'M_Rev02_PuddleFilm'), {'Strength': 0.42, 'EdgeBlur': 0.014, 'Roughness': 0.04}, {'WaterColor': (0.10, 0.085, 0.07, 1)})
# BR-BED-03 frame: the README's painterly walnut image (was flat white Phong)
instance('MI_Bed03_Walnut', texpbr, {'Roughness': 0.55, 'Metallic': 0.0}, textures={'BaseColorMap': EAL.load_asset(R2 + 'BR_Bed03/T_Bed_WalnutPainted')})
# LV-BOOK-01 keepsake tin (bookcase + :063 shelf): its 'Ceramic_Pot' body/lid slot was flat cream FBX Phong. Painted
# enamel tin: the joinery ivory-enamel image under a soft sage tint, slight metal sheen; knob/hinge -> aged brass (05m).
instance('MI_Tin_PaintedEnamel', texpbr, {'Roughness': 0.34, 'Metallic': 0.15}, {'Tint': (0.46, 0.62, 0.50, 1)},
         {'BaseColorMap': EAL.load_asset(R2 + 'Joinery02/T_Joinery_IvoryEnamel')})
# round 3 BA-TOWEL-RAIL-01 rail/brackets/finials (README): aged-brass image, subdued tint, metallic .68, roughness .45
instance('MI_TowelRail_AgedBrass', texpbr, {'Roughness': 0.45, 'Metallic': 0.68}, {'Tint': (0.85, 0.80, 0.70, 1)},
         {'BaseColorMap': EAL.load_asset(R2 + 'BA_TowelRail/T_TowelRail_AgedBrass')})
unreal.log('[Rev02 feedback materials] built')
