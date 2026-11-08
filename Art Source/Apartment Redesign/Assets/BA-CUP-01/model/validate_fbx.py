import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parent
for path in sorted(root.glob('*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(path));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bad=0;uvbad=0;verts=0;tris=0
 for o in obs:
  me=o.data;me.calc_loop_triangles();verts+=len(me.vertices);tris+=len(me.loop_triangles)
  bad+=sum(1 for v in me.vertices if not all(math.isfinite(q) for q in v.co))
  bad+=sum(1 for t in me.loop_triangles if (me.vertices[t.vertices[1]].co-me.vertices[t.vertices[0]].co).cross(me.vertices[t.vertices[2]].co-me.vertices[t.vertices[0]].co).length < 1e-12)
  if not me.uv_layers: uvbad+=1
  for layer in me.uv_layers:
   uvbad+=sum(1 for uv in layer.data if not all(math.isfinite(q) for q in uv.uv))
 assert obs and not bad and not uvbad, (path.name,bad,uvbad)
 coords=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
 bounds=tuple(round(max(v[i] for v in coords)-min(v[i] for v in coords),5) for i in range(3))
 print(path.name,'meshes',len(obs),'vertices',verts,'triangles',tris,'bounds_m',bounds,'invalid',bad,'uv_errors',uvbad)
