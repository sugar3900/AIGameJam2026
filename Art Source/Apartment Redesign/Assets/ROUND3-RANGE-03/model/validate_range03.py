"""Independent fresh-FBX normals, appearance and working-envelope checks."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent.parent;A=P.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
report={'status':'PASS','parts':{},'sweep':[]}
def load(file):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(file));obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(obs)==1;return obs[0]
def coords(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
parts={}
for group in ['Body','Door']:
 ob=load(P/f'model/KI_RANGE03_{group}.fbx');parts[group]=ob;me=ob.data;me.calc_loop_triangles();vv=coords(ob)
 assert all(all(math.isfinite(c) for c in v) for v in vv)
 assert all(t.area>1e-12 for t in me.loop_triangles)
 assert len(me.uv_layers)==1
 uv=me.uv_layers.active;slots=[m.name for m in me.materials]
 for i in range(len(slots)):
  cc=[uv.data[l].uv for f in me.polygons if f.material_index==i for l in f.loop_indices]
  assert cc and all(all(math.isfinite(c) for c in v) for v in cc)
  assert max(v.x for v in cc)-min(v.x for v in cc)>1e-5 and max(v.y for v in cc)-min(v.y for v in cc)>1e-5,(group,slots[i])
 bm=bmesh.new();bm.from_mesh(me);remaining=set(bm.verts);volumes=[]
 while remaining:
  seed=remaining.pop();island={seed};stack=[seed]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q in remaining:remaining.remove(q);island.add(q);stack.append(q)
  faces={f for v in island for f in v.link_faces};verts=list(island);idx={v:i for i,v in enumerate(verts)};part=bmesh.new();new=[part.verts.new(v.co) for v in verts]
  for f in faces:part.faces.new([new[idx[v]] for v in f.verts])
  assert all(e.is_manifold for e in part.edges),(group,'boundary edges')
  vol=part.calc_volume(signed=True);assert vol>1e-12,(group,vol);volumes.append(vol);part.free()
 bm.free()
 bounds=[[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]]
 pivot=list(ob.matrix_world.translation);want=[0,-.363,.23] if group=='Door' else [0,0,0]
 assert all(abs(a-b)<1e-6 for a,b in zip(pivot,want)),(group,pivot)
 report['parts'][group]={'bounds_m':bounds,'pivot_m':pivot,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'closed_components':len(volumes),'all_component_volumes_positive':True,'nonmanifold_edges':0,'degenerate_triangles':0,'single_UV0_all_material_slots_nonzero':True,'slots':slots}
# Successful cooktop and burner geometry is unchanged at all vertices above z .9.
old=load(A/'KI-RANGE-02/models/KI_RANGE02_Body.fbx')
def upper(ob):return sorted(tuple(round(c,6) for c in v) for v in coords(ob) if v.z>.90001)
assert upper(old)==upper(parts['Body'])
report['upper_body_burner_geometry_identical_to_range02']=True
old.hide_render=True;old.hide_set(True)
# The rebuilt door has a real aperture; a straight front ray at the centre hits
# its pane, never a hidden enamel slab.
door=parts['Door'];point=Vector((0,-.5,.485));direction=Vector((0,1,0));inv=door.matrix_world.inverted()
hit,loc,n,face=door.ray_cast(inv@point,inv.to_3x3()@direction)
assert hit and door.data.materials[door.data.polygons[face].material_index].name.startswith('Range03_OvenGlass')
report['real_window_aperture_first_ray_hit']='Range03_OvenGlass'
# New door remains clear of adjacent cabinet envelopes at x +/- .375 across the
# complete 82 degree opening. Its hinge and lateral limits retain the 45mm gap.
base=door.matrix_world.copy();pivot=Vector((0,-.363,.23))
for i in range(21):
 angle=82*i/20;pose=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(angle),4,'X')@Matrix.Translation(-pivot)@base
 vv=[pose@v.co for v in door.data.vertices];xmin=min(v.x for v in vv);xmax=max(v.x for v in vv);zmin=min(v.z for v in vv)
 assert xmin>=-.33001 and xmax<=.33001 and zmin>.20,(angle,xmin,xmax,zmin)
 report['sweep'].append({'degrees':angle,'side_clearance_m':min(xmin+.375,.375-xmax),'minimum_height_m':zmin})
report['gameplay_contract']='retain oven hinge/collision, burner click+flame+light and kettle transforms; engine clicks and neighbour sweep remain required'
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(P/'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f.name!='file-manifest.json'},indent=2)+'\n')
print('RANGE03 PASS: fresh FBXs, outward closed solids, meaningful UV0, real window aperture, identical upper body and 21 opening samples')
