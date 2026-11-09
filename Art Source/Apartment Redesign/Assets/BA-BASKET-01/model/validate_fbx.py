import bpy,math
from pathlib import Path
root=Path(__file__).resolve().parent
for file in sorted(root.glob('BA_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(file)); objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert objs
 bpy.context.view_layer.update(); world=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
 dims=[max(v[i] for v in world)-min(v[i] for v in world) for i in range(3)]; tris=0
 for o in objs:
  assert o.data.uv_layers and all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   a,b,c=(o.data.vertices[i].co for i in t.vertices); assert (b-a).cross(c-a).length>1e-11
   tris+=1
  for loop in o.data.uv_layers.active.data:
   assert all(math.isfinite(x) for x in loop.uv)
 print(file.name,'PASS vertices',len(world),'triangles',tris,'bounds',[round(x,4) for x in dims])
 if file.name=='BA_Basket.fbx': assert dims[0] <= .50 and dims[1] <= .40,(file,dims)
