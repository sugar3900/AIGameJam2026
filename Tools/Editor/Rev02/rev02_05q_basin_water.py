"""Rev02 step 5q (user feedback round 3): BA-BASIN-01 taps run independently with authored water.

Left tap (Basin_Tap): its generic tinted reveal cylinder hung 5 cm off the spout. Both spout outlets were measured from
the basin's chrome (lowest chrome in each tap column, z 84.8) and the bowl under them by trace; the stream now runs from
the outlet to the bowl with MI_Rev02_BasinStream (lit translucent water, streaks, wobble anchored at the spout) through
the FixHimInteractable authored-reveal opt-in, plus a splash plane (MI_Rev02_TapSplash) in RevealActors.
Right tap (new Basin_Tap_R): a duplicate of Basin_Tap (same room, prompts, REVEAL toggle and body collision), its click
body taken from the right-tap art (hidden source pattern, GameplayBodySource), its own stream and splash. The two taps
toggle independently. Water and splash are NoCollision and excluded from hover/outline. Re-runnable.
"""
import unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
MATS = '/Game/ICanFixHim/Environment/Rev02/Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
_missing = [l for l in ['Basin_Tap', 'Art_BA_Basin_BA_BA_BasinTap_R', 'Art_BA_Basin_BA_BasinBody'] if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
world = unreal.EditorLevelLibrary.get_editor_world()
log = []
CYL = EAL.load_asset('/Engine/BasicShapes/Cylinder'); PLANE = EAL.load_asset('/Engine/BasicShapes/Plane')

# basin stream MI (wobble anchored at the basin spout height); created here so rev02_02b need not be re-run
path = MATS + 'MI_Rev02_BasinStream'
mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset('MI_Rev02_BasinStream', MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, EAL.load_asset(MATS + 'M_Rev02_WaterStream'))
for k, v in (('Opacity', 0.55), ('Streak', 0.55), ('Speed', 2.6), ('NormalBreakup', 0.45), ('WobbleAmp', 0.06), ('TopZ', 84.8)):
    MEL.set_material_instance_scalar_parameter_value(mi, k, v)
MEL.set_material_instance_vector_parameter_value(mi, 'BaseColor', unreal.LinearColor(0.16, 0.2, 0.22, 1))
EAL.save_asset(path)
splash_mi = EAL.load_asset(MATS + 'MI_Rev02_TapSplash')

# spout outlets: lowest chrome of each tap column on the basin body (world), measured round 3
SPOUT = {'L': (760.45, 774.5, 84.83), 'R': (760.45, 810.5, 84.83)}

left = acts['Basin_Tap']
if 'Basin_Tap_R' in acts: A.destroy_actor(acts.pop('Basin_Tap_R'))
for k in ('L', 'R'):
    l = 'Art_BA_BasinSplash_' + k
    if l in acts: A.destroy_actor(acts.pop(l))
assert L.set_current_level_by_name(left.get_outer().get_outer().get_name())
right = A.duplicate_actor(left, world, unreal.Vector(0, 0, 0))
right.set_actor_label('Basin_Tap_R'); right.set_folder_path(str(left.get_folder_path())); acts['Basin_Tap_R'] = right
art = acts['Art_BA_Basin_BA_BA_BasinTap_R']; src = art.static_mesh_component
rb = right.get_editor_property('body'); rb.set_static_mesh(src.static_mesh)
rb.set_world_location_and_rotation(art.get_actor_location(), art.get_actor_rotation(), False, False)
for i in range(src.get_num_materials()): rb.set_material(i, src.get_material(i))
art.modify(); art.set_actor_hidden_in_game(True); src.set_visibility(False); art.tags = [unreal.Name('GameplayBodySource')]

for k, tap in (('L', left), ('R', right)):
    sx, sy, sz = SPOUT[k]
    hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(sx, sy, sz - 0.5), unreal.Vector(sx, sy, 40), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                 True, [left, right], unreal.DrawDebugTrace.NONE, True).to_tuple()
    floor = hit[4].z if hit[0] else 72.2
    h = sz - floor
    tap.modify()
    rp = tap.get_editor_property('reveal_part'); rp.set_static_mesh(CYL)
    rp.set_world_location(unreal.Vector(sx, sy, floor + h / 2), False, False); rp.set_world_rotation(unreal.Rotator(0, 0, 0), False, False)
    rp.set_world_scale3d(unreal.Vector(0.011, 0.011, h / 100.0)); rp.set_cast_shadow(False); rp.set_material(0, mi)
    sp = A.spawn_actor_from_object(PLANE, unreal.Vector(sx, sy, floor + 0.3), unreal.Rotator(0, 0, 0))
    sp.set_actor_label('Art_BA_BasinSplash_' + k); sp.set_folder_path(str(left.get_folder_path())); acts[sp.get_actor_label()] = sp
    sp.set_actor_scale3d(unreal.Vector(0.09, 0.09, 1))
    c = sp.static_mesh_component; c.set_collision_profile_name('NoCollision'); c.set_cast_shadow(False); c.set_material(0, splash_mi)
    sp.set_actor_hidden_in_game(True); c.set_visibility(False)
    tap.set_editor_property('is_on', False)
    tap.set_editor_property('use_authored_reveal_material', True)
    tap.set_editor_property('reveal_actors', [sp])
    log.append('%s: spout (%.2f, %.2f, %.2f) -> bowl z %.2f (%s), stream %.1f cm, splash %s' % (tap.get_actor_label(), sx, sy, sz, floor,
               hit[9].get_actor_label() if hit[0] and hit[9] else 'trace miss', h, sp.get_actor_label()))
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 basin water]\n' + '\n'.join(log))
