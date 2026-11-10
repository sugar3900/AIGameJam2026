"""Independent fresh FBX import checks. Geometry/UCX validation and closet door sweep clearance."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def bb(obs):
 vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
 return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def bvh(obs,transform=Matrix.Identity(4)):
 verts=[];faces=[]
 for o in obs:
  start=len(verts);verts.extend(transform@o.matrix_world@v.co for v in o.data.vertices)
  faces.extend(tuple(start+i for i in p.vertices) for p in o.data.polygons)
 return BVHTree.FromPolygons(verts,faces,all_triangles=False)
report={'asset':'BR-CLOSET-STORAGE-03','exports':[]};storage=[]
for side in ('West','East'):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/f'BR_ClosetStorage03_{side}.fbx'))
 obs=[o for o in set(bpy.data.objects)-before if o.type=='MESH'];render=[o for o in obs if not o.name.startswith('UCX_')];hulls=[o for o in obs if o.name.startswith('UCX_')]
 assert len(render)==1 and len(hulls)==14,(side,len(render),len(hulls))
 for o in obs:
  assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
  assert o.location.length<1e-5 if not o.name.startswith('UCX_') else True
  o.data.calc_loop_triangles()
  assert all(t.area>1e-12 for t in o.data.loop_triangles),o.name
  if o in render:assert len(o.data.uv_layers)>0 and all(math.isfinite(x) for u in o.data.uv_layers.active.data for x in u.uv)
  else:
   assert len(o.data.vertices)==8 and len(o.data.polygons)==6,o.name
   edge_counts={}
   for p in o.data.polygons:
    vs=list(p.vertices)
    for a,b in zip(vs,vs[1:]+vs[:1]):key=tuple(sorted((a,b)));edge_counts[key]=edge_counts.get(key,0)+1
   assert all(n==2 for n in edge_counts.values()),o.name
 bounds=bb(render);report['exports'].append({'side':side,'render_meshes':len(render),'ucx_hulls':len(hulls),'bounds':bounds,'vertices':len(render[0].data.vertices),'uv_valid':True,'nondegenerate':True});storage+=render
west,east=[i['bounds'] for i in report['exports']]
aisle=east[0][0]-west[1][0];assert aisle>1.0
report['central_aisle_width']=aisle;report['player_capsule_diameter']=.76;report['centered_capsule_margin_per_side']=(aisle-.76)/2
assert abs(west[1][2]-1.88)<.001 and abs(east[1][2]-1.88)<.001
assert min(west[0][1],east[0][1])>=-.836 and max(west[1][1],east[1][1])<=.836
storage_tree=bvh(storage);min_y_gap=100.;sweeps=[]
for side,hingex,sign in [('L',-.5,-1),('R',.5,1)]:
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT.parent/'BR-CLOSET-02/model'/f'BR_Closet02_Door_{side}.fbx'))
 obs=[o for o in set(bpy.data.objects)-before if o.type=='MESH' and not o.name.startswith('UCX_')]
 for angle in range(96):
  trans=Matrix.Translation((hingex,-.978,0))@Matrix.Rotation(math.radians(sign*angle),4,'Z')
  assert not storage_tree.overlap(bvh(obs,trans)),(side,angle)
  max_y=max((trans@o.matrix_world@v.co).y for o in obs for v in o.data.vertices)
  min_y_gap=min(min_y_gap,-.835-max_y)
 sweeps.append({'door':side,'samples':96,'angles_degrees':[0,95],'overlaps':0})
report['door_sweeps']=sweeps;report['minimum_front_storage_to_door_y_gap']=min_y_gap
report['limits']='Source mesh sampled checks only; Unreal collision recognition, exact capsule, hook appearance and encounter visibility still need integrated review.'
(ROOT/'model/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
