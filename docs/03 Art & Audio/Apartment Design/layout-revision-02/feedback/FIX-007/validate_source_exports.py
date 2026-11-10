import bpy,json,math
from pathlib import Path
A=Path(__file__).resolve().parents[6]/'Art Source/Apartment Redesign/Assets'
for kit in ['BA-HAND-TOWEL-RING-02','BA-TUB-FIXTURES-02']:
 p=A/kit;manifest=json.loads((p/'assembly.json').read_text());report={'status':'PASS source FBX roundtrip; engine acceptance pending','exports':[]}
 for e in manifest['exports']:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p/e['file']))
  meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
  o=meshes[0];v=[o.matrix_world@q.co for q in o.data.vertices]
  assert all(math.isfinite(c) for q in v for c in q)
  lo=[min(q[i] for q in v) for i in range(3)];hi=[max(q[i] for q in v) for i in range(3)]
  err=max(abs(a-b) for aa,bb in [(lo,e['min']),(hi,e['max'])] for a,b in zip(aa,bb));assert err<.0001,(kit,e['file'],lo,hi)
  assert o.location.length<.0001;assert o.data.uv_layers
  o.data.calc_loop_triangles();degenerate=sum(t.area<1e-12 for t in o.data.loop_triangles)
  assert degenerate==0,(kit,e['file'],degenerate)
  item={'file':e['file'],'vertices':len(v),'triangles':len(o.data.loop_triangles),'uv_layers':len(o.data.uv_layers),'origin':list(o.location),'min':lo,'max':hi,'max_bound_error_m':err,'zero_area_triangles':degenerate}
  if kit=='BA-HAND-TOWEL-RING-02':
   # Test complete triangles overlapping the cap band, using their conservative Y extrema.
   ys=[]
   for t in o.data.loop_triangles:
    tri=[v[i] for i in t.vertices];zs=[q.z+1.15 for q in tri]
    if min(zs)<=1.05 and max(zs)>=1.00:ys.extend(q.y for q in tri)
   if ys:
    item['tile_cap_clearance_m']=-.036-max(ys);assert item['tile_cap_clearance_m']>.015
   else:item['tile_cap_clearance']='No triangle intersects world Z1.00..1.05'
  report['exports'].append(item)
 (p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(kit,report)
