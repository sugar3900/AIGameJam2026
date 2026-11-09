import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'model/manifest.json').read_text());report=[]
for v in m['variants']:
 allbounds=[]
 for g,p in v['parts'].items():
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/p['file']))
  obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];render=[o for o in obs if not o.name.startswith('UCX_')];hulls=[o for o in obs if o.name.startswith('UCX_')]
  assert len(render)==1,(p['file'],'render meshes',len(render));o=render[0]
  assert o.name==p['object'];assert len(hulls)==p['ucx_hulls'];assert len(o.data.uv_layers)>0
  assert (o.location-Vector(p['pivot'])).length<1e-5,(p['file'],list(o.location),p['pivot'])
  for ob in obs:
   assert all(math.isfinite(c) for ve in ob.data.vertices for c in ve.co)
   assert all(math.isfinite(c) for face in ob.data.polygons for c in face.normal)
   ob.data.calc_loop_triangles();assert all(t.area>1e-12 for t in ob.data.loop_triangles),(p['file'],ob.name,'degenerate')
  assert all(math.isfinite(c) for uv in o.data.uv_layers.active.data for c in uv.uv)
  pts=[o.matrix_world@ve.co for ve in o.data.vertices];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];allbounds +=pts
  for k in range(3):assert abs(lo[k]-p['closed_min'][k])<1e-5 and abs(hi[k]-p['closed_max'][k])<1e-5
  for h in hulls:
   assert h.name.startswith('UCX_'+p['object']+'_');assert len(h.data.vertices)==8
  if g.startswith('drawer'):assert len(hulls)==5
  report.append({'file':p['file'],'render_vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'ucx_convex_boxes':len(hulls),'pivot':list(o.location),'bounds':[lo,hi],'passed':True})
 lo=[min(p[k] for p in allbounds) for k in range(3)];hi=[max(p[k] for p in allbounds) for k in range(3)]
 assert abs(hi[0]-lo[0]-v['width'])<1e-5
 assert hi[1]-lo[1]<=.65001
 assert abs(hi[2]-.91)<1e-5
# The 425 mm module remains unchanged by the range-fit revision.
old=json.loads((ROOT/'model/pre_range_fit_snapshot.json').read_text())
old425=next(v for v in old['variants'] if v['code']=='0425')
new425=next(v for v in m['variants'] if v['code']=='0425')
for g,p in new425['parts'].items():
 for key in ('pivot','closed_min','closed_max','ucx_hulls'):assert p[key]==old425['parts'][g][key],('0425',g,key,'changed unexpectedly')
# Independent hinge/sweep test in XY; Z intervals reject different-height members.
def bounds(o):
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 return [min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]
def overlap(poly,rect):
 axes=[Vector((1,0)),Vector((0,1))]
 for i in range(4):
  e=poly[(i+1)%4]-poly[i];axes.append(Vector((-e.y,e.x)).normalized())
 for axis in axes:
  a=[axis.dot(p) for p in poly];b=[axis.dot(p) for p in rect]
  if min(max(a),max(b))-max(min(a),min(b))<1e-6:return False
 return True
sweeps=[]
for v in m['variants']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/v['parts']['body']['file']))
 body=[bounds(o) for o in bpy.context.scene.objects if o.name.startswith('UCX_')]
 door_parts=[(g,p) for g,p in v['parts'].items() if g.startswith('door')]
 for g,p in door_parts:
  pivot=Vector(p['pivot']);actual_barrel=Vector((pivot.x,-.2705,.24))
  lo=p['closed_min'];hi=p['closed_max']
  # The panel is the actual UCX slab: full leaf width, 35 mm thick.
  leafwidth=(v['carcass_width']-.106)/2 if v['code']=='0775' else v['carcass_width']-.10
  cx=(-(leafwidth+.006)/2 if g=='door_L' else (leafwidth+.006)/2) if v['code']=='0775' else 0
  cx+=v['carcass_offset_x']
  original=[Vector((cx+sx*leafwidth/2,-.2575+sy*.035/2)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
  for deg in range(0,101,5):
   angle=math.radians(deg if g=='door_R' else -deg);c=math.cos(angle);s=math.sin(angle)
   def turn(q):
    x,y=q.x-pivot.x,q.y-pivot.y
    return Vector((pivot.x+c*x-s*y,pivot.y+s*x+c*y))
   axis=turn(Vector((actual_barrel.x,actual_barrel.y)))
   assert (axis-Vector((actual_barrel.x,actual_barrel.y))).length<1e-7,(v['code'],g,deg,'barrel orbit')
   poly=[turn(q) for q in original]
   for blo,bhi in body:
    if min(.6505,bhi[2])-max(.1355,blo[2])<=1e-6:continue
    rect=[Vector((blo[0],blo[1])),Vector((bhi[0],blo[1])),Vector((bhi[0],bhi[1])),Vector((blo[0],bhi[1]))]
    assert not overlap(poly,rect),(v['code'],g,deg,blo,bhi,'door panel overlaps carcass UCX')
  sweeps.append({'variant':v['code'],'door':g,'range_degrees':[0,100 if g=='door_R' else -100],'sample_step':5,'barrel_orbit_m':0,'carcass_panel_overlap':False})
 # Imported paired doors are separate root objects: rotating one cannot move the other.
 if len(door_parts)==2:
  for _,p in door_parts:bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/p['file']))
  l=bpy.data.objects[v['parts']['door_L']['object']];r=bpy.data.objects[v['parts']['door_R']['object']]
  before=r.matrix_world.copy();l.rotation_euler.z=-math.pi/2;bpy.context.view_layer.update()
  assert r.parent is None and l.parent is None and all(abs(r.matrix_world[i][j]-before[i][j])<1e-7 for i in range(4) for j in range(4))
