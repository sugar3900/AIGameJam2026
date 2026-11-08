import bpy, math
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(base/'KI_Geranium.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
coords=[];tris=0;bad=0;uvless=[]
for ob in meshes:
 me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles)
 if not me.uv_layers:uvless.append(ob.name)
 for v in me.vertices:
  c=ob.matrix_world@v.co;coords.append(c);bad+=not all(math.isfinite(x) for x in c)
 for uv in me.uv_layers:
  for item in uv.data:bad+=not all(math.isfinite(x) for x in item.uv)
 for tri in me.loop_triangles:
  a,b,c=(me.vertices[i].co for i in tri.vertices);bad+=(b-a).cross(c-a).length<1e-12
if not meshes or not coords or bad or uvless:raise RuntimeError(f'Invalid: meshes={len(meshes)} bad={bad} uvless={uvless}')
lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
print('mesh_count',len(meshes),'vertices',len(coords),'triangles',tris,'bounds_m',[round(hi[i]-lo[i],5) for i in range(3)],'min_z',round(lo[2],5),'bad',bad)
