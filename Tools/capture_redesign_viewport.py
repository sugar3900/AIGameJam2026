#!/usr/bin/env python3
"""Capture redesign review shots through the real editor viewport (Lumen GI/reflections),
unlike SceneCapture2D actors, which do not render Lumen in this project.

    python3 Tools/capture_redesign_viewport.py [shot ...] [--out DIR]
Shot names/cameras are shared with Tools/Editor/capture_redesign_rooms.py. Each shot sets the
level-viewport camera in game view, issues HighResShot, and waits for the file (async, needs ticks).
"""
import argparse, os, re, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src = open(os.path.join(ROOT, 'Tools/Editor/capture_redesign_rooms.py')).read()
SHOTS = eval(re.search(r'SHOTS = (\[.*?\])\n', src, re.S).group(1))
ap = argparse.ArgumentParser(); ap.add_argument('shots', nargs='*'); ap.add_argument('--out', default=os.path.join(ROOT, 'Saved/ApartmentProgress/review'))
ap.add_argument('--size', default='1200x800'); args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
for name, eye, tgt in SHOTS:
    if args.shots and name not in args.shots: continue
    path = os.path.join(args.out, name + '.png')
    if os.path.exists(path): os.remove(path)
    cmd = f'''
import math, unreal
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
eye, tgt = {eye}, {tgt}
dx, dy, dz = (t - e for t, e in zip(tgt, eye))
UES.set_level_viewport_camera_info(unreal.Vector(*eye), unreal.Rotator(roll=0, pitch=math.degrees(math.atan2(dz, math.hypot(dx, dy))), yaw=math.degrees(math.atan2(dy, dx))))
unreal.SystemLibrary.execute_console_command(UES.get_editor_world(), 'HighResShot {args.size} filename="{path}"')
'''
    subprocess.run([sys.executable, os.path.join(ROOT, 'Tools/run_in_editor.py'), '-c', cmd], capture_output=True)
    for _ in range(60):
        if os.path.exists(path) and os.path.getsize(path) > 0: break
        time.sleep(1)
    time.sleep(1)
    print(name, 'ok' if os.path.exists(path) else 'TIMEOUT')
