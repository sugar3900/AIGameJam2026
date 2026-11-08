"""Build a 6 x .8m flat woven runner; run with Blender --background --python."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name, color, rough=.95):
 m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=rough;return m

def image_mat(name,path):
 m=material(name,(1,1,1,1));n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);return m

rug=image_mat('Runner_Painterly',ROOT/'textures/runner-albedo.png')
edge=material('Runner_RoseBinding',(.28,.12,.10,1))
back=material('Runner_WovenBacking',(.32,.25,.17,1))
nx,ny=90,12;v=[];f=[]
for j in range(ny+1):
 for i in range(nx+1):
  x=-2.994+5.988*i/nx;y=-.394+.788*j/ny
  z=.013+.0007*math.sin(i*.43)*math.sin(j*.9)
  v.append((x,y,z))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;f.append((a,a+1,a+nx+2,a+nx+1))
mesh=bpy.data.meshes.new('runner textile top');mesh.from_pydata(v,[],f);mesh.update();obj=bpy.data.objects.new('Runner textile top',mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(rug)
uv=mesh.uv_layers.new(name='RunnerUV')
for p in mesh.polygons:
 for li in p.loop_indices:
  x,y,_=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((x+2.994)/5.988,(y+.394)/.788)

def box(name,loc,dims,mat, bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft edge','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);return o
box('Reverse textile backing',(0,0,.005),(5.988,.788,.01),back,.001)
for y in (-.397,.397):box('Lengthwise bound edge',(0,y,.008),(6,.006,.014),edge,.001)
for x in (-2.997,2.997):box('End binding',(x,0,.008),(.006,.788,.014),edge,.001)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();obj=bpy.context.object;obj.name='HA_RUNNER_01';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/HA_RUNNER_01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/HA-RUNNER-01.blend'))
# Preview uses wood-color proxy, not the exported art asset.
floor=image_mat('PREVIEW wood approximation',ROOT.parent/'ARC-FLOOR-WOOD-01/textures/wood-candidate-c.png')
floor.node_tree.nodes['Image Texture'].extension='REPEAT'
box('PREVIEW floor', (0,0,-.025),(7,2.3,.05),floor)
bpy.ops.object.light_add(type='AREA',location=(-1,-1,5));bpy.context.object.data.energy=1100;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
bpy.ops.object.camera_add(location=(3,-4.5,5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.6;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.render.filepath=str(ROOT/'previews/runner-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,7);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7;s.render.filepath=str(ROOT/'previews/runner-top.png');bpy.ops.render.render(write_still=True)
