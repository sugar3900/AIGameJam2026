import bpy,math
from pathlib import Path
p=Path(__file__).resolve().parent/'LV-SOFA-01.fbx';bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(p));objects=[o for o in bpy.context.selected_objects if o.type=='MESH'];bad=zero=uvbad=0
for o in objects:
 for v in o.data.vertices: bad+=not all(math.isfinite(n) for n in v.co)
 for f in o.data.polygons: zero+=f.area<1e-11
 for layer in o.data.uv_layers:
  for u in layer.data: uvbad+=not all(math.isfinite(n) for n in u.uv)
 if not o.data.uv_layers: print('NO UV:',o.name)
print('VALIDATION',len(objects),'meshes',bad,'nonfinite verts',zero,'zero area faces',uvbad,'nonfinite UVs')
if bad or zero or uvbad: raise RuntimeError('invalid mesh')
