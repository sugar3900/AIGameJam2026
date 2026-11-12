"""Copy licensed UI fonts and rasterize Phosphor Bold icons for Unreal import (macOS)."""
from pathlib import Path
import shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[3]
kit=ROOT/'Art Source/UI Concepts/Selected 07/Foundation 02'
out=ROOT/'Art Source/UI/Design'
(out/'Fonts').mkdir(parents=True,exist_ok=True)
(out/'Icons').mkdir(exist_ok=True)
for p in (kit/'Fonts').iterdir():
    if p.suffix in ('.ttf','.txt'): shutil.copy2(p,out/'Fonts'/p.name)
for p in (kit/'Icons/Phosphor').glob('*.svg'):
    name=p.stem.removesuffix('-bold').replace('-','_')
    with tempfile.TemporaryDirectory() as tmp:
        svg=Path(tmp)/p.name
        svg.write_text(p.read_text().replace('currentColor','#FFFFFF'))
        subprocess.run(['swift',str(ROOT/'Tools/render_svg.swift'),str(svg),str(out/'Icons'/f'T_Icon_{name}.png'),'96'],check=True)
shutil.copy2(kit/'Icons/Phosphor/LICENSE',out/'Icons/LICENSE')
print('Prepared fonts and icons in',out)
