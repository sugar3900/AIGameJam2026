"""BA-SWITCH-01: metres, +Z up, mounting wall at Y=0, front faces -Y."""
import bpy, math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name, col, tex=None, metallic=0, rough=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=rough
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(root/'textures'/tex),check_existing=True);m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
ivory=material('IvoryCeramic',(.87,.81,.71),'ivory-ceramic.png',0,.58)
enamel=ivory.node_tree.nodes.new('ShaderNodeTexImage');enamel.image=bpy.data.images.load(str(root/'textures'/'enamel-brush.png'),check_existing=True)
nt=ivory.node_tree; base=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n != enamel); mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.32;nt.links.new(base.outputs['Color'],mix.inputs[1]);nt.links.new(enamel.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
brass=material('AgedBrass',(.38,.27,.12),'aged-brass.png',.6,.54)
dark=material('ScrewSlot',(.10,.075,.045),None,.35,.72)
plate=[];lever=[]
def add(o,name,mat,group):
 o.name=name;o.data.materials.append(mat);group.append(o);return o
def box(name,loc,size,mat,group,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return add(o,name,mat,group)
def cylinder(name,loc,r,depth,mat,group,axis='Y'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc);o=bpy.context.object
 if axis=='Y':o.rotation_euler.x=math.pi/2
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Round edge','BEVEL');mod.width=min(.0008,depth*.15);mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
 return add(o,name,mat,group)
box('CeramicPlate',(0,-.005,0),(.1,.010,.12),ivory,plate,.004)
# Back mounting block; wall recess may need a cutout or omission in the level.
box('RearSwitchHousing',(0,.002,0),(.035,.009,.05),dark,plate,.002)
cylinder('ToggleCollar',(0,-.012,0),.014,.004,brass,plate)
cylinder('ToggleCollarInset',(0,-.0142,0),.010,.0015,dark,plate)
for z in (-.045,.045):
 cylinder('ScrewHead',(0,-.011,z),.004,.0025,brass,plate)
 box('ScrewSlot',(0,-.0125,z),(.0044,.0007,.00055),dark,plate,.0001)
# Toggle assembly: exported at neutral centre; rotation about local X through pivot.
cylinder('ToggleRoot',(0,-.0165,0),.0065,.006,brass,lever)
box('IvoryToggle',(0,-.0295,0),(.009,.027,.009),ivory,lever,.0024)
def join_group(objs,name,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
p=join_group(plate,'BA_Switch_Plate',(0,0,0));t=join_group([lever[1],lever[0]],'BA_Switch_Toggle',(0,-.014,0))
for o in (p,t):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Preview wall and camera; never exported.
wall=material('PreviewWall',(.62,.48,.46),None,0,.9)
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,.008,0),rotation=(math.pi/2,0,0));bpy.context.object.name='PreviewWall';bpy.context.object.data.materials.append(wall)
bpy.ops.object.camera_add(location=(.12,-.40,.04));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.01,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.20;bpy.context.scene.camera=cam
for pos,power,size in [((.1,-.4,.4),6,.45),((-.35,-.25,.1),4,.4)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.image_settings.file_format='PNG';sc.world.color=(.12,.12,.12);sc.view_settings.view_transform='AgX'
for state,angle in [('off',28),('on',-28)]:
 t.rotation_euler.x=math.radians(angle);sc.render.filepath=str(root/'previews'/('switch-'+state+'.png'));bpy.ops.render.render(write_still=True)
t.rotation_euler.x=0
for img in bpy.data.images:
 if img.source=='FILE' and Path(img.filepath).name in ('ivory-ceramic.png','aged-brass.png','enamel-brush.png'):img.filepath='//../textures/'+Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'BA-SWITCH-01.blend'))
