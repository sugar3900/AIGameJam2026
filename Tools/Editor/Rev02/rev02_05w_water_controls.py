"""Rev02 step 5w (user feedback: water controls): paired tap knobs, a filling bath, the leaking drain's spray, Lukey's
under-sink target and a reflective leak puddle. Needs the FixHimInteractable fill opt-in (FillSurface...) and the
FixHimMalady spray opt-in (LeakSpray...). Run after rev02_05n / 05o / 05q / 05s. Re-runnable.

- Kitchen: the right knob (Art_KI_SinkNarrow_R_tap) becomes Sink_Tap_R, a click body like Sink_Tap (hidden source art,
  GameplayBodySource). Both share ToggleGroup KitchenSinkTaps, so either knob turns the one spout on or off.
- Bath: likewise Tub_Faucet_R on Art_BA_Tub_BA_TapRight, ToggleGroup TubTaps with Tub_Faucet. Tub_Faucet's reveal is
  now the spout stream (MI_Rev02_TubStream, the sink stream material) from the BA-TUB-FIXTURES-02 spout outlet,
  leaning 3.5 deg into the tub, down to the tub floor. The bath water is Art_BA_TubWater (the BA_TUB_WATER surface,
  MI_Rev02_BathWater: the reflective water below at coverage .55) as the tap's FillSurface: it rises from the tub floor to the old full
  level over 45 s while the water runs and drains over 60 s once off; the stream ends on the surface and a splash
  (Art_BA_TubSplash, MI_Rev02_TapSplash) rides it. Water levels are not saved.
- Lukey (Malady_Sink): the invisible inspect proxy covers the open space under the sink (x 165-265, y 18-83,
  z 1-67: trap, bucket, puddle) instead of the sink apron. Its hover shell and glow overlay are off (a box under the
  sink would read as a stray pale shape); reticle, prompt, glow light, inspect and repair are unchanged.
  While either kitchen knob runs and the leak is unrepaired, the trap's upper slip nut sprays a light droplet fan
  east into the open floor area (clear of the bucket), drawn with the leak drop material.
- Puddle (Art_KI_SINK_damage_Film): the mirror recipe (M_Rev02_MirrorAged: metallic aged silver, Lumen reflections,
  low-frequency roughness/tint variation) on the same world-XY puddle mask, with a hard edge (mask alpha >= .5, no blur)
  and coverage .55 so the tile shows through (user: more floor, hard edge).
  The bath water uses the same recipe (M_Rev02_MirrorWater) with a flat dithered coverage.
  The puddle's stain decal (Art_KI_SINK_damage) is lightened to Strength .08 through MI_Rev02_LeakPuddleDecal.
"""
import math, os, unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; MP = unreal.MaterialProperty
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert not L.is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
_missing = [l for l in ['Sink_Tap', 'Art_KI_SinkNarrow_R_tap', 'Tub_Faucet', 'Art_BA_Tub_BA_TapRight', 'Art_BA_Tub_BA_Tub',
                        'Malady_Sink', 'Art_KI_SINK_damage', 'Art_KI_SINK_damage_Film', 'Art_KI_SinkNarrow_body'] if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
CYL = EAL.load_asset('/Engine/BasicShapes/Cylinder'); PLANE = EAL.load_asset('/Engine/BasicShapes/Plane')
log = []

def find(p): return EAL.load_asset(p) if EAL.does_asset_exist(p) else unreal.load_object(None, p + '.' + p.split('/')[-1])
def load(p):
    o = find(p); assert o, p; return o
def on_disk(o):
    rel = o.get_outermost().get_name()[len('/Game/'):] + '.uasset'
    return os.path.isfile(os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()), rel))
def save(o):
    if not EAL.save_loaded_asset(o, False): unreal.EditorLoadingAndSavingUtils.save_packages([o.get_outermost()], False)
    assert on_disk(o), 'not written to disk: ' + o.get_path_name()
def instance(name, parent, scalars=None, vectors=None):
    mi = find(MATS + name) or tools.create_asset(name, MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (scalars or {}).items(): MEL.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (vectors or {}).items(): MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
    save(mi); return mi
def down(x, y, z0, ignore):
    h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, z0), unreal.Vector(x, y, -5), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                               True, ignore, unreal.DrawDebugTrace.NONE, True)
    assert h, 'trace miss at (%.1f, %.1f)' % (x, y)
    return h.to_tuple()[4].z
def bb(a):
    o, e = a.get_actor_bounds(False); return 'x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z)

