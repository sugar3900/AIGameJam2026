import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p/'LV-ART-04.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert meshes
points=[];triangles=0
for o in meshes:
 m=o.data; assert len(m.uv_layers)>0, o.name
 for v in m.vertices:
  q=o.matrix_world@v.co; assert all(math.isfinite(x) for x in q);points.append(q)
 for loop in m.uv_layers.active.data:
  assert all(math.isfinite(x) for x in loop.uv),o.name
 m.calc_loop_triangles()
 for tri in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in tri.vertices]; assert (b-a).cross(c-a).length>1e-10, o.name
  uv=m.uv_layers.active.data; u,v,w=[uv[i].uv for i in tri.loops]
  assert abs((v.x-u.x)*(w.y-u.y)-(v.y-u.y)*(w.x-u.x))>1e-12, o.name
  triangles+=1
lo=[min(q[i] for q in points) for i in range(3)];hi=[max(q[i] for q in points) for i in range(3)]; size=[round(hi[i]-lo[i],4) for i in range(3)]
print('REIMPORT',len(meshes),'meshes',triangles,'triangles','bounds',size)
assert abs(size[0]-.72)<.001 and abs(size[1]-.035)<.001 and abs(size[2]-.52)<.001
