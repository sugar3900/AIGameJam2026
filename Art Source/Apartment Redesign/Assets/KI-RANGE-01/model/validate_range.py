import bpy, math
from pathlib import Path
p=Path(__file__).resolve().parent
for name in ['KI_RANGE_Body.fbx','KI_RANGE_Door.fbx']:
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(p/name)); meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']; assert meshes
 for o in meshes:
  m=o.data
  assert all(all(math.isfinite(v) for v in p.co) for p in m.vertices),name+' nonfinite vertex'
  assert all(p.area > 1e-12 for p in m.polygons),name+' zero area'
  assert len(m.uv_layers)>0,name+' missing UV'
  assert all(all(math.isfinite(v) for v in u.uv) for uv in m.uv_layers for u in uv.data),name+' nonfinite UV'
 print('PASS',name,'meshes',len(meshes),'bounds',tuple(round(x,3) for x in meshes[0].dimensions))
