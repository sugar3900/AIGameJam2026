import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root/'LV-CHAIR-01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
if not meshes:raise RuntimeError('No mesh geometry imported')
for o in meshes:
 if not o.data.uv_layers:raise RuntimeError('Missing UVs: '+o.name)
 for v in o.data.vertices:
  if not all(math.isfinite(c) for c in v.co):raise RuntimeError('Non-finite vertex: '+o.name)
 for p in o.data.polygons:
  if not all(math.isfinite(c) for c in p.normal):raise RuntimeError('Non-finite normal: '+o.name)
 for layer in o.data.uv_layers:
  for uv in layer.data:
   if not all(math.isfinite(c) for c in uv.uv):raise RuntimeError('Non-finite UV: '+o.name)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices)
  if (b-a).cross(c-a).length<1e-12:raise RuntimeError('Degenerate triangle: '+o.name)
coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
mins=[min(v[i] for v in coords) for i in range(3)];maxs=[max(v[i] for v in coords) for i in range(3)]
print('PASS meshes',len(meshes),'bounds',mins,maxs,'dimensions',[maxs[i]-mins[i] for i in range(3)])
