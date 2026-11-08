"""Optional hand-painted 4x3 m unique wear overlay; base remains a repeating module."""
import bpy
from pathlib import Path
P=Path(__file__).resolve().parent.parent;M=P/'model';O=P/'previews';T=P/'textures'
bpy.ops.wm.open_mainfile(filepath=str(M/'KI-TILE-01.blend'))
mat=bpy.data.materials.new('KI_WEAR_translucent_warm_umber');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;nodes.clear()
out=nodes.new('ShaderNodeOutputMaterial'); mix=nodes.new('ShaderNodeMixShader'); clear=nodes.new('ShaderNodeBsdfTransparent'); diffuse=nodes.new('ShaderNodeBsdfDiffuse')
diffuse.inputs['Color'].default_value=(.24,.14,.085,1)
image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(T/'wear-overlay.png'));image.image.pack()
math=nodes.new('ShaderNodeMath');math.operation='MULTIPLY';math.inputs[1].default_value=.38
links.new(image.outputs['Alpha'],math.inputs[0]);links.new(math.outputs[0],mix.inputs[0]);links.new(clear.outputs[0],mix.inputs[1]);links.new(diffuse.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(-.5,0,.0011));obj=bpy.context.object;obj.name='KI_TILE_WEAR_4x3';obj.dimensions=(4,3,0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(M/'KI_TILE_WEAR_4x3.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
scene=bpy.context.scene;scene.render.filepath=str(O/'checker-worn.png');bpy.ops.render.render(write_still=True)
scene.camera.data.ortho_scale=2.3;scene.render.filepath=str(O/'checker-worn-detail.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'KI-TILE-01-wear-preview.blend'))
print('Alpha range',min(image.image.pixels[3::4]),max(image.image.pixels[3::4]))
