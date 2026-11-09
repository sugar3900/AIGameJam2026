import bpy, math
from pathlib import Path
from mathutils import Vector
M=Path(__file__).resolve().parent
for fname in ('BR_BOX_BODY.fbx','BR_BOX_LID.fbx'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(M/fname))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert meshes, f'{fname}: no meshes'
 verts=tris=bad=uv_bad=0; coords=[]
 for o in meshes:
  m=o.data; assert m.uv_layers.active, f'{o.name}: missing UV';m.calc_loop_triangles()
  for v in m.vertices:
   assert all(math.isfinite(x) for x in v.co); coords.append(o.matrix_world @ v.co);verts+=1
  for uv in m.uv_layers.active.data:assert all(math.isfinite(x) for x in uv.uv)
  for face in m.loop_triangles:
   a,b,c=(m.vertices[i].co for i in face.vertices)
   if (b-a).cross(c-a).length<1e-12: bad+=1
   a_uv,b_uv,c_uv=(m.uv_layers.active.data[i].uv for i in face.loops)
   if abs((b_uv.x-a_uv.x)*(c_uv.y-a_uv.y)-(b_uv.y-a_uv.y)*(c_uv.x-a_uv.x))<1e-14: uv_bad+=1
   tris+=1
 assert not bad,f'{fname}: {bad} degenerate triangles'
 assert not uv_bad,f'{fname}: {uv_bad} degenerate UV triangles'
 lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
 print(fname,'meshes',len(meshes),'vertices',verts,'triangles',tris,'bounds',tuple(round(hi[i]-lo[i],6) for i in range(3)),'origins',[tuple(round(x,6) for x in o.location) for o in meshes])
 assert hi[0]-lo[0]<.305 and hi[1]-lo[1]<.255
