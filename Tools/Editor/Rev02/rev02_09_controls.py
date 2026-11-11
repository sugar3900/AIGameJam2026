"""Wire room light circuits, paired closet doors, and walk-away closing on the loaded Rev02 map.

Run with Tools/run_in_editor.py after building the native linked-toggle properties.
Re-runnable; also called by rev02_05_gameplay so rebuilding gameplay preserves the wiring.
"""
import unreal

A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not W.get_game_world(), 'Stop PIE before wiring controls'
assert W.get_editor_world().get_name() == 'L_Apartment_Rev02', 'Open the Rev02 map first'
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}

# Existing switch art already sits on the room-facing side of the relevant wall.
SWITCH_ART = {
    'bedroom': 'Art_BA_Switch_BA_Switch_Plate_S068',
    'office': 'Art_BA_Switch_BA_Switch_Plate_S075',
    'bathroom': 'Art_BA_Switch_BA_Switch_Plate',
    'kitchen': 'Art_BA_Switch_BA_Switch_Plate_S086',
}
# Entry controls share the east wall, beyond the door trim; hallway has its own circuit.
NEW_SWITCHES = {
    'living': ((1194, 535, 114), 90),
    'entry_sconce': ((1194, 520, 114), 90),
    'hall': ((430, 386, 114), 0),
    'closet': ((214, 520, 114), 90),
}
FIXTURES = {
    'living': ('Living', 'CeilingLight_Living'),
    'hall': ('HallWest', 'CeilingLight_HallWest'),
    # This fixture moved to the kitchen in Rev02, despite its legacy label.
    'kitchen': ('HallEast', 'CeilingLight_HallEast'),
    'bedroom': ('Bedroom', 'CeilingLight_Bedroom'),
    'bathroom': ('Bath', 'CeilingLight_Bath'),
    'office': ('Office', 'CeilingLight_Office'),
}
# FIX-029/021: the closet light is the pull-chain interactable Light_Closet (pendant + C-50 doorway fill + glass/filament
# glow, all one toggle). The closet wall switch joins its circuit group instead of driving a standalone light, so the
# switch and the chain always agree. Legacy maps without it still use the old always-on Bulb_Closet.
CLOSET_INTERACTIVE = 'Light_Closet' in acts
required = list(SWITCH_ART.values()) + ['Wardrobe_Door_L', 'Wardrobe_Door_R', 'Light_Closet' if CLOSET_INTERACTIVE else 'Bulb_Closet',
                                      'Art_BA_Switch_BA_Switch_Toggle', 'Sconce_Hall_2', 'Sconce_Hall_1', 'Sconce_Kitchen']
required += ['Art_CeilingLight_%s_Glass' % name for name, _ in FIXTURES.values()]
assert all(k in acts for k in required), 'Missing required Rev02 art or gameplay actors'


def group(room):
    return unreal.Name('Overhead_' + room)


def interactable(label, transform):
    a = acts.get(label)
    if a is None:
        a = A.spawn_actor_from_class(unreal.FixHimInteractable, transform.translation, transform.rotation.rotator())
        a.set_actor_label(label)
        acts[label] = a
    a.modify()
    return a


def copy_body(a, art):
    src = art.static_mesh_component
    body = a.get_editor_property('body')
    body.modify()
    body.set_static_mesh(src.static_mesh)
    body.set_world_transform(src.get_world_transform(), False, False)
    for i in range(src.get_num_materials()):
        body.set_material(i, src.get_material(i))
    a.set_editor_property('use_authored_body_materials', True)
    art.modify()
    src.modify()
    art.set_actor_hidden_in_game(True)
    src.set_visibility(False)
    src.set_collision_profile_name('NoCollision')
    tags = list(art.tags)
    if unreal.Name('GameplayBodySource') not in tags:
        tags.append(unreal.Name('GameplayBodySource'))
    art.tags = tags


def duplicate_art(source_label, label, position, yaw):
    a = acts.get(label)
    if a is None:
        a = A.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*position), unreal.Rotator(yaw=yaw))
        a.set_actor_label(label)
        acts[label] = a
    a.modify()
    src = acts[source_label].static_mesh_component
    dst = a.static_mesh_component
    dst.modify()
    dst.set_static_mesh(src.static_mesh)
    for i in range(src.get_num_materials()):
        dst.set_material(i, src.get_material(i))
    a.set_actor_location_and_rotation(unreal.Vector(*position), unreal.Rotator(yaw=yaw), False, True)
    a.set_actor_scale3d(acts[source_label].get_actor_scale3d())
    a.set_folder_path('Gameplay/WallSwitches')
    return a


# Both leaves keep their own opposite hinge rotations, but always receive the same requested state.
door_state = acts['Wardrobe_Door_L'].get_editor_property('is_on')
for name in ('Wardrobe_Door_L', 'Wardrobe_Door_R'):
    a = acts[name]
    a.modify()
    a.set_editor_property('toggle_group', unreal.Name('MalcolmClosetDoors'))
    a.set_editor_property('is_on', door_state)

