from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'model/LV-ARMCHAIR-02.fbx'))
meshes=[o for o in bpy.data.objects if o.type=='MESH'];render=[o for o in meshes if not o.name.startswith('UCX_')];ucx=[o for o in meshes if o.name.startswith('UCX_')]
assert len(render)==1 and len(ucx)==15,(len(render),len(ucx))
o=render[0];m=o.data;m.calc_loop_triangles()
assert all(math.isfinite(x) for v in m.vertices for x in v.co)
assert m.uv_layers and all(math.isfinite(x) for l in m.uv_layers.active.data for x in l.uv)
zero=[t.index for t in m.loop_triangles if t.area<1e-12]
assert not zero,('zero area',len(zero),zero[:20])
for h in ucx:
 assert len(h.data.vertices)==8 and len(h.data.polygons)==6
 edges={}
 for p in h.data.polygons:
  ids=list(p.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
 assert all(v==2 for v in edges.values())
vs=[o.matrix_world@v.co for v in m.vertices]
bounds={'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]}
assert o.location.length<1e-6
assert abs(bounds['min'][2])<1e-6
result={'asset':'LV-ARMCHAIR-02','render_meshes':len(render),'ucx_members':len(ucx),'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'zero_area_triangles':len(zero),'uv_finite':True,'origin':[0,0,0],'bounds':bounds}
newobs=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(ROOT.parent/'LV-CHAIR-01/model/LV-CHAIR-01.fbx'))
old=[o for o in bpy.data.objects if o not in newobs and o.type=='MESH'];vs=[o.matrix_world@v.co for o in old for v in o.data.vertices]
result['previous_bounds']={'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]}
result['within_previous_bounds']=all(bounds['min'][k]>=result['previous_bounds']['min'][k]-.0001 and bounds['max'][k]<=result['previous_bounds']['max'][k]+.0001 for k in range(3))
assert result['within_previous_bounds']
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model/LV-ARMCHAIR-02.blend'))
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[p.vertices for p in ob.data.polygons],all_triangles=False)
cloth=tree(bpy.data.objects['Contact draped openwork antimacassar'])
contacts={}
for name in ('Shaped sloping back frame','Stuffed tailored back'):
 contacts[name]=len(cloth.overlap(tree(bpy.data.objects[name])))
assert not any(contacts.values()),('lace intersections',contacts)
result['lace_surface_intersections']=contacts
result['limits']='Source FBX roundtrip only. Unreal legacy-import UCX recognition, fitted material appearance and in-room clearance require integration verification.'
for kind in ('fbx','blend'):result['validated_'+kind+'_sha256']=hashlib.sha256((ROOT/'model'/('LV-ARMCHAIR-02.'+kind)).read_bytes()).hexdigest()
(ROOT/'model/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
