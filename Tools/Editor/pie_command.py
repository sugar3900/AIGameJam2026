"""Helpers for driving Play-In-Editor from Tools/run_in_editor.py (used for automated playtests)."""
import unreal


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def start():
    if not world():
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        unreal.log("[FixHim] PIE requested")


def stop():
    if world():
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        unreal.log("[FixHim] PIE stop requested")


def run(cmd):
    w = world()
    if not w:
        unreal.log_warning("[FixHim] No PIE world")
        return
    unreal.SystemLibrary.execute_console_command(w, cmd)
    unreal.log(f"[FixHim] ran: {cmd}")


def aim_at(x, y, z, passes=3):
    """Point the player's view at a world location (spring-arm camera needs a few passes)."""
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    cam = unreal.GameplayStatics.get_player_camera_manager(w, 0)
    for _ in range(passes):
        loc = cam.get_camera_location()
        r = unreal.MathLibrary.find_look_at_rotation(loc, unreal.Vector(x, y, z))
        pc.set_control_rotation(r)
    unreal.log(f"[FixHim] aimed from {cam.get_camera_location()} at ({x},{y},{z})")
