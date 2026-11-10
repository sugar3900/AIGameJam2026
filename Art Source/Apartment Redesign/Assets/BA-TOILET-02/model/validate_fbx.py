"""Fresh FBX roundtrip, finite/UV/triangle checks and open bowl sightline."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
result={'status':'PASS','files':{}}
for name in ['BA_Toilet02_Body','BA_Toilet02_Lid','BA_Toilet02_Water']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(P/'model'/f'{name}.fbx'));obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];main=next(o for o in obs if o.name==name);hulls=[o for o in obs if o.name.startswith('UCX_')]
 assert len(hulls)=={'BA_Toilet02_Body':21,'BA_Toilet02_Lid':1,'BA_Toilet02_Water':0}[name]
 me=main.data;me.calc_loop_triangles();assert me.uv_layers
 assert all(math.isfinite(v) for x in me.vertices for v in x.co)
 assert all(math.isfinite(v) for u in me.uv_layers.active.data for v in u.uv)
 zero=[t.index for t in me.loop_triangles if t.area<1e-12]
 assert not zero,(name,'degenerate triangles',len(zero))
 vs=[main.matrix_world@v.co for v in me.vertices]
 result['files'][name]={'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'material_slots':[m.name for m in me.materials],'ucx_count':len(hulls),'zero_area_triangles':len(zero),'world_bounds':{'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]},'origin':list(main.location)}
 if name in ['BA_Toilet02_Body','BA_Toilet02_Water']:
  inv=main.matrix_world.inverted();origin=inv@Vector((0,-.075,1.2));direction=(inv.to_3x3()@Vector((0,0,-1))).normalized();hit,loc,n,idx=main.ray_cast(origin,direction)
  assert hit
  z=(main.matrix_world@loc).z
  result['files'][name]['center_downward_ray_hit_z']=z
  if name.endswith('Body'):assert z<.16,('bowl blocked before trap',z)
  else:assert abs(z-.275)<.0001,('water elevation',z)
result['scope']='Fresh Blender legacy FBX roundtrip. Source geometry/material appearance only; Unreal collision, materials, click binding and gameplay remain engine acceptance.'
(P/'validation/fbx-roundtrip.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
