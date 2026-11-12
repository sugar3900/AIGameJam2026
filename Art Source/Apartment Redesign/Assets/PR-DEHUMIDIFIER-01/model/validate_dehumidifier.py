"""Fresh FBX round-trip checks: topology, UV0, material slots, split alignment."""
import bpy, bmesh, math, json, fcntl
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

LOCK=open('/tmp/apartment_blender.lock','w')
fcntl.flock(LOCK,fcntl.LOCK_EX)
ROOT=Path(__file__).resolve().parents[1]
expected={m['slot'] for m in json.loads((ROOT/'materials.json').read_text())}

def inspect(filename):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/filename))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    art=[o for o in meshes if not o.name.startswith('UCX_')]
    assert len(art)==1,(filename,[o.name for o in art])
    o=art[0]; me=o.data
    coords=[o.matrix_world@v.co for v in me.vertices]
    assert all(math.isfinite(c) for co in coords for c in co)
    lo=[min(co[i] for co in coords) for i in range(3)]
    hi=[max(co[i] for co in coords) for i in range(3)]
    assert (o.matrix_world.translation-Vector((0,0,0))).length<1e-5,'Pivot lost'
    assert all(abs(s-1)<1e-5 for s in o.scale),'Unexpected import scale'
    assert len(me.uv_layers)==1,'Expected explicit UV0 only'
    uv=me.uv_layers[0].data
    assert all(math.isfinite(x) for p in uv for x in p.uv)
    assert len(me.materials)>0 and all(m for m in me.materials)
    slots={m.name.split('.')[0] for m in me.materials}
    assert slots<=expected,slots-expected
    me.calc_loop_triangles()
    degenerate=sum(t.area<1e-13 for t in me.loop_triangles)
    assert degenerate==0,(filename,'degenerate triangles',degenerate)
    uv_areas={s:0 for s in slots}
    for t in me.loop_triangles:
        a,b,c=[uv[i].uv for i in t.loops]
        area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2
        uv_areas[me.materials[t.material_index].name.split('.')[0]]+=area
    assert all(a>1e-8 for a in uv_areas.values()),uv_areas
    bm=bmesh.new(); bm.from_mesh(me)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    assert nonmanifold==0,(filename,'nonmanifold edges',nonmanifold)
    # Every disconnected closed solid must be wound outward independently.
    remaining=set(bm.verts); volumes=[]
    while remaining:
        seed=remaining.pop(); verts={seed}; stack=[seed]
        while stack:
            for e in stack.pop().link_edges:
                for n in e.verts:
                    if n in remaining:remaining.remove(n);verts.add(n);stack.append(n)
        faces={f for v in verts for f in v.link_faces}
        volume=0
        for f in faces:
            vs=[v.co for v in f.verts]
            for i in range(1,len(vs)-1):volume+=vs[0].dot(vs[i].cross(vs[i+1]))/6
        assert volume>1e-15,(filename,'inverted or zero-volume component',volume)
        volumes.append(volume)
    bm.free()
    collision=[x for x in meshes if x.name.startswith('UCX_')]
    if filename=='DH_Dehumidifier01.fbx':
        assert len(collision)==1 and collision[0].name=='UCX_DH_Dehumidifier01_00'
        assert slots==expected,(slots,expected)
        assert abs(lo[2])<1e-5 and .52<hi[2]<.55,(lo,hi)
        assert .42<hi[0]-lo[0]<.44 and .34<hi[1]-lo[1]<.40,(lo,hi)
        c=collision[0]
        assert len(c.data.vertices)==8,'Collision should be one simple box'
    else:assert not collision,'Split exports intentionally omit collision'
    return dict(file=filename,vertices=len(me.vertices),triangles=len(me.loop_triangles),
        closed_positive_components=len(volumes),nonmanifold_edges=nonmanifold,
        degenerate_triangles=degenerate,bounds_m=[lo,hi],uv0_area_by_slot=uv_areas,
        collision_meshes=len(collision))

