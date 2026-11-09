import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root/'KI_CHAIR_01.fbx'))
for o in bpy.context.selected_objects:
 if o.type!='MESH': continue
 m=o.data; m.calc_loop_triangles()
 badv=sum(not all(math.isfinite(float(c)) for c in v.co) for v in m.vertices)
 badn=sum(not all(math.isfinite(float(c)) for c in v.normal) for v in m.vertices)
 baduv=sum(not all(math.isfinite(float(c)) for c in uv.uv) for layer in m.uv_layers for uv in layer.data)
 deg=sum(t.area < 1e-10 for t in m.loop_triangles)
 print('CHECK',o.name,'vertices',len(m.vertices),'triangles',len(m.loop_triangles),'bad vertex',badv,'bad normal',badn,'bad uv',baduv,'degenerate',deg,'dimensions',tuple(o.dimensions))
 if badv or badn or baduv or deg or not m.uv_layers: raise RuntimeError('Invalid mesh export')
