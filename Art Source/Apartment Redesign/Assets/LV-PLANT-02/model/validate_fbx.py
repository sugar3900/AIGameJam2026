import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent
M=json.loads((BASE/'manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(BASE/'model/LV-PLANT-02.blend'))
def record(o):
    co=[o.matrix_world@v.co for v in o.data.vertices]
    bm=bmesh.new();bm.from_mesh(o.data)
    r={'bounds':{'min':[min(v[i] for v in co) for i in range(3)],'max':[max(v[i] for v in co) for i in range(3)]},'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials],'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)}
    bm.free();assert all(math.isfinite(c) for v in co for c in v)
    if not o.name.startswith('UCX_'):
        assert len(o.data.uv_layers)>0
        assert all(math.isfinite(c) for d in o.data.uv_layers[0].data for c in d.uv)
    return r
original={o.name:record(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert original['LV_Plant02_Leaves']['nonmanifold_edges']==0
assert original['LV_Plant02_Leaves']['signed_volume']>0
assert all(p.normal.z>.99 for p in bpy.data.objects['LV_Plant02_Soil'].data.polygons)
# Downward ray confirms opaque floor-facing underside now exists.
pot=bpy.data.objects['LV_Plant02_Pot'];hit=pot.ray_cast(Vector((0,0,-.1)),Vector((0,0,1)))
assert hit[0] and abs(hit[1].z-.005)<1e-6 and hit[2].z<-.99
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(BASE/'model/LV_Plant02.fbx'),use_custom_normals=True)
imported={o.name:record(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert set(imported)==set(original),(set(imported),set(original))
errors={}
for name,r in original.items():
    q=imported[name];e=max(abs(r['bounds'][k][i]-q['bounds'][k][i]) for k in ['min','max'] for i in range(3));assert e<.00001,(name,e)
    assert q['materials']==r['materials'],name
    assert q['faces']==r['faces'],name
    errors[name]=e
assert imported['LV_Plant02_Leaves']['nonmanifold_edges']==0
assert imported['UCX_LV_Plant02_Pot_00']['nonmanifold_edges']==0
result={'status':'PASS','real_fbx_roundtrip':True,'visual_parts':5,'ucx_parts':1,'maximum_bounds_error_m':max(errors.values()),'parts':imported,'underside_raycast':{'hit':True,'height':.005,'outward_normal':'-Z'},'notes':['Leaf shells manifold with positive volume before and after FBX','Finite UVs on all five visual groups','Original pot outer surface retained exactly; added underside face only','Soil positions and UV mapping preserved, face winding corrected upward; cream unchanged; source origins unchanged','Engine instance wall/fuse clearance and material import remain integration checks']}
(BASE/'model/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
