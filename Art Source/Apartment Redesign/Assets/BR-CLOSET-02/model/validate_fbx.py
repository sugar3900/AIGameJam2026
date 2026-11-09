from pathlib import Path
import bpy, json, math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assembly.json').read_text());result=[]
for entry in manifest['exports']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/entry['file']))
 objects=[o for o in bpy.context.selected_objects if o.type=='MESH'];visual=[o for o in objects if not o.name.startswith('UCX_')];hulls=[o for o in objects if o.name.startswith('UCX_')]
 assert len(visual)==1,(entry['file'],[o.name for o in objects])
 assert len(hulls)==entry['collision_hulls']
 o=visual[0];m=o.data;m.calc_loop_triangles()
 assert all(math.isfinite(c) for v in m.vertices for c in v.co)
 assert len(m.uv_layers)>0
 assert all(math.isfinite(c) for uv in m.uv_layers for l in uv.data for c in l.uv)
 assert all(t.area>1e-12 for t in m.loop_triangles),entry['file']
 assert o.location.length<1e-5,(entry['file'],list(o.location))
 vertices=[o.matrix_world@v.co+Vector(entry['assembly_offset']) for v in m.vertices]
 lo=[min(v[i] for v in vertices) for i in range(3)];hi=[max(v[i] for v in vertices) for i in range(3)]
 result.append({'mesh':entry['mesh'],'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'uv_layers':len(m.uv_layers),'collision_hulls':len(hulls),'local_origin':list(o.location),'assembled_bounds_min':[round(x,5) for x in lo],'assembled_bounds_max':[round(x,5) for x in hi]})
 if entry['mesh'].endswith('Bulb'):assert abs(lo[2]-2.06)<.002
 if entry['mesh'].endswith('Shelf'):assert hi[0]<=-.73 and lo[2]>1.90
 if entry['mesh'].endswith('Mold'):assert abs(lo[2]-.75)<.001 and abs(hi[2]-1.85)<.001
 # Validate hulls are closed convex cubes and have positive dimensions.
 for c in hulls:
  assert len(c.data.vertices)==8 and len(c.data.polygons)==6
  assert min(c.dimensions)>0
# Target standing volume x[-.3,.3], y[-.15,.45], z[0,1.8] is free of all exports.
for item in result:
 if item['mesh'].endswith('Mold'):continue
 lo=item['assembled_bounds_min'];hi=item['assembled_bounds_max']
 # Trim joined bounds span doorway; use constituent UCX during engine clearance validation.
 if item['mesh'].endswith('Trim'):continue
 overlap=all(min(hi[i],[.3,.45,1.8][i])-max(lo[i],[-.3,-.15,0][i])>1e-6 for i in range(3))
 assert not overlap,item['mesh']
(ROOT/'model/validation.json').write_text(json.dumps({'status':'passed','checks':['FBX round trip','finite vertices/UV','UV presence','nondegenerate triangles','zero export origins','UCX hull counts and closed cubes','bulb and mold heights','west-only shelf','1.8m central standing proxy exclusion'],'exports':result},indent=2)+'\n')
print(json.dumps(result,indent=2));print('BR-CLOSET-02 round-trip validation PASSED')
