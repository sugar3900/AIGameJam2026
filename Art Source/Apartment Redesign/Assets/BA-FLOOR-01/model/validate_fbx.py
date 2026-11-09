import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent

def check(path):
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(path))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert obs
 for ob in obs:
  mesh=ob.data; assert mesh.uv_layers.active, ob.name
  for v in mesh.vertices: assert all(math.isfinite(c) for c in v.co),ob.name
  for uv in mesh.uv_layers.active.data: assert all(math.isfinite(c) for c in uv.uv),ob.name
  mesh.calc_loop_triangles()
  for tri in mesh.loop_triangles:
   a,b,c=(mesh.vertices[i].co for i in tri.vertices)
   assert (b-a).cross(c-a).length>1e-10,(ob.name,tuple(tri.vertices))
 coords=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
 bounds=[max(c[i] for c in coords)-min(c[i] for c in coords) for i in range(3)]
 print(path.name,'meshes',len(obs),'bounds',bounds)
 return obs,bounds
obs,bounds=check(P/'BA_FLOOR_MODULE.fbx')
assert abs(bounds[0]-.9)<.0001 and abs(bounds[1]-1.03923048)<.0001,bounds
# Compare UV and material at matching seam coordinates. Ignore grout substrate vertices.
mosaic=max(obs,key=lambda o:len(o.data.polygons)); mesh=mosaic.data; uv=mesh.uv_layers.active.data
for axis,length in [(0,.9),(1,1.0392304845)]:
 sides=[[],[]]
 for p in mesh.polygons:
  for li in p.loop_indices:
   vertex=mesh.vertices[mesh.loops[li].vertex_index]; c=mosaic.matrix_world@vertex.co
   for s,bound in enumerate((0,length)):
    if abs(c[axis]-bound)<1e-5:
     side=round(c[1-axis],5); coord=tuple(round(x,5) for x in uv[li].uv)
     sides[s].append((side,coord,p.material_index))
 assert sorted(sides[0])==sorted(sides[1]),(axis,len(sides[0]),len(sides[1]),set(sides[0])-set(sides[1]))
 print('seam',axis,'matched',len(sides[0]))
obs,bounds=check(P/'BA_FLOOR_WEAR.fbx'); assert abs(bounds[0]-1.8)<.001 and abs(bounds[1]-2.07846)<.001,bounds
print('PASS')
