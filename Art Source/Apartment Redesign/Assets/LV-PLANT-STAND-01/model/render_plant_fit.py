"""Preview only: append the separate plant source, do not include it in stand export."""
import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'model'/'LV-PLANT-STAND-01.blend'))
bpy.data.objects['Optional pot riser'].hide_render=False
plant=P.parent/'LV-PLANT-01'/'model'/'LV-PLANT-01.blend'
with bpy.data.libraries.load(str(plant),link=False) as (source,target):
 target.objects=source.objects
for o in target.objects:
 if o and o.type=='MESH':
  bpy.context.scene.collection.objects.link(o);o.location.z+=.516
cam=bpy.context.scene.camera;cam.location=(1.5,-2.3,1.5);cam.rotation_euler=(Vector((0,0,.42))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.04
bpy.context.scene.render.filepath=str(P/'previews'/'stand-with-plant.png');bpy.ops.render.render(write_still=True)
