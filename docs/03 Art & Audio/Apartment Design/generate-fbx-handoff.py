#!/usr/bin/env python3
"""Regenerate the FBX handoff snapshot from the current production log and files."""
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / 'Art Source' / 'Apartment Redesign' / 'Assets'
log = (HERE / 'Asset production.md').read_text()
rows = {}
for line in log.splitlines():
    cells = [v.strip() for v in line.strip('|').split('|')]
    if len(cells) < 4:
        continue
    match = re.match(r'([A-Z][A-Z0-9-]*-\d+)', cells[0])
    if match:
        rows[match.group(1)] = cells[3]
ready, other = [], []
for folder in sorted(p for p in ASSETS.iterdir() if p.is_dir()):
    files = sorted(folder.rglob('*.fbx'))
    if not files:
        continue
    status = rows.get(folder.name, 'Not listed as reviewed; check with art owner')
    readme = folder / 'README.md'
    if readme.exists():
        relative = readme.relative_to(ROOT)
        name = f'[{folder.name}](../../../{quote(str(relative), safe="/")})'
    else:
        name = f'`{folder.name}` (README not yet available)'
    files_text = ', '.join('`' + str(f.relative_to(folder)) + '`' for f in files)
    row = f'| {name} | {files_text} | {status} |'
    (ready if status.startswith('Provisional visual pass') else other).append(row)
header = f'''# FBX handoff snapshot

Snapshot generated {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')} from the art worktree. The [asset production log](Asset%20production.md) remains authoritative for current review status, because files and reviews can change while agents work. Run `python3 "docs/03 Art & Audio/Apartment Design/generate-fbx-handoff.py"` from the repository root to regenerate. The [coverage tracker](Inventory%20coverage.md) maps exports to the design inventory, and the [room build guide](Room%20build%20guide.md) covers coordinates and known fit conflicts. These are **provisional Blender visual passes for import and in-room evaluation**, not approved Unreal-ready materials, interaction, collision, transforms or gameplay. Do not infer a visual pass merely from the presence of an FBX. Each asset link goes to its README; listed FBX paths are relative to that asset folder in `Art Source/Apartment Redesign/Assets/`.

Each README records source axes, local origin and assembly conventions; **do not assume all FBXs use one common local pivot or a universal Unreal rotation**. See the FBX transform cautions in the room guide and validate a test import of each multipart assembly. Raw files may include LODs, alternate states or standalone pieces: use the README to choose and assemble them, rather than importing every file into the level.

'''
columns = '| Asset and README | FBX paths relative to asset folder | Review and remaining checks |\n|---|---|---|\n'
(HERE / 'FBX handoff snapshot.md').write_text(header + f'## Provisional visual pass ({len(ready)} asset folders)\n\n' + columns + '\n'.join(ready) + f'\n\n## Other exported folders ({len(other)}; not yet marked reviewed)\n\n' + columns + '\n'.join(other) + '\n')
print(f'{len(ready)} provisional review rows; {len(other)} other exported asset folders')
