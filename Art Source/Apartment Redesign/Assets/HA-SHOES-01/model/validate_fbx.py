import bpy,math
from pathlib import Path
P=Path(__file__).resolve().parent
names=['HA_ShoeTray','HA_Oxford_1','HA_Oxford_2','HA_SlipOn_1','HA_SlipOn_2']
for name in names:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/(name+'.fbx')))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1,(name,len(obs))
 o=obs[0];me=o.data;assert me.uv_layers.active,name
 assert all(math.isfinite(c) for v in me.vertices for c in v.co),name
 assert all(math.isfinite(c) for v in me.vertices for c in v.normal),name
 assert all(math.isfinite(c) for u in me.uv_layers.active.data for c in u.uv),name
 me.calc_loop_triangles();bad=sum(t.area<=1e-10 for t in me.loop_triangles)
 assert bad==0,(name,bad)
 if name=='HA_ShoeTray':assert o.dimensions.x<=.38001 and o.dimensions.y<=.25001,tuple(o.dimensions)
 else:assert o.dimensions.x<=.081 and o.dimensions.y<=.223,tuple(o.dimensions)
 print('PASS',name,'vertices',len(me.vertices),'triangles',len(me.loop_triangles),'bounds',tuple(round(v,6) for v in o.dimensions),'origin',tuple(round(v,6) for v in o.location))