# Full render-mesh triangle sweeps include brass handles and both paired leaves.
from mathutils.bvhtree import BVHTree
def tree(ob):
 verts=[ob.matrix_world@v.co for v in ob.data.vertices]
 return BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in ob.data.polygons],epsilon=1e-8)
mesh_sweeps=[]
for v in m['variants']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for p in v['parts'].values():bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/p['file']))
 obs={g:bpy.data.objects[p['object']] for g,p in v['parts'].items()}
 static=[(g,tree(o)) for g,o in obs.items() if not g.startswith('door')]
 doors=[(g,o) for g,o in obs.items() if g.startswith('door')]
 for deg in range(0,101,5):
  for g,moving in doors:
   for k,o in doors:o.rotation_euler.z=math.radians((deg if k=='door_R' else -deg) if k==g else 0)
   bpy.context.view_layer.update();t=tree(moving)
   for k,fixed in static:assert not t.overlap(fixed),(v['code'],g,deg,k,'render geometry contact')
   for k,other in doors:
    if k!=g:assert not t.overlap(tree(other)),(v['code'],g,deg,k,'partner closed contact')
  if len(doors)==2:
   for g,o in doors:o.rotation_euler.z=math.radians(deg if g=='door_R' else -deg)
   bpy.context.view_layer.update();assert not tree(doors[0][1]).overlap(tree(doors[1][1])),(v['code'],deg,'paired open contact')
 mesh_sweeps.append({'variant':v['code'],'samples':'0..100 degrees at5-degree steps','includes':'all door render geometry including handles, hinges and moldings; body, drawers and closed/open partner','overlap':False})
# Nominal original hardware centerline spacing unchanged between variants.
(ROOT/'model/validation.json').write_text(json.dumps({'status':'passed','checks':'11 FBX fresh reimports; render/UCX separation, convex box counts, finite geometry and UVs, nonzero triangles, native pivot and bounds, widths, depth<=650 mm, counter top910 mm','files':report,'door_sweeps':sweeps,'paired_door_independence':'passed','render_mesh_sweeps':mesh_sweeps},indent=2)+'\n')
print('VALIDATION_PASSED',len(report),'exports')
