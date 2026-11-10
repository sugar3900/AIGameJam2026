"""Paired source-material renders, preserving the original glaze colour graph and tile UVs."""
from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'BA-TILE-01/model/BA-TILE-01.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100
for o in list(s.objects):
 if o.type=='LIGHT':
  bpy.data.objects.remove(o,do_unlink=True);continue
 if any(t in o.name for t in ('Crack branch','chip','exposed tile','shard','fragment')):o.hide_render=True
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   p=R.parent/'BA-TILE-01/textures'/Path(n.image.filepath).name
   if p.exists():n.image=bpy.data.images.load(str(p),check_existing=True)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,power,size in [((-.10,-1.0,.356),35,.35),((1.5,-2,.7),15,1.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.size=size;l.rotation_euler=(Vector((.5,0,.6))-l.location).to_track_quat('-Z','Y').to_euler()
cam=s.camera;cam.location=(1.25,-1.25,.95);cam.rotation_euler=(Vector((.5,0,.62))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.72
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.render.filepath=str(R/'previews/glaze-before.png');bpy.ops.render.render(write_still=True)
norm=bpy.data.images.load(str(R/'textures/T_BathGlaze_NormalDX.png'));norm.colorspace_settings.name='Non-Color'
rough=bpy.data.images.load(str(R/'textures/T_BathGlaze_Roughness.png'));rough.colorspace_settings.name='Non-Color'
for m in bpy.data.materials:
 if not m.name.startswith('Pink glaze'):continue
 n=m.node_tree.nodes;lk=m.node_tree.links;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage');t.image=norm;t.extension='REPEAT'
 # Convert DirectX green to Blender/OpenGL green for this preview only.
 sep=n.new('ShaderNodeSeparateXYZ');lk.new(t.outputs['Color'],sep.inputs[0]);neg=n.new('ShaderNodeMath');neg.operation='SUBTRACT';neg.inputs[0].default_value=1;lk.new(sep.outputs['Y'],neg.inputs[1]);comb=n.new('ShaderNodeCombineXYZ');lk.new(sep.outputs['X'],comb.inputs['X']);lk.new(neg.outputs[0],comb.inputs['Y']);lk.new(sep.outputs['Z'],comb.inputs['Z'])
 nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=1;lk.new(comb.outputs[0],nm.inputs['Color']);lk.new(nm.outputs[0],p.inputs['Normal']);t=n.new('ShaderNodeTexImage');t.image=rough;lk.new(t.outputs['Color'],p.inputs['Roughness'])
s.render.filepath=str(R/'previews/glaze-after.png');bpy.ops.render.render(write_still=True)
print('GLAZE PREVIEW COMPLETE')
