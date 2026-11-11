"""Rev02 step 5o (batch 2, leak puddle wet sheen): Art_KI_SINK_damage_Film, a thin lit water film under Lukey's sink.

The DBuffer roughness decal (Art_KI_SINK_damage_Wet) could not produce a visible reflection, so it is hidden and replaced
by a dielectric film: an Engine plane 1.5 mm above the floor covering the decal footprint (68.2 x 86.2 cm), with
MI_Rev02_PuddleFilm (world-XY UVs on the same T_Leak_Puddle_Mask and centre as the stain decal; dithered soft edges;
roughness .04). The stain decal stays. The film carries the decal's RepairDamage/lukey tags and is attached to
Malady_Sink, so the existing repair rule hides it with the stain. NoCollision, no shadow. Re-runnable.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MEL = unreal.MaterialEditingLibrary
MATS = '/Game/ICanFixHim/Environment/Rev02/Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
dmg, wet, mal = acts['Art_KI_SINK_damage'], acts['Art_KI_SINK_damage_Wet'], acts['Malady_Sink']
c = dmg.get_actor_location(); sz = dmg.decal.get_editor_property('decal_size')     # (depth, half Y, half X)
SX, SY = sz.z * 2, sz.y * 2
mi = EAL.load_asset(MATS + 'MI_Rev02_PuddleFilm')
# world-XY UVs follow the README mask basis directly (u along +X, v along +Y), so no flips; verified against the stain
for k, v in (('CX', c.x), ('CY', c.y), ('SX', SX), ('SY', SY), ('FlipU', 0.0), ('FlipV', 0.0)): MEL.set_material_instance_scalar_parameter_value(mi, k, v)
EAL.save_loaded_asset(mi, False)
if 'Art_KI_SINK_damage_Film' in acts: A.destroy_actor(acts.pop('Art_KI_SINK_damage_Film'))
assert L.set_current_level_by_name(dmg.get_outer().get_outer().get_name())
f = A.spawn_actor_from_object(EAL.load_asset('/Engine/BasicShapes/Plane'), unreal.Vector(c.x, c.y, 0.15), unreal.Rotator(0, 0, 0))
f.set_actor_label('Art_KI_SINK_damage_Film'); f.set_folder_path(str(dmg.get_folder_path()))
f.set_actor_scale3d(unreal.Vector(SX / 100.0, SY / 100.0, 1))
fc = f.static_mesh_component; fc.set_collision_profile_name('NoCollision'); fc.set_cast_shadow(False); fc.set_material(0, mi)
# Movable: UE refuses to attach a Static root under the movable malady, and the repair rule only reaches attached actors
fc.set_mobility(unreal.ComponentMobility.MOVABLE)
f.tags = [t for t in dmg.tags if str(t) != 'AuthoredLeakDamage']
f.attach_to_actor(mal, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
assert f.get_attach_parent_actor() == mal, 'film not attached to Malady_Sink'
f.set_actor_hidden_in_game(dmg.get_editor_property('hidden'))
wet.modify(); wet.set_actor_hidden_in_game(True); wet.decal.set_visibility(False)
wet.tags = [t for t in wet.tags if str(t) != 'RepairDamage']     # retired: never re-shown by the repair rule
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 puddle film] centre (%.2f, %.2f) size %.1f x %.1f, tags %s, parent %s' % (c.x, c.y, SX, SY, [str(t) for t in f.tags], f.get_attach_parent_actor().get_actor_label()))
