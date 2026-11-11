"""Rev02 step 5u (user feedback round 3): picture-frame finishes. Re-runnable; run after rev02_02b (which creates the FIX-006
slot instances this step re-parents).

Every ART-REV02 frame read as a flat brown/dark slab: each kit's T_Frame_BaseColor is a baked, almost uniform wood colour,
and the painterly walnut image it was baked from (T_Frame_Grain, one shared image in all 17 kits) was never used in engine.
  - '*_Frame' slots -> M_Rev02_FramePBR: the baked colour (unchanged hue/value) x the grain image's normalised luminance,
    world-planar projected per face (~30 cm per image; the bevel UVs are near-constant over the visible faces), grain-driven
    roughness variation around the manifest roughness; stained woods
    (walnut/oak/mahogany/ebony/umber/olive...) GrainStrength .85, painted/lacquered/chalk/ivory/teal finishes .35.
  - '*_Aged_Gilt' slots (flat constants) -> the existing aged-brass image under the manifest gilt colour, metallic .64,
    roughness .48 (ART-REV02-014's textured gilt keeps its own image, gains the gilt metallic).
Artwork, mount, slip and backboard instances are untouched.
"""
import json, os, unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; MP = unreal.MaterialProperty
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'
log = []
def find(p): return EAL.load_asset(p) if EAL.does_asset_exist(p) else unreal.load_object(None, p + '.' + p.split('/')[-1])
def load(p):
    o = find(p); assert o, p; return o
def save(o):
    if not EAL.save_loaded_asset(o, False): assert unreal.EditorLoadingAndSavingUtils.save_packages([o.get_outermost()], False), o.get_path_name()

