import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'HA_BENCH_01.fbx'))
mesh_objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(mesh_objects)==1
obj=mesh_objects[0];mesh=obj.data;assert mesh.uv_layers.active
assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
assert all(math.isfinite(c) for v in mesh.vertices for c in v.normal)
assert all(math.isfinite(c) for uv in mesh.uv_layers.active.data for c in uv.uv)
mesh.calc_loop_triangles();assert all(t.area>1e-10 for t in mesh.loop_triangles)
assert all(abs(c)<1e-5 for c in obj.location),obj.location
assert abs(obj.dimensions.x-.62)<.001 and obj.dimensions.y<=.250001 and abs(obj.dimensions.z-.45)<.001,tuple(obj.dimensions)
print('PASS: vertices',len(mesh.vertices),'triangles',len(mesh.loop_triangles),'dimensions',tuple(round(v,6) for v in obj.dimensions),'origin',tuple(round(v,6) for v in obj.location))
