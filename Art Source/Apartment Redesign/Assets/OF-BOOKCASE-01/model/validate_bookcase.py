import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT,'model','OF_BOOKCASE_BODY.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
points=[];tris=0
for o in meshes:
 assert o.data.uv_layers
 assert all(math.isfinite(c) for uv in o.data.uv_layers.active.data for c in uv.uv)
 for v in o.data.vertices:
  w=o.matrix_world @ v.co;assert all(math.isfinite(c) for c in w);points.append(w)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-10;tris+=1
bounds=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
print('VALID mesh_count',len(meshes),'vertices',len(points),'triangles',tris,'bounds',bounds)
assert all(abs(a-b)<.003 for a,b in zip(bounds,[1.1,.30,.90]))
