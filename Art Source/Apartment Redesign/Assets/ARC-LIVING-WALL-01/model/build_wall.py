"""Build two modular wall pieces and window casing in metres, Z up.
Run Blender --background --python <this file>. Front is -Y; origin at floor centre.
"""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'model'); TEX=os.path.join(ROOT,'textures'); PRE=os.path.join(ROOT,'previews')
for p in (OUT,PRE): os.makedirs(p,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

def material(name,file,rough=.9):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
 img=n.new('ShaderNodeTexImage');img.image=bpy.data.images.load(os.path.join(TEX,file),check_existing=True);m.node_tree.links.new(img.outputs['Color'],p.inputs['Base Color']);return m
plaster=material('Plaster_Painterly','plaster-candidate-d.png')
# Place a continuous X/Z projection in world space. Mirror repeats meet in value
# at each tile edge, and adjacent separate modules share the same coordinates.
nodes=plaster.node_tree.nodes; links=plaster.node_tree.links
tex=next(n for n in nodes if n.bl_idname=='ShaderNodeTexImage'); tex.extension='MIRROR'
geo=nodes.new('ShaderNodeNewGeometry'); xyz=nodes.new('ShaderNodeSeparateXYZ'); uv=nodes.new('ShaderNodeCombineXYZ'); scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/3.2
links.new(geo.outputs['Position'],xyz.inputs[0]);links.new(xyz.outputs['X'],uv.inputs['X']);links.new(xyz.outputs['Z'],uv.inputs['Y']);links.new(uv.outputs[0],scale.inputs[0]);links.new(scale.outputs[0],tex.inputs['Vector'])
trim=material('Trim_Ivory','trim-candidate-a.png')
glass=bpy.data.materials.new('Window_Glass');glass.diffuse_color=(.29,.38,.38,1);glass.use_nodes=True;gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Base Color'].default_value=(.92,.96,.97,1);gp.inputs['Roughness'].default_value=.08;gp.inputs['Transmission Weight'].default_value=1.0;gp.inputs['IOR'].default_value=1.45

def box(name,loc,size,mat,group,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft edge','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);o['export_group']=group
 # World-projected UVs avoid stretching across disparate trim geometries.
 uv=o.data.uv_layers.active
 if not uv: uv=o.data.uv_layers.new(name='UVMap')
 for poly in o.data.polygons:
  n=poly.normal
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co+o.location
   if abs(n.y)>=max(abs(n.x),abs(n.z)): u,w=v.x,v.z
   elif abs(n.x)>=abs(n.z): u,w=v.y,v.z
   else: u,w=v.x,v.y
   # A single image covers 3.2 m horizontally/vertically; all adjoining pieces align.
   uv.data[li].uv=((u+1.6)/3.2,w/3.2)
 return o

def trim_run(width,group):
 # Subtle original base and crown, non-overlapping volumes.
 box('Baseboard',(0,-.082,.095),(width,.044,.19),trim,group,.004)
 box('Base cap',(0,-.09,.202),(width,.055,.025),trim,group,.003)
 box('Crown fascia',(0,-.079,2.695),(width,.038,.11),trim,group,.004)
 box('Crown lower',(0,-.092,2.638),(width,.065,.024),trim,group,.003)
 box('Crown top',(0,-.094,2.742),(width,.070,.016),trim,group,.002)
# Solids: avoid overlap between the opening's jamb pieces and its lintel/sill.
box('Solid wall core',(0,0,1.375),(2,.12,2.75),plaster,'solid');trim_run(2,'solid')
for x in (-1.,1.):box('Window wall pier',(x,0,1.375),(.4,.12,2.75),plaster,'windowwall')
box('Under sill',(0,0,.45),(1.6,.12,.9),plaster,'windowwall')
box('Window lintel',(0,0,2.525),(1.6,.12,.45),plaster,'windowwall');trim_run(2.4,'windowwall')
# Independent casing, matching 1.60 m opening, sill .90 m, head 2.30 m.
for x in (-.815,.815):box('Casing jamb',(x,-.084,1.5975),(.09,.048,1.355),trim,'casing',.004)
box('Casing head',(0,-.084,2.325),(1.80,.048,.10),trim,'casing',.004)
box('Sill',(0,-.10,.885),(1.86,.12,.07),trim,'casing',.004)
box('Apron',(0,-.084,.835),(1.72,.045,.06),trim,'casing',.003)
# Reusable static sash parts, glass separate to permit correct Unreal window material.
for x in (-.77,.0,.77):box('Sash vertical',(x,-.015,1.6),(.034,.04,1.4),trim,'casing',.003)
for z in (.93,1.61,2.27):
 for x in (-.385,.385): box('Sash rail',(x,-.015,z),(.73,.04,.035),trim,'casing',.003)
for x in (-.385,.385):
 for z in (1.27,1.94): box('Muntin',(x,-.015,z),(.018,.04,.63),trim,'casing',.002)
for x in (-.395,.395):
 for z in (1.26,1.94):box('Glazing',(x,.007,z),(.735,.012,.635),glass,'glazing')
# Export each group with common floor-centred origin, maintaining their material slots.
def export_group(group,filename):
 bpy.ops.object.select_all(action='DESELECT');obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('export_group')==group]
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=group
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,filename+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
 return o
solid=export_group('solid','ARC_Living_SolidWall_2m'); ww=export_group('windowwall','ARC_Living_WindowWall_2p4m');cas=export_group('casing','ARC_Window_Casing_Sash');panes=export_group('glazing','ARC_Window_Glazing')
# Preview: window + adjoining 2 m solid module. They touch at x=1.2 m.
solid.location.x=2.2
# Illustration card is for the Blender preview only; it is not exported.
project=os.path.abspath(os.path.join(ROOT,'../../../..'))
backdrop_path=os.path.join(project,'Art Source','Environment Textures','T_WindowView.png')
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,.12,1.6),rotation=(math.pi/2,0,0)); bg=bpy.context.object;bg.name='PreviewOnly_ExteriorCard';bg.scale=(.79,.69,1)
bmat=bpy.data.materials.new('PreviewOnly_ExteriorImage');bmat.use_nodes=True;bn=bmat.node_tree.nodes;bl=bmat.node_tree.links;bp=bn.get('Principled BSDF');im=bn.new('ShaderNodeTexImage');im.image=bpy.data.images.load(backdrop_path,check_existing=True);bl.new(im.outputs['Color'],bp.inputs['Base Color']);bl.new(im.outputs['Color'],bp.inputs['Emission Color']);bp.inputs['Emission Strength'].default_value=.65;bg.data.materials.append(bmat)
world=bpy.context.scene.world;world.color=(.28,.23,.19)
bpy.ops.object.light_add(type='AREA',location=(0,-4,4));light=bpy.context.object;light.data.energy=500;light.data.shape='DISK';light.data.size=5;light.rotation_euler=(Vector((0,0,1.35))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.3,-6.5,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((1.1,0,1.38))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.2
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.render.filepath=os.path.join(PRE,'adjacent-modules-d.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'ARC-LIVING-WALL-01.blend'));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'ARC-LIVING-WALL-01.blend'));bpy.ops.render.render(write_still=True)
