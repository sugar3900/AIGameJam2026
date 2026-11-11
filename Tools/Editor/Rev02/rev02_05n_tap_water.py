"""Rev02 step 5n (batch 2, sink water): the kitchen Sink_Tap's running water uses authored materials instead of the
generic tinted reveal cylinder. Needs the FixHimInteractable opt-in (bUseAuthoredRevealMaterial, RevealActors). Re-runnable.

- Stream: the tap's RevealPart keeps its slim cylinder from the KI-FAUCET-02 outlet down to the basin floor (measured by
  a trace this run), ~1.4 cm thick, with MI_Rev02_TapStream (lit translucent water, panning streaks, RevealAlpha fade).
- Splash: Art_KI_SinkSplash, an 18 cm plane 3 mm above the basin floor where the stream lands, MI_Rev02_TapSplash
  (time-driven expanding rings), in RevealActors, so it shows/fades with the stream. NoCollision, no shadow.
Toggle, prompts, room, save state and the tap click body are unchanged.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MATS = '/Game/ICanFixHim/Environment/Rev02/Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
tap = acts['Sink_Tap']
SPOUT = (215.0, 50.05, 123.0)          # KI-FAUCET-02 outlet (rev02_05_gameplay FIX-027)
world = unreal.EditorLevelLibrary.get_editor_world()
rp = tap.get_editor_property('reveal_part')
hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(SPOUT[0], SPOUT[1], SPOUT[2] - 2), unreal.Vector(SPOUT[0], SPOUT[1], 40),
                                             unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [tap], unreal.DrawDebugTrace.NONE, True)
floor = hit.to_tuple()[4].z if hit and hit.to_tuple()[0] else 70.0
h = SPOUT[2] - floor
tap.modify()
rp.set_world_location(unreal.Vector(SPOUT[0], SPOUT[1], floor + h / 2), False, False)
rp.set_world_scale3d(unreal.Vector(0.014, 0.014, h / 100.0)); rp.set_cast_shadow(False)
rp.set_material(0, EAL.load_asset(MATS + 'MI_Rev02_TapStream'))
if 'Art_KI_SinkSplash' in acts: A.destroy_actor(acts.pop('Art_KI_SinkSplash'))
assert L.set_current_level_by_name(tap.get_outer().get_outer().get_name())
sp = A.spawn_actor_from_object(EAL.load_asset('/Engine/BasicShapes/Plane'), unreal.Vector(SPOUT[0], SPOUT[1], floor + 0.3), unreal.Rotator(0, 0, 0))
sp.set_actor_label('Art_KI_SinkSplash'); sp.set_folder_path('Gameplay/Interactables/kitchen')
sp.set_actor_scale3d(unreal.Vector(0.18, 0.18, 1))
c = sp.static_mesh_component; c.set_collision_profile_name('NoCollision'); c.set_cast_shadow(False)
c.set_material(0, EAL.load_asset(MATS + 'MI_Rev02_TapSplash'))
on = tap.get_editor_property('is_on')
sp.set_actor_hidden_in_game(not on); c.set_visibility(on)
tap.set_editor_property('use_authored_reveal_material', True)
tap.set_editor_property('reveal_actors', [sp])
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 tap water] basin floor z %.1f (trace %s), stream %.1f cm, splash at z %.1f, is_on=%s'
           % (floor, bool(hit and hit.to_tuple()[0]), h, floor + 0.3, on))
