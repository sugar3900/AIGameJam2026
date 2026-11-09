"""Reimport each FBX in a clean scene and reject nonfinite/degenerate geometry."""
import bpy,math
from pathlib import Path
root=Path(__file__).resolve().parent
for path in sorted(root.glob('LV_TV_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(path)); meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']
 if not meshes:raise RuntimeError(f'{path.name}: no meshes')
 vcount=bad=deg=uvbad=0
 for o in meshes:
  m=o.data;vcount+=len(m.vertices);bad+=sum(not all(math.isfinite(c) for c in v.co) for v in m.vertices)
  deg+=sum(p.area < 1e-10 for p in m.polygons)
  if not m.uv_layers:raise RuntimeError(f'{path.name}: missing UVs')
  uvbad+=sum(not all(math.isfinite(c) for c in l.uv) for u in m.uv_layers for l in u.data)
 if bad or deg or uvbad:raise RuntimeError(f'{path.name}: invalid={bad}, degenerate={deg}, uv={uvbad}')
 print('VALID',path.name,'meshes',len(meshes),'vertices',vcount,'bad',bad,'degenerate',deg,'uvbad',uvbad)
