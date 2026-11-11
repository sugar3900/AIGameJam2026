"""Fresh FBX geometry and matching-casing / unchanged slide clearance checks."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;A=P.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
def load(file):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(file));return [o for o in bpy.data.objects if o not in before and o.type=='MESH']
def bounds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def near(aa,bb,tol=1e-6):return all(abs(a-b)<=tol for a,b in zip(aa,bb))
def islands(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);remaining=set(bm.verts);out=[]
 while remaining:
  v=remaining.pop();isl={v};stack=[v]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q in remaining:remaining.remove(q);isl.add(q);stack.append(q)
  fs={f for v in isl for f in v.link_faces};vv=list(isl);idx={v:i for i,v in enumerate(vv)};part=bmesh.new();new=[part.verts.new(v.co) for v in vv]
  for f in fs:part.faces.new([new[idx[v]] for v in f.verts])
  assert all(e.is_manifold for e in part.edges);vol=part.calc_volume(signed=True);assert vol>0
  bb=bounds([ob.matrix_world@v.co for v in vv]);out.append({'bounds':bb,'dims':[b-a for a,b in zip(*bb)],'volume_m3':vol});part.free()
 bm.free();return out
obs=load(P/'model/ARC_ClosetFrame04.fbx');frame=next(o for o in obs if not o.name.startswith('UCX_'));hulls=[o for o in obs if o.name.startswith('UCX_')];assert len(hulls)==3
assert near(frame.matrix_world.translation,[0,0,0])
me=frame.data;me.calc_loop_triangles();assert all(t.area>1e-12 for t in me.loop_triangles)
assert len(me.uv_layers)==1 and [m.name for m in me.materials]==['Painted warm ivory','Aged track']
uv=me.uv_layers.active
for i in range(len(me.materials)):
 cc=[uv.data[li].uv for f in me.polygons if f.material_index==i for li in f.loop_indices]
 assert cc and all(math.isfinite(c) for v in cc for c in v)
 assert max(v.x for v in cc)-min(v.x for v in cc)>.01 and max(v.y for v in cc)-min(v.y for v in cc)>.01
vv=[frame.matrix_world@v.co for v in me.vertices];bb=bounds(vv);assert all(near(a,b) for a,b in zip(bb,[[-.55,-.101,0],[.55,.101,2.259]])),bb
floor_points=[v for v in vv if v.z<=.13]
for edge in me.edges:
 a,b=[vv[i] for i in edge.vertices]
 if (a.z-.13)*(b.z-.13)<0:floor_points.append(a+(b-a)*((.13-a.z)/(b.z-a.z)))
floor=bounds(floor_points);assert near(floor[0][:2],[-.54,-.0945]) and near(floor[1][:2],[.54,.0945]),floor
parts=islands(frame);assert len(parts)==15
# Independently compare actual cross sections to regular door casing geometry.
regular=next(o for o in load(A/'ARC-DOOR-03/model/ARC_Door03_Frame.fbx') if not o.name.startswith('UCX_'))
rparts=islands(regular)
assert any(near(p['dims'],[.09,.025,2.1225]) for p in rparts)
assert sum(near(p['dims'],[.09,.025,2.1625]) for p in parts)==4
assert any(near(p['dims'],[1.17,.028,.075]) for p in rparts)
assert sum(near(p['dims'],[1.08,.028,.075]) for p in parts)==2
assert any(near(p['dims'],[1.19,.038,.022]) for p in rparts)
assert sum(near(p['dims'],[1.10,.038,.022]) for p in parts)==2
# Exact old structural hulls, including open centre and no collision bridge.
actual=sorted(tuple(round(c,6) for line in bounds([o.matrix_world@v.co for v in o.data.vertices]) for c in line) for o in hulls)
want=sorted([(-.48,-.07,0,-.45,.07,2.15),(.45,-.07,0,.48,.07,2.15),(-.48,-.07,2.15,.48,.07,2.18)])
assert actual==want,(actual,want)
# Freshly import both old panel exports, assemble at their documented roots and
# test the full +/-44cm stroke. Only unchanged guide seating is intentional.
samples=[]
for name,root,travel in [('LeftPanel',(-.22,-.028,0),.44),('RightPanel',(.22,.028,0),-.44)]:
 panel=next(o for o in load(A/f'ARC-SLIDING-CLOSET-02/model/ARC_Sliding02_{name}.fbx') if not o.name.startswith('UCX_'))
 pv=[panel.matrix_world@v.co for v in panel.data.vertices]
 for i in range(21):
  pos=Vector(root)+Vector((travel*i/20,0,0));ps=[v+pos for v in pv];bbp=bounds(ps)
  assert bbp[0][0]>=-.450001 and bbp[1][0]<=.450001,(name,i,bbp)
  gap=.0695-max(abs(v.y) for v in ps);assert gap>.0139,(name,i,gap)
  assert bbp[0][2]>=.01999 and bbp[1][2]<=2.125001
  samples.append({'panel':name,'travel_m':travel*i/20,'casing_gap_m':gap,'jamb_lateral_gap_m':min(bbp[0][0]+.45,.45-bbp[1][0])})
report={'status':'PASS','bounds_m':bb,'floor_band_bounds_m':floor,'main_mesh_closed_components':len(parts),'all_component_signed_volumes_positive':True,'nonmanifold_edges':0,'degenerate_triangles':0,'single_finite_UV0_both_slots_nonzero':True,'regular_door_casing_sections_match':True,'collision_hulls_unchanged':actual,'panel_motion_samples':samples,'guide_seating':'unchanged top/bottom tracks; original panel-to-guide contact retained','slots':['Painted warm ivory','Aged track']}
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(P/'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f.name!='file-manifest.json'},indent=2)+'\n')
print('CLOSET FRAME PASS: regular sections, 15 outward closed solids, 3 unchanged hulls, 42 complete panel stroke samples')
