import bpy, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'model/HA_RUNNER_02.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==1
obj=meshes[0]; coords=[obj.matrix_world@v.co for v in obj.data.vertices]
assert all(math.isfinite(c) for v in coords for c in v)
assert obj.data.uv_layers
assert all(math.isfinite(x) for uv in obj.data.uv_layers for t in uv.data for x in t.uv)
obj.data.calc_loop_triangles()
assert all(t.area>1e-14 for t in obj.data.loop_triangles)
bounds={'min':[min(v[i] for v in coords) for i in range(3)],'max':[max(v[i] for v in coords) for i in range(3)]}
a=json.loads((ROOT/'assembly.json').read_text())
error=max(abs(bounds[k][i]-a['bounds'][k][i]) for k in bounds for i in range(3))
assert error<1e-5,(error,bounds)
assert [m.name for m in obj.data.materials]==[m['name'] for m in a['materials']]
origin=a['placement']['origin_plan_m']; world={k:[v+origin[i] for i,v in enumerate(bounds[k])] for k in bounds}
assert world['min'][0]-2.5275>.14
assert abs(world['max'][0]-7.8)<.001
assert world['min'][2]>.0019
result={'status':'PASS','checks':['one render mesh','finite geometry and UVs','nonzero triangles','FBX/source bounds match','four material slots match','minimum 14cm cabinet-front gap','east endpoint retained within1mm','floor clearance2mm','no UCX or blocking collision intended'],'vertices':len(coords),'triangles':len(obj.data.loop_triangles),'bounds_m':bounds,'max_roundtrip_error_m':error,'world_bounds_m':world,'cabinet_gap_m':world['min'][0]-2.5275,'engine_validation':'pending: actual cabinet feet, placement, route and grazing-angle review'}
(ROOT/'model/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