# ---------------- materials ----------------
tub_stream = instance('MI_Rev02_TubStream', load(MATS + 'M_Rev02_WaterStream'),
                      {'Opacity': 0.55, 'Streak': 0.55, 'Speed': 2.6, 'NormalBreakup': 0.45, 'WobbleAmp': 0.08, 'TopZ': 73.4},
                      {'BaseColor': (0.16, 0.2, 0.22, 1)})
splash_mi = load(MATS + 'MI_Rev02_TapSplash')

# Reflective water: the aged-mirror recipe (rev02_02b aged_metal / M_Rev02_MirrorAged: metallic, Lumen reflections,
# low-frequency roughness/tint variation), dithered to partial coverage so what lies under the water shows through.
# Plain lit translucent water (M_Rev02_Water) only picks up the bright fallback reflection and reads milky in the tub.
# The puddle takes its coverage from the puddle film's world-XY mask; the bath from a flat Coverage.
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
def build_mirror_water(name, puddle_mask):
    path = MATS + name; m = find(path)
    if m: MEL.delete_all_material_expressions(m)
    else: m = tools.create_asset(name, MATS[:-1], unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property('dither_opacity_mask', True)
    def sp(n, v, x, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
        e.set_editor_property('parameter_name', n); e.set_editor_property('default_value', float(v)); return e
    def vp(n, v, x, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, x, y)
        e.set_editor_property('parameter_name', n); e.set_editor_property('default_value', unreal.LinearColor(*v)); return e
    def custom(code, ins, x, y, out=unreal.CustomMaterialOutputType.CMOT_FLOAT1):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
        e.set_editor_property('code', code); e.set_editor_property('output_type', out)
        cl = []
        for n in ins:
            ci = unreal.CustomInput(); ci.set_editor_property('input_name', n); cl.append(ci)
        e.set_editor_property('inputs', cl); return e
    wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1500, 200)
    if not puddle_mask:
        MEL.connect_material_property(sp('Coverage', 0.6, -500, 200), '', MP.MP_OPACITY_MASK)
    else:
        puddle_coverage(m, sp, custom, wp)
    mirror_surface(m, sp, vp, custom, wp)
    MEL.recompile_material(m); save(m); return m

def puddle_coverage(m, sp, custom, wp):
    wuv = custom('float2 uv = float2((WP.x - CX) / SX, (WP.y - CY) / SY) + 0.5;\n'
                 'return float2(lerp(uv.x, 1.0 - uv.x, FU), lerp(uv.y, 1.0 - uv.y, FV));',
                 ['WP', 'CX', 'CY', 'SX', 'SY', 'FU', 'FV'], -1200, 200, unreal.CustomMaterialOutputType.CMOT_FLOAT2)
    assert MEL.connect_material_expressions(wp, '', wuv, 'WP')
    for k, (n, v) in enumerate((('CX', 206.7), ('CY', 75.9), ('SX', 68.2221), ('SY', 86.1652), ('FlipU', 0.0), ('FlipV', 0.0))):
        assert MEL.connect_material_expressions(sp(n, v, -1500, 320 + 70 * k), '', wuv, {'FlipU': 'FU', 'FlipV': 'FV'}.get(n, n))
    tob = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -900, 500)
    tob.set_editor_property('parameter_name', 'PuddleMaskObj'); tob.set_editor_property('texture', load(R2 + 'KI_Leak02/T_Leak_Puddle_Mask'))
    # hard edge (user): the mask alpha thresholded at Cut, no blur; Strength is the flat dithered coverage inside it
    op = custom('float a = Texture2DSample(Tex, TexSampler, U).a;\n'
                'float inside = (U.x > 0 && U.x < 1 && U.y > 0 && U.y < 1) ? 1.0 : 0.0;\n'
                'return step(Cut, a) * Strength * inside;', ['Tex', 'U', 'Cut', 'Strength'], -550, 200)
    assert MEL.connect_material_expressions(tob, '', op, 'Tex'); assert MEL.connect_material_expressions(wuv, '', op, 'U')
    assert MEL.connect_material_expressions(sp('Cut', 0.5, -900, 700), '', op, 'Cut')
    assert MEL.connect_material_expressions(sp('Strength', 0.55, -900, 800), '', op, 'Strength')
    MEL.connect_material_property(op, '', MP.MP_OPACITY_MASK)

