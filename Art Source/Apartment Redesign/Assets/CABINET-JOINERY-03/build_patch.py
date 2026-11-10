"""FIX033 fitted sink-side door correction; preserve immutable JOINERY-02 release."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;A=R.parent
# Reuse the established geometry/export helpers without running the batch builder.
ns={'__file__':str(A/'CABINET-JOINERY-02/build_joinery.py')}
exec((A/'CABINET-JOINERY-02/build_joinery.py').read_text().split("for kit in ('Base0425'")[0],ns)
ns['R']=R;ns['REPORT']=[]
for d in ('models','textures','previews'):(R/d).mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
im=bpy.data.images.load(str(A/'CABINET-JOINERY-02/textures/T_Joinery_Sage.png'))
paint=ns['material']('Joinery_Sage',(.30,.36,.20),.78,image=im)
brass=ns['material']('Joinery_AgedBrass',(.32,.22,.085),.42,.65)
# Original frame [-.3745,-.026], latch edge kept; hinge side narrowed by 32mm.
pv=(-.3455,-.253,0);left=-.3425;right=-.026;w=right-left;cx=(left+right)/2
parts=[]
ns['framed'](cx,-.264,.393,w,.515,.040,paint,parts)
ns['pull'](right-.020,-.275,.440,True,brass,parts)
ns['hinge'](pv,(.24,.53),-1,brass,parts)
ns['export']('KI_Cab04_0775_door_L',parts,pv,[ns['hull']((cx,-.264,.393),(w,.022,.515))],'Base0775')
# Stationary painted hinge-side filler, ending 1mm clear of the barrel.
parts=[]
ns['box']('Fixed hinge-side filler',((-.3745-.352)/2,-.239,.393),(.0225,.022,.515),paint,parts)
ns['export']('KI_Cab04_0775_Filler',parts,(0,0,0),[ns['hull'](((-.3745-.352)/2,-.239,.393),(.0225,.022,.515))],'Base0775')
recs=ns['REPORT'];recs[0].update(replaces='CABINET-JOINERY-02/models/KI_Cab03_0775_door_L.fbx',gameplay_identity='Sink_Door_L',world_pivot_cm=[271.7,72.8,0],max_angle_deg=100)
recs[1].update(placement='same assembly transform as 0775 body; static, never attach to rotating door',world_assembly_cm=[306.25,47.5,0])
(R/'assembly.json').write_text(json.dumps({'parts':recs,'unchanged':'All other JOINERY-02 meshes/materials/interactions. Identity pivot-local door; assembly-origin filler.'},indent=2)+'\n')
# Fresh import each output; source-world uses +X, -Y relative to Unreal world.
def read(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];o=next(o for o in objs if not o.name.startswith('UCX_'))
 return [o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],len([o for o in objs if o.name.startswith('UCX_')]),bool(o.data.uv_layers)
def tree(v,f):return BVHTree.FromPolygons(v,f,epsilon=0)
dv,df,dc,du=read(R/'models/KI_Cab04_0775_door_L.fbx')
fv,ff,fc,fu=read(R/'models/KI_Cab04_0775_Filler.fbx')
bv,bf,_,_=read(A/'CABINET-JOINERY-02/models/KI_Cab03_0775_Body.fbx')
sv,sf,_,_=read(A/'KI-FAUCET-02/models/KI_FAUCET_02_sink_body.fbx')
# Sink origin(215,46.05), cabinet(306.25,47.5): metres in cabinet's source axes.
sv=[v+Vector((-.9125,.0145,0)) for v in sv]
obstacles={'carcass':tree(bv,bf),'fixed_filler':tree(fv,ff),'installed_sink':tree(sv,sf)}
hits=[]
for angle in range(101):
 rot=Matrix.Rotation(math.radians(-angle),3,'Z');dt=tree([rot@v+Vector(pv) for v in dv],df)
 for name,t in obstacles.items():
  pairs=t.overlap(dt)
  if pairs:hits.append({'angle':angle,'obstacle':name,'pairs':len(pairs)})
report={'passed':not hits and dc==fc==1 and du and fu,'samples':101,'range_deg':[0,100],'source_swing_sign':-1,'engine_swing_sign':1,'intersections':hits,'door_ucx':dc,'filler_ucx':fc,'uv_present':du and fu,'limits':'Exact source triangle tests using measured installed origins, not engine gameplay/collision tests. Engine must repeat neighbour sweep and real clicks.'}
(R/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['passed']
# Review assembled cabinet at the new closed and fully open positions.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=1
bpy.context.preferences.filepaths.save_version=0
old=json.loads((A/'CABINET-JOINERY-02/assembly.json').read_text())
for rec in old['parts']:
 if rec['kit']!='Base0775' or rec['file'].endswith('door_L.fbx'):continue
 ob,hs=ns['load'](A/'CABINET-JOINERY-02/models'/rec['file']);ob.location=Vector(rec['pivot_source_m'])
 for h in hs:bpy.data.objects.remove(h,do_unlink=True)
for rec in recs:
 ob,hs=ns['load'](R/'models'/rec['file']);ob.location=Vector(rec['pivot_source_m'])
 for h in hs:bpy.data.objects.remove(h,do_unlink=True)
 if 'door_L' in rec['file']:door=ob
ns['preview']('SinkLeftCorrection',[(door,-100)],1.20,.45)
