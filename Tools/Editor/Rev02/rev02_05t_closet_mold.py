"""Rev02 step 5t (user feedback round 3): the bedroom walk-in closet mold, ORIGINAL BR-MOLD-02 pattern, larger and contiguous.

User direction (final): keep the original BR-MOLD-02 texture/pattern and its README coverage formula; change only the coverage
extent and the mapping. The installed back plane mapped ~160 cm of wall per texture width, and the east return re-used a crop
of the same texture region (the mirrored-copy look). M_Rev02_Mold02Wrap keeps M_Rev02_Mold02's exact look (texture alpha x
pigment-darkness gate, pow 1.35, dithered, near-black, matte, two-sided) but takes UVs from one unfolded wall coordinate that
runs west wall -> back wall -> east wall continuously through both corners (u in cm along the walls, v down from the crown),
at the original ~160 cm scale, with the original dense region kept at the back/east corner. The larger area is covered by
two offset samples of the same texture, each faded toward its own tile edges (no seams, no flips, no procedural shapes);
a soft envelope only fades the bottom, the crown clearance (z 2.64) and the door-side ends.
Surfaces (2 mm off the plaster, NoCollision, no shadow): back wall x 6.2-213.8, both side walls y 386-554, z 0.55-2.64 m.
Repair: the original two actors are re-used (Malady_Mold attachment + RepairDamage/AuthoredMoldDamage/malcolm tags) and the
west wall surface is attached/tagged the same way, so the existing rule hides all of them together, including on load.
The round-3 ceiling strip is retired (the original pattern leaves the ceiling clean). Re-runnable.
"""
import unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; MP = unreal.MaterialProperty
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
MATS = '/Game/ICanFixHim/Environment/Rev02/Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
_missing = [l for l in ['Malady_Mold', 'Art_BR_Closet_Mold', 'Art_BR_Closet_Mold_Return'] if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
log = []

def find(p): return EAL.load_asset(p) if EAL.does_asset_exist(p) else unreal.load_object(None, p + '.' + p.split('/')[-1])
def save(o):
    if not EAL.save_loaded_asset(o, False): assert unreal.EditorLoadingAndSavingUtils.save_packages([o.get_outermost()], False), o.get_path_name()

CODE = '''
// unfolded wall coordinate (cm): west wall (x 6) y 554->386, back wall (y 386) x 6->214, east wall (x 214) y 386->554
// continuous fold (no wall classifier): the back plane is at y 386.5 so SideDepth = 0 there; the side walls fold +-depth
// from the same 3D corner coordinates, so U agrees on both sides of each shared corner (no seam/jump)
float SideDepth = max(WP.y - (BackY + 0.5), 0.0);
float U = 168.0 + (WP.x - CornerAX) + ((WP.x < 110.0) ? -SideDepth : SideDepth);
float2 uv = float2(CornerU - (CornerUcm - U) / TileCm, VTop + (CrownZ - WP.z) / TileCm);
float2 uvB = uv + float2(0.5, 0.37);
float2 fa = frac(uv), fb = frac(uvB);
float wA = saturate(min(min(fa.x, 1.0 - fa.x), min(fa.y, 1.0 - fa.y)) * 6.0);
float wB = saturate(min(min(fb.x, 1.0 - fb.x), min(fb.y, 1.0 - fb.y)) * 6.0);
float4 ta = Texture2DSample(Tex, TexSampler, uv), tb = Texture2DSample(Tex, TexSampler, uvB);
float ga = dot(ta.rgb, float3(0.2126, 0.7152, 0.0722)), gb = dot(tb.rgb, float3(0.2126, 0.7152, 0.0722));
float ca = ta.a * pow(saturate((0.56 - ga) / 0.38), 1.35), cb = tb.a * pow(saturate((0.56 - gb) / 0.38), 1.35);
float env = smoothstep(Floor, Floor + 55.0, WP.z) * (1.0 - smoothstep(CrownZ - 4.0, CrownZ, WP.z)) * smoothstep(0.0, 25.0, U) * smoothstep(544.0, 519.0, U);
float cov = saturate(max(ca * wA, cb * wB) * Strength) * env;
'''
def build():
    path = MATS + 'M_Rev02_Mold02Wrap'
    m = find(path)
    if m: MEL.delete_all_material_expressions(m)
    else: m = tools.create_asset('M_Rev02_Mold02Wrap', MATS[:-1], unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED); m.set_editor_property('two_sided', True)
    m.set_editor_property('opacity_mask_clip_value', 0.5)          # DitherTemporalAA output is centred on the clip value
    wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1500, 0)
    tob = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -1500, -160)
    tob.set_editor_property('parameter_name', 'MoldTexture'); tob.set_editor_property('texture', EAL.load_asset('/Game/ICanFixHim/Environment/Rev02/BR_Mold02/mold_colonies_rgba'))
    P = {}
    for k, (n, v) in enumerate((('CornerAX', 6.0), ('BackY', 386.0), ('CrownZ', 264.0), ('Floor', 55.0), ('TileCm', 160.0),
                                ('CornerU', 0.86), ('CornerUcm', 376.0), ('VTop', 0.04), ('Strength', 1.15))):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1500, 80 + 60 * k)
        e.set_editor_property('parameter_name', n); e.set_editor_property('default_value', v); P[n] = e
    e = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 0)
    e.set_editor_property('code', CODE + 'return cov;'); e.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    ins = []
    for n in ['WP', 'Tex'] + list(P):
        ci = unreal.CustomInput(); ci.set_editor_property('input_name', n); ins.append(ci)
    e.set_editor_property('inputs', ins)
    assert MEL.connect_material_expressions(wp, '', e, 'WP'); assert MEL.connect_material_expressions(tob, '', e, 'Tex')
    for n, pe in P.items(): assert MEL.connect_material_expressions(pe, '', e, n)
    dither = MEL.create_material_expression(m, unreal.MaterialExpressionMaterialFunctionCall, -300, 300)
    dither.set_editor_property('material_function', EAL.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'))
    assert MEL.connect_material_expressions(e, '', dither, 'Alpha Threshold')
    MEL.connect_material_property(dither, '', MP.MP_OPACITY_MASK)
    bcp = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -300, -100)
    bcp.set_editor_property('parameter_name', 'BaseColor'); bcp.set_editor_property('default_value', unreal.LinearColor(0.022, 0.021, 0.020, 1))
    MEL.connect_material_property(bcp, '', MP.MP_BASE_COLOR)
    for prop, val, y in ((MP.MP_ROUGHNESS, 1.0, 120), (MP.MP_METALLIC, 0.0, 170), (MP.MP_SPECULAR, 0.0, 220)):
        c = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -300, y); c.set_editor_property('r', val)
        MEL.connect_material_property(c, '', prop)
    MEL.recompile_material(m); save(m); return m

