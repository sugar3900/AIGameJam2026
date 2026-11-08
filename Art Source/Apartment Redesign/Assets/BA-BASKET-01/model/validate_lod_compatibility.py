import bpy
from pathlib import Path
root=Path(__file__).resolve().parent
results=[]
for name in ['BA_Basket.fbx','BA_Basket_LOD1.fbx']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for m in list(bpy.data.materials): bpy.data.materials.remove(m)
 bpy.ops.import_scene.fbx(filepath=str(root/name));o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 print(name,'origin',tuple(round(x,5) for x in o.location),'materials',[m.name for m in o.data.materials]);results.append((tuple(round(x,5) for x in o.location),[m.name for m in o.data.materials]))
assert results[0]==results[1],results
print('PASS matching origin and material slots')
