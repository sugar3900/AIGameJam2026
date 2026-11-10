"""Independent FBX reimport, mitre pairing and volume/topology checks."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
P=json.loads((ROOT/'profiles.json').read_text())['profiles_m'];report={'status':'PASS','units':'metres','files':{},'pairs':{}}
for family,profile in P.items():
 edges=[];solids=[]
 for side in ('End','Start'):
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  name=f'{family}_Outside_{side}';bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/f'{name}.fbx'))
  objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==1
  ob=objs[0];me=ob.data;co=[ob.matrix_world@v.co for v in me.vertices]
  assert ob.location.length<1e-6,(name,'origin')
  assert me.uv_layers and all(math.isfinite(x) for uv in me.uv_layers.active.data for x in uv.uv)
  assert len(me.materials)==1 and me.materials[0].name.split('.')[0]=='AgedIvoryPaint'
  assert all(math.isfinite(x) for v in co for x in v)
  bm=bmesh.new();bm.from_mesh(me)
  # Import can split positions at UV/material seams; geometric weld restores solid topology.
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
  assert all(e.is_manifold for e in bm.edges),(name,'nonmanifold')
  assert all(e.is_contiguous for e in bm.edges),(name,'inconsistent winding')
  volume=bm.calc_volume(signed=True);assert volume>0,(name,'inverted normals',volume)
  bm.free();me.calc_loop_triangles()
  assert all((co[t.vertices[1]]-co[t.vertices[0]]).cross(co[t.vertices[2]]-co[t.vertices[0]]).length>1e-10 for t in me.loop_triangles)
  front=max(-y for y,z in profile);height=max(z for y,z in profile)
  lo=[min(v[i] for v in co) for i in range(3)];hi=[max(v[i] for v in co) for i in range(3)]
  expected_lo=[0 if side=='End' else -front,-front,0];expected_hi=[1+front if side=='End' else 1,0,height]
  assert max(abs(a-b) for a,b in zip(lo+hi,expected_lo+expected_hi))<1e-6,(name,lo,hi)
  # Both square-end and mitre retain the exact original cross-section.
  for y,z in profile:assert any(abs(v.y-y)<1e-6 and abs(v.z-z)<1e-6 for v in co)
  if side=='End':edge=[v for v in co if abs(v.x+v.y-1)<1e-6];world=co
  else:edge=[Vector((1-v.y,v.x,v.z)) for v in co if abs(v.x-v.y)<1e-6];world=[Vector((1-v.y,v.x,v.z)) for v in co]
  unique=[]
  for v in edge:
   if not any((v-w).length<1e-6 for w in unique):unique.append(v)
  assert len(unique)==len(profile),(name,len(unique))
  edges.append(unique);solids.append(world)
  report['files'][name]={'bounds_min':lo,'bounds_max':hi,'triangles':len(me.loop_triangles),'profile_vertices':len(profile),'signed_volume':volume,'closed_manifold_consistent_normals':True,'material_slot':'AgedIvoryPaint','uv_layers':len(me.uv_layers)}
 maxgap=max(min((v-w).length for w in edges[1]) for v in edges[0]);assert maxgap<1e-6
 # Exact separating half-spaces prove no volumetric overlap, even for concave profiles.
 end_plane=max(v.x+v.y-1 for v in solids[0]);start_plane=min(v.x+v.y-1 for v in solids[1])
 assert end_plane<1e-6 and start_plane>-1e-6
 report['pairs'][family]={'max_matching_profile_error_m':maxgap,'end_halfspace_max':end_plane,'start_halfspace_min':start_plane,'zero_volumetric_overlap':'End x+y<=1 and transformed Start x+y>=1; intersection is only the matching mitre face','assembly':'End origin(0,0,z), Start origin(1,0,z) rotated+90deg about source Z','ue_example_cm':'End(386,386,Z) yaw0; Start(486,386,Z) yaw-90; verify expected sourceY flip in importer'}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
