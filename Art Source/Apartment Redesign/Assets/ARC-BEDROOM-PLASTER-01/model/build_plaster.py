"""Build a wall finish panel and four-metre wainscot comparison. Blender background."""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL=os.path.join(ROOT,'model');TEX=os.path.join(ROOT,'textures');PRE=os.path.join(ROOT,'previews')
for d in (MODEL,PRE):os.makedirs(d,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def image_mat(name,path):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.92
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(path,check_existing=True);t.extension='MIRROR'
 g=n.new('ShaderNodeNewGeometry');s=n.new('ShaderNodeSeparateXYZ');c=n.new('ShaderNodeCombineXYZ');v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs[3].default_value=1/3.2
 l.new(g.outputs['Position'],s.inputs[0]);l.new(s.outputs['X'],c.inputs['X']);l.new(s.outputs['Z'],c.inputs['Y']);l.new(c.outputs[0],v.inputs[0]);l.new(v.outputs[0],t.inputs['Vector']);l.new(t.outputs['Color'],p.inputs['Base Color']);return m
candidates=[image_mat('Bedroom_Plas A Ivory',os.path.join(TEX,'candidate-a-ivory.png')),image_mat('Bedroom_Plas B Sage',os.path.join(TEX,'candidate-b-sage.png')),image_mat('Bedroom_Plas C Blush',os.path.join(TEX,'candidate-c-blush.png'))]
# Mesh is 2 m along +X, one-sided facing -Y. Floor-left origin; Z starts at wainscot top.
mesh=bpy.data.meshes.new('UpperPlasterMesh');mesh.from_pydata([(0,0,1.1),(2,0,1.1),(2,0,2.75),(0,0,2.75)],[],[(0,1,2,3)]);mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
 for li in p.loop_indices:
  co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.x/3.2,co.z/3.2)
wall=bpy.data.objects.new('Bedroom_UpperPlaster_2m',mesh);bpy.context.collection.objects.link(wall);wall.data.materials.append(candidates[0]);wall.select_set(True);bpy.context.view_layer.objects.active=wall
bpy.ops.export_scene.fbx(filepath=os.path.join(MODEL,'ARC_Bedroom_UpperPlaster_2m.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
wall2=wall.copy();wall2.data=wall.data.copy();bpy.context.collection.objects.link(wall2);wall2.location.x=2
# Existing actual wainscot provides context only. Exports remain independent.
wain=os.path.abspath(os.path.join(ROOT,'../BR-WAINSCOT-01/model/BR_Wainscot_Module.fbx'))
bpy.ops.object.select_all(action='DESELECT');bpy.ops.import_scene.fbx(filepath=wain);panel=list(bpy.context.selected_objects)
paint=bpy.data.materials.new('Preview Wainscot Ivory');paint.use_nodes=True;p=paint.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8
t=paint.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(os.path.abspath(os.path.join(ROOT,'../BR-WAINSCOT-01/textures/candidate-d-brush-ivory.png')),check_existing=True);paint.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
for o in panel:
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(paint)
for i in (1,2,3):
 for o in panel:
  d=o.copy();d.data=o.data.copy() if o.data else None;bpy.context.collection.objects.link(d);d.location.x+=i
# Context floor only; not part of export.
f=bpy.data.materials.new('Preview Honey Floor');f.diffuse_color=(.30,.16,.075,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(2,-.4,-.03));floor=bpy.context.object;floor.dimensions=(4.2,.8,.06);floor.data.materials.append(f)
bpy.ops.object.light_add(type='AREA',location=(.7,-3.5,4.5));light=bpy.context.object;light.data.energy=600;light.data.size=5;light.rotation_euler=(Vector((2,0,1.3))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.6,-6.5,2.9));cam=bpy.context.object;cam.rotation_euler=(Vector((2,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.1
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world.color=(.35,.33,.30);s.view_settings.view_transform='AgX'
for i,key in enumerate(('a','b','c')):
 wall.data.materials[0]=candidates[i];wall2.data.materials[0]=candidates[i];s.render.filepath=os.path.join(PRE,'comparison-'+key+'.png');bpy.ops.render.render(write_still=True)
# Provisional selection B; parent can compare the three equal-light previews.
wall.data.materials[0]=candidates[1];wall2.data.materials[0]=candidates[1]
# Re-export with selected material slot label and restore source selection.
bpy.ops.object.select_all(action='DESELECT');wall.select_set(True);bpy.context.view_layer.objects.active=wall
bpy.ops.export_scene.fbx(filepath=os.path.join(MODEL,'ARC_Bedroom_UpperPlaster_2m.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(MODEL,'ARC-BEDROOM-PLASTER-01.blend'))
