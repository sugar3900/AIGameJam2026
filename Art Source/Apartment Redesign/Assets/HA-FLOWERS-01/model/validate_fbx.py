import bpy,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(D/'model/HA_FLOWERS_01.fbx'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert obs, 'No mesh objects'
points=[];tris=0;bad=0;missing=[];bad_uv=0
for o in obs:
 m=o.data;m.calc_loop_triangles()
 if not m.uv_layers:missing.append(o.name)
 for v in m.vertices:
  p=o.matrix_world@v.co
  assert all(math.isfinite(c) for c in p)
  points.append(p)
 for t in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in t.vertices];tris+=1
  if (b-a).cross(c-a).length < 1e-12:bad+=1
 if m.uv_layers:
  for v in m.uv_layers.active.data:
   if not all(math.isfinite(a) for a in v.uv):bad_uv+=1
assert not missing, missing
assert bad==0,(bad,tris)
assert bad_uv==0,bad_uv
lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
print('MESHES',len(obs),'VERTICES',len(points),'TRIANGLES',tris,'DEGENERATE',bad,'NONFINITE_UV',bad_uv,'MIN',lo,'MAX',hi,'BOUNDS',size)