states = {}
for room, (art_name, label) in FIXTURES.items():
    art = acts['Art_CeilingLight_%s_Glass' % art_name]
    is_new = label not in acts
    a = interactable(label, art.get_actor_transform())
    if is_new:
        copy_body(a, art)
        a.set_editor_property('is_on', True)
        a.set_editor_property('light_intensity_on', 2200.0)
        light = a.get_editor_property('light')
        light.set_world_location(art.get_actor_location() + unreal.Vector(0, 0, -25), False, False)
    a.set_editor_property('toggle', unreal.InteractToggle.LIGHT)
    a.set_editor_property('room_id', room)
    a.set_editor_property('toggle_group', group(room))
    a.set_editor_property('enabled', False)
    a.set_editor_property('shine', False)
    a.set_folder_path('Gameplay/OverheadLights/' + room)
    states[room] = a.get_editor_property('is_on')

sconce = acts['Sconce_Hall_2']
sconce.modify()
sconce.set_editor_property('toggle_group', group('entry_sconce'))
sconce.set_editor_property('enabled', False)
sconce.set_editor_property('shine', False)
states['entry_sconce'] = sconce.get_editor_property('is_on')

for room, label in (('kitchen', 'Sconce_Kitchen'), ('hall', 'Sconce_Hall_1')):
    fixture = acts[label]
    fixture.modify()
    fixture.set_editor_property('toggle_group', group(room))
    fixture.set_editor_property('enabled', False)
    fixture.set_editor_property('shine', False)
    fixture.set_editor_property('is_on', states[room])

# Absolute positions keep regeneration idempotent, including the visible rocker.
KITCHEN_SWITCH_Y = 217.0
for label in ('Art_BA_Switch_BA_Switch_Plate_S086', 'Art_BA_Switch_BA_Switch_Toggle_S086'):
    art = acts[label]
    art.modify()
    # user correction: left of the kitchen portal (from the kitchen), 10 cm clear of the north casing (y 232)
    art.set_actor_location(unreal.Vector(474.075, KITCHEN_SWITCH_Y, 114), False, True)

for a in acts.values():
    if isinstance(a, unreal.FixHimInteractable):
        a.modify()
        a.set_editor_property('shine_strength', 0.65)
        prompt = str(a.get_editor_property('prompt_off')).lower()
        if a.get_editor_property('toggle') in (unreal.InteractToggle.SLIDE, unreal.InteractToggle.ROTATE):
            a.modify()
            a.set_editor_property('auto_close_on_walk_away', any(word in prompt for word in
                                  ('drawer', 'oven', 'pantry', 'cupboard', 'cabinet', 'fridge')))

states['closet'] = True
if CLOSET_INTERACTIVE:
    lc = acts['Light_Closet']; lc.modify()
    lc.set_editor_property('toggle_group', group('closet'))
    states['closet'] = lc.get_editor_property('is_on')
for room in list(FIXTURES) + ['closet', 'entry_sconce']:
    if room in SWITCH_ART:
        plate = acts[SWITCH_ART[room]]
    else:
        position, yaw = NEW_SWITCHES[room]
        plate = duplicate_art('Art_BA_Switch_BA_Switch_Plate', 'Art_WallSwitch_' + room + '_Plate', position, yaw)
        duplicate_art('Art_BA_Switch_BA_Switch_Toggle', 'Art_WallSwitch_' + room + '_Toggle', position, yaw)
    a = interactable('WallSwitch_' + room, plate.get_actor_transform())
    a.set_actor_transform(plate.get_actor_transform(), False, True)
    copy_body(a, plate)
    # The small rocker remains visible but must not intercept the plate's click trace.
    rocker_label = (SWITCH_ART[room].replace('_Plate', '_Toggle') if room in SWITCH_ART
                    else 'Art_WallSwitch_' + room + '_Toggle')
    rocker = acts[rocker_label].static_mesh_component
    rocker.modify()
    rocker.set_collision_profile_name('NoCollision')
    a.set_editor_property('room_id', 'bedroom' if room == 'closet' else 'hall' if room == 'entry_sconce' else room)
    a.set_editor_property('toggle_group', group(room))
    a.set_editor_property('toggle', unreal.InteractToggle.LIGHT)
    a.set_editor_property('light_intensity_on', 0.0)
    a.set_editor_property('on_emissive', unreal.LinearColor(0, 0, 0, 1))
    a.set_editor_property('enabled', True)
    a.set_editor_property('is_on', states[room])
    target = {'closet': 'closet light', 'entry_sconce': 'entry sconce',
              'kitchen': 'kitchen lights', 'hall': 'hallway lights'}.get(room, 'overhead light')
    a.set_editor_property('prompt_off', 'Turn on ' + target)
    a.set_editor_property('prompt_on', 'Turn off ' + target)
    a.set_editor_property('interact_sfx', unreal.Name('SwitchOn'))
    a.set_editor_property('interact_sfx_off', unreal.Name('SwitchOff'))
    a.set_editor_property('controlled_lights', [acts['Bulb_Closet']] if room == 'closet' and not CLOSET_INTERACTIVE else [])
    a.set_folder_path('Gameplay/WallSwitches')

assert L.save_all_dirty_levels()
unreal.log('[Rev02 controls] Linked both Malcolm doors; wired eight wall switches and disabled direct ceiling/sconce clicks')
