"""Rev02 step 5s (user feedback round 3, kitchen metals). Re-runnable; builds its own materials (rev02_02b is not re-run).

Faucet / taps / drain / trap / under-sink pipes read as bright new chrome (M_Rev02_AgedChrome, rough .24). In KI-FAUCET-02 they
all share the sink body's single 'Aged_Chrome' slot (and the taps' own 'Aged_Chrome'), so one world-space alloy material
drives the whole set: one coherent tarnished-nickel family for faucet, taps and drain (the drain matches the faucet), and,
below CorrodeZ (the trap and pipes under the basin), the same alloy progressively corroded: oxidation, whitish mineral
crust at joints, dark damp streaks running down. UVs are not used (world triplanar on the existing aged-metal image, its
luminance x nickel tint), roughness .35-.6 with only small rubbed highlights; no mirror strip. The leak water/stain keep
their repair-hide rules; the corrosion stays after repair (it is the pipe's age, not the leak).

KI-RANGE-02 (material audit, interim until the stove source revision): every slot was FBX legacy Phong. Enamel -> its own
range-enamel-v2 image as PBR; Aged_Steel knobs/handles/markings -> the same alloy family without corrosion (cooler steel
tint); cast-iron burners, oven cavity, gasket and oven window -> PBR constants.
"""
import unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; MP = unreal.MaterialProperty
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
_missing = [l for l in ['Art_KI_SinkNarrow_body', 'Art_KI_SinkNarrow_R_tap', 'Art_KI_SinkNarrow_L_tap', 'Sink_Tap', 'Art_KI_Range_Body', 'Art_KI_Range_Door', 'Oven_Door', 'Stove_Burner'] if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
log = []

def find(p): return EAL.load_asset(p) if EAL.does_asset_exist(p) else unreal.load_object(None, p + '.' + p.split('/')[-1])
def load(p):
    o = find(p); assert o, p; return o
def save(o):
    if not EAL.save_loaded_asset(o, False): assert unreal.EditorLoadingAndSavingUtils.save_packages([o.get_outermost()], False), o.get_path_name()
def instance(name, parent, scalars=None, vectors=None, textures=None):
    mi = find(MATS + name) or tools.create_asset(name, MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (scalars or {}).items(): MEL.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (vectors or {}).items(): MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
    for k, v in (textures or {}).items(): MEL.set_material_instance_texture_parameter_value(mi, k, v)
    save(mi); return mi

NOISE = '''
struct FNoise {
  float h3(float3 p){ p = frac(p * 0.3183099 + 0.1); p *= 17.0; return frac(p.x * p.y * p.z * (p.x + p.y + p.z)); }
  float vn(float3 x){ float3 i = floor(x); float3 f = frac(x); f = f * f * (3.0 - 2.0 * f);
    return lerp(lerp(lerp(h3(i), h3(i + float3(1,0,0)), f.x), lerp(h3(i + float3(0,1,0)), h3(i + float3(1,1,0)), f.x), f.y),
                lerp(lerp(h3(i + float3(0,0,1)), h3(i + float3(1,0,1)), f.x), lerp(h3(i + float3(0,1,1)), h3(i + float3(1,1,1)), f.x), f.y), f.z); }
  float fbm(float3 p){ return 0.55 * vn(p) + 0.3 * vn(p * 2.03 + 7.1) + 0.15 * vn(p * 4.1 + 3.3); }
};
FNoise nz;
'''
COMMON = NOISE + '''
float3 n = abs(N); n = pow(n, 4.0); n /= (n.x + n.y + n.z + 1e-5);
float3 q = WP / TileCm;
float3 img = Texture2DSample(Tex, TexSampler, q.yz).rgb * n.x + Texture2DSample(Tex, TexSampler, q.xz).rgb * n.y + Texture2DSample(Tex, TexSampler, q.xy).rgb * n.z;
float lum = dot(img, float3(0.3, 0.59, 0.11));
float tarn = saturate(nz.fbm(WP * 0.09) * 1.25 - 0.15) * Tarnish;
float corr = saturate((CorrodeZ - WP.z) / 8.0);
float crust = smoothstep(0.62, 0.8, nz.fbm(WP * 0.35 + 11.0)) * corr;
float damp = smoothstep(0.55, 0.75, nz.fbm(float3(WP.x * 0.6, WP.y * 0.6, WP.z * 0.08) + 5.0)) * corr;
float oxid = smoothstep(0.45, 0.7, nz.fbm(WP * 0.18 + 2.0)) * corr;
'''
def build():
    path = MATS + 'M_Rev02_TarnishedAlloy'
    m = find(path)
    if m: MEL.delete_all_material_expressions(m)
    else: m = tools.create_asset('M_Rev02_TarnishedAlloy', MATS[:-1], unreal.Material, unreal.MaterialFactoryNew())
    def sp(name, v, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1500, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', float(v)); return e
    def vp(name, v, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -1500, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', unreal.LinearColor(*v)); return e
    tob = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -1500, 0)
    tob.set_editor_property('parameter_name', 'MetalImage'); tob.set_editor_property('texture', load(R2 + 'Tub03/T_Tub03_AgedMetal'))
    wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1500, 150)
    wn = MEL.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -1500, 220)
    params = {'TileCm': sp('TileCm', 9.0, 300), 'Tarnish': sp('Tarnish', 0.8, 370), 'CorrodeZ': sp('CorrodeZ', 62.0, 440),
              'Metal': vp('MetalTint', (0.66, 0.64, 0.60, 1), 510), 'Corroded': vp('CorrodedTint', (0.20, 0.17, 0.12, 1), 580),
              'Oxide': vp('OxideTint', (0.24, 0.29, 0.21, 1), 650), 'Crust': vp('CrustTint', (0.62, 0.60, 0.54, 1), 720),
              'Rough': sp('BaseRoughness', 0.42, 790)}
    def node(code, extra, out, y):
        ins = ['Tex', 'WP', 'N', 'TileCm', 'Tarnish', 'CorrodeZ'] + extra
        e = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -700, y)
        e.set_editor_property('code', COMMON + code); e.set_editor_property('output_type', out)
        cis = []
        for nm in ins:
            ci = unreal.CustomInput(); ci.set_editor_property('input_name', nm); cis.append(ci)
        e.set_editor_property('inputs', cis)
        assert MEL.connect_material_expressions(tob, '', e, 'Tex'); assert MEL.connect_material_expressions(wp, '', e, 'WP')
        assert MEL.connect_material_expressions(wn, '', e, 'N')
        for nm in ('TileCm', 'Tarnish', 'CorrodeZ'): assert MEL.connect_material_expressions(params[nm], '', e, nm)
        for nm in extra: assert MEL.connect_material_expressions(params[nm], '', e, nm)
        return e
    bc = node('''float3 metal = Metal.rgb * (0.55 + 0.6 * lum) * lerp(1.0, 0.55, tarn);
float3 c = lerp(metal, Corroded.rgb * (0.7 + 0.6 * lum), corr * 0.85);
c = lerp(c, Oxide.rgb, oxid * 0.6); c = lerp(c, Crust.rgb, crust * 0.8); c *= lerp(1.0, 0.55, damp);
return c;''', ['Metal', 'Corroded', 'Oxide', 'Crust'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, 0)
    ro = node('''float r = Rough + 0.18 * (nz.fbm(WP * 0.5) - 0.5) + 0.12 * tarn;
r = lerp(r, 0.78, corr * 0.8); r = lerp(r, 0.95, crust); r = lerp(r, 0.28, damp * 0.7);
return clamp(r, 0.3, 0.97);''', ['Rough'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, 400)
    me = node('''float mtl = lerp(0.85, 0.35, corr); mtl = lerp(mtl, 0.0, max(crust, oxid * 0.6)); return mtl;''', [], unreal.CustomMaterialOutputType.CMOT_FLOAT1, 700)
    MEL.connect_material_property(bc, '', MP.MP_BASE_COLOR); MEL.connect_material_property(ro, '', MP.MP_ROUGHNESS); MEL.connect_material_property(me, '', MP.MP_METALLIC)
    MEL.recompile_material(m); save(m); return m

alloy = build()
sink_mi = instance('MI_KI_TarnishedAlloy', alloy, {'TileCm': 9.0, 'Tarnish': 0.8, 'CorrodeZ': 62.0, 'BaseRoughness': 0.42})
texpbr = load(MATS + 'M_Rev02_TexPBR'); cpbr = load(MATS + 'M_Rev02_ConstPBR')
RANGE = {}
if not find(R2 + 'Range03/KI_RANGE03_Body'):
    # interim KI-RANGE-02 PBR (only when the ROUND3-RANGE-03 release is not imported)
    RANGE = {'Enamel_Painted': instance('MI_Range02_Enamel', texpbr, {'Roughness': 0.30, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, {'BaseColorMap': load(R2 + 'KI_Range02/T_Range02_Enamel')}),
             'Aged_Steel': instance('MI_Range02_AgedSteel', alloy, {'TileCm': 7.0, 'Tarnish': 0.6, 'CorrodeZ': -1000.0, 'BaseRoughness': 0.38}, {'MetalTint': (0.60, 0.61, 0.60, 1)}),
             'Burner_Cast_Iron': instance('MI_Range02_CastIron', cpbr, {'Metallic': 0.55, 'Roughness': 0.62}, {'BaseColor': (0.045, 0.040, 0.035, 1)}),
             'Oven_Dark': instance('MI_Range02_OvenDark', cpbr, {'Metallic': 0.0, 'Roughness': 0.55}, {'BaseColor': (0.025, 0.020, 0.018, 1)}),
             'Gasket': instance('MI_Range02_Gasket', cpbr, {'Metallic': 0.0, 'Roughness': 0.9}, {'BaseColor': (0.06, 0.055, 0.045, 1)}),
             'Oven_Window': instance('MI_Range02_OvenWindow', cpbr, {'Metallic': 0.0, 'Roughness': 0.06}, {'BaseColor': (0.015, 0.013, 0.012, 1)})}

def bind(label, comp_name, mapping):
    a = acts[label]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if comp_name and c.get_name() != comp_name: continue
        if not c.static_mesh: continue
        for i, s in enumerate(c.static_mesh.static_materials):
            mt = mapping.get(str(s.material_slot_name))
            if mt is not None: a.modify(); c.set_material(i, mt); log.append('%s/%s %s -> %s' % (label, c.get_name(), s.material_slot_name, mt.get_name()))
for lab, comp in (('Art_KI_SinkNarrow_body', None), ('Art_KI_SinkNarrow_R_tap', None), ('Art_KI_SinkNarrow_L_tap', None), ('Sink_Tap', 'Body')):
    bind(lab, comp, {'Aged_Chrome': sink_mi})
# ROUND3-RANGE-03 (when imported): body/door meshes swap in place (same body origin, same door hinge root); the Range02
# collision policy is copied (no hulls generated). README material contract, every slot explicit.
R3 = R2 + 'Range03/'
if find(R3 + 'KI_RANGE03_Body'):
    SM = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    def copy_col(src, dst):
        SM.remove_collisions(dst); bs = dst.get_editor_property('body_setup'); bs.modify()
        bs.set_editor_property('collision_trace_flag', src.get_editor_property('body_setup').get_editor_property('collision_trace_flag')); save(dst)
    B3, D3 = load(R3 + 'KI_RANGE03_Body'), load(R3 + 'KI_RANGE03_Door')
    copy_col(load(R2 + 'KI_Range02/KI_RANGE02_Body'), B3); copy_col(load(R2 + 'KI_Range02/KI_RANGE02_Door'), D3)
    water = load(MATS + 'M_Rev02_Water')
    RANGE = {'Enamel_Painted': instance('MI_Range03_Enamel', texpbr, {'Roughness': 0.49, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, {'BaseColorMap': load(R3 + 'T_Range03_Enamel')}),
             'Range03_AgedSteel': instance('MI_Range03_AgedSteel', texpbr, {'Roughness': 0.34, 'Metallic': 0.78}, {'Tint': (0.72, 0.76, 0.78, 1)}, {'BaseColorMap': load(R3 + 'T_Range03_AgedSteel')}),
             'Range03_Bakelite': instance('MI_Range03_Bakelite', texpbr, {'Roughness': 0.36, 'Metallic': 0.04}, {'Tint': (0.42, 0.34, 0.28, 1)}, {'BaseColorMap': load(R3 + 'T_Range03_IronGrain')}),
             'Range03_CeramicMarkings': instance('MI_Range03_CeramicMarkings', texpbr, {'Roughness': 0.40, 'Metallic': 0.0}, {'Tint': (1.05, 1.05, 1.01, 1)}, {'BaseColorMap': load(R3 + 'T_Range03_Enamel')}),
             # dark translucent lit pane (source transmission .38 -> opacity .62) so the real aperture/cavity reads subtly
             'Range03_OvenGlass': instance('MI_Range03_OvenGlass', water, {'Opacity': 0.62, 'Roughness': 0.23, 'Specular': 0.5}, {'BaseColor': (0.085, 0.075, 0.061, 1)}),
             'Oven_Dark': instance('MI_Range03_OvenDark', cpbr, {'Metallic': 0.0, 'Roughness': 0.50}, {'BaseColor': (0.082, 0.065, 0.052, 1)}),
             'Burner_Cast_Iron': instance('MI_Range03_CastIron', cpbr, {'Metallic': 0.25, 'Roughness': 0.80}, {'BaseColor': (0.075, 0.067, 0.060, 1)}),
             'Gasket': instance('MI_Range03_Gasket', cpbr, {'Metallic': 0.0, 'Roughness': 0.80}, {'BaseColor': (0.13, 0.115, 0.09, 1)})}
    # Stove_Burner's Body is the range body (rev02_05x_outline_bodies), like Oven_Door's is the oven door.
    for lab, comp, mesh in (('Art_KI_Range_Body', None, B3), ('Stove_Burner', 'Body', B3), ('Art_KI_Range_Door', None, D3), ('Oven_Door', 'Body', D3)):
        a = acts[lab]
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if comp and c.get_name() != comp: continue
            if c.static_mesh and c.static_mesh.get_name().startswith('KI_RANGE0'):
                a.modify(); c.set_static_mesh(mesh); log.append('%s/%s -> %s' % (lab, c.get_name(), mesh.get_name()))
    missing = [str(s.material_slot_name) for m in (B3, D3) for s in m.static_materials if str(s.material_slot_name) not in RANGE]
    assert not missing, 'unbound Range03 slots %s' % missing
for lab, comp in (('Art_KI_Range_Body', None), ('Stove_Burner', 'Body'), ('Art_KI_Range_Door', None), ('Oven_Door', 'Body')):
    bind(lab, comp, RANGE)
assert L.save_all_dirty_levels()
unreal.log('[Rev02 kitchen metal]\n' + '\n'.join(log))
