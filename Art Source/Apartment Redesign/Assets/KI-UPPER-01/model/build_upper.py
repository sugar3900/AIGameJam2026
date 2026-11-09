import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def image_mat(name, files, mix_factor=None, color=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8
 a=m.node_tree.nodes.new('ShaderNodeTexImage');a.image=bpy.data.images.load(os.path.join(ROOT,'textures',files[0]),check_existing=True)
 out=a.outputs['Color']
 if len(files)>1:
  b=m.node_tree.nodes.new('ShaderNodeTexImage');b.image=bpy.data.images.load(os.path.join(ROOT,'textures',files[1]),check_existing=True)
  mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.inputs[0].default_value=mix_factor; m.node_tree.links.new(out,mix.inputs[1]);m.node_tree.links.new(b.outputs['Color'],mix.inputs[2]);out=mix.outputs['Color']
 if color:
  mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.48;mix.inputs[2].default_value=(*color,1);m.node_tree.links.new(out,mix.inputs[1]);out=mix.outputs['Color']
 m.node_tree.links.new(out,p.inputs['Base Color']);return m
def solid(name,color,metal=0,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
paint=image_mat('Sage paint matching pantry',['sage-B.png','sage-A.png'],.28);wood=image_mat('Aged interior wood',['interior-wood.png'],color=(.36,.26,.18)); brass=solid('Aged brass',(.35,.24,.08),.65,.48); ivory=solid('Ivory knobs',(.8,.73,.57),0,.38); rub=solid('Exposed worn edges',(.37,.24,.12),0,.85)
groups={'Body':[],'LeftDoor':[],'RightDoor':[]}
def box(name,loc,dim,mat,g,bevel=.0025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('rounded edges','BEVEL');b.width=bevel;b.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 o.data.materials.append(mat);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');groups[g].append(o)
def knob(name,loc,mat,g):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=.013,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat);bpy.ops.object.shade_smooth();groups[g].append(o)
# Front is -Y. Body is bottom centered; 1.00m including crown, 0.32m deep, 0.55m high.
for x in (-.463,.463):box('side',(x,.005,.263),(.034,.285,.49),paint,'Body')
box('back',(0,.139,.263),(.895,.018,.49),wood,'Body')
for z in (.026,.266,.500):box('shelf',(0,.002,z),(.90,.27,.022),wood,'Body')
box('lower rail',(0,-.146,.022),(.94,.018,.035),paint,'Body')
box('crown lower',(0,0,.514),(.96,.30,.024),paint,'Body')
box('crown cap',(0,0,.537),(1.0,.32,.026),paint,'Body')
box('crown bead',(0,-.159,.522),(.982,.009,.008),paint,'Body',.001)
box('lower bead',(0,-.158,.023),(.936,.008,.009),paint,'Body',.001)
# Framed inset on both exposed side panels, like the companion pantry.
for side in (-1,1):
 x=side*.482
 for y in (-.11,.11):box('side inset vertical',(x,y,.268),(.008,.008,.35),paint,'Body',.001)
 for z in (.093,.443):box('side inset horizontal',(x,0,z),(.008,.228,.008),paint,'Body',.001)
# Small individually modeled edge rubs stay localized and non-repeating.
for x,z,w in [(-.45,.545,.025),(-.29,.545,.014),(.22,.545,.023),(.42,.545,.017),(-.37,.022,.015),(.32,.022,.018)]:
 box('worn crown or apron',(x,-.162,z),(w,.002,.0025),rub,'Body',.0003)
for name,center,side in [('LeftDoor',-.235,-1),('RightDoor',.235,1)]:
 box('solid door',(center,-.150,.265),(.462,.027,.47),paint,name)
 for dx in (-.212,.212):box('door stile',(center+dx,-.167,.265),(.035,.015,.468),paint,name,.0015)
 for z in (.047,.483):box('door rail',(center,-.167,z),(.40,.015,.035),paint,name,.0015)
 for dx in (-.168,.168):box('inset trim',(center+dx,-.178,.265),(.009,.012,.365),paint,name,.001)
 for z in (.083,.447):box('inset trim',(center,-.178,z),(.344,.012,.009),paint,name,.001)
 knob('ivory handle',(center-side*.145,-.193,.26),ivory,name)
 for z in (.13,.40):box('brass hinge',(center+side*.232,-.17,z),(.016,.012,.04),brass,name,.001)
 for dx,z,h in [(-.21,.10,.014),(.21,.44,.016),(-.21,.35,.012),(.21,.13,.018),(-.21,.46,.012)]:box('worn edge',(center+dx,-.177,z),(.0025,.0015,h),rub,name,.0004)
 for dx,z,w in [(-.14,.048,.018),(.11,.048,.013),(-.10,.483,.016),(.13,.483,.012)]:box('worn rail',(center+dx,-.178,z),(w,.0015,.0025),rub,name,.0004)
pivots={'Body':(0,0,0),'LeftDoor':(-.47,-.165,.265),'RightDoor':(.47,-.165,.265)};objs={}
for g,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_Upper_'+g;objs[g]=o
 bpy.context.scene.cursor.location=pivots[g];bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
s=bpy.context.scene;bpy.ops.object.camera_add(location=(1.7,-2.6,1.35));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.27))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.55;s.camera=cam
for pos,power,size in [((2,-3,3),230,3),((-2,-1,2),110,2),((0,2,2),120,2)]:
 bpy.ops.object.light_add(type='AREA',location=pos);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.rotation_euler=(Vector((0,0,.3))-a.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG'
s.render.filepath=os.path.join(ROOT,'previews','upper-closed.png');bpy.ops.render.render(write_still=True)
objs['LeftDoor'].rotation_euler.z=math.radians(-100);objs['RightDoor'].rotation_euler.z=math.radians(100)
cam.data.ortho_scale=2.05
s.render.filepath=os.path.join(ROOT,'previews','upper-open.png');bpy.ops.render.render(write_still=True)
objs['LeftDoor'].rotation_euler.z=0;objs['RightDoor'].rotation_euler.z=0
cam.data.ortho_scale=1.55
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','KI-UPPER-01.blend'))
