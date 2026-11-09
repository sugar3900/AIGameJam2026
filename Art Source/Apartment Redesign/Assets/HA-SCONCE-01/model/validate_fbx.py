import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
for file in sorted(root.glob('HA_Sconce_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(file))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes,file
 nvert=ntri=0;bounds=[]
 for o in meshes:
  assert o.data.uv_layers, (file,o.name,'missing UV')
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co), file
  assert all(math.isfinite(c) for uv in o.data.uv_layers.active.data for c in uv.uv), file
  o.data.calc_loop_triangles()
  for tri in o.data.loop_triangles:
   a,b,c=[o.data.vertices[i].co for i in tri.vertices]
   assert (b-a).cross(c-a).length > 1e-12,(file,'degenerate')
  nvert+=len(o.data.vertices);ntri+=len(o.data.loop_triangles)
  bounds.extend(o.matrix_world @ Vector(corner) for corner in o.bound_box)
 mins=[min(p[i] for p in bounds) for i in range(3)];maxs=[max(p[i] for p in bounds) for i in range(3)]
 print(file.name,'meshes',len(meshes),'vertices',nvert,'triangles',ntri,'bounds',list(zip(mins,maxs)),'origin',tuple(o.location))
