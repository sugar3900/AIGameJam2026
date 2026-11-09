import bpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'KI_Pottery_01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
verts=tris=bad=deg=bad_uv=deg_uv=0;coords=[]
for ob in meshes:
 me=ob.data;me.calc_loop_triangles();assert me.uv_layers.active
 verts+=len(me.vertices);tris+=len(me.loop_triangles)
 for v in me.vertices:
  w=ob.matrix_world@v.co;coords.append(tuple(w));bad+=not all(math.isfinite(x) for x in w)
 for tr in me.loop_triangles:
  a,b,c=(me.vertices[x].co for x in tr.vertices);deg+=((b-a).cross(c-a).length<1e-12)
  u=[me.uv_layers.active.data[i].uv for i in tr.loops];bad_uv+=not all(math.isfinite(x) for q in u for x in q)
  deg_uv+=abs((u[1].x-u[0].x)*(u[2].y-u[0].y)-(u[1].y-u[0].y)*(u[2].x-u[0].x))<1e-12
lo=[min(q[i] for q in coords) for i in range(3)];hi=[max(q[i] for q in coords) for i in range(3)];bounds=[hi[i]-lo[i] for i in range(3)]
# Object is not transformed in this Blender reimport; ray should reach the cavity floor, not a filled mouth.
ob=meshes[0];tree=BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get());hit=tree.ray_cast(Vector((0,0,.30)),Vector((0,0,-1)),.4)
print('RESULT',len(meshes),'meshes',verts,'vertices',tris,'triangles','bounds_m',[round(v,5) for v in bounds],'nonfinite',bad,'degenerate',deg,'nonfinite_uv',bad_uv,'degenerate_uv',deg_uv,'ray_hit',tuple(round(x,5) for x in hit[0]) if hit[0] else None)
assert not any((bad,deg,bad_uv,deg_uv))
assert abs(bounds[0]-.16)<.002 and abs(bounds[1]-.16)<.002 and abs(bounds[2]-.239)<.002
assert hit[0] is not None and hit[0].z<.03
