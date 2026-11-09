import bpy,math
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(here/'ARC_Ceiling_Module_2m.fbx'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert len(objs)==1
obj=objs[0]; mesh=obj.data
assert len(mesh.uv_layers)>0
assert len(mesh.polygons)==4
points=[obj.matrix_world@v.co for v in mesh.vertices]
for p in points: assert all(math.isfinite(a) for a in p)
mins=[min(p[i] for p in points) for i in range(3)]; maxs=[max(p[i] for p in points) for i in range(3)]
assert abs(maxs[0]-mins[0]-2)<1e-5 and abs(maxs[1]-mins[1]-2)<1e-5 and abs(maxs[2]-mins[2])<1e-5, (mins,maxs)
uvs=mesh.uv_layers.active.data
for poly in mesh.polygons:
 assert poly.area>1e-9
 n=(obj.matrix_world.to_3x3()@poly.normal).normalized(); assert n.z<-.999, tuple(n)
 for i in poly.loop_indices: assert all(math.isfinite(a) for a in uvs[i].uv)
# Boundary matching for mirrored mesh, regardless of winding.
for axis in [0,1]:
 edges={}
 for poly in mesh.polygons:
  for i in poly.loop_indices:
   loop=mesh.loops[i]; p=obj.matrix_world@mesh.vertices[loop.vertex_index].co
   if abs(p[axis])<1e-5 or abs(p[axis]-2)<1e-5:
    key=(round(p[1-axis],5),0 if p[axis]<1 else 2)
    edges.setdefault(key,set()).add(tuple(round(u,5) for u in uvs[i].uv))
 for other in (0,1,2):
  assert edges[(other,0)]==edges[(other,2)], (axis,other,edges)
print('PASS bounds',mins,maxs,'four downward faces, UVs and mirrored edge matches')
