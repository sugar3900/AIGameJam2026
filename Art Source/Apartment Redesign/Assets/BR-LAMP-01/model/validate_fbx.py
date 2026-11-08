"""Validate each exported FBX in a clean Blender scene."""
import bpy,math,os
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ('BR_LampBody','BR_LampShade','BR_LampBulb'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(root/(name+'.fbx')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert meshes, name+' has no mesh'
 nverts=ntri=0
 for o in meshes:
  m=o.data;m.calc_loop_triangles();nverts+=len(m.vertices);ntri+=len(m.loop_triangles)
  assert all(all(math.isfinite(c) for c in v.co) for v in m.vertices),name+' invalid vertices'
  assert all(all(math.isfinite(c) for c in v.normal) for v in m.vertices),name+' invalid normals'
  assert len(m.uv_layers)>0,name+' missing UV'
  assert all(all(math.isfinite(c) for c in x.uv) for uv in m.uv_layers for x in uv.data),name+' invalid UV'
  assert all(t.area>1e-12 for t in m.loop_triangles),name+' degenerate triangle'
 print(name,'PASS vertices',nverts,'triangles',ntri,'bounds',tuple(round(x,4) for x in meshes[0].dimensions))