def mirror_surface(m, sp, vp, custom, wp):
    nz = custom(NOISE, ['W', 'Freq'], -900, -300)
    assert MEL.connect_material_expressions(wp, '', nz, 'W'); assert MEL.connect_material_expressions(sp('NoiseFreq', 0.08, -1200, -300), '', nz, 'Freq')
    col = custom('return Base * (1.0 + TVar * (N - 0.5));', ['Base', 'TVar', 'N'], -500, -100, unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    assert MEL.connect_material_expressions(vp('WaterColor', (0.72, 0.70, 0.66, 1), -900, -150), '', col, 'Base')
    assert MEL.connect_material_expressions(sp('TintVar', 0.08, -900, -80), '', col, 'TVar'); assert MEL.connect_material_expressions(nz, '', col, 'N')
    MEL.connect_material_property(col, '', MP.MP_BASE_COLOR)
    rg = custom('return saturate(R0 + RV * (N - 0.5));', ['R0', 'RV', 'N'], -500, 0)
    assert MEL.connect_material_expressions(sp('Roughness', 0.14, -900, 0), '', rg, 'R0')
    assert MEL.connect_material_expressions(sp('RoughVar', 0.08, -900, 60), '', rg, 'RV'); assert MEL.connect_material_expressions(nz, '', rg, 'N')
    MEL.connect_material_property(rg, '', MP.MP_ROUGHNESS)
    MEL.connect_material_property(sp('Metallic', 1.0, -500, 120), '', MP.MP_METALLIC)

puddle_m = build_mirror_water('M_Rev02_PuddleMirror', True)
film_mi = load(MATS + 'MI_Rev02_PuddleFilm')
keep = {k: MEL.get_material_instance_scalar_parameter_value(film_mi, k) for k in ('CX', 'CY', 'SX', 'SY', 'FlipU', 'FlipV')}
MEL.set_material_instance_parent(film_mi, puddle_m)
for k, v in dict(keep, Strength=0.55, Cut=0.5, Roughness=0.14, RoughVar=0.08, TintVar=0.08, NoiseFreq=0.08, Metallic=1.0).items():
    MEL.set_material_instance_scalar_parameter_value(film_mi, k, v)
MEL.set_material_instance_vector_parameter_value(film_mi, 'WaterColor', unreal.LinearColor(0.72, 0.70, 0.66, 1))
save(film_mi)
log.append('puddle film -> M_Rev02_PuddleMirror (metallic, roughness .14 +-.04, hard edge at mask .5, coverage .55), mask %s' % keep)
# The stain decal under the film (M_Rev02_LeakPuddleDecal, used directly at Strength .22) darkened the tile too much
# (user): an instance at .08 keeps a faint wet tint under the reflective film.
stain_mi = instance('MI_Rev02_LeakPuddleDecal', load(MATS + 'M_Rev02_LeakPuddleDecal'), {'Strength': 0.08})
stain = acts['Art_KI_SINK_damage']; stain.modify(); stain.decal.set_decal_material(stain_mi)
log.append('stain decal -> MI_Rev02_LeakPuddleDecal (Strength .08, was .22)')
bath_water = instance('MI_Rev02_BathWater', build_mirror_water('M_Rev02_MirrorWater', False),
                      {'Coverage': 0.55, 'Roughness': 0.08, 'RoughVar': 0.06, 'TintVar': 0.06, 'NoiseFreq': 0.08, 'Metallic': 1.0},
                      {'WaterColor': (0.66, 0.70, 0.70, 1)})

# ---------------- paired knobs ----------------
def knob(src_label, new_label, art_label, group):
    """Second knob: a copy of the tap's click actor with only a click body (no stream/fill), state shared by group."""
    src = acts[src_label]
    if new_label in acts: A.destroy_actor(acts.pop(new_label))
    assert L.set_current_level_by_name(src.get_outer().get_outer().get_name())
    k = A.duplicate_actor(src, world, unreal.Vector(0, 0, 0))
    k.set_actor_label(new_label); k.set_folder_path(str(src.get_folder_path())); acts[new_label] = k
    art = acts[art_label]; c = art.static_mesh_component
    b = k.get_editor_property('body'); b.set_static_mesh(c.static_mesh)
    b.set_world_location_and_rotation(art.get_actor_location(), art.get_actor_rotation(), False, False)
    for i in range(c.get_num_materials()): b.set_material(i, c.get_material(i))
    k.get_editor_property('reveal_part').set_static_mesh(None)
    k.set_editor_property('reveal_actors', []); k.set_editor_property('fill_surface', None); k.set_editor_property('fill_followers', [])
    k.set_editor_property('use_authored_reveal_material', False); k.set_editor_property('is_on', False)
    art.modify(); art.set_actor_hidden_in_game(True); c.set_visibility(False); c.set_collision_profile_name('NoCollision')
    art.tags = [unreal.Name('GameplayBodySource')]
    for a in (src, k):
        a.modify(); a.set_editor_property('toggle_group', unreal.Name(group))
    log.append('%s + %s (group %s): body %s' % (src_label, new_label, group, bb(art)))
    return k

# ---------------- bath: stream, filling water, splash, right knob ----------------
tf = acts['Tub_Faucet']; tub = acts['Art_BA_Tub_BA_Tub']
old_rp = tf.get_editor_property('reveal_part')
# first run: the old reveal is the bath surface (mesh + transform at the full level); re-runs: the Art_BA_TubWater it became
if 'Art_BA_TubWater' in acts:
    w = acts['Art_BA_TubWater']; water_mesh = w.static_mesh_component.static_mesh; water_xf = w.get_actor_transform()
else:
    assert old_rp.static_mesh and 'WATER' in old_rp.static_mesh.get_name().upper(), 'Tub_Faucet reveal is not the bath surface'
    water_mesh = old_rp.static_mesh; water_xf = old_rp.get_world_transform()
for lab in ('Art_BA_TubWater', 'Art_BA_TubSplash'):
    if lab in acts: A.destroy_actor(acts.pop(lab))
knob('Tub_Faucet', 'Tub_Faucet_R', 'Art_BA_Tub_BA_TapRight', 'TubTaps')
assert L.set_current_level_by_name(tf.get_outer().get_outer().get_name())
# spout outlet: BA-TUB-FIXTURES-02 nozzle tip x 512.8, lowest lip z 73.4 (centre y 907); lands a few cm out, on the floor
TOP = unreal.Vector(511.6, 907.0, 73.4)
bx = 515.0; BOT = unreal.Vector(bx, 907.0, down(bx, 907.0, 70, [tf]))
axis = BOT - TOP; length = axis.length()
pitch = math.degrees(math.atan2(axis.x, -axis.z))           # lean the cylinder's +Z (up) back toward the spout
tf.modify()
rp = tf.get_editor_property('reveal_part'); rp.set_static_mesh(CYL)
rp.set_world_location((TOP + BOT) * 0.5, False, False); rp.set_world_rotation(unreal.Rotator(roll=0, pitch=pitch, yaw=0), False, False)
rp.set_world_scale3d(unreal.Vector(0.02, 0.02, length / 100.0)); rp.set_cast_shadow(False); rp.set_material(0, tub_stream)
up = rp.get_up_vector(); top_chk = rp.get_world_location() + up * (length / 2)
assert (top_chk - TOP).length() < 0.5, 'stream lean sign wrong: top %s vs %s' % (top_chk, TOP)
# the bath water surface (old reveal mesh/transform, surface at its full level) and its splash
FULL_Z = water_xf.translation.z + water_mesh.get_bounding_box().max.z
water = A.spawn_actor_from_object(water_mesh, water_xf.translation, water_xf.rotation.rotator())
water.set_actor_label('Art_BA_TubWater'); water.set_folder_path(str(tf.get_folder_path())); acts['Art_BA_TubWater'] = water
wc = water.static_mesh_component; wc.set_mobility(unreal.ComponentMobility.MOVABLE)
wc.set_collision_profile_name('NoCollision'); wc.set_cast_shadow(False); wc.set_material(0, bath_water)
floor_z = min(down(x, y, 70, [tf, water]) for x, y in ((540, 907), (580, 907), (620, 907), (580, 892), (580, 922)))
depth = FULL_Z - (floor_z + 0.3)
sx = TOP.x + (BOT.x - TOP.x) * (TOP.z - FULL_Z) / (TOP.z - BOT.z)        # where the stream meets the full surface
splash = A.spawn_actor_from_object(PLANE, unreal.Vector(sx, 907.0, FULL_Z + 0.5), unreal.Rotator(0, 0, 0))
splash.set_actor_label('Art_BA_TubSplash'); splash.set_folder_path(str(tf.get_folder_path())); acts['Art_BA_TubSplash'] = splash
splash.set_actor_scale3d(unreal.Vector(0.14, 0.14, 1))
sc = splash.static_mesh_component; sc.set_mobility(unreal.ComponentMobility.MOVABLE)
sc.set_collision_profile_name('NoCollision'); sc.set_cast_shadow(False); sc.set_material(0, splash_mi)
splash.set_actor_hidden_in_game(True); sc.set_visibility(False)
# tub interior cross-section (complex traces from the centre): near the floor vs at the full level -> empty XY scale
def span(z):
    def hor(dx, dy):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(580, 907, z), unreal.Vector(580 + dx, 907 + dy, z), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                   True, [tf, water, splash], unreal.DrawDebugTrace.NONE, True)
        assert h, 'tub wall trace miss z %.1f' % z
        p = h.to_tuple()[4]; return p.x if dx else p.y
    return hor(120, 0) - hor(-120, 0), hor(0, 60) - hor(0, -60)
