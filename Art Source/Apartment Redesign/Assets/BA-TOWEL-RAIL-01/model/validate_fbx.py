import bpy, math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
for path in sorted(R.glob('BA_Towel_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(path))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert meshes
 pts=[]; tris=0
 for o in meshes:
  assert o.data.uv_layers, (path,'missing UV')
  o.data.calc_loop_triangles()
  for v in o.data.vertices:
   p=o.matrix_world@v.co; assert all(math.isfinite(q) for q in p);pts.append(p)
  for t in o.data.loop_triangles:
   p=[o.data.vertices[i].co for i in t.vertices]; assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-10,(path,o.name,'degenerate',[(tuple(v)) for v in p])
   tris+=1
  for uv in o.data.uv_layers.active.data: assert all(math.isfinite(x) for x in uv.uv)
 dims=tuple(round(max(p[i] for p in pts)-min(p[i] for p in pts),4) for i in range(3))
 print(path.name,'meshes',len(meshes),'triangles',tris,'dimensions',dims,'PASS')
