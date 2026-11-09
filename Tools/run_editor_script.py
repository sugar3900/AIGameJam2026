#!/usr/bin/env python3
"""Run an editor Python script in an isolated namespace, then drop it and gc.collect().

    python3 Tools/run_editor_script.py Tools/Editor/some_script.py [--set NAME=PYTHON_LITERAL ...]

Remote-exec scripts otherwise share the editor's __main__ namespace; stale actor wrappers kept
there across level reloads caused SIGSEGVs in Python GC (seen twice on 2026-11-08).
"""
import argparse, os, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('--set', action='append', default=[])
ap.add_argument('--timeout', default='1500'); a = ap.parse_args()
path = os.path.abspath(a.script)
pre = '\n'.join("_ns[%r] = %s" % tuple(s.split('=', 1)) for s in a.set)
cmd = f'''
import gc
_ns = {{'__file__': {path!r}, '__name__': '__main__'}}
{pre}
try:
    exec(compile(open({path!r}).read(), {path!r}, 'exec'), _ns)
finally:
    _ns.clear(); del _ns; gc.collect()
'''
sys.exit(subprocess.call([sys.executable, os.path.join(os.path.dirname(__file__), 'run_in_editor.py'), '--timeout', a.timeout, '-c', cmd]))
