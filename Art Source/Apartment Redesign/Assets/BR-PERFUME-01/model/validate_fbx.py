import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
for fn in ['BR_Perfume_Body.fbx','BR_Perfume_Stopper.fbx']:
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/fn)); meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; bad=0; tris=0; coords=[]
 for o in meshes:
  me=o.data; me.calc_loop_triangles()
  if not me.uv_layers: bad+=1
  for v in me.vertices:
   co=o.matrix_world@v.co; coords.append(co); bad+=int(not all(math.isfinite(c) for c in co))
  for t in me.loop_triangles:
   a,b,c=(me.vertices[i].co for i in t.vertices); bad+=int((b-a).cross(c-a).length<1e-12); tris+=1
  if me.uv_layers:
   for u in me.uv_layers.active.data: bad+=int(not all(math.isfinite(x) for x in u.uv))
 bounds=[round(max(v[i] for v in coords)-min(v[i] for v in coords),5) for i in range(3)]
 print(f'{fn}: meshes={len(meshes)} triangles={tris} bounds={bounds} errors={bad}')
 if bad or not coords: raise RuntimeError('Validation failure')
