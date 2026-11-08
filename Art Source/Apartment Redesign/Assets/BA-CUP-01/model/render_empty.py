import bpy
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(root/'model/BA-CUP-01.blend'))
for name in ['BA_Brush_Ivory','BA_Brush_Sage']:bpy.data.objects[name].hide_render=True
cam=bpy.context.scene.camera;cam.location=(.23,-.32,.43);cam.rotation_euler=(Vector((0,0,.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.18
bpy.context.scene.render.filepath=str(root/'previews/cup-empty.png');bpy.ops.render.render(write_still=True)
