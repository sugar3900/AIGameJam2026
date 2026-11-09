import bpy, math, os
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
for name in ('KI_Pan_Body','KI_Pan_Handle'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(root,name+'.fbx'))
 objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
 assert objs, name
 verts=[]; tris=0; baduvtri=0
 for o in objs:
  m=o.data;m.calc_loop_triangles()
  assert m.uv_layers, o.name
  assert all(all(math.isfinite(v) for v in p.co) for p in m.vertices)
  assert all(all(math.isfinite(v) for v in p.normal) for p in m.polygons)
  assert all(all(math.isfinite(v) for v in uv.uv) for layer in m.uv_layers for uv in layer.data)
  assert all(t.area>1e-12 for t in m.loop_triangles)
  uvs=m.uv_layers.active.data
  for t in m.loop_triangles:
   a,b,c=[uvs[i].uv for i in t.loops]; area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x));baduvtri+=area<1e-12
  tris+=len(m.loop_triangles);verts += [o.matrix_world @ v.co for v in m.vertices]
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 print(f'VALID {name}: meshes={len(objs)} vertices={len(verts)} triangles={tris} bounds_m={[round(hi[i]-lo[i],4) for i in range(3)]} degenerate_uv_triangles={baduvtri}')
 if baduvtri:raise RuntimeError('degenerate UV triangles')
