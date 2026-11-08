import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'KI_Mug_01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert meshes
verts=tris=deg=bad=uvbad=0
coords=[]
for ob in meshes:
 me=ob.data; me.calc_loop_triangles(); assert me.uv_layers.active,ob.name
 verts+=len(me.vertices); tris+=len(me.loop_triangles)
 for v in me.vertices:
  w=ob.matrix_world@v.co;coords.append(tuple(w));bad+=not all(math.isfinite(x) for x in w)
 for tr in me.loop_triangles:
  a,b,c=(me.vertices[x].co for x in tr.vertices)
  deg+=((b-a).cross(c-a).length < 1e-12)
  us=[me.uv_layers.active.data[i].uv for i in tr.loops]
  uvbad+=not all(math.isfinite(z) for u in us for z in u)
lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
print('RESULT',meshes.__len__(),'meshes',verts,'verts',tris,'tris','nonfinite',bad,'degenerate',deg,'nonfinite_uv',uvbad,'bounds_m',[round(hi[i]-lo[i],5) for i in range(3)])
assert not bad and not deg and not uvbad
