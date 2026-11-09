"""Check the active conversation's headroom and face clearance at 16:9 during PIE."""
import math
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert w, 'Start PIE and enter a conversation first'
pc = unreal.GameplayStatics.get_player_controller(w, 0)
target = pc.get_view_target()
assert isinstance(target, unreal.FixHimMalady), 'Wait for the conversation camera blend to finish'
name = target.get_editor_property('hunk_id')
hunk = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimHunk)
            if a.get_editor_property('hunk_id') == name)
camera = target.get_editor_property('dialogue_camera')
transform = camera.get_world_transform()
half_height = math.tan(math.radians(camera.get_editor_property('field_of_view') / 2)) / (16 / 9)


def screen_y(position):
    local = transform.inverse_transform_location(position)
    assert local.x > 0, 'Character must be in front of the camera'
    return 0.5 - local.z / (2 * local.x * half_height)


head = hunk.mesh.get_socket_location('head')
origin, extent, _ = unreal.SystemLibrary.get_component_bounds(hunk.mesh)
crown = unreal.Vector(head.x, head.y, origin.z + extent.z)
face = head + unreal.Vector(0, 0, 8 * hunk.get_actor_scale3d().z)
crown_y, face_y = screen_y(crown), screen_y(face)
assert crown_y >= 0.05, '%s has insufficient headroom: %.3f' % (name, crown_y)
assert 0.12 < face_y < 0.60, '%s face overlaps the top edge or dialogue panel: %.3f' % (name, face_y)
if name == 'wyatt':
    toward = camera.get_world_location() - hunk.get_actor_location()
    toward.z = 0
    forward = hunk.get_actor_forward_vector()
    dot = (toward.x * forward.x + toward.y * forward.y) / math.hypot(toward.x, toward.y)
    assert dot > 0.995, 'Wyatt is not facing the conversation camera'
unreal.log('[Conversation framing] PASS %s: crown %.1f%%, face %.1f%% from top' %
           (name, crown_y * 100, face_y * 100))
