import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent/'HA_RUNNER_01.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
bpy.context.view_layer.update()
world=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
mins=[min(v[i] for v in world) for i in range(3)];maxs=[max(v[i] for v in world) for i in range(3)];dims=[b-a for a,b in zip(mins,maxs)]
assert abs(dims[0]-6)<.002 and abs(dims[1]-.8)<.002 and dims[2]<.02,(mins,maxs,dims)
faces=triangles=0
for o in meshes:
 assert o.data.uv_layers and all(math.isfinite(q) for v in o.data.vertices for q in v.co)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices)
  assert (b-a).cross(c-a).length>1e-10
  triangles+=1
 for p in o.data.polygons:
  faces+=1
  for i in p.loop_indices:
   assert all(math.isfinite(q) for q in o.data.uv_layers.active.data[i].uv)
print('PASS meshes',len(meshes),'vertices',len(world),'faces',faces,'triangles',triangles,'bounds',dims)
