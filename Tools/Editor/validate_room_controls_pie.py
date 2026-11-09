"""Regression checks for linked closet doors and wall-operated overhead lights. Run during Rev02 PIE."""
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert w, 'Start PIE first'
actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimInteractable)
by = {a.get_actor_label(): a for a in actors}
pc = unreal.GameplayStatics.get_player_controller(w, 0)
original = {a: a.get_editor_property('is_on') for a in actors}


def on(a):
    return a.get_editor_property('is_on')


def states():
    return {a: on(a) for a in actors}


def unchanged_except(before, allowed):
    assert all(on(a) == state for a, state in before.items() if a not in allowed), 'Unrelated control changed'


try:
    left, right = by['Wardrobe_Door_L'], by['Wardrobe_Door_R']
    before = states()
    for opener, closer in ((left, right), (right, left)):
        opener.set_on(False, True)
        opener.interact(pc)
        assert on(left) and on(right), 'Opening either door must open both'
        closer.interact(pc)
        assert not on(left) and not on(right), 'Closing either door must close both'
    right.set_on(True, True)
    assert abs(left.get_editor_property('pivot').get_editor_property('relative_rotation').yaw - 95) < 0.1
    assert abs(right.get_editor_property('pivot').get_editor_property('relative_rotation').yaw + 95) < 0.1
    unchanged_except(before, {left, right})
    unreal.log('[Controls test] both door directions, opposite hinges, and unrelated state passed')

    fixtures = {'living': 'CeilingLight_Living', 'hall': 'CeilingLight_HallWest',
                'kitchen': 'CeilingLight_HallEast', 'bedroom': 'CeilingLight_Bedroom',
                'bathroom': 'CeilingLight_Bath', 'office': 'CeilingLight_Office',
                'entry_sconce': 'Sconce_Hall_2'}
    for room, label in fixtures.items():
        switch, light = by['WallSwitch_' + room], by[label]
        extra = by.get({'kitchen': 'Sconce_Kitchen', 'hall': 'Sconce_Hall_1'}.get(room, ''))
        circuit = {switch, light} | ({extra} if extra else set())
        before = states()
        assert switch.can_interact() and not light.can_interact(), room + ': wrong interaction eligibility'
        assert switch.get_editor_property('room_id') == light.get_editor_property('room_id') == ('hall' if room == 'entry_sconce' else room)
        switch.set_on(False, True)
        assert light.get_editor_property('light').get_editor_property('intensity') == 0
        light.interact(pc)
        assert not on(light) and not on(switch), room + ': ceiling accepted direct interaction'
        switch.interact(pc)
        assert on(light) and on(switch), room + ': wall switch failed to turn on fixture'
        switch.set_on(True, True)
        assert light.get_editor_property('light').get_editor_property('intensity') > 0
        switch.interact(pc)
        assert not on(light) and not on(switch), room + ': wall switch failed to turn off fixture'
        if extra:
            assert not extra.can_interact() and not on(extra)
            extra.interact(pc)
            assert not on(extra), room + ': sconce accepted direct interaction'
            switch.set_on(True, True)
            assert on(extra) and extra.get_editor_property('light').get_editor_property('intensity') > 0
            switch.set_on(False, True)
            assert not on(extra) and extra.get_editor_property('light').get_editor_property('intensity') == 0
        unchanged_except(before, circuit)
        unreal.log('[Controls test] %s switch, light output, disabled ceiling click, isolation passed' % room)

    closet_switch = by['WallSwitch_closet']
    bulb = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.PointLight)
                if a.get_actor_label() == 'Bulb_Closet')
    component = bulb.get_component_by_class(unreal.PointLightComponent)
    closet_switch.set_on(False, True)
    assert not component.is_visible(), 'Closet light did not turn off (check PIE soft-reference resolution)'
    closet_switch.interact(pc)
    assert component.is_visible(), 'Closet light did not turn on'

    living_pos = by['WallSwitch_living'].get_actor_location()
    sconce_pos = by['WallSwitch_entry_sconce'].get_actor_location()
    assert abs(living_pos.x - sconce_pos.x) < 0.1 and abs(living_pos.z - sconce_pos.z) < 0.1
    assert abs(living_pos.y - sconce_pos.y - 15) < 0.1, 'Entry switches must sit side by side'
    all_by = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)}
    door_center, door_extent = all_by['Door_Entry_Frame'].get_actor_bounds(False)
    closet_center, closet_extent = all_by['Art_CoatCloset_Frame'].get_actor_bounds(False)
    for name in ('WallSwitch_living', 'WallSwitch_entry_sconce'):
        center, extent, _ = unreal.SystemLibrary.get_component_bounds(by[name].get_editor_property('body'))
        assert center.y - extent.y > door_center.y + door_extent.y + 2
        assert center.y + extent.y < closet_center.y - closet_extent.y - 2

    # Verify the actual click traces, including switches made from formerly decorative wall art.
    for room in list(fixtures) + ['closet']:
        switch = by['WallSwitch_' + room]
        center, _, _ = unreal.SystemLibrary.get_component_bounds(switch.get_editor_property('body'))
        # Switch meshes face local +Y; start in the room at eye height, in interaction range.
        start = center + switch.get_actor_right_vector() * 70 + unreal.Vector(0, 0, 46)
        hit = unreal.SystemLibrary.line_trace_single(w, start, center, unreal.TraceTypeQuery.ECC_VISIBILITY,
                                                    False, [], unreal.DrawDebugTrace.NONE, True)
        assert hit and hit.to_dict()['hit_actor'] == switch, room + ': wall switch click is obstructed'
    unreal.log('[Controls test] closet circuit and all eight wall-switch click traces passed')
finally:
    for a, state in original.items():
        a.set_on(state, True)

unreal.log('[Controls test] PASS')
