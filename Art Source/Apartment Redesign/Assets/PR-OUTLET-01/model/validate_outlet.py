"""Independent fresh-FBX inspection and fit of the matching grounded plug."""
import bpy,bmesh,math,json,fcntl
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LOCK=open('/tmp/apartment_blender.lock','w');fcntl.flock(LOCK,fcntl.LOCK_EX)
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/'PR_Outlet01.fbx'))
art=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
assert len(art)==1
o=art[0];me=o.data;me.calc_loop_triangles()
assert all(math.isfinite(c) for v in me.vertices for c in v.co)
assert o.location.length<1e-6 and all(abs(s-1)<1e-5 for s in o.scale)
assert len(me.uv_layers)==1
uv=me.uv_layers[0].data;assert all(math.isfinite(c) for p in uv for c in p.uv)
assert all(t.area>1e-13 for t in me.loop_triangles)
slots={m.name.split('.')[0] for m in me.materials}
assert slots=={'Outlet_Ivory_Painted','Outlet_Aged_Receptacle','Outlet_Aged_Screw','Outlet_Socket_Shadow'}
areas={s:0 for s in slots}
for t in me.loop_triangles:
    a,b,c=[uv[i].uv for i in t.loops]
    areas[me.materials[t.material_index].name.split('.')[0]]+=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2
assert all(a>1e-8 for a in areas.values())
bm=bmesh.new();bm.from_mesh(me)
assert all(e.is_manifold for e in bm.edges)
remaining=set(bm.verts);volumes=[]
while remaining:
    seed=remaining.pop();vs={seed};stack=[seed]
    while stack:
        for e in stack.pop().link_edges:
            for v in e.verts:
                if v in remaining:remaining.remove(v);vs.add(v);stack.append(v)
    faces={f for v in vs for f in v.link_faces};volume=0
    for f in faces:
        co=[v.co for v in f.verts]
        for i in range(1,len(co)-1):volume+=co[0].dot(co[i].cross(co[i+1]))/6
    assert volume>1e-15;volumes.append(volume)
bm.free()
coords=[o.matrix_world@v.co for v in me.vertices]
lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
assert abs((hi[0]-lo[0])-.070)<1e-5 and abs((hi[2]-lo[2])-.115)<1e-5
collision=[x for x in bpy.context.scene.objects if x.name.startswith('UCX_')]
assert len(collision)==1 and collision[0].name=='UCX_PR_Outlet01_00' and len(collision[0].data.vertices)==8
tree=BVHTree.FromPolygons(coords,[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True)
anchors=json.loads((ROOT/'interaction-anchors.json').read_text())
holes=[]
for key in ['upper_socket','lower_socket']:
    z=anchors[key][2]
    for x,h in [(-.00635,z+.004),(.00635,z+.004),(0,z-.006)]:
        hit,normal,index,distance=tree.ray_cast(Vector((x,-.05,h)),Vector((0,1,0)),.1)
        assert hit is not None and hit.y>.003,(key,x,h,hit)
        holes.append(dict(socket=key,x=x,z=h,backing_hit_y=hit.y))
bpy.ops.import_scene.fbx(filepath=str(ROOT.parent/'PR-DEHUMIDIFIER-01'/'model'/'DH_Plug01.fbx'))
plug=bpy.context.selected_objects[0];plug.data.calc_loop_triangles()
fits=[]
for key in ['upper_socket','lower_socket']:
    loc=Vector(anchors[key])
    ptree=BVHTree.FromPolygons([plug.matrix_world@v.co+loc for v in plug.data.vertices],[tuple(t.vertices) for t in plug.data.loop_triangles],all_triangles=True)
    contacts=len(tree.overlap(ptree));assert contacts==0,(key,contacts)
    fits.append(dict(socket=key,triangle_contacts=contacts))
report={'status':'PASS','blender':bpy.app.version_string,'triangles':len(me.loop_triangles),
        'positive_closed_components':len(volumes),'bounds_m':[lo,hi],
        'degenerate_triangles':0,'nonmanifold_edges':0,'uv0_areas':areas,
        'open_socket_throats':holes,'seated_plug_clearance':fits,
        'limits':'Source geometry only; runtime interaction and Unreal import not implemented.'}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
