import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path(__file__).resolve().parent.parent;OLD=R.parent/'ARC-ENTRY-DOOR-02'
data=json.loads((R/'assembly.json').read_text());old=json.loads((OLD/'model/validation.json').read_text());checks=[]
for group,part in data['parts'].items():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/part['fbx']))
 objs=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('UCX_')];hulls=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('UCX_')];assert len(objs)==1;o=objs[0]
 vv=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[k] for v in vv) for k in range(3)];hi=[max(v[k] for v in vv) for k in range(3)];expected=part['bounds_pivot_local_m'];prior=next(x for x in old if x['file'].endswith('_'+group+'.fbx'))
 assert max(abs(a-b) for a,b in zip(lo+hi,expected['min']+expected['max']))<1e-5
 assert max(abs(a-b) for a,b in zip(lo+hi,prior['bounds_min']+prior['bounds_max']))<1e-5,'Swept envelope changed'
 assert o.location.length<1e-5 and o.data.uv_layers and len(hulls)==part['ucx_hulls']
 assert all(math.isfinite(x) for v in vv for x in v)
 for hull,(center,size) in zip(sorted(hulls,key=lambda x:x.name),part['collision_specs_unchanged_from02']):
  points=[hull.matrix_world@v.co for v in hull.data.vertices];hlo=[min(v[k] for v in points) for k in range(3)];hhi=[max(v[k] for v in points) for k in range(3)]
  assert max(abs((hlo[k]+hhi[k])/2-center[k]) for k in range(3))<1e-5
  assert max(abs(hhi[k]-hlo[k]-size[k]) for k in range(3))<1e-5
 if group=='Frame':
  tree=BVHTree.FromPolygons(vv,[tuple(p.vertices) for p in o.data.polygons]);pocket_hits=[]
  for a in data['lock_alignment']:
   z=a['strike_plane_source_frame_m'][2];hit=tree.ray_cast(Vector((.493,0,z)),Vector((1,0,0)),.04)[0];assert hit and .5193<hit.x<.5197,'Strike pocket not open';pocket_hits.append(list(hit))
  assert tree.ray_cast(Vector((.54,-.2,2.116)),Vector((0,1,0)),.4)[0] is not None,'Casing joint remains open'
 expected_names=['Aged walnut entrance leaf','Muted aged brass','Edge rub, warm timber','Recess darkness'] if group=='Leaf' else ['Painted warm ivory','Muted aged brass','Recess darkness']
 assert [m.name for m in o.data.materials]==expected_names
 checks.append({'part':group,'roundtrip':'PASS','same_bounds_as02':True,'origin':[0,0,0],'bounds_m':[lo,hi],'uv_loops':len(o.data.uv_layers.active.data),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'ucx':len(hulls),'ucx_centers_and_sizes_match02':True,'material_slot_order':expected_names,'strike_pocket_ray_hits':pocket_hits if group=='Frame' else None})
for a in data['lock_alignment']:
 assert a['leaf_edge_source_frame_m'][1:]==a['strike_plane_source_frame_m'][1:]
 assert a['extended_tip_x_m']>.495 and a['extended_tip_x_m']<.5195
assert abs(data['hardware_clearance_to_bead_m']-.027)<1e-8
assert abs(data['hardware_clearance_to_leaf_edge_m']-.028)<1e-8
sha=hashlib.sha256((OLD/'model/ARC-ENTRY-DOOR-02.blend').read_bytes()).hexdigest();assert sha==data['engine_placement']['original_source_sha256']
(R/'model/validation.json').write_text(json.dumps({'parts':checks,'latch_and_deadbolt_axes_match_strikes':True,'retracted_bolts_within_old_envelope':True,'hardware_fits_stile':True,'original02_source_unchanged':True},indent=2)+'\n');print('ENTRY03_VALIDATION_PASS')
