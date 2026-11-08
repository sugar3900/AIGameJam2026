import bpy,math
from pathlib import Path
P=Path(__file__).resolve().parent
for fn in ['BA_SoapDish.fbx','BA_SoapBar.fbx']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/fn))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1,(fn,len(obs))
 o=obs[0];m=o.data;assert m.uv_layers
 assert all(math.isfinite(x) for v in m.vertices for x in v.co)
 assert all(math.isfinite(x) for p in m.polygons for x in p.normal)
 assert all(math.isfinite(x) for uv in m.uv_layers.active.data for x in uv.uv)
 m.calc_loop_triangles();assert all(t.area>1e-12 for t in m.loop_triangles)
 pts=[o.matrix_world@v.co for v in m.vertices];bounds=[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)]
 if 'Dish' in fn: assert .145<bounds[0]<.155 and .102<bounds[1]<.110 and .025<bounds[2]<.04,bounds
 else: assert .094<bounds[0]<.096 and .059<bounds[1]<.061 and .023<bounds[2]<.025,bounds
 print('PASS',fn,'vertices',len(m.vertices),'triangles',len(m.loop_triangles),'bounds_m',*[round(x,6) for x in bounds],'origin',*[round(x,6) for x in o.location])
