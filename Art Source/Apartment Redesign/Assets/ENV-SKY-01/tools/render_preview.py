import bpy
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=8
scene.render.resolution_x=800; scene.render.resolution_y=500; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
world=bpy.data.worlds.new('SkyPreview'); world.use_nodes=True; scene.world=world
nodes=world.node_tree.nodes; nodes.clear(); env=nodes.new('ShaderNodeTexEnvironment'); env.image=bpy.data.images.load(str(base/'textures/ENV-SKY-01_painterly_2k_LDR-derived.hdr')); env.projection='EQUIRECTANGULAR'
bg=nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value=1
out=nodes.new('ShaderNodeOutputWorld'); world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color']); world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface'])
cam=bpy.data.cameras.new('PreviewCamera'); ob=bpy.data.objects.new('PreviewCamera',cam); scene.collection.objects.link(ob); scene.camera=ob; cam.lens_unit='FOV'; cam.angle=1.309
for name,d in [('sun_side',(1,0,.1)),('sun_disc',(.788,0,.616)),('seam_side',(-1,0,.1)),('side_a',(0,1,.1)),('side_b',(0,-1,.1)),('zenith',(0,.001,1))]:
 ob.rotation_euler=Vector(d).to_track_quat('-Z','Y').to_euler(); scene.render.filepath=str(base/'previews'/f'{name}.png'); bpy.ops.render.render(write_still=True)