fx, fy = span(FULL_Z); ex, ey = span(floor_z + 2.0)
empty = unreal.Vector2D(round(min(ex / fx, 1.0) - 0.01, 3), round(min(ey / fy, 1.0) - 0.01, 3))
for k, v in (('use_authored_reveal_material', True), ('reveal_actors', [splash]), ('fill_surface', water), ('fill_depth', depth),
             ('fill_empty_scale', empty), ('fill_seconds', 45.0), ('drain_seconds', 60.0), ('fill_followers', [splash]),
             ('fill_trims_reveal', True), ('is_on', False)):
    tf.set_editor_property(k, v)
log.append('Tub_Faucet stream (%.1f, %.1f, %.1f) -> (%.1f, %.1f, %.1f) pitch %.2f, %.1f cm; water full z %.1f, floor %.1f, depth %.1f, '
           'span full %.1fx%.1f empty %.1fx%.1f -> empty scale (%.3f, %.3f); splash x %.1f'
           % (TOP.x, TOP.y, TOP.z, BOT.x, BOT.y, BOT.z, pitch, length, FULL_Z, floor_z, depth, fx, fy, ex, ey, empty.x, empty.y, sx))

# ---------------- kitchen: right knob ----------------
knob('Sink_Tap', 'Sink_Tap_R', 'Art_KI_SinkNarrow_R_tap', 'KitchenSinkTaps')

