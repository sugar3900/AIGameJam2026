from pathlib import Path
import bpy, json, math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];manifest=json.loads((R/'assembly.json').read_text());results=[];parts={};colliders={}
for entry in manifest['exports']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(R/entry['file']))
 objs=[o for o in bpy.context.selected_objects if o.type=='MESH'];vis=[o for o in objs if not o.name.startswith('UCX_')];hulls=[o for o in objs if o.name.startswith('UCX_')]
 assert len(vis)==1 and len(hulls)==entry['collision_hulls'];o=vis[0];m=o.data;m.calc_loop_triangles()
 assert o.location.length<1e-5
 assert all(math.isfinite(c) for v in m.vertices for c in v.co)
 assert len(m.uv_layers)>0
 assert all(math.isfinite(c) for u in m.uv_layers for l in u.data for c in l.uv)
 assert all(t.area>1e-12 for t in m.loop_triangles)
 vv=[o.matrix_world@v.co+Vector(entry['assembly_offset']) for v in m.vertices];lo=[min(v[i] for v in vv) for i in range(3)];hi=[max(v[i] for v in vv) for i in range(3)]
 info={'mesh':entry['mesh'],'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'collision_hulls':len(hulls),'assembled_min':lo,'assembled_max':hi};results.append(info);parts[entry['mesh']]=info
 hullbounds=[]
 for c in hulls:
  assert len(c.data.vertices)==8 and len(c.data.polygons)==6
  vv=[c.matrix_world@v.co+Vector(entry['assembly_offset']) for v in c.data.vertices];l=[min(v[i] for v in vv) for i in range(3)];h=[max(v[i] for v in vv) for i in range(3)];hullbounds.append((l,h))
 colliders[entry['mesh']]=hullbounds
frame=colliders['ARC_Sliding02_Frame'];assert len(frame)==3
assert abs(frame[0][1][0]+.45)<1e-5 and abs(frame[1][0][0]-.45)<1e-5
assert abs(frame[0][0][0]+.48)<1e-5 and abs(frame[1][1][0]-.48)<1e-5
assert abs(frame[2][0][2]-2.15)<1e-5 and abs(frame[2][1][2]-2.18)<1e-5
left=parts['ARC_Sliding02_LeftPanel'];right=parts['ARC_Sliding02_RightPanel']
assert right['assembled_min'][1]-left['assembled_max'][1]>.004
assert abs(left['assembled_min'][0]+.44-(-.01))<1e-5
assert abs(left['assembled_max'][0]+.44-.45)<1e-5
assert abs(right['assembled_max'][0]-.44-.01)<1e-5
assert abs(right['assembled_min'][0]-.44+.45)<1e-5
# Neither individual frame side nor head intersects standing central opening bounds.
for lo,hi in frame:
 assert not all(min(hi[i],[.44,.05,2.14][i])-max(lo[i],[-.44,-.05,.02][i])>1e-6 for i in range(3))
report={'status':'passed','checks':['finite vertices and UV','UV presence','nondegenerate triangles','zero object origins','three open frame UCX boxes','one panel UCX each','0.96x2.18 rough lining bounds','0.90x2.15 clear jamb opening','0.44m track travel within jambs','more than4mm panel hardware depth clearance at overlap'],'exports':results}
(R/'model/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
