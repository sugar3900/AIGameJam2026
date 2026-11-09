import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root/'BA_Folded_Towel.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes
vertices=triangles=0; coords=[]
for o in meshes:
 assert len(o.data.uv_layers)>0
 o.data.calc_loop_triangles()
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  assert all(math.isfinite(x) for x in p);coords.append(p);vertices+=1
 for t in o.data.loop_triangles:
  a,b,c=(o.matrix_world@o.data.vertices[i].co for i in t.vertices)
  assert (b-a).cross(c-a).length>1e-10;triangles+=1
 for uv in o.data.uv_layers.active.data: assert all(math.isfinite(x) for x in uv.uv)
lo=[min(p[i] for p in coords) for i in range(3)];hi=[max(p[i] for p in coords) for i in range(3)];dims=[hi[i]-lo[i] for i in range(3)]
assert .29<dims[0]<.31 and .19<dims[1]<.21 and .07<dims[2]<.09, dims
message=f'meshes={len(meshes)} vertices={vertices} triangles={triangles} bounds_m={dims}; finite coordinates and UVs, UV layers present, no degenerate geometry triangles\n'
(root/'validation.txt').write_text(message);print(message)
