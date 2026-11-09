import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
for f in sorted(P.glob('Bin_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(f));objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert objs, f
 verts=[];tris=0;zero=0
 for o in objs:
  assert o.data.uv_layers, f'{f}: missing UV'
  assert all(math.isfinite(v) for p in o.data.vertices for v in p.co)
  assert all(math.isfinite(v) for poly in o.data.polygons for v in poly.normal)
  assert all(math.isfinite(v) for u in o.data.uv_layers.active.data for v in u.uv)
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   a,b,c=[o.data.vertices[i].co for i in t.vertices];tris+=1
   if (b-a).cross(c-a).length < 1e-10:zero+=1
  verts.extend(o.matrix_world@v.co for v in o.data.vertices)
 assert zero==0, f'{f}: {zero} degenerate triangles'
 bounds=[round(max(v[i] for v in verts)-min(v[i] for v in verts),5) for i in range(3)]
 print(f.name,'meshes',len(objs),'triangles',tris,'bounds',bounds,'origin',tuple(round(v,5) for v in objs[0].location))
