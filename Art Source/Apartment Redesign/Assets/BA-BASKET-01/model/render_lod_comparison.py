import bpy
from pathlib import Path
D=Path(__file__).resolve().parent.parent; P=D/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for x,name in [(-.5,'basket-perspective.png'),(.5,'basket-lod1-perspective.png')]:
 bpy.ops.mesh.primitive_plane_add(size=1,location=(x,0,0));o=bpy.context.object
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');transparent=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(P/name));links=m.node_tree.links;links.new(tex.outputs['Color'],em.inputs['Color']);links.new(tex.outputs['Alpha'],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(em.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface']);o.data.materials.append(m)
bpy.ops.object.camera_add(location=(0,0,3));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=8;sc.render.film_transparent=True;sc.render.resolution_x=2200;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'basket-lod-comparison.png');bpy.ops.render.render(write_still=True)