mold = build()
PLANE = EAL.load_asset('/Engine/BasicShapes/Plane')
# (label, centre, rotation, size u x v cm): Engine Plane is 100 x 100 in its XY plane
SURF = [('Art_BR_Closet_Mold', (110.0, 386.5, 159.5), unreal.Rotator(roll=90, pitch=0, yaw=0), (207.6, 209.0)),
        ('Art_BR_Closet_Mold_Return', (213.8, 470.0, 159.5), unreal.Rotator(roll=90, pitch=0, yaw=90), (168.0, 209.0)),
        ('Art_BR_Closet_Mold_West', (6.2, 470.0, 159.5), unreal.Rotator(roll=90, pitch=0, yaw=90), (168.0, 209.0))]
if 'Art_BR_Closet_Mold_Ceiling' in acts: A.destroy_actor(acts.pop('Art_BR_Closet_Mold_Ceiling'))     # retired: the original leaves the ceiling clean
mal = acts['Malady_Mold']; ref = acts['Art_BR_Closet_Mold']
tags = list(ref.tags); folder = str(ref.get_folder_path()); hidden = ref.get_editor_property('hidden')
assert L.set_current_level_by_name(ref.get_outer().get_outer().get_name())
for lab, c, rot, (u, v) in SURF:
    a = acts.get(lab)
    if a is None:
        a = A.spawn_actor_from_object(PLANE, unreal.Vector(*c), rot); a.set_actor_label(lab); a.set_folder_path(folder); acts[lab] = a
    a.modify()
    if a.get_attach_parent_actor(): a.detach_from_actor()
    comp = a.static_mesh_component; comp.set_static_mesh(PLANE)
    a.set_actor_location_and_rotation(unreal.Vector(*c), rot, False, True); a.set_actor_scale3d(unreal.Vector(u / 100.0, v / 100.0, 1))
    comp.set_collision_profile_name('NoCollision'); comp.set_cast_shadow(False)
    comp.set_mobility(unreal.ComponentMobility.MOVABLE)       # a Static root cannot attach under the movable malady
    for i in range(comp.get_num_materials()): comp.set_material(i, mold)
    a.tags = tags
    a.attach_to_actor(mal, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    assert a.get_attach_parent_actor() == mal, lab
    a.set_actor_hidden_in_game(hidden)
    o, e = a.get_actor_bounds(False)
    log.append('%s x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f tags %s' % (lab, o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z, [str(t) for t in a.tags]))
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 closet mold]\n' + '\n'.join(log))
