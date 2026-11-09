import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
expected=json.loads((ROOT/'model/dimensions.json').read_text());results=[]
for key,ex in expected.items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 path=ROOT/'model'/f"{ex['mesh']}.fbx";bpy.ops.import_scene.fbx(filepath=str(path))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];render=[o for o in meshes if not o.name.startswith('UCX_')];hulls=[o for o in meshes if o.name.startswith('UCX_')]
 assert len(render)==1,(key,len(render));ob=render[0]
 assert ob.data.uv_layers,(key,'no UV')
 assert all(math.isfinite(v) for vert in ob.data.vertices for v in vert.co),(key,'nonfinite vertex')
 assert all(math.isfinite(v) for loop in ob.data.uv_layers.active.data for v in loop.uv),(key,'nonfinite UV')
 ob.data.calc_loop_triangles();bad=sum(t.area<1e-12 for t in ob.data.loop_triangles);assert bad==0,(key,'zero area geometry',bad)
 corners=[ob.matrix_world@Vector(c) for c in ob.bound_box];lo=[min(v[i] for v in corners) for i in range(3)];hi=[max(v[i] for v in corners) for i in range(3)]
 assert max(abs(a-b) for a,b in zip(lo+hi,ex['bounds_min']+ex['bounds_max']))<1e-5,(key,'bounds changed',lo,hi)
 assert ob.location.length<1e-5,(key,'origin moved',list(ob.location))
 assert len(hulls)==ex['collision_hulls'],(key,'collision hull count')
 for h in hulls:
  assert h.name.startswith('UCX_'+ex['mesh']+'_'),h.name
  assert len(h.data.vertices)==8 and len(h.data.polygons)==6,(h.name,'not convex box')
 if key=='frame':
  assert abs(lo[2]+.07)<1e-5
  assert abs(lo[1]+.17)<1e-5
 results.append({'part':key,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),'collision_hulls':len(hulls),'bounds_min':lo,'bounds_max':hi,'origin':list(ob.location),'UV':'finite and present','zero_area_geometry_triangles':bad})
# Analytic track check: lower and upper wood bands do not overlap in depth.
lower=(-.028-.014,-.028+.014);upper=(.023-.014,.023+.014)
assert lower[1]<upper[0]
assert .310+.537/2+.48 < 1.15-.044
out={'status':'PASS','units':'metres','parts':results,'fit':{'apron_world_bottom':1.18,'sill_projection_from_wall_face':.11,'lower_slide_max':.48,'wood_track_gap':upper[0]-lower[1]},'limitations':'Unreal import/pivots/materials/collision recognition and complete sink/faucet/camera fit still require engine review.'}
(ROOT/'model/validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
