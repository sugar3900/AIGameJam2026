import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
for filename in ('KI_Jar_Body.fbx','KI_Jar_Lid.fbx'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(P/filename))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert obs,filename
 triangles=verts=0
 for o in obs:
  assert o.data.uv_layers, (filename,'missing UV')
  assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
  assert all(math.isfinite(x) for u in o.data.uv_layers.active.data for x in u.uv)
  o.data.calc_loop_triangles()
  assert all(t.area>1e-12 for t in o.data.loop_triangles),(filename,'zero-area triangle')
  triangles+=len(o.data.loop_triangles);verts+=len(o.data.vertices)
 print(filename,'meshes',len(obs),'verts',verts,'triangles',triangles,'location',tuple(round(x,6) for x in obs[0].location),'dimensions',tuple(round(x,6) for x in obs[0].dimensions))
print('PASS finite geometry, UVs and nonzero geometry triangle area')
