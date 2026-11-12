#!/usr/bin/env python3
"""macOS: split the approved reticle SVGs into animation layers and rasterize them.
Run from any directory: python3 Tools/Art/Reticles/render_reticles.py

Layers (all on the shared 64-unit viewBox, so they stack centered with no offsets):
  T_Reticle_Background   ink disc behind actionable icons (fill of the contextual outer circle)
  T_Reticle_Ring         ink outline + white rim, identical in every state (asserted)
  T_Reticle_RingIdle     the same ring at 75% radius on a 48-unit canvas (96px) with the SAME stroke
                         widths, so the idle ring keeps full-size line weights instead of being scaled
  T_Reticle_Dot          idle center dot (from default.svg)
  T_Reticle_Icon_<State> white contextual glyph (inspect / talk / use / end-day)
Elements are copied, never redrawn. The background disc stops at r=28, under the opaque rim, so
background + ring + icon composites to the original contextual SVG. Unavailable stays design-only.
"""
from pathlib import Path
import copy, subprocess, tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'Art Source/UI Concepts/Selected 07/Foundation 02/Reticles'
OUTPUT = ROOT / 'Art Source/UI/Reticles'
ICONS = {'inspect': 'Inspect', 'talk': 'Talk', 'use': 'Use', 'end-day': 'EndDay'}
SIZE = '128'  # 2x the 64-unit runtime box: 1:1 at 4K, <=2x minification at 1080p (no mips needed)
IDLE_SCALE = 0.75  # must match ReticleIdleRingScale: 48-unit idle box, rendered at 2x
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def children(name):
    root = ET.parse(SOURCE / f'{name}.svg').getroot()
    assert root.get('viewBox') == '0 0 64 64', f'{name}: unexpected viewBox'
    return root, list(root)


def write_layer(root, elements, path, attrib=None):
    layer = ET.Element(root.tag, attrib or root.attrib)
    layer.extend(copy.deepcopy(e) for e in elements)
    ET.ElementTree(layer).write(path, encoding='unicode')


def ring_key(elements):
    return [(e.tag, {k: v for k, v in e.attrib.items() if k != 'fill'}) for e in elements]


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    layers = {}
    root, (outer, rim, dot) = children('default')
    assert outer.get('fill') == 'none' and dot.tag == f'{{{NS}}}circle', 'default.svg: expected ring + dot'
    layers['T_Reticle_Ring'] = [outer, rim]
    layers['T_Reticle_Dot'] = [dot]
    for source, state in ICONS.items():
        _, (ink, white, glyph) = children(source)
        assert ring_key([ink, white]) == ring_key([outer, rim]), f'{source}.svg: ring differs from default'
        assert glyph.tag == f'{{{NS}}}g', f'{source}.svg: expected glyph group'
        layers[f'T_Reticle_Icon_{state}'] = [glyph]
        if 'T_Reticle_Background' not in layers:
            disc = ET.Element(ink.tag, {k: ink.get(k) for k in ('cx', 'cy', 'r', 'fill')})
            layers['T_Reticle_Background'] = [disc]
        else:
            assert layers['T_Reticle_Background'][0].get('fill') == ink.get('fill'), f'{source}.svg: ink differs'
    # Idle ring: same circles re-centred on a smaller canvas with the radius scaled; strokes untouched.
    box = 64 * IDLE_SCALE
    assert box == int(box), 'idle box must be a whole number of units'
    idle = []
    for circle in (outer, rim):
        c = copy.deepcopy(circle)
        c.set('cx', f'{box / 2:g}'); c.set('cy', f'{box / 2:g}')
        c.set('r', f'{float(circle.get("r")) * IDLE_SCALE:g}')
        idle.append(c)
    idle_attrib = dict(root.attrib, viewBox=f'0 0 {box:g} {box:g}', width=f'{box:g}', height=f'{box:g}')
    with tempfile.TemporaryDirectory() as tmp:
        jobs = [(name, elements, None, SIZE) for name, elements in layers.items()]
        jobs.append(('T_Reticle_RingIdle', idle, idle_attrib, str(int(box * 2))))
        for name, elements, attrib, size in jobs:
            svg = Path(tmp) / f'{name}.svg'
            write_layer(root, elements, svg, attrib)
            subprocess.run(['swift', str(ROOT / 'Tools/render_svg.swift'), str(svg),
                            str(OUTPUT / f'{name}.png'), size], check=True)
