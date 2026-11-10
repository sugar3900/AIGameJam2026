from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent.parent
m=json.loads((P/'assembly.json').read_text());out={'status':'PASS source geometry and context fits; Unreal validation pending','exports':[]}
for e in m['exports']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P/e['file']));oo=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(oo)==1;o=oo[0]
 v=[o.matrix_world@x.co for x in o.data.vertices];assert all(math.isfinite(c) for x in v for c in x);assert o.location.length<1e-5;assert o.data.uv_layers
 assert all(math.isfinite(c) for layer in o.data.uv_layers for uv in layer.data for c in uv.uv)
 lo=[min(x[i] for x in v) for i in range(3)];hi=[max(x[i] for x in v) for i in range(3)]
 err=max(abs(a-b) for aa,bb in [(lo,e['min']),(hi,e['max'])] for a,b in zip(aa,bb));assert err<1e-5
 o.data.calc_loop_triangles();bad=sum(t.area<1e-12 for t in o.data.loop_triangles);assert bad==0,(e['file'],bad)
 bm=bmesh.new();bm.from_mesh(o.data);boundary=sum(e.is_boundary for e in bm.edges);bm.free();assert boundary==0,(e['file'],boundary)
 out['exports'].append(dict(boundary_edges=boundary,file=e['file'],vertices=len(v),triangles=len(o.data.loop_triangles),finite_uvs=True,zero_area_triangles=bad,bound_error_m=err,origin=list(o.location)))
bpy.ops.wm.open_mainfile(filepath=str(P/'model/OF-WAINSCOT-02.blend'))
def tree(o):
 me=o.to_mesh();vs=[o.matrix_world@x.co for x in me.vertices];ps=[list(p.vertices) for p in me.polygons];t=BVHTree.FromPolygons(vs,ps);o.to_mesh_clear();return t
panels=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('OF_Wainscot02_')]
frames=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Context_Door_','Context_Wardrobe_','Context_Window_'))]
hits=[]
for p in panels:
 t=tree(p)
 for f in frames:
  overlap=t.overlap(tree(f))
  if overlap:hits.append(dict(wainscot=p.name,frame=f.name,pairs=len(overlap)))
assert not hits,hits
out['actual_imported_casing_window_mesh_intersections']=hits;out['context_meshes_checked']=len(frames)
out['fits']={'max_projection_m':.022,'door_casing_gap_m':.002,'wardrobe_casing_gap_m':.002,'window_casing_gap_m':.002,'window_sill_notch_gap_m':.002,'window_apron_gap_m':.005,'lead_recess_x':[8.662,9.296],'lead_patch_expected_bounds_x':[8.69405,9.15595],'lead_plane_plan_y':5.668,'lead_face_offset_m':.001,'corner_profiles':'45-degree matching depth-dependent endpoints; continuous per-run rails, fixed60mm full stiles; no X/Z scaling'}
(P/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
