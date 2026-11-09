import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'LV_Plant_Stand.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes
verts=[];triangles=0
for o in meshes:
 assert o.data.uv_layers, o.name
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  assert all(math.isfinite(a) for a in p)
  verts.append(p)
 for uv in o.data.uv_layers.active.data:
  assert all(math.isfinite(a) for a in uv.uv)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-10
  triangles+=1
lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
assert abs(size[0]-.45)<.003 and abs(size[1]-.35)<.003 and abs(size[2]-.48)<.003, size
assert abs(lo[2])<.002, lo
print('PASS',len(meshes),'meshes,',len(verts),'vertices,',triangles,'triangles; bounds',size,'floor',lo[2])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'LV_Plant_Stand_Riser.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
r=meshes[0];assert r.data.uv_layers
assert all(math.isfinite(v) for p in r.data.vertices for v in p.co)
r.data.calc_loop_triangles()
for tri in r.data.loop_triangles:
 a,b,c=[r.data.vertices[i].co for i in tri.vertices];assert (b-a).cross(c-a).length>1e-10
sizes=[max(v.co[i] for v in r.data.vertices)-min(v.co[i] for v in r.data.vertices) for i in range(3)]
assert abs(sizes[0]-.156)<.002 and abs(sizes[1]-.156)<.002 and abs(sizes[2]-.036)<.002,sizes
print('RISER PASS',len(r.data.loop_triangles),'triangles; bounds',sizes)
