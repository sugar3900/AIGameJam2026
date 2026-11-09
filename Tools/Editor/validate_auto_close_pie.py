"""During free-walk PIE, verify every authored auto-closing door/drawer near and far.

Runs over several frames; results are logged and written to Saved/AutoCloseTest.txt.
Restores the original player transform and object states on completion or failure.
"""
import pathlib
import time
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(w, 0)
assert pc.get_state() == unreal.FixHimState.PLAYING
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
original_transform = pawn.get_actor_transform()
actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimInteractable)
targets = [a for a in actors if a.get_editor_property('auto_close_on_walk_away')]
assert targets
original = {a: a.get_editor_property('is_on') for a in targets}
result = pathlib.Path(unreal.Paths.project_saved_dir()) / 'AutoCloseTest.txt'
result.write_text('RUNNING')
state = {'index': 0, 'phase': 'open', 'deadline': 0}


def finish(message):
    unreal.unregister_slate_post_tick_callback(state['handle'])
    pawn.set_actor_transform(original_transform, False, True)
    for a, is_on in original.items():
        a.set_on(is_on, True)
    result.write_text(message)
    unreal.log('[Auto-close test] ' + message)


def tick(delta):
    if time.monotonic() < state['deadline']:
        return
    try:
        a = targets[state['index']]
        body = a.get_editor_property('body')
        if state['phase'] == 'open':
            a.set_on(False, True)
            center, _, _ = unreal.SystemLibrary.get_component_bounds(body)
            state['center'] = center
            pawn.set_actor_location(center + unreal.Vector(0, 100, 100), False, True)
            a.set_on(True, True)
            state['phase'] = 'near'
        elif state['phase'] == 'near':
            assert a.get_editor_property('is_on'), a.get_actor_label() + ' closed while nearby'
            pawn.set_actor_location(state['center'] + unreal.Vector(0, 1000, 100), False, True)
            state['phase'] = 'far'
        else:
            assert not a.get_editor_property('is_on'), a.get_actor_label() + ' stayed open after walking away'
            unreal.log('[Auto-close test] PASS ' + a.get_actor_label())
            state['index'] += 1
            state['phase'] = 'open'
            if state['index'] == len(targets):
                finish('PASS: %d doors and drawers stay open nearby and close at distance' % len(targets))
                return
        state['deadline'] = time.monotonic() + 0.6
    except Exception as exc:
        finish('FAIL: ' + str(exc))


state['handle'] = unreal.register_slate_post_tick_callback(tick)
