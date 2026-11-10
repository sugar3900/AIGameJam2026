"""Fresh-export structural validation and door/carcass triangle sweeps.
Source-only: installed neighbours and gameplay traces still require Unreal checks.
"""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent
assembly=json.loads((R/'assembly.json').read_text());results=[];meshes={}
def tree(o,transform):
 return BVHTree.FromPolygons([transform@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=0)
for rec in assembly['parts']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(R/'models'/rec['file']))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];o=next(o for o in objs if not o.name.startswith('UCX_'));hs=[h for h in objs if h.name.startswith('UCX_')]
 verts=[o.matrix_world@v.co+Vector(rec['pivot_source_m']) for v in o.data.vertices]
 bounds=[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]]
 err=max(abs(bounds[j][i]-rec[['assembly_min','assembly_max'][j]][i]) for j in range(2) for i in range(3))
 bm=bmesh.new();bm.from_mesh(o.data);deg=sum(f.calc_area()<1e-12 for f in bm.faces);open_edges=sum(not e.is_manifold for e in bm.edges);bm.free()
 failures=[]
 if err>1e-5:failures.append('bounds')
 if len(hs)!=rec['ucx']:failures.append('UCX count')
 if not o.data.uv_layers:failures.append('UV absent')
 if deg:failures.append('degenerate faces')
 # Cache transformed geometry independently of scene lifetime.
 meshes[rec['file']]=([tuple(o.matrix_world@v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
 results.append({'file':rec['file'],'bounds_error_m':err,'ucx':len(hs),'uv_layers':len(o.data.uv_layers),'degenerate_faces':deg,'open_edges':open_edges,'failures':failures})
sweeps=[]
for rec in assembly['parts']:
 if 'max_angle_deg' not in rec:continue
 body=next(r for r in assembly['parts'] if r['kit']==rec['kit'] and r['file'].endswith('_Body.fbx'))
 bv,bf=meshes[body['file']];bt=BVHTree.FromPolygons(bv,bf,epsilon=0)
 dv,df=meshes[rec['file']];pv=Vector(rec['pivot_source_m']);hits=[]
 for step in range(101):
  angle=rec['max_angle_deg']*step/100;rot=Matrix.Rotation(math.radians(angle*rec['source_swing_sign']),3,'Z');dt=BVHTree.FromPolygons([rot@Vector(v)+pv for v in dv],df,epsilon=0);pairs=bt.overlap(dt)
  if pairs:hits.append({'angle':angle,'intersections':len(pairs)})
 sweeps.append({'door':rec['file'],'body':body['file'],'samples':101,'max_angle_deg':rec['max_angle_deg'],'intersections':hits})
report={'fresh_imports':results,'door_carcass_sweeps':sweeps,'passed':all(not r['failures'] for r in results) and all(not r['intersections'] for r in sweeps),'limits':'Triangle surface intersections against own carcass only; Unreal must verify installed neighbours, collision, clicking, materials and complete opening/closing.'}
(R/'fbx-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
assert report['passed'],'validation failures'
