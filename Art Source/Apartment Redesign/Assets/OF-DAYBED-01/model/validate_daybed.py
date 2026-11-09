import bpy, math, os
from mathutils import Vector
D=os.path.dirname(os.path.abspath(__file__))
for name in ('OF_DAYBED_Assembly','OF_DAYBED_Frame','OF_DAYBED_Bedding'):
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(D,name+'.fbx'))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; triangles=bad=missing=nonfinite=0
 points=[]
 for o in meshes:
  m=o.data; m.calc_loop_triangles(); triangles+=len(m.loop_triangles)
  if not m.uv_layers:missing+=1
  else:
   for uv in m.uv_layers.active.data:
    if not all(math.isfinite(x) for x in uv.uv):nonfinite+=1
  for v in m.vertices:
   p=o.matrix_world @ v.co; points.append(p)
   if not all(math.isfinite(x) for x in p):nonfinite+=1
  for t in m.loop_triangles:
   a,b,c=(m.vertices[i].co for i in t.vertices)
   if (b-a).cross(c-a).length < 1e-10: bad+=1
 dims=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
 print('VALIDATION',name,'meshes',len(meshes),'triangles',triangles,'zero_area',bad,'missing_uv',missing,'nonfinite',nonfinite,'bounds',dims)
 if bad or missing or nonfinite:raise RuntimeError('Validation failure')
