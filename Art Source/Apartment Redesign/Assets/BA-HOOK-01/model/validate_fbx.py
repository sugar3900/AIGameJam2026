import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'BA_Hook_01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
coords=[];tris=0
for o in meshes:
 assert o.data.uv_layers and all(math.isfinite(x) for v in o.data.vertices for x in v.co)
 assert all(math.isfinite(x) for uv in o.data.uv_layers.active.data for x in uv.uv)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length > 1e-12
  tris+=1
 coords.extend(o.matrix_world@v.co for v in o.data.vertices)
mins=[min(v[i] for v in coords) for i in range(3)];maxs=[max(v[i] for v in coords) for i in range(3)]
dims=[maxs[i]-mins[i] for i in range(3)]
print('meshes',len(meshes),'triangles',tris,'bounds_m',dims,'local_origin',list(meshes[0].location),'min/max',mins,maxs)
assert .045<dims[0]<.09 and .05<dims[1]<.10 and .06<dims[2]<.12
assert meshes[0].location.length < 1e-5
