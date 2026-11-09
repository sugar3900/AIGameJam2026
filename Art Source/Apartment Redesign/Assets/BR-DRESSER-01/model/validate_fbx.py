import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parent
for p in sorted(root.glob('*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(p)); objects=[o for o in bpy.context.selected_objects if o.type=='MESH']
 assert objects, str(p)
 badv=sum(not all(math.isfinite(c) for c in v.co) for o in objects for v in o.data.vertices)
 baduv=sum(not all(math.isfinite(c) for c in l.uv) for o in objects for uv in o.data.uv_layers for l in uv.data)
 zero=sum(p.area < 1e-10 for o in objects for p in o.data.polygons)
 missing=sum(not o.data.uv_layers for o in objects)
 print(p.name, 'bad vertices',badv,'bad uv',baduv,'zero faces',zero,'missing uv',missing)
 assert not (badv or baduv or zero or missing),p
