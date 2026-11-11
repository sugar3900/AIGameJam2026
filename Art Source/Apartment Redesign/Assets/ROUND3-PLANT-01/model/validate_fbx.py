"""Fresh original and patch FBX imports: foliage continuity, pot normals and UVs."""
import bpy,bmesh,json,math
from collections import Counter
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT.parent


def foliage_corners(objects):
    result=Counter()
    for o in objects:
        uv=o.data.uv_layers.active
        for p in o.data.polygons:
            material=o.data.materials[p.material_index].name
            if material not in ('Plant_Leaf','Plant_Leaf_Light'):continue
            for li in p.loop_indices:
                v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                tex=tuple(round(float(x),5) for x in uv.data[li].uv) if uv else (0.,0.)
                result[(tuple(round(float(x),5) for x in v),tex,material)]+=1
    return result


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ASSETS/'FEEDBACK-ROOM-03/model/LV_Book03_Plant.fbx'))
oldfoliage=foliage_corners([o for o in bpy.context.scene.objects if o.type=='MESH'])
old_world_bounds=[[min((o.matrix_world@v.co)[i] for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices),
    max((o.matrix_world@v.co)[i] for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices)] for i in range(3)]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'model/LV_Book04_Plant.fbx'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objects)==1
o=objects[0];me=o.data
materials=[m.name for m in me.materials]
assert materials==['Plant_Leaf','Plant_Leaf_Light','Ceramic_Pot','Pot_Soil'],materials
newfoliage=foliage_corners(objects)
assert not (oldfoliage-newfoliage),('missing/changed foliage corners',sum((oldfoliage-newfoliage).values()))
added=newfoliage-oldfoliage
assert sum(added.values())==96,('only 16-sided root cylinder may add foliage corners',sum(added.values()))
assert all(abs(pos[0]+.33)<.002 and abs(pos[1]+.08)<.002 and 1.655<pos[2]<1.668 for pos,uv,m in added)
world_bounds=[[min((o.matrix_world@v.co)[i] for v in me.vertices),max((o.matrix_world@v.co)[i] for v in me.vertices)] for i in range(3)]
assert abs(world_bounds[2][0]-1.49)<1e-6
for i in range(3):
    for j in (0,1):assert abs(world_bounds[i][j]-old_world_bounds[i][j])<1e-6,(i,j,world_bounds,old_world_bounds)
assert all(abs(float(x))<1e-8 for x in o.location)

bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table()
clayfaces={f for f in bm.faces if f.material_index==2}
left=set(clayfaces);islands=[]
while left:
    first=left.pop();group={first};stack=[first]
    while stack:
        f=stack.pop()
        for e in f.edges:
            for g in e.link_faces:
                if g in left:left.remove(g);group.add(g);stack.append(g)
    islands.append(group)
assert len(islands)==2,('expected vessel and saucer, no floating ornament',len(islands))
me.calc_loop_triangles()
report=[]
for fs in sorted(islands,key=len,reverse=True):
    edges={e for f in fs for e in f.edges}
    assert all(e.is_manifold for e in edges)
    ids={f.index for f in fs}
    volume=sum(me.vertices[t.vertices[0]].co.dot(me.vertices[t.vertices[1]].co.cross(me.vertices[t.vertices[2]].co))/6
        for t in me.loop_triangles if t.polygon_index in ids)
    assert volume>0
    sidefaces=[f for f in fs if len(f.verts)==4]
    assert all(me.polygons[f.index].use_smooth for f in sidefaces)
    uv=me.uv_layers.active.data
    uvareas=[]
    for tri in me.loop_triangles:
        if tri.polygon_index not in ids:continue
        a,b,c=[uv[i].uv for i in tri.loops]
        area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5
        assert area>1e-12,('collapsed ceramic UV',tri.polygon_index,area)
        uvareas.append(area)
    report.append({'faces':len(fs),'closed_manifold':True,'signed_volume_m3':volume,
        'smooth_quad_faces':len(sidefaces),'minimum_uv_triangle_area':min(uvareas)})

def interp(z,points):
    for (z0,r0),(z1,r1) in zip(points,points[1:]):
        if z0<=z<=z1:return r0+(r1-r0)*(z-z0)/(z1-z0)
    raise AssertionError(z)

outer=[];inner=[]
vessel=max(islands,key=len)
for f in vessel:
    p=f.calc_center_median()
    if not 1.545<p.z<1.61:continue
    radial=Vector((p.x+.33,p.y+.08,0));radius=radial.length
    outerr=interp(p.z,[(1.536,.074),(1.573,.081),(1.609,.088),(1.637,.093)])
    innerr=interp(p.z,[(1.540,.070),(1.580,.078),(1.620,.086)])
    (outer if radius>(outerr+innerr)*.5 else inner).append(f.normal.dot(radial.normalized()))
assert outer and min(outer)>.95
assert inner and max(inner)<-.95
bm.free()
REPORT={'status':'PASS','materials':materials,'mesh_count':len(objects),'vertices':len(me.vertices),
    'polygons':len(me.polygons),'triangles':len(me.loop_triangles),'assembly_origin':[float(x) for x in o.location],
    'matrix_world':[list(row) for row in o.matrix_world], 'world_bounds_m':world_bounds,
    'world_bounds_match_original':True,'foliage_corners_preserved':sum(oldfoliage.values()),
    'new_root_corners':sum(added.values()),'ceramic_islands':report,
    'outer_radial_min':min(outer),'bore_radial_max':max(inner),'floating_botanical_ornament_count':0}
(ROOT/'model/fbx-validation.json').write_text(json.dumps(REPORT,indent=2)+'\n')
print('ROUND3_PLANT_FBX_PASS',json.dumps(REPORT))
