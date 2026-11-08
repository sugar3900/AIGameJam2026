import bpy,math,os
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__))
for name in ('Frame','LeftPanel','RightPanel'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(R,'ARC_Sliding_'+name+'.fbx'))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert objs
 count=0
 for o in objs:
  assert o.data.uv_layers, name+' missing UV'
  for v in o.data.vertices: assert all(math.isfinite(n) for n in v.co)
  for p in o.data.polygons: assert p.area>1e-12,(name,p.index)
  count+=len(o.data.polygons)
 print(name,'meshes',len(objs),'faces',count,'UV',len(objs[0].data.uv_layers))
print('Model track centers y=-.028 and +.028 m, slab thickness .024 m; panel face mouldings project .006 m. Slide left panel +.44 m, exposing .44 m on left.')
