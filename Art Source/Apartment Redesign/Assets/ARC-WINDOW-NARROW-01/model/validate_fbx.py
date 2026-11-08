"""Round-trip check wall FBX. Run with Blender --background --python."""
import bpy, math, os
from mathutils import Vector
base=os.path.dirname(os.path.abspath(__file__))
names=("ARC_Window_frame", "ARC_Window_upper_sash", "ARC_Window_lower_sash", "ARC_Window_upper_glass", "ARC_Window_lower_glass")
for name in names:
 bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(base,name+".fbx"))
 objs=[o for o in bpy.context.selected_objects if o.type=="MESH"]
 assert objs, name+" contains no meshes"
 for o in objs:
  m=o.data; m.calc_loop_triangles()
  badv=sum(not all(math.isfinite(c) for c in v.co) for v in m.vertices)
  badn=sum(not all(math.isfinite(c) for c in p.normal) for p in m.polygons)
  baduv=sum(not all(math.isfinite(c) for c in uv.uv) for layer in m.uv_layers for uv in layer.data)
  badtri=sum(t.area<1e-10 for t in m.loop_triangles)
  assert m.uv_layers, name+" has no UV layer"
  uv=m.uv_layers.active.data
  zerouv=0
  for t in m.loop_triangles:
   a,b,c=[uv[i].uv for i in t.loops]
   zerouv+=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-12
  assert not (badv or badn or baduv or badtri or zerouv), (name,badv,badn,baduv,badtri,zerouv)
  print("VALID",name,"objects",len(objs),"vertices",len(m.vertices),"triangles",len(m.loop_triangles),"bounds",tuple(round(v,4) for v in o.dimensions),"nonfinite",badv+badn+baduv,"degenerate",badtri,"zero UV triangles",zerouv)
