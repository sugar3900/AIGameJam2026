#!/usr/bin/env python3
"""Switch all character materials in the open editor; stop PIE first."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('style', choices=('original', 'illustrated', 'matte', 'cel'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    script = str(root / 'Tools/Editor/style_characters.py')
    command = f"import runpy; runpy.run_path({script!r}, init_globals={{'STYLE': {args.style!r}}})"
    return subprocess.call([sys.executable, str(root / 'Tools/run_in_editor.py'), '-c', command])


if __name__ == '__main__':
    sys.exit(main())
