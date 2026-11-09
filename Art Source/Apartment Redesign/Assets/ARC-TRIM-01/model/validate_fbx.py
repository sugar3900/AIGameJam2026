import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
for stem,expected in [('Baseboard_1m',(1,.03,.13)),('Crown_1m',(1,.035,.10)),('Casing_1m',(1,.026,.08)),('Baseboard_Inside_Start',(1,.03,.13)),('Baseboard_Inside_End',(1,.03,.13)),('Crown_Inside_Start',(1,.035,.10)),('Crown_Inside_End',(1,.035,.10))]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(root/(stem+'.fbx')))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==1,(stem,len(objs))
 obj=objs[0];mesh=obj.data;assert mesh.uv_layers,stem
 for v in mesh.vertices:assert all(math.isfinite(c) for c in v.co),stem
 for loop in mesh.uv_layers.active.data:assert all(math.isfinite(v) for v in loop.uv),stem
 mesh.calc_loop_triangles()
 for tri in mesh.loop_triangles:
  a,b,c=[mesh.vertices[i].co for i in tri.vertices]
  assert (b-a).cross(c-a).length>1e-10,(stem,tri.index)
 for actual,want in zip(sorted(obj.dimensions),sorted(expected)):
  assert abs(actual-want)<.001,(stem,tuple(obj.dimensions),expected)
 print('VALID',stem,'dims',tuple(round(x,4) for x in obj.dimensions),'triangles',len(mesh.loop_triangles),'uv_layers',len(mesh.uv_layers))