# ---------------- Lukey: under-sink target and drain spray ----------------
ms = acts['Malady_Sink']; xf = ms.get_actor_transform(); ms.modify()
assert L.set_current_level_by_name(ms.get_outer().get_outer().get_name())
BOX_MIN, BOX_MAX = unreal.Vector(165.0, 18.0, 1.0), unreal.Vector(265.0, 83.0, 67.0)   # under the basin: trap, bucket, puddle
b = ms.get_editor_property('body')
b.set_world_location((BOX_MIN + BOX_MAX) * 0.5, False, False)
size = xf.inverse_transform_direction(BOX_MAX - BOX_MIN)                        # world extents into actor axes
b.set_relative_scale3d(unreal.Vector(abs(size.x) / 100.0, abs(size.y) / 100.0, abs(size.z) / 100.0))
ms.set_editor_property('hover_outline', False); ms.set_editor_property('body_glow_overlay', False)
ms.get_editor_property('glow_light').set_world_location(unreal.Vector(215, 66, 42), False, False)
# spray: the upper slip nut of the trap (tailpiece/J-bend joint, nut z 40-45, front y 49.3) east into the open floor
NUT = unreal.Vector(216.0, 49.8, 42.5)
ms.set_editor_property('leak_spray_taps', [acts['Sink_Tap'], acts['Sink_Tap_R']])
ms.set_editor_property('leak_spray_origin', xf.inverse_transform_location(NUT))
ms.set_editor_property('leak_spray_direction', xf.inverse_transform_direction(unreal.Vector(0.75, 0.6, 0.3)))
ms.set_editor_property('leak_spray_cone', 22.0); ms.set_editor_property('leak_spray_speed', unreal.Vector2D(70.0, 135.0))
ms.set_editor_property('leak_spray_rate', 55.0)
ms.set_editor_property('leak_spray_floor_z', xf.inverse_transform_location(unreal.Vector(0, 0, 0.4)).z)
log.append('Malady_Sink proxy x%.0f-%.0f y%.0f-%.0f z%.0f-%.0f (local scale %s), hover shell/glow overlay off; spray nut %s'
           % (BOX_MIN.x, BOX_MAX.x, BOX_MIN.y, BOX_MAX.y, BOX_MIN.z, BOX_MAX.z, b.get_editor_property('relative_scale3d'), NUT))

assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 water controls]\n' + '\n'.join(log))
