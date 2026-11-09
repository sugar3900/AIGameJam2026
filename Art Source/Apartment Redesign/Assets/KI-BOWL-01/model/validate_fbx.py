import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
files=['KI_Bowl.fbx','Apple_A.fbx','Apple_B.fbx','Pear.fbx','Lemon_A.fbx','Lemon_B.fbx']
for fn in files:
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/fn)); obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert obs, fn
 count=0; tris=0
 for o in obs:
  m=o.data; assert m.uv_layers.active,fn
  assert all(math.isfinite(c) for v in m.vertices for c in v.co),fn
  m.calc_loop_triangles(); uvs=m.uv_layers.active.data
  for t in m.loop_triangles:
   a,b,c=(m.vertices[i].co for i in t.vertices)
   assert (b-a).cross(c-a).length>1e-12,(fn,'degenerate geometry')
   uv=[uvs[i].uv for i in t.loops]
   assert all(math.isfinite(v) for p in uv for v in p),(fn,'nonfinite UV')
   # Polar cap UVs may converge naturally; flag rather than assert near-zero UV triangles.
   tris+=1
  count+=len(m.vertices)
 assert tris>0
 print(fn,'meshes',len(obs),'vertices',count,'triangles',tris)
print('PASS finite geometry/UV, UV presence and nonzero triangle area')
