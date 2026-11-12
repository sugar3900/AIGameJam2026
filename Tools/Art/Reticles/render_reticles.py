#!/usr/bin/env python3
"""macOS: rasterize the approved individual SVGs with the repository's AppKit renderer.
Run from any directory: python3 Tools/Art/Reticles/render_reticles.py
No artwork is redrawn; unavailable is retained only in the design source, not imported.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'Art Source/UI Concepts/Selected 07/Foundation 02/Reticles'
OUTPUT = ROOT / 'Art Source/UI/Reticles'
STATES = {'default': 'Default', 'inspect': 'Inspect', 'talk': 'Talk', 'use': 'Use', 'end-day': 'EndDay'}

if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for source, name in STATES.items():
        subprocess.run(['swift', str(ROOT / 'Tools/render_svg.swift'), str(SOURCE / f'{source}.svg'),
                        str(OUTPUT / f'T_Reticle_{name}.png'), '128'], check=True)
