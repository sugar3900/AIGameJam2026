import bpy, os
from mathutils import Vector
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
expected={'body':(0,0,0),'damage':(0,0,0),'L_tap':(-.25,.21,1.075),'R_tap':(.25,.21,1.075)}
for name,loc in expected.items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(root,'KI_SINK_NARROW_'+name+'.fbx'))
 objects=[o for o in bpy.context.selected_objects if o.type=='MESH']
 assert len(objects)==1,(name,len(objects))
 actual=objects[0].matrix_world.translation
 err=(actual-Vector(loc)).length
 print(name,'origin',tuple(round(x,5) for x in actual),'error',err)
 assert err < 1e-4,(name,actual,loc)
