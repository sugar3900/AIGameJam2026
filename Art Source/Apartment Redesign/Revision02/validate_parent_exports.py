import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1]/'Assets'
for aid in ('KI-WALL-TABLE-02','KI-STOOL-02','ARC-DOOR-02','ARC-ENTRY-DOOR-02'):
 root=B/aid;report=[]
 for file in sorted((root/'model').glob('*.fbx')):
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(file))
  objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];vis=[o for o in objs if not o.name.startswith('UCX_')];coll=[o for o in objs if o.name.startswith('UCX_')]
  assert len(vis)==1 and coll,(aid,file,len(vis),len(coll))
  o=vis[0];m=o.data;assert m.uv_layers
  assert all(math.isfinite(c) for v in m.vertices for c in v.co)
  assert all(math.isfinite(c) for l in m.uv_layers for u in l.data for c in u.uv)
  m.calc_loop_triangles();bad=sum(t.area<=1e-12 for t in m.loop_triangles);assert bad==0,(file,bad)
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];low=[min(v[i] for v in pts) for i in range(3)];high=[max(v[i] for v in pts) for i in range(3)]
  for co in coll:assert co.name.startswith('UCX_'+o.name+'_'),(co.name,o.name)
  assert o.matrix_world.to_3x3().determinant()>0
  report.append(dict(file=file.name,render_mesh=o.name,location=list(o.location),bounds_min=low,bounds_max=high,triangles=len(m.loop_triangles),collision_hulls=len(coll),status='pass'))
 if aid.startswith('KI-'):
  dims=[b-a for a,b in zip(report[0]['bounds_min'],report[0]['bounds_max'])];expected=[.9,.45,.74] if 'TABLE' in aid else [.3,.3,.45]
  assert all(abs(a-b)<.001 for a,b in zip(dims,expected)),(aid,dims)
 else:
  frame=next(r for r in report if 'Frame' in r['file']);leaf=next(r for r in report if 'Leaf' in r['file']);assert frame['collision_hulls']==3 and leaf['collision_hulls']==1
 (root/'model/validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS',aid,len(report),'exports')
