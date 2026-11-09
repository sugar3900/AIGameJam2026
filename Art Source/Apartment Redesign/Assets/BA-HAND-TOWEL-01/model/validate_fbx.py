import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'BA_Hand_Towel.fbx'),axis_forward='-Z',axis_up='Y')
meshes=[o for o in bpy.context.selected_objects if o.type=='MESH'];assert len(meshes)==1
obj=meshes[0]; mesh=obj.data; assert mesh.uv_layers.active
verts=[obj.matrix_world @ v.co for v in mesh.vertices]
assert all(math.isfinite(x) for v in verts for x in v)
assert all(math.isfinite(x) for loop in mesh.uv_layers.active.data for x in loop.uv)
mesh.calc_loop_triangles();assert all((verts[t.vertices[1]]-verts[t.vertices[0]]).cross(verts[t.vertices[2]]-verts[t.vertices[0]]).length>1e-10 for t in mesh.loop_triangles)
lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
origin=tuple(round(float(v),5) for v in obj.location);dims=tuple(round(hi[i]-lo[i],5) for i in range(3))
print('VALID meshes',len(meshes),'vertices',len(mesh.vertices),'triangles',len(mesh.loop_triangles),'UV',mesh.uv_layers.active.name,'origin',origin,'bounds',dims,'lower',lo,'upper',hi)
