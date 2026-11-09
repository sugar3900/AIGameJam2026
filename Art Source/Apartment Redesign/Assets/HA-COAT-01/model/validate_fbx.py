import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p/'HA_Coat.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes
count=tris=bad=uvmissing=0; lo=[1e9]*3;hi=[-1e9]*3
for o in meshes:
 mesh=o.data;mesh.calc_loop_triangles();uvmissing+=int(not mesh.uv_layers)
 for v in mesh.vertices:
  co=o.matrix_world@v.co; count+=1
  assert all(math.isfinite(x) for x in co)
  for i in range(3):lo[i]=min(lo[i],co[i]);hi[i]=max(hi[i],co[i])
 for t in mesh.loop_triangles:
  a,b,c=[mesh.vertices[v].co for v in t.vertices];tris+=1
  if (b-a).cross(c-a).length<1e-10:bad+=1
 for uv in mesh.uv_layers:
  assert all(math.isfinite(q) for x in uv.data for q in x.uv)
bounds=[hi[i]-lo[i] for i in range(3)]
out=f'meshes={len(meshes)} vertices={count} triangles={tris} degenerate={bad} missing_uv={uvmissing} bounds_m={bounds} min={lo} max={hi}'
print(out);(p/'validation.txt').write_text(out+'\n')
assert not bad and not uvmissing
