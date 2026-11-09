import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent/'HA_Hooks.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
nvert=ntri=0;bounds=[]
for o in meshes:
 assert o.data.uv_layers,(o.name,'missing UVs')
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 assert all(math.isfinite(c) for uv in o.data.uv_layers.active.data for c in uv.uv),o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-12,(o.name,'degenerate')
 nvert+=len(o.data.vertices);ntri+=len(o.data.loop_triangles)
 bounds.extend(o.matrix_world @ Vector(corner) for corner in o.bound_box)
mins=[min(v[i] for v in bounds) for i in range(3)];maxs=[max(v[i] for v in bounds) for i in range(3)]
print('meshes',len(meshes),'vertices',nvert,'triangles',ntri,'bounds',list(zip(mins,maxs)),'size',[maxs[i]-mins[i] for i in range(3)])
assert maxs[0]-mins[0]<.721 and maxs[1]-mins[1]<.071 and maxs[2]-mins[2]<.121
