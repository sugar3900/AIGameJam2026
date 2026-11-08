import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
for name in ('KI_Pan_Rail_Assembly.fbx','KI_Pan_Rail_Body.fbx','KI_Pan_Rail_Hooks.fbx'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/name));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
 pts=[];nv=nt=0
 for o in meshes:
  assert o.data.uv_layers,(name,o.name,'missing UV')
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) for uv in o.data.uv_layers.active.data for c in uv.uv)
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-12,(name,o.name,'degenerate triangle')
  nv+=len(o.data.vertices);nt+=len(o.data.loop_triangles);pts.extend(o.matrix_world @ Vector(c) for c in o.bound_box)
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
 print(name,'meshes',len(meshes),'vertices',nv,'triangles',nt,'bounds',size)
 if 'Assembly' in name:assert .59 < size[0] < .60 and size[1]<.09 and size[2]<.12,size
