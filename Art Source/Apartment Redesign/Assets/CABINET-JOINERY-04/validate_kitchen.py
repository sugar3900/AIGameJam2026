import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
A=Path(__file__).resolve().parent.parent
def read(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];o=next(x for x in objs if not x.name.startswith('UCX_'))
 return [o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],len(objs)-1,len(o.data.uv_layers)
def tree(v,f):return BVHTree.FromPolygons(v,f,epsilon=0)
for kit in ('CABINET-JOINERY-04','KI-BACKSPLASH-02','KI-RANGE-02'):
 r=A/kit;records=json.loads((r/'assembly.json').read_text())['parts'];out=[]
 for rec in records:
  v,f,nh,uv=read(r/'models'/rec['file']);good=uv>0 and len(v)>0 and all(math.isfinite(c) for p in v for c in p)
  if kit=='CABINET-JOINERY-04':good=good and nh==rec['ucx']
  # Compare fresh imported local bounds with source assembly minus pivot.
  if kit=='KI-BACKSPLASH-02':
   error=max(abs(min(p[i] for p in v)-rec['source_min'][i]) for i in range(3));good=good and error<.0001
  out.append({'file':rec['file'],'passed':good,'vertices':len(v),'triangles':sum(len(p)-2 for p in f),'ucx':nh,'uv_layers':uv})
 if kit=='CABINET-JOINERY-04':
  base=json.loads((A/'CABINET-JOINERY-02/assembly.json').read_text())['parts'];hits=[]
  for rec in records:
   if '_door' not in rec['file']:continue
   kitname=rec['kit'];pv=Vector(rec['pivot_source_m']);dv,df,_,_=read(r/'models'/rec['file'])
   br=next(x for x in base if x['kit']==kitname and '_Body' in x['file']);bv,bf,_,_=read(A/'CABINET-JOINERY-02/models'/br['file']);obs={'carcass':tree(bv,bf)}
   if kitname=='Base0775':
    fv,ff,_,_=read(A/'CABINET-JOINERY-03/models/KI_Cab04_0775_Filler.fbx');obs['filler']=tree(fv,ff)
    sv,sf,_,_=read(A/'KI-FAUCET-02/models/KI_FAUCET_02_sink_body.fbx');obs['sink']=tree([p+Vector((-.9125,.0145,0)) for p in sv],sf)
   for angle in range(101):
    rot=Matrix.Rotation(math.radians(angle*rec['source_swing_sign']),3,'Z');t=tree([rot@p+pv for p in dv],df)
    for name,ob in obs.items():
     pairs=t.overlap(ob)
     if pairs:hits.append({'file':rec['file'],'angle':angle,'obstacle':name,'pairs':len(pairs)})
  report={'passed':all(x['passed'] for x in out) and not hits,'files':out,'door_sweep_samples_each':101,'sweep_hits':hits,'limits':'Source mesh round-trip and own carcass/sink/filler sweeps only. Engine must repeat all neighbours and real clicks.'}
 else:report={'passed':all(x['passed'] for x in out),'files':out,'limits':'FBX source round-trip only; engine materials, fit, collision and interactions pending.'}
 (r/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(kit,report['passed']);assert report['passed'],report
