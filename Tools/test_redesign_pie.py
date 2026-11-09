#!/usr/bin/env python3
"""Drive a PIE session of the currently open editor map with FixHim console commands and collect
screenshots (Saved/Screenshots/FixHim/<name>.png) and FixHimDump log lines.

    python3 Tools/test_redesign_pie.py "FixHimNewGame Rosie" "wait 4" "shot new_game" "dump" ... "stop"
Steps: 'wait N' sleeps on the host (the editor keeps ticking), 'shot NAME' -> FixHimShot,
'dump' -> FixHimDump, 'start'/'stop' begin/end PIE; anything else is sent as a console command.
"""
import os, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RUN = [sys.executable, os.path.join(ROOT, 'Tools/run_in_editor.py'), '--timeout', '60', '-c']
def editor(code):
    r = subprocess.run(RUN + [code], capture_output=True, text=True)
    return [l for l in (r.stdout + r.stderr).splitlines() if 'PIE|' in l or 'LogFixHim' in l or 'Error' in l]
CMD = '''
import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if not w: unreal.log('PIE| no game world')
else:
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    unreal.SystemLibrary.execute_console_command(w, %r, pc)
    p = pc.get_controlled_pawn() if pc else None
    unreal.log('PIE| ran %%s pawn=%%s' %% (%r, p.get_actor_location() if p else None))
'''
for step in sys.argv[1:]:
    if step == 'start':
        print(editor("import unreal\nunreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()\nunreal.log('PIE| start requested')"))
    elif step == 'stop':
        print(editor("import unreal\nunreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()\nunreal.log('PIE| stop requested')"))
    elif step.startswith('wait '):
        time.sleep(float(step[5:]))
    else:
        cmd = 'FixHimShot ' + step[5:] if step.startswith('shot ') else ('FixHimDump' if step == 'dump' else step)
        print(step, '->', editor(CMD % (cmd, cmd)))
