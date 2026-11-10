from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model/LV-ARMCHAIR-02.blend'))
sc=bpy.context.scene;sc.cycles.samples=28;sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
views={
'context':((1.8,-2.6,1.5),(0,0,.46),1.38),
'front':((0,-3,.46),(0,0,.46),1.12),
'back':((0,3,.46),(0,0,.46),1.12),
'left':((-3,0,.46),(0,0,.46),1.12),
'right':((3,0,.46),(0,0,.46),1.12),
'lace-detail':((.8,-1.5,1.30),(0,.18,.82),.62),
'seat-detail':((1.1,-1.6,1.12),(0,-.04,.44),.82)}
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(views)
for name in names:
 for o in bpy.data.collections['PREVIEW_ONLY'].objects:o.hide_render=(name!='context')
 sc.render.film_transparent=(name!='context')
 loc,target,scale=views[name];cam=sc.camera;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
 sc.render.filepath=str(ROOT/'previews'/('armchair-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('Requested armchair views complete.')
