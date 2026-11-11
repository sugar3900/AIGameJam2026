"""Fresh FBX triangle/island evidence on the exact installed 85-degree oven rig."""
import bpy,math,json
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
A=Path(__file__).resolve().parents[2]
KIT=A/'ROUND3-RANGE-03'
bpy.ops.wm.read_factory_settings(use_empty=True)
def load(path):
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path));o=[x for x in bpy.data.objects if x not in old and x.type=='MESH'][0]
 me=o.data;me.calc_loop_triangles();v=[o.matrix_world@x.co for x in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
 # Independent connected islands, indexed by their earliest vertex.
 parent=list(range(len(v)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  x,y=map(root,e.vertices)
  if x!=y:parent[max(x,y)]=min(x,y)
 islands=defaultdict(list)
 for i in range(len(v)):islands[root(i)].append(i)
 info={}
 for i,indices in islands.items():
  vids=set(indices);faces=[p for p in me.polygons if p.vertices[0] in vids]
  info[i]={'vertices':len(indices),'bounds':[[min(v[j][k] for j in indices) for k in range(3)],[max(v[j][k] for j in indices) for k in range(3)]],'materials':sorted(set(me.materials[p.material_index].name for p in faces))}
 return {'v':v,'tris':tris,'island':[root(t[0]) for t in tris],'info':info}
def tree(d,pose=None):return BVHTree.FromPolygons([pose@x for x in d['v']] if pose else d['v'],d['tris'],all_triangles=True,epsilon=0)
def sweep(label,b,d,hinge=(0,-.38,.22)):
 bt=tree(b);report=[]
 for k in range(21):
  angle=k*85/20;p=Vector(hinge);pose=Matrix.Translation(p)@Matrix.Rotation(math.radians(angle),4,'X')@Matrix.Translation(-p)
  pairs=bt.overlap(tree(d,pose));counter=Counter((b['island'][a],d['island'][c]) for a,c in pairs)
  details=[]
  for (ib,id),n in counter.most_common():
   examples=[]
   for a,c in pairs:
    if (b['island'][a],d['island'][c])!=(ib,id):continue
    bv=[b['v'][j] for j in b['tris'][a]];dv=[pose@d['v'][j] for j in d['tris'][c]]
    lo=[max(min(x[i] for x in bv),min(x[i] for x in dv)) for i in range(3)]
    hi=[min(max(x[i] for x in bv),max(x[i] for x in dv)) for i in range(3)]
    examples.append({'body_triangle':a,'door_triangle':c,'contact_aabb':[lo,hi]})
    if len(examples)>=2:break
   details.append({'pairs':n,'body_island':ib,'body':b['info'][ib],'door_island':id,'door':d['info'][id],'examples':examples})
  report.append({'degrees':angle,'pairs':len(pairs),'contacts':details})
 print(label,[(x['degrees'],x['pairs']) for x in report if x['pairs']],flush=True)
 return report
b3=load(A/'ROUND3-RANGE-03/model/KI_RANGE03_Body.fbx');d3=load(A/'ROUND3-RANGE-03/model/KI_RANGE03_Door.fbx')
b2=load(A/'KI-RANGE-02/models/KI_RANGE02_Body.fbx');d2=load(A/'KI-RANGE-02/models/KI_RANGE02_Door.fbx')
b1=load(A/'KI-RANGE-01/model/KI_RANGE_Body.fbx');d1=load(A/'KI-RANGE-01/model/KI_RANGE_Door.fbx')
R={'live_hinge_source_m':[0,-.38,.22],'live_UE_root_cm':[382.5,88.025,22],
 'source_to_engine':'(x,-y,z)*100; opening +X source / UE roll+85',
 '03':sweep('03',b3,d3),'02':sweep('02',b2,d2),'01':sweep('01',b1,d1)}
assert all(not pose['pairs'] for pose in R['03'][6:]),'new contacts after old baseline seating arc'
for pose in R['03']:
 for contact in pose['contacts']:
  assert not any(x.startswith('Enamel_Painted') for x in contact['door']['materials']), 'pressed frame still penetrates fixed hinge plate'
# Dense extra sampling around the actual rig, independent of the 21-pose harness.
bt=tree(b3);dense=[]
for k in range(171):
 angle=k*.5;p=Vector((0,-.38,.22));pose=Matrix.Translation(p)@Matrix.Rotation(math.radians(angle),4,'X')@Matrix.Translation(-p)
 pairs=bt.overlap(tree(d3,pose))
 if angle>=10:assert not pairs,(angle,len(pairs))
 dense.append({'degrees':angle,'triangle_pairs':len(pairs)})
R['dense_half_degree_actual_hinge_sweep']=dense
R['status']='PASS'
(KIT/'contact-validation.json').write_text(json.dumps(R,indent=2)+'\n')
print('RANGE03_CONTACT_PASS',flush=True)
