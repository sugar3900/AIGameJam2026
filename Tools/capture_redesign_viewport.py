#!/usr/bin/env python3
"""Capture redesign review shots through the real editor viewport (Lumen GI/reflections),
unlike SceneCapture2D actors, which do not render Lumen in this project.

    python3 Tools/capture_redesign_viewport.py [shot ...] [--out DIR] [--size WxH]
Shot names/cameras are shared with Tools/Editor/capture_redesign_rooms.py. Each shot sets the
level-viewport camera in game view, issues HighResShot, and waits for the file (async, needs ticks).
"""
import argparse, ast, os, re, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src = open(os.path.join(ROOT, 'Tools/Editor/capture_redesign_rooms.py')).read()
SHOTS = ast.literal_eval(re.search(r'SHOTS = (\[.*?\])\n', src, re.S).group(1))
ap = argparse.ArgumentParser(); ap.add_argument('shots', nargs='*')
ap.add_argument('--out', default=os.path.join(ROOT, 'Saved/ApartmentProgress/review'))
ap.add_argument('--size', default='1200x800'); args = ap.parse_args()
if not re.fullmatch(r'\d{2,5}x\d{2,5}', args.size):
    sys.exit('--size must look like 1200x800')
out = os.path.abspath(args.out)   # host and editor resolve relative paths differently
os.makedirs(out, exist_ok=True)
failed = 0
for name, eye, tgt in SHOTS:
    if args.shots and name not in args.shots: continue
    path = os.path.join(out, name + '.png')
    if os.path.exists(path): os.remove(path)
    console = 'HighResShot %s filename="%s"' % (args.size, path.replace('"', ''))
    # Every value is embedded with repr() so paths with quotes cannot break or inject into the editor code.
    cmd = '\n'.join([
        'import math, unreal',
        'UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)',
        'unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)',
        'eye, tgt = %r, %r' % (tuple(eye), tuple(tgt)),
        'dx, dy, dz = (t - e for t, e in zip(tgt, eye))',
        'UES.set_level_viewport_camera_info(unreal.Vector(*eye), unreal.Rotator(roll=0, pitch=math.degrees(math.atan2(dz, math.hypot(dx, dy))), yaw=math.degrees(math.atan2(dy, dx))))',
        'unreal.SystemLibrary.execute_console_command(UES.get_editor_world(), %r)' % console,
    ])
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'Tools/run_in_editor.py'), '-c', cmd], capture_output=True, text=True)
    if r.returncode != 0 or 'Error' in r.stdout + r.stderr:
        print(name, 'EDITOR ERROR:', (r.stdout + r.stderr).strip()[-300:]); failed += 1; continue
    for _ in range(60):
        if os.path.exists(path) and os.path.getsize(path) > 0: break
        time.sleep(1)
    time.sleep(1)
    ok = os.path.exists(path)
    failed += not ok
    print(name, 'ok' if ok else 'TIMEOUT')
sys.exit(1 if failed else 0)
