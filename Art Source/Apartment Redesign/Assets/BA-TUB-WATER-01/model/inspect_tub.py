import bpy
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'BA-TUB-01/model/BA_Tub.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  print(o.name, tuple(round(x,3) for x in o.location), tuple(round(x,3) for x in o.dimensions),len(o.data.vertices))
