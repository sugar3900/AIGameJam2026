import bpy, os
from mathutils import Vector
p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ARC_Door_Leaf.fbx')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=p)
o=next(o for o in bpy.context.selected_objects if o.type=='MESH')
coords=[o.matrix_world @ v.co for v in o.data.vertices]
lo=min(v.x for v in coords);hi=max(v.x for v in coords)
print('Leaf FBX origin',tuple(round(x,4) for x in o.matrix_world.translation),'hinge-relative x extents',round(lo,4),round(hi,4))
assert o.matrix_world.translation.length<1e-5 and -.02<lo<.02 and .87<hi<.92
print('Hinge origin validation passed')
