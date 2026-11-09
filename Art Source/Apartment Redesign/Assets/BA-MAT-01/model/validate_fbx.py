import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'BA_Mat.fbx'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1
obj=obs[0];mesh=obj.data;assert mesh.uv_layers
assert all(math.isfinite(v) for p in mesh.vertices for v in p.co)
assert all(math.isfinite(v) for p in mesh.polygons for v in p.normal)
assert all(math.isfinite(v) for l in mesh.uv_layers.active.data for v in l.uv)
mesh.calc_loop_triangles();assert all(t.area>1e-12 for t in mesh.loop_triangles)
world=[obj.matrix_world@v.co for v in mesh.vertices]
bounds=[max(p[i] for p in world)-min(p[i] for p in world) for i in range(3)]
assert .545<bounds[0]<.555 and .395<bounds[1]<.405 and bounds[2]<.02, bounds
print('PASS meshes',len(obs),'vertices',len(mesh.vertices),'triangles',len(mesh.loop_triangles),'bounds_m',*[round(x,6) for x in bounds], 'uv_layers',len(mesh.uv_layers))