files=['DH_Dehumidifier01.fbx','DH_Dehumidifier01_Body.fbx','DH_Dehumidifier01_Tank.fbx',
       'DH_Dehumidifier01_CordStowed.fbx','DH_Plug01.fbx']
results=[inspect(f) for f in files]
assert sum(r['triangles'] for r in results[1:])==results[0]['triangles']
# Confirm the authored bucket can actually slide out without touching the casing.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
parts=[]
for file in ['DH_Dehumidifier01_Body.fbx','DH_Dehumidifier01_Tank.fbx']:
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/file))
    parts.append(bpy.context.selected_objects[0])
def tree(o,offset=0):
    me=o.data; me.calc_loop_triangles()
    vertices=[o.matrix_world@v.co+Vector((0,-offset,0)) for v in me.vertices]
    return BVHTree.FromPolygons(vertices,[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True)
fixed=tree(parts[0]); travel=[]
for i in range(11):
    offset=.245*i/10
    contacts=len(fixed.overlap(tree(parts[1],offset)))
    assert contacts==0,('Bucket extraction intersects casing',offset,contacts)
    travel.append(dict(pull_m=offset,triangle_contacts=contacts))
report=dict(status='PASS',blender=bpy.app.version_string,checks=results,
            bucket_pull_sweep=travel,
            limits='Geometry/source checks only; no Unreal import or gameplay validation claimed.')
# Reassemble all four exports, including the plug's authored seating pivot.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
anchors=json.loads((ROOT/'interaction-anchors.json').read_text())
coords=[]
for file in files[1:]:
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'model'/file))
    o=bpy.context.selected_objects[0]
    if file=='DH_Plug01.fbx':
        p=anchors['plug']
        o.matrix_world=Matrix.Translation(p['stored_location'])@Matrix.Rotation(math.radians(p['stored_rotation_x_deg']),4,'X')@o.matrix_world
    coords += [o.matrix_world@v.co for v in o.data.vertices]
for i in range(3):
    assert abs(min(co[i] for co in coords)-results[0]['bounds_m'][0][i])<1e-5
    assert abs(max(co[i] for co in coords)-results[0]['bounds_m'][1][i])<1e-5
assert anchors['plug']['insertion_axis']==[0,1,0]
assert anchors['runtime_cable']['radius_m']==.003
report['split_assembly_with_stored_plug']='PASS'
cable=inspect('DH_CableSegment01.fbx')
assert abs(cable['bounds_m'][0][0])<1e-5 and abs(cable['bounds_m'][1][0]-1)<1e-5
assert abs(cable['bounds_m'][1][1]-cable['bounds_m'][0][1]-.006)<1e-5
report['spline_cable']=cable
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model'/'PR-DEHUMIDIFIER-01.blend'))
normal=Vector((0,-1,.5)).normalized();plane=Vector((0,-.130,.455))
mounts={}
for name in ['Dial seating ring','Power rocker','Tank lamp bezel']:
    obj=bpy.data.objects[name]
    depth=min((obj.matrix_world@v.co-plane).dot(normal) for v in obj.data.vertices)
    assert -.0011<depth<.0001,(name,'Unseated control mount',depth)
    mounts[name]=dict(back_surface_depth_mm=depth*1000)
vanes=[o for o in bpy.data.objects if o.name.startswith('Cream vertical intake vane')]
assert len(vanes)==15
setback=min((o.matrix_world@v.co).y for o in vanes for v in o.data.vertices)+.155
assert setback>.009,('Front vents project too far',setback)
for obj in vanes:
    z=[(obj.matrix_world@v.co).z for v in obj.data.vertices]
    assert min(z)<.273 and max(z)>.413,('Unseated vane end',obj.name,z)
report['flat_panel_control_seating']=mounts
report['front_vent_setback_mm']=setback*1000
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
