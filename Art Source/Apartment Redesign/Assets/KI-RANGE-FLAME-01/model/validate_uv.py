import bpy
from pathlib import Path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(Path(__file__).parent/'KI_Range_Flame.fbx'))
for o in bpy.context.selected_objects:
 if o.type!='MESH': continue
 m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active.data;n=0
 for t in m.loop_triangles:
  a,b,c=[uv[i].uv for i in t.loops]
  if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-12:n+=1
 print(o.name,'uv_degenerate',n,'of',len(m.loop_triangles))
