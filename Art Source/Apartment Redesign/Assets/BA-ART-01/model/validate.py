import bpy, math
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p/'BA-ART-01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
points=[];triangles=0
for o in meshes:
 m=o.data;assert len(m.uv_layers)>0,o.name
 for uv in m.uv_layers.active.data:assert all(math.isfinite(x) for x in uv.uv),o.name
 for v in m.vertices:
  q=o.matrix_world@v.co;assert all(math.isfinite(x) for x in q);points.append(q)
 m.calc_loop_triangles()
 for tri in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in tri.vertices];assert (b-a).cross(c-a).length>1e-10,o.name;triangles+=1
lo=[min(q[i] for q in points) for i in range(3)];hi=[max(q[i] for q in points) for i in range(3)];size=[round(hi[i]-lo[i],4) for i in range(3)]
print('REIMPORT',len(meshes),'meshes',triangles,'triangles','bounds',size)
assert abs(size[0]-.30)<.001 and abs(size[1]-.035)<.001 and abs(size[2]-.36)<.001
