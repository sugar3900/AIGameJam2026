"""From free-walk PIE, verify Tyler's first reveal and separate capture-only portrait materials."""
import pathlib
import time
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(w, 0)
assert pc.get_state() == unreal.FixHimState.PLAYING
unreal.SystemLibrary.execute_console_command(w, 'FixHimSetFixed tyler 0')
hunk = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimHunk)
            if a.get_editor_property('hunk_id') == 'tyler')
portrait = hunk.get_editor_property('portrait_mesh')
assert portrait.get_editor_property('visible_in_scene_capture_only')
for i in range(hunk.mesh.get_num_materials()):
    world_material = hunk.mesh.get_material(i)
    portrait_material = portrait.get_material(i)
    assert world_material != portrait_material
    assert world_material.get_scalar_parameter_value('Dissolve') == 0
    assert portrait_material.get_scalar_parameter_value('Dissolve') == 1
result = pathlib.Path(unreal.Paths.project_saved_dir()) / 'CharacterRevealTest.txt'
result.write_text('RUNNING')
state = {'last': 0, 'partial': 0, 'samples': 0, 'start': time.monotonic()}


def finish(message):
    unreal.unregister_slate_post_tick_callback(state['handle'])
    result.write_text(message)
    unreal.log('[Character reveal test] ' + message)


def tick(delta):
    try:
        value = hunk.mesh.get_material(0).get_scalar_parameter_value('Dissolve')
        assert value >= state['last'], 'Reveal became fully visible and then reset'
        state['last'] = value
        state['samples'] += 1
        state['partial'] += int(0 < value < 1)
        assert portrait.get_material(0).get_scalar_parameter_value('Dissolve') == 1
        if time.monotonic() - state['start'] > 3:
            assert value == 1 and state['partial'] > 2
            finish('PASS: %d frames, %d partially dissolved; portrait materials stay independent' %
                   (state['samples'], state['partial']))
    except Exception as exc:
        finish('FAIL: ' + str(exc))


state['handle'] = unreal.register_slate_post_tick_callback(tick)
unreal.SystemLibrary.execute_console_command(w, 'FixHimTalk tyler')
assert hunk.mesh.get_material(0).get_scalar_parameter_value('Dissolve') == 0
