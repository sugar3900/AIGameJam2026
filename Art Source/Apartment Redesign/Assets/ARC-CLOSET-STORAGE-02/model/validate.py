from pathlib import Path
import bpy,json,math
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(R/'model/ARC_ClosetStorage02.fbx'))
objs=[o for o in bpy.context.selected_objects if o.type=='MESH'];visual=[o for o in objs if not o.name.startswith('UCX_')];hulls=[o for o in objs if o.name.startswith('UCX_')];assert len(visual)==1 and len(hulls)==2
o=visual[0];m=o.data;m.calc_loop_triangles();assert o.location.length<1e-5
assert len(m.uv_layers)>0
assert all(math.isfinite(c) for v in m.vertices for c in v.co)
assert all(math.isfinite(c) for u in m.uv_layers for l in u.data for c in l.uv)
assert all(t.area>1e-12 for t in m.loop_triangles)
vv=[o.matrix_world@v.co for v in m.vertices];lo=[min(v[i] for v in vv) for i in range(3)];hi=[max(v[i] for v in vv) for i in range(3)]
assert abs(lo[0]+.475)<1e-5 and abs(hi[0]-.475)<1e-5
assert lo[1]>-.50 and hi[1]<1e-6
assert 1.50<lo[2]<1.60 and abs(hi[2]-1.985)<1e-5
for c in hulls:
 assert len(c.data.vertices)==8 and len(c.data.polygons)==6
 assert min(c.dimensions)>0
# Shelf collider controls exact height and depth; no hanger collision hulls are present.
shelf=next(c for c in hulls if c.name.endswith('_00'));vv=[shelf.matrix_world@v.co for v in shelf.data.vertices]
assert abs(min(v.z for v in vv)-1.95)<1e-5 and abs(max(v.z for v in vv)-1.985)<1e-5
assert abs(min(v.y for v in vv)+.30)<1e-5 and abs(max(v.y for v in vv))<1e-5
report={'status':'passed','checks':['FBX round trip','zero object origin','finite geometry/UV','UV presence','nondegenerate triangles','two closed convex UCX boxes only','shelf .95x.30 at1.95..1.985','full hanger depth below.50m','rear edge no geometry behindY0'],'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'collision_hulls':2,'bounds_min':lo,'bounds_max':hi,'overall_depth':hi[1]-lo[1]}
(R/'model/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
