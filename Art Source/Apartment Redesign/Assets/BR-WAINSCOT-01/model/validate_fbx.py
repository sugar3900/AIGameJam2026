import bpy, math, os
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
for f in ('BR_Wainscot_Module.fbx','BR_Wainscot_Damage.fbx'):
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(root,f))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert objs
 verts=tris=bad=zero=uvbad=0; xyz=[]
 for o in objs:
  m=o.data; m.calc_loop_triangles(); verts+=len(m.vertices); tris+=len(m.loop_triangles)
  for v in m.vertices:
   p=o.matrix_world @ v.co; xyz.append(p); bad+=not all(math.isfinite(c) for c in p)
  for t in m.loop_triangles:
   a,b,c=(o.matrix_world @ m.vertices[i].co for i in t.vertices); zero+=(b-a).cross(c-a).length<1e-10
  for uv in m.uv_layers:
   for t in uv.data: uvbad+=not all(math.isfinite(c) for c in t.uv)
 lo=tuple(round(min(v[i] for v in xyz),4) for i in range(3)); hi=tuple(round(max(v[i] for v in xyz),4) for i in range(3))
 print('FBX_CHECK',f,'objects',len(objs),'vertices',verts,'triangles',tris,'bad',bad,'zero',zero,'badUV',uvbad,'bounds',lo,hi)
 if bad or zero or uvbad: raise RuntimeError('Invalid export '+f)
 if f=='BR_Wainscot_Damage.fbx':
  # Overlay must stay within the 1 x 1.1 m module after FBX round trip.
  if not (0 <= lo[0] <= hi[0] <= 1 and 0 <= lo[2] <= hi[2] <= 1.1): raise RuntimeError('Damage is not in module coordinates')
print('FBX_VALIDATION_OK')
