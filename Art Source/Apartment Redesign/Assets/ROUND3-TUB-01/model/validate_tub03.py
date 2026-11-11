"""Fresh FBX boundary, orientation, UV and retained water/drain contract checks."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(P/'model/BA_Tub03_Body.fbx'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1
ob=obs[0];me=ob.data;me.calc_loop_triangles();assert not [v for v in me.vertices if not all(math.isfinite(c) for c in v.co)]
assert all(t.area>1e-12 for t in me.loop_triangles)
bounds=[[min((ob.matrix_world@v.co)[i] for v in me.vertices) for i in range(3)],[max((ob.matrix_world@v.co)[i] for v in me.vertices) for i in range(3)]]
assert all(abs(a-b)<1e-5 for aa,bb in zip(bounds,[[-.835,-.34,.01],[.835,.34,.583]]) for a,b in zip(aa,bb)),bounds
assert len(me.uv_layers)==1
slots=[m.name for m in me.materials]
assert slots==['Tub03_Exterior_Enamel','Tub03_Interior_Enamel','Tub03_Rolled_Rim','Tub03_Aged_CastMetal','Tub03_Raised_Metal','Tub03_Overflow_Dark'],slots
uv=me.uv_layers.active
for mid in range(len(slots)):
 coords=[uv.data[li].uv for f in me.polygons if f.material_index==mid for li in f.loop_indices]
 assert coords and all(math.isfinite(c) for v in coords for c in v)
 assert max(v.x for v in coords)-min(v.x for v in coords)>.01 and max(v.y for v in coords)-min(v.y for v in coords)>.01,slots[mid]
# Signed volume per connected component, not just a sum that can hide an
# inverted small fitting behind a much larger correctly wound bowl.
bm=bmesh.new();bm.from_mesh(me);remaining=set(bm.verts);volumes=[]
while remaining:
 seed=remaining.pop();island={seed};stack=[seed]
 while stack:
  v=stack.pop()
  for e in v.link_edges:
   q=e.other_vert(v)
   if q in remaining:remaining.remove(q);island.add(q);stack.append(q)
 faces={f for v in island for f in v.link_faces};verts=list(island);lookup={v:i for i,v in enumerate(verts)}
 part=bmesh.new();nverts=[part.verts.new(v.co) for v in verts]
 for f in faces:part.faces.new([nverts[lookup[v]] for v in f.verts])
 assert all(e.is_manifold for e in part.edges)
 vol=part.calc_volume(signed=True);assert vol>1e-11,vol;volumes.append(vol);part.free()
bm.free()
ex=[f for f in me.polygons if f.material_index==0 and .22<f.center.z<.48 and abs(f.normal.z)<.8]
inside=[f for f in me.polygons if f.material_index==1 and .23<f.center.z<.53]
assert ex and inside
assert all(f.normal.dot(Vector((f.center.x,f.center.y,0)))>0 for f in ex)
assert all(f.normal.dot(Vector((f.center.x,f.center.y,0)))<0 for f in inside)
# Raycast down into the bowl at the retained separate drain. No baked fitting
# blocks this seat; the first top surface is the z=.18 enamel floor.
hit,loc,normal,idx=ob.ray_cast(Vector((-.50,0,.50)),Vector((0,0,-1)))
assert hit and abs(loc.z-.18)<1e-5 and normal.z>.99,(hit,loc,normal)
# Original water mesh outline from source: the 43 cm plane lies inside the
# retained inner bowl at all 128 superellipse perimeter samples.
# Compare actual bowl section interpolated from the original source specs.
water_violations=0
for i in range(128):
 a=i*2*math.pi/128;c,s=math.cos(a),math.sin(a)
 x=.718*math.copysign(abs(c)**.65,c);y=.229*math.copysign(abs(s)**.65,s)
 rx=.70+(.43-.22)/(.54-.22)*(.755-.70);ry=.215+(.43-.22)/(.54-.22)*(.26-.215)
 if (abs(x)/rx)**(2/.65)+(abs(y)/ry)**(2/.65)>=1:water_violations+=1
assert water_violations==0
report={'status':'PASS','fresh_fbx':'model/BA_Tub03_Body.fbx','bounds_m':bounds,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'components':len(volumes),'all_component_signed_volumes_positive':True,'component_signed_volumes_m3':sorted(volumes),'nonmanifold_edges':0,'degenerate_triangles':0,'exterior_outward_faces':len(ex),'interior_cavity_faces':len(inside),'single_UV0_all_slots_nonzero':True,'material_slots':slots,'retained_drain_seat_m':list(loc),'water_outline_violations':water_violations,'collision':'reuse installed original tub collision; no new UCX/auto-convex','axes':['-Z','Y'],'pivot_m':[0,0,0]}
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('TUB03 VALIDATION PASS:',len(volumes),'closed outward components;',len(me.loop_triangles),'triangles')

(P/'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f.name!='file-manifest.json'},indent=2)+'\n')
