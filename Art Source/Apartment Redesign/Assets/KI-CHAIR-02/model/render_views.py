from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model/KI-CHAIR-02.blend'))
s=bpy.context.scene;s.cycles.samples=32;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;c=s.camera
views={
 'context':((1.5,-2.3,1.35),(0,0,.46),1.20),
 'front':((0,-3,.46),(0,0,.46),1.04),
 'back':((0,3,.46),(0,0,.46),1.04),
 'right':((3,0,.46),(0,0,.46),1.04),
 'left':((-3,0,.46),(0,0,.46),1.04),
 'seated-eye':((.28,-.55,1.05),(0,.22,.74),.63),
 'slat-detail':((.8,-1.2,1.05),(0,.23,.75),.56),
 'rear-detail':((-.6,1.2,1.04),(0,.23,.75),.56),
}
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(views)
for name in selected:
 loc,at,scale=views[name];c.location=loc;c.rotation_euler=(Vector(at)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'previews'/('chair-'+name+'.png'));bpy.ops.render.render(write_still=True)
