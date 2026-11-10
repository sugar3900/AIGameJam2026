import bpy,json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'manifest.json').read_text());checks=[]
for name,expected in report['component_bounds'].items():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(ROOT/'models'/(name+'.fbx')))
 objs=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('UCX_')];hulls=[o for o in bpy.data.objects if o.name.startswith('UCX_')]
 assert len(objs)==1;o=objs[0];v=[o.matrix_world@x.co for x in o.data.vertices];lo=[min(p[k] for p in v) for k in range(3)];hi=[max(p[k] for p in v) for k in range(3)]
 assert max(abs(a-b) for a,b in zip(lo+hi,expected['min']+expected['max']))<1e-5
 assert o.location.length<1e-5 and o.data.uv_layers
 assert all(math.isfinite(c) for p in v for c in p)
 assert len(hulls)==(1 if name.endswith('Hardware') else 0)
 checks.append({'name':name,'bounds_m':[lo,hi],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'uv_loops':len(o.data.uv_layers.active.data),'ucx_hulls':len(hulls),'origin_m':list(o.location),'roundtrip':'PASS'})
old=ROOT.parent/'HA-SCONCE-01/model/HA-SCONCE-01.blend';assert hashlib.sha256(old.read_bytes()).hexdigest()==report['original_source_sha256']
(ROOT/'validation.json').write_text(json.dumps({'parts':checks,'original_source_unchanged':True},indent=2)+'\n');print('SCONCE02_EXPORTS_PASS')
