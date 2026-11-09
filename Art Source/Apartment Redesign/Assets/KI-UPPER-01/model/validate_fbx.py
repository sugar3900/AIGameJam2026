import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
expected={'Body':(0,0,0),'LeftDoor':(-.47,-.165,.265),'RightDoor':(.47,-.165,.265)}
for name,pivot in expected.items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT,'model','KI_Upper_'+name+'.fbx'))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes,name
 points=[];triangles=0
 for o in meshes:
  assert o.data.uv_layers, f'{name}: no UVs'
  assert all(math.isfinite(c) for loop in o.data.uv_layers.active.data for c in loop.uv), f'{name}: nonfinite UV'
  assert all(math.isfinite(c) for poly in o.data.polygons for c in poly.normal), f'{name}: nonfinite normal'
  o.data.calc_loop_triangles()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;assert all(math.isfinite(c) for c in p);points.append(p)
  for tri in o.data.loop_triangles:
   a,b,c=(o.matrix_world@o.data.vertices[i].co for i in tri.vertices);assert (b-a).cross(c-a).length>1e-10;triangles+=1
  assert all(abs(o.location[i]-pivot[i])<.001 for i in range(3)),(name,list(o.location),pivot)
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 print(name,'triangles',triangles,'origin',tuple(round(v,4) for v in meshes[0].location),'bounds',tuple(round(hi[i]-lo[i],4) for i in range(3)))
 if name=='Body': assert all(abs((hi[i]-lo[i])-t)<.003 for i,t in enumerate((1,.3235,.5455)))
print('PASS')
