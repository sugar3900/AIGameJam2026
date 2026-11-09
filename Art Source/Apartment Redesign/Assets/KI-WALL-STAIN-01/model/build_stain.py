import bpy, math
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parents[1]; ROOT=A.parents[3]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials: bpy.data.materials.remove(m)
# Movable surface: origin at decal centre, front -Y, +Z up.
mesh=bpy.data.meshes.new('StainSurface'); mesh.from_pydata([(-.35,0,-.235),(.35,0,-.235),(.35,0,.235),(-.35,0,.235)],[],[(0,1,2,3)]);mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 for li,xy in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=xy
obj=bpy.data.objects.new('KI_Wall_Stain',mesh);bpy.context.collection.objects.link(obj)
mat=bpy.data.materials.new('M_Stain_Alpha');mat.use_nodes=True
nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
out=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent');paint=nodes.new('ShaderNodeBsdfPrincipled');paint.inputs['Roughness'].default_value=.9
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(A/'textures/stain-candidate-b.png'));tex.image.pack()
tint=nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1.;tint.inputs[2].default_value=(.58,.46,.31,1);alpha=nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';alpha.inputs[1].default_value=1.25;alpha.use_clamp=True;links.new(tex.outputs['Color'],tint.inputs[1]);links.new(tint.outputs[0],paint.inputs['Base Color']);cut=nodes.new('ShaderNodeMath');cut.operation='SUBTRACT';cut.inputs[1].default_value=.008;cut.use_clamp=True;links.new(tex.outputs['Alpha'],cut.inputs[0]);links.new(cut.outputs[0],alpha.inputs[0]);links.new(alpha.outputs[0],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(paint.outputs['BSDF'],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
mat.surface_render_method='DITHERED';obj.data.materials.append(mat)
# Export local-centred geometry only, prior to any placement/preview geometry.
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(A/'model/KI_Wall_Stain.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
# Preview only: wall, integrated sink body, lights; omitted from export.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.385,1.18));wall=bpy.context.object;wall.name='PreviewWall';wall.dimensions=(2.8,.12,2.36);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
wallmat=bpy.data.materials.new('Preview warm plaster');wallmat.use_nodes=True;wallmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.56,.47,.36,1);wallmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9;wall.data.materials.append(wallmat)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Art Source/Apartment Redesign/Assets/KI-SINK-NARROW-01/models/KI_SINK_NARROW_body.fbx'))
for im in bpy.data.images:
 if im.source=='FILE' and im.name!='stain-candidate-b.png':
  match=ROOT/'Art Source/Apartment Redesign/Assets/KI-SINK-NARROW-01/textures'/Path(im.filepath).name
  if match.exists(): im.filepath=str(match);im.reload()
obj.location=(.48,.323,1.63)
# camera toward wall with some angle, but stain isolated from aperture plans.
bpy.ops.object.camera_add(location=(2.5,-4.6,2.4));cam=bpy.context.object;cam.rotation_euler=(Vector((.15,.30,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.35;bpy.context.scene.camera=cam
for loc,power,size in [((-.5,-3.3,3.9),700,4),((2,-2,2.8),250,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,.3,1.2))-l.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.19,.19,.19);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(A/'previews/stain-before.png');bpy.ops.render.render(write_still=True)
obj.hide_render=True;scene.render.filepath=str(A/'previews/stain-after.png');bpy.ops.render.render(write_still=True);obj.hide_render=False
# Save reusable source with context, preserving object pose; FBX stays local-centred.
bpy.ops.wm.save_as_mainfile(filepath=str(A/'model/KI-WALL-STAIN-01.blend'))
