"""Kitchen plaster kit: Blender metres, +Z up, visible face -Y.
A continuous world-space X/Z projection with mirrored repetition keeps modules continuous.
"""
import bpy, os, math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'model'); TEX=os.path.join(ROOT,'textures'); PRE=os.path.join(ROOT,'previews')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Kitchen_Plaster_Mirrored');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.94
tex=nodes.new('ShaderNodeTexImage');tex.name='Selected_Plaster';tex.image=bpy.data.images.load(os.path.join(TEX,'plaster-candidate-b.png'),check_existing=True);tex.extension='MIRROR';links.new(tex.outputs['Color'],p.inputs['Base Color'])
geo=nodes.new('ShaderNodeNewGeometry');xyz=nodes.new('ShaderNodeSeparateXYZ');combine=nodes.new('ShaderNodeCombineXYZ');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/3.2
links.new(geo.outputs['Position'],xyz.inputs[0]);links.new(xyz.outputs['X'],combine.inputs['X']);links.new(xyz.outputs['Z'],combine.inputs['Y']);links.new(combine.outputs[0],scale.inputs[0]);links.new(scale.outputs[0],tex.inputs['Vector'])
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1.375));wall=bpy.context.object;wall.name='Kitchen_Plaster_Wall_2m';wall.dimensions=(2,.12,2.75);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.data.materials.append(mat)
uv=wall.data.uv_layers.active
for poly in wall.data.polygons:
 for li in poly.loop_indices:
  v=wall.data.vertices[wall.data.loops[li].vertex_index].co
  # End walls use their y extent; front and rear use same 2m horizontal phase.
  if abs(poly.normal.y)>.5: u=(v.x+1)*1.0
  elif abs(poly.normal.x)>.5: u=(v.y+.06)/.12*2
  else: u=(v.x+1)*1.0
  z=(v.z+1.375)/2.75*2
  if abs(poly.normal.z)>.5: z=(v.y+.06)/.12*2
  uv.data[li].uv=(u,z)
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'ARC_Kitchen_Plaster_Wall_2m.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
# Duplicate for a repeat test only; other modules are not exported.
for x in (2,4):
 o=wall.copy();o.data=wall.data.copy();bpy.context.collection.objects.link(o);o.location.x=x;o.name='PreviewRepeat'
world=bpy.context.scene.world;world.color=(.22,.20,.18)
bpy.ops.object.light_add(type='AREA',location=(2,-5,4));light=bpy.context.object;light.data.energy=700;light.data.size=6;light.rotation_euler=(Vector((2,0,1.3))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-8,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((2,0,1.38))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.4
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1400;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'ARC-KITCHEN-PLASTER-01.blend'))
for candidate in ('a','b','c'):
 tex.image=bpy.data.images.load(os.path.join(TEX,'plaster-candidate-'+candidate+'.png'),check_existing=True)
 scene.render.filepath=os.path.join(PRE,'wall-repeat-'+candidate+'.png');bpy.ops.render.render(write_still=True)
tex.image=bpy.data.images.load(os.path.join(TEX,'plaster-candidate-b.png'),check_existing=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'ARC-KITCHEN-PLASTER-01.blend'))
# Optional localized cracks are separate geometry; absent from the clean base.
crack_mat=bpy.data.materials.new('Optional_Hairline_Crack');crack_mat.diffuse_color=(.29,.19,.12,1);crack_mat.use_nodes=True
cp=crack_mat.node_tree.nodes.get('Principled BSDF');cp.inputs['Base Color'].default_value=(.29,.19,.12,1);cp.inputs['Roughness'].default_value=.98
paths=[[(.17,2.31),(.21,2.24),(.19,2.17),(.25,2.10),(.24,2.03),(.28,1.95),(.26,1.89)],[(.20,2.17),(.15,2.13),(.12,2.08)],[(.25,2.10),(.30,2.08),(.33,2.03)]]
cracks=[]
for n,path in enumerate(paths):
 curve=bpy.data.curves.new('Hairline','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.0012;curve.bevel_resolution=1
 spl=curve.splines.new('POLY');spl.points.add(len(path)-1)
 for p,(x,z) in zip(spl.points,path):p.co=(x,-.062,z,1)
 obj=bpy.data.objects.new('Hairline_%d'%n,curve);bpy.context.collection.objects.link(obj);obj.data.materials.append(crack_mat);cracks.append(obj)
bpy.ops.object.select_all(action='DESELECT')
for o in cracks:o.select_set(True)
bpy.context.view_layer.objects.active=cracks[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();damage=bpy.context.object;damage.name='Optional_Local_Hairlines'
# UVs are generated for mesh round-trip even though the material is constant.
if not damage.data.uv_layers.active:damage.data.uv_layers.new(name='UVMap')
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'ARC_Kitchen_Optional_Hairlines.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
scene.render.filepath=os.path.join(PRE,'wall-local-damage.png');bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'ARC-KITCHEN-PLASTER-01.blend'));bpy.ops.render.render(write_still=True)
