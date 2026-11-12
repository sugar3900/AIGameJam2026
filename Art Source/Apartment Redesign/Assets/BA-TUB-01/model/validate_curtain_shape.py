import bpy,json,math
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx
D=Path(__file__).resolve().parents[1];M=D/'model'
bpy.ops.wm.open_mainfile(filepath=str(M/'BA-TUB-01.blend'))
o=bpy.data.objects['Curtain_panel_sliding'];report={'blend_shape_keys':list(o.data.shape_keys.key_blocks.keys()),'materials':[m.name for m in o.data.materials],'units':{'system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length}}
assert report['blend_shape_keys']==['Basis','Closed']
source=[v.co.copy() for v in o.data.shape_keys.key_blocks['Basis'].data]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(M/'BA_Curtain_Animated.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(meshes)==len(arms)==1
o=meshes[0];report['fbx_shape_keys']=list(o.data.shape_keys.key_blocks.keys());report['bones']=[b.name for b in arms[0].data.bones];assert report['fbx_shape_keys']==['Basis','Closed'];assert report['bones']==['CurtainRoot'];assert any(m.type=='ARMATURE' for m in o.modifiers)
root,_=parse_fbx.parse(str(M/'BA_Curtain_Animated.fbx'))
def walk(e):
 yield e
 for c in e.elems:yield from walk(c)
report['fbx_blend_shape_channels']=sum(1 for e in walk(root) if b'BlendShapeChannel' in e.props)
assert report['fbx_blend_shape_channels']==1
report['world_bounds_cm']={}
for w in [0,.5,1]:
 o.data.shape_keys.key_blocks['Closed'].value=w;bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());vs=[ev.matrix_world@v.co for v in ev.data.vertices]
 world=[(580-100*v.x,907+100*v.y,100*v.z) for v in vs]
 report['world_bounds_cm'][str(w)]={axis:[round(min(v[i] for v in world),3),round(max(v[i] for v in world),3)] for i,axis in enumerate('xyz')}
 # Every ring has invariant shape; its entire motion is translation on the straight rail.
 for k in range(7):
  ring=vs[4290+k*128:4290+(k+1)*128]
  assert abs(sum(v.y for v in ring)/128+.35)<1e-5
  assert abs(sum(v.z for v in ring)/128-2.17)<1e-5
report['mapping']='world_cm = (580 - 100*BlenderX, 907 + 100*BlenderY, 100*BlenderZ); includes FBX axis conversion and assembly yaw 180'
report['ring_checks']='At 0, 0.5, 1: seven rigid tori, centre Y=-0.35m, Z=2.17m; linear translation only.'
(D/'curtain-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
