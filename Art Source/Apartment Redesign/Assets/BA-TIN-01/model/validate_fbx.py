import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
for path in sorted(P.glob('BA_Tin_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(path)); meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert meshes, path
 verts=0; tris=0; pts=[]
 for o in meshes:
  assert o.data.uv_layers.active is not None, (path,o.name,'missing UV')
  for v in o.data.vertices:
   assert all(math.isfinite(x) for x in v.co), (path,o.name,'nonfinite')
   pts.append(o.matrix_world @ v.co);verts+=1
  for uv in o.data.uv_layers.active.data:assert all(math.isfinite(x) for x in uv.uv), (path,o.name,'bad UV')
  o.data.calc_loop_triangles()
  for tri in o.data.loop_triangles:
   a,b,c=(o.data.vertices[i].co for i in tri.vertices)
   assert (b-a).cross(c-a).length>1e-10,(path,o.name,'degenerate')
   tris+=1
 mins=[min(v[i] for v in pts) for i in range(3)];maxs=[max(v[i] for v in pts) for i in range(3)]
 print(path.name,'meshes',len(meshes),'vertices',verts,'triangles',tris,'bounds',[round(maxs[i]-mins[i],5) for i in range(3)],'origins',[tuple(round(v,5) for v in o.location) for o in meshes])
 assert all(.0001 < maxs[i]-mins[i] < 1 for i in range(3))
