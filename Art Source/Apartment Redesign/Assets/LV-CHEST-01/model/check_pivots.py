import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
for name in ['LV_CHEST_BODY.fbx','LV_CHEST_LID.fbx']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(p/name))
 o=next(o for o in bpy.context.selected_objects if o.type=='MESH')
 print(name,'origin',tuple(round(v,4) for v in o.location),'bounds',tuple(round(v,4) for v in o.dimensions))
 if 'LID' in name:
  assert abs(o.location.y-.175)<.0001 and abs(o.location.z-.35)<.0001
print('PIVOT PASS')
