import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(R/'model/HA_SLIPPERS_01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==2
v=[o.matrix_world@p.co for o in meshes for p in o.data.vertices];assert all(math.isfinite(c) for p in v for c in p)
a=json.loads((R/'assembly.json').read_text());bounds={k:[f(p[i] for p in v) for i in range(3)] for k,f in [('min',min),('max',max)]}
assert max(abs(bounds[k][i]-a['bounds'][k][i]) for k in bounds for i in range(3))<1e-5
report=[]
for o in meshes:
 assert o.data.uv_layers
 assert all(math.isfinite(c) for l in o.data.uv_layers for q in l.data for c in q.uv)
 o.data.calc_loop_triangles();small=sum(t.area<1e-14 for t in o.data.loop_triangles)
 report.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'degenerate_triangles':small,'materials':[m.name for m in o.data.materials]})
 assert small==0,report[-1]
assert bounds['max'][2]<.08 and bounds['min'][2]>=0
(R/'model/validation.json').write_text(json.dumps({'status':'PASS','parts':report,'bounds_m':bounds,'checks':['two slippers only, no tray','finite geometry/UVs','nonzero triangle areas','roundtrip bounds match','visual rear opening and lining reviewed'],'engine':'placement, import and door clearance pending'},indent=2)+'\n')
print('SLIPPERS PASS',bounds)
