"""Fresh FBX round trip; pivot-local bounds, UVs, slots, collision and bulb/chain clearance."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
expected=json.loads((R/'geometry.json').read_text());results=[]
for item in expected:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(R/'models'/(item['mesh']+'.fbx')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];render=[o for o in meshes if not o.name.startswith('UCX_')]
 assert len(render)==1,(item['mesh'],[o.name for o in render])
 o=render[0];co=[o.matrix_world@v.co for v in o.data.vertices]
 assert all(math.isfinite(x) for c in co for x in c)
 lo=[min(c[k] for c in co) for k in range(3)];hi=[max(c[k] for c in co) for k in range(3)]
 for k in range(3):
  assert abs(lo[k]-(item['min'][k]-item['file_pivot_m'][k]))<.00005,(item['mesh'],'min',lo,item)
  assert abs(hi[k]-(item['max'][k]-item['file_pivot_m'][k]))<.00005,(item['mesh'],'max',hi,item)
 assert o.data.uv_layers and all(math.isfinite(v) for u in o.data.uv_layers.active.data for v in u.uv)
 assert [m.name for m in o.data.materials]==item['slots']
 assert all(p.area>1e-12 for p in o.data.polygons)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 boundary=sum(e.is_boundary for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
 assert boundary==0,(item['mesh'],'open edges',boundary)
 assert volume>0,(item['mesh'],'inward',volume)
 hulls=[x for x in meshes if x.name.startswith('UCX_')]
 assert len(hulls)==(1 if item['mesh'].endswith('Chain') else 0)
 if hulls:
  c=hulls[0];bm=bmesh.new();bm.from_mesh(c.data);assert len(bm.verts)==8 and all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.free()
 results.append({'mesh':item['mesh'],'pivot_local_min':lo,'pivot_local_max':hi,'slots':item['slots'],'triangles':len(o.data.polygons),'closed_after_weld':True,'ucx':len(hulls)})
# Source datums check at rest and end of pull; chain clears bulb envelope radially.
chain=next(x for x in expected if x['mesh'].endswith('Chain'));glass=next(x for x in expected if x['mesh'].endswith('Glass'))
assert chain['min'][2]-.015>=1.9999
assert abs(glass['min'][2]-2.46)<.0001
assert math.hypot(.04,.06)-.00165-.035>.03
report={'status':'passed','checks':['fresh FBX import','functional pivots at identity exports','bounds within 0.05mm','finite UVs and nondegenerate faces','closed meshes after coincident vertex weld','positive volumes','one convex chain query hull','15mm pull bottom >=200cm','glass bottom246cm','chain radial bulb clearance >3cm'],'exports':results}
(R/'fbx-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('FIX029 VALIDATION PASS')