GRAIN = load(R2 + 'ArtFrames/T_Frame_Grain')
def build():
    path = MATS + 'M_Rev02_FramePBR'; m = find(path)
    if m: MEL.delete_all_material_expressions(m)
    else: m = tools.create_asset('M_Rev02_FramePBR', MATS[:-1], unreal.Material, unreal.MaterialFactoryNew())
    def tp(name, tex, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -1200, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('texture', tex)
        e.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_COLOR); return e
    def sp(name, v, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1200, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', float(v)); return e
    base = tp('BaseColorMap', load(R2 + 'ART_REV02_001/T_Frame_BaseColor'), 0)
    # grain coordinates: the frame bevel UVs are near-constant across the visible faces (one stroke smeared over a rail), so
    # the grain is projected from world position on the face's dominant plane (GrainCm per image); UseWorldGrain 0 -> UV0
    uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1500, 300)
    wpe = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1500, 200)
    wne = MEL.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -1500, 250)
    uvs = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -1350, 300)
    uvs.set_editor_property('code', 'float3 n = abs(N); float2 pl = (n.x > n.y && n.x > n.z) ? WP.yz : ((n.y > n.z) ? WP.xz : WP.xy);\n'
                                    'return lerp(UV * float2(TU, TV), pl / Cm, W);')
    uvs.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT2)
    cis = []
    for n_ in ('UV', 'TU', 'TV', 'WP', 'N', 'Cm', 'W'):
        ci = unreal.CustomInput(); ci.set_editor_property('input_name', n_); cis.append(ci)
    uvs.set_editor_property('inputs', cis)
    assert MEL.connect_material_expressions(uv, '', uvs, 'UV'); assert MEL.connect_material_expressions(wpe, '', uvs, 'WP'); assert MEL.connect_material_expressions(wne, '', uvs, 'N')
    assert MEL.connect_material_expressions(sp('GrainTileU', 1.0, 380), '', uvs, 'TU'); assert MEL.connect_material_expressions(sp('GrainTileV', 1.0, 440), '', uvs, 'TV')
    assert MEL.connect_material_expressions(sp('GrainCm', 30.0, 700), '', uvs, 'Cm'); assert MEL.connect_material_expressions(sp('UseWorldGrain', 1.0, 760), '', uvs, 'W')
    grain = tp('GrainMap', GRAIN, 300); assert MEL.connect_material_expressions(uvs, '', grain, 'UVs')
    def custom(code, ins, out, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -700, y)
        e.set_editor_property('code', code); e.set_editor_property('output_type', out)
        cl = []
        for n_ in ins:
            ci = unreal.CustomInput(); ci.set_editor_property('input_name', n_); cl.append(ci)
        e.set_editor_property('inputs', cl); return e
    strength = sp('GrainStrength', 0.85, 520); rough = sp('Roughness', 0.64, 580); metal = sp('Metallic', 0.0, 640)
    bc = custom('float g = dot(G, float3(0.3, 0.59, 0.11)) / 0.07; return B * lerp(1.0, clamp(g, 0.5, 1.8), S);', ['B', 'G', 'S'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, 0)
    assert MEL.connect_material_expressions(base, 'RGB', bc, 'B'); assert MEL.connect_material_expressions(grain, 'RGB', bc, 'G'); assert MEL.connect_material_expressions(strength, '', bc, 'S')
    ro = custom('float g = dot(G, float3(0.3, 0.59, 0.11)) / 0.07; return clamp(R + (1.0 - clamp(g, 0.5, 1.8)) * 0.18 * S, 0.3, 0.95);', ['R', 'G', 'S'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, 400)
    assert MEL.connect_material_expressions(rough, '', ro, 'R'); assert MEL.connect_material_expressions(grain, 'RGB', ro, 'G'); assert MEL.connect_material_expressions(strength, '', ro, 'S')
    MEL.connect_material_property(bc, '', MP.MP_BASE_COLOR); MEL.connect_material_property(ro, '', MP.MP_ROUGHNESS); MEL.connect_material_property(metal, '', MP.MP_METALLIC)
    MEL.recompile_material(m); save(m); return m

frame_m = build(); texpbr = load(MATS + 'M_Rev02_TexPBR')
BRASS = load(R2 + 'HA_Sconce02/aged_brass')
PAINTED = ('chalk', 'ivory', 'cream', 'teal', 'painted', 'lacquer', 'bleached')
inv = json.load(open(os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json')))
for it in inv['items']:
    sa = it['source_art']; kit = sa['asset'].replace('-', '_'); desc = sa['frame'].lower()
    own = desc.split(',')[0].split(' with ')[0]                     # the frame's own finish (not its mount/liner)
    gs = 0.35 if any(k in own for k in PAINTED) else 0.85
    for mt in sa['materials']:
        slot = mt['name'].split('_', 1)[1]; mi = find(MATS + 'MI_' + mt['name'].replace('-', '_'))
        if mi is None: continue
        if slot == 'Frame':
            MEL.set_material_instance_parent(mi, frame_m)
            for k, v in (('GrainStrength', gs), ('Roughness', mt['roughness']), ('Metallic', mt.get('metallic', 0.0)), ('GrainTileU', 1.0), ('GrainTileV', 1.0), ('GrainCm', 30.0), ('UseWorldGrain', 1.0)):
                MEL.set_material_instance_scalar_parameter_value(mi, k, v)
            MEL.set_material_instance_texture_parameter_value(mi, 'BaseColorMap', load(R2 + kit + '/T_Frame_BaseColor'))
            MEL.set_material_instance_texture_parameter_value(mi, 'GrainMap', GRAIN)
            save(mi); log.append('%s Frame grain %.2f (%s)' % (kit, gs, sa['frame'][:40]))
        elif slot == 'Aged_Gilt':
            MEL.set_material_instance_parent(mi, texpbr)
            if mt.get('base_color_texture'):
                MEL.set_material_instance_texture_parameter_value(mi, 'BaseColorMap', load(R2 + kit + '/T_Frame_BaseColor'))
                MEL.set_material_instance_vector_parameter_value(mi, 'Tint', unreal.LinearColor(1, 1, 1, 1))
            else:
                c = mt['base_color_linear']; k = 1.0 / 0.42                   # aged-brass image mean luminance ~ .42
                MEL.set_material_instance_texture_parameter_value(mi, 'BaseColorMap', BRASS)
                MEL.set_material_instance_vector_parameter_value(mi, 'Tint', unreal.LinearColor(min(c[0] * k, 2), min(c[1] * k, 2), min(c[2] * k, 2), 1))
            MEL.set_material_instance_scalar_parameter_value(mi, 'Metallic', mt.get('metallic', 0.64)); MEL.set_material_instance_scalar_parameter_value(mi, 'Roughness', mt['roughness'])
            save(mi); log.append('%s Aged_Gilt aged-brass image' % kit)
unreal.log('[Rev02 art frames]\n' + '\n'.join(log))
