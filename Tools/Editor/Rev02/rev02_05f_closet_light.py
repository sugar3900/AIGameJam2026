"""Rev02 step 5f (FIX-029): BR-CLOSET-LIGHT-01 pull-chain pendant in the bedroom walk-in closet.

Source (README/assembly.json): functional-pivot local exports at identity. Hardware, glass and filament share the
ceiling mount (114,468,275); the chain hangs from its top attachment (118,474,264.5), rest bottom 201.5. Retires the
old pendant mesh (Art_BR_Closet02_Bulb) and the always-on Bulb_Closet point light.

Light_Closet (gameplay level, room bedroom, initially ON, 'Pull chain' both states): the chain is the click Body
(its single UCX, query-only: visibility traces only, never blocks the pawn); a click pulls it 1.5 cm and back over
0.25 s (bPullOnClick) and toggles, with the existing 0.29 s fade, the point light (60 lm, 2300 K, radius 8, specular
0.35, attenuation 260 at (114,468,250); the user's dim/warm tuning) and GlowStrength on the glass and filament
(GlowActors; authored GlowStrength = ON value, zero when off). Re-runnable. Run after rev02_05e.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'
KIT, MATS = R2 + 'BR_ClosetLight01/', R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
MOUNT, CHAIN_TOP, LIGHT_AT = (114, 468, 275), (118, 474, 264.5), (114, 468, 250)
SLOT = {'Closet_ClearAmberGlass': 'M_Rev02_ClosetGlass', 'Closet_Filament': 'M_Rev02_ClosetFilament'}

def mat_for(slot):
    return EAL.load_asset(MATS + SLOT.get(slot, 'MI_ClosetLight01_' + slot))

def place(part, loc, level):
    label = 'Art_BR_ClosetLight01_' + part
    if label in acts: A.destroy_actor(acts.pop(label))
    assert L.set_current_level_by_name(level)
    sm = EAL.load_asset(KIT + 'BR_ClosetLight01_' + part)
    a = A.spawn_actor_from_object(sm, unreal.Vector(*loc), unreal.Rotator(0, 0, 0))
    a.set_actor_label(label); a.set_folder_path('Redesign/Imported Art/Furnishing'); acts[label] = a
    c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
    # The pendant light sits inside this fixture: as shadow casters its wires/socket/filament threw huge sharp
    # radial spokes and a filament loop across the ceiling and walls. Fixture parts don't cast; the light still
    # shadows the room.
    c.set_cast_shadow(False)
    for i, s in enumerate(sm.static_materials): c.set_material(i, mat_for(str(s.material_slot_name)))
    return a

# keep the old light's shadow/volumetric settings, then retire the old pendant and light
old = acts.get('Bulb_Closet')
shadows = old.light_component.get_editor_property('cast_shadows') if old else True
for l in ('Art_BR_Closet02_Bulb', 'Bulb_Closet'):
    if l in acts: A.destroy_actor(acts.pop(l))

hw = place('Hardware', MOUNT, 'L_Apartment_Rev02')
glass = place('Glass', MOUNT, 'L_Apartment_Rev02_Gameplay')
fil = place('Filament', MOUNT, 'L_Apartment_Rev02_Gameplay')
chain = place('Chain', CHAIN_TOP, 'L_Apartment_Rev02_Gameplay')

assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
lc_actor = acts.get('Light_Closet')
if lc_actor is None:
    lc_actor = A.spawn_actor_from_class(unreal.FixHimInteractable, unreal.Vector(*CHAIN_TOP), unreal.Rotator(0, 0, 0))
    lc_actor.set_actor_label('Light_Closet'); lc_actor.set_folder_path('Gameplay/Interactables/bedroom')
a = lc_actor; a.modify()
a.set_actor_location_and_rotation(unreal.Vector(*CHAIN_TOP), unreal.Rotator(0, 0, 0), False, True)
for k, v in (('room_id', 'bedroom'), ('toggle', unreal.InteractToggle.LIGHT), ('prompt_off', 'Pull chain'), ('prompt_on', 'Pull chain'),
             ('is_on', True), ('light_intensity_on', 60.0), ('use_authored_body_materials', True),
             ('glow_actors', [glass, fil]), ('glow_param', 'GlowStrength'),
             ('pull_on_click', True), ('pull_offset', unreal.Vector(0, 0, -1.5)), ('pull_seconds', 0.25)):
    a.set_editor_property(k, v)
a.get_editor_property('pivot').set_relative_location(unreal.Vector(0, 0, 0), False, False)
# chain = click body at its art transform; the art copy is hidden (same pattern as rev02_05 body_from_art)
src = chain.static_mesh_component; body = a.get_editor_property('body')
body.set_static_mesh(src.static_mesh)
body.set_world_location_and_rotation(chain.get_actor_location(), chain.get_actor_rotation(), False, False)
for i in range(src.get_num_materials()): body.set_material(i, src.get_material(i))
body.set_cast_shadow(False)   # the chain hangs beside the bulb; same self-shadow reason as the fixture parts
body.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
body.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
body.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_BLOCK)
chain.set_actor_hidden_in_game(True); src.set_visibility(False); chain.tags = [unreal.Name('GameplayBodySource')]
lt = a.get_editor_property('light'); lt.modify()
lt.set_world_location(unreal.Vector(*LIGHT_AT), False, False)
lt.set_editor_property('intensity_units', unreal.LightUnits.LUMENS)
lt.set_editor_property('use_temperature', True); lt.set_editor_property('temperature', 2300.0)
lt.set_editor_property('light_color', unreal.Color(255, 255, 255, 255))
lt.set_editor_property('source_radius', 8.0); lt.set_editor_property('specular_scale', 0.35)
lt.set_editor_property('attenuation_radius', 260.0); lt.set_editor_property('cast_shadows', shadows)
# FIX-021 (art decision C-50): a weak broad doorway fill so Malcolm's face reads evenly under the dim warm pendant.
# Supplemental closet light, tied to the pull chain (ToggleLightActors: its authored 50 lm fades 50 -> 0 with the
# toggle). Just outside the closet doorway facing in, never a close source beside his head; no shadows, low specular.
if 'Light_ClosetDoorFill' in acts: A.destroy_actor(acts.pop('Light_ClosetDoorFill'))
fl = A.spawn_actor_from_class(unreal.PointLight, unreal.Vector(110, 590, 185), unreal.Rotator(0, 0, 0))
fl.set_actor_label('Light_ClosetDoorFill'); fl.set_folder_path('Gameplay/Interactables/bedroom'); acts['Light_ClosetDoorFill'] = fl
fc = fl.light_component; fc.set_mobility(unreal.ComponentMobility.MOVABLE)
for k, v in (('intensity_units', unreal.LightUnits.LUMENS), ('intensity', 50.0), ('use_temperature', True), ('temperature', 3100.0),
             ('source_radius', 45.0), ('soft_source_radius', 60.0), ('specular_scale', 0.1), ('attenuation_radius', 280.0),
             ('cast_shadows', False), ('light_color', unreal.Color(255, 255, 255, 255))):
    fc.set_editor_property(k, v)
a.set_editor_property('toggle_light_actors', [fl])
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
o, e = a.get_editor_property('body').get_editor_property('static_mesh').get_bounds().origin, None
cb = unreal.SystemLibrary.get_component_bounds(body)
unreal.log('[Rev02 closet light] (+ Light_ClosetDoorFill 50 lm 3100 K, chain-tied) Light_Closet chain z %.1f-%.1f, light (114,468,250) 60 lm 2300 K shadows=%s; old pendant/light retired'
           % (cb[0].z - cb[1].z, cb[0].z + cb[1].z, shadows))
