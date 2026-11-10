from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model/LV-SOFA-02.blend'))
sc=bpy.context.scene;sc.cycles.samples=28;sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
# Hide room context for turnarounds so the back view is not behind the wall.
for o in bpy.data.collections['PREVIEW_ONLY'].objects:o.hide_render=True
sc.render.film_transparent=True
views={
'context':((2.7,-4.3,2.15),(0,0,.48),2.65),
'front':((0,-4,1.12),(0,0,.48),2.4),
'back':((0,4,1.30),(0,0,.48),2.4),
'left':((-4,0,.48),(0,0,.48),1.4),
'right':((4,0,.48),(0,0,.48),1.4),
'cushion-detail':((-1.45,-2.0,1.34),(-.42,-.04,.63),.95),
'arm-throw-detail':((2.0,-1.8,1.55),(.80,-.03,.56),1.12)}
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(views)
for name in names:
 for o in bpy.data.collections['PREVIEW_ONLY'].objects:o.hide_render=(name!='context')
 sc.render.film_transparent=(name!='context')
 loc,target,scale=views[name];cam=sc.camera;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
 sc.render.filepath=str(ROOT/'previews'/('sofa-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('Requested sofa views complete.')
