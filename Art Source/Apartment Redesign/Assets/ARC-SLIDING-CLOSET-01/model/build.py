import bpy, math, os
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.78,img=None):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if img:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(os.path.join(R,'textures',img),check_existing=True);mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.35;mix.inputs[2].default_value=(.85,.79,.68,1);m.node_tree.links.new(t.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
 return m
paint=mat('Ivory painted wood',(.76,.69,.58),img='ivory-paint-reused.png');brass=mat('Aged brass',(.31,.205,.075),.62,.5);dark=mat('Recessed pull shadow',(.075,.052,.035),.18,.72);track=mat('Aged track',(.25,.22,.18),.45,.58)
groups={'Frame':[],'LeftPanel':[],'RightPanel':[]}
def box(n,loc,dim,material,g,bev=.002):
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  mod=o.modifiers.new('Eased edges','BEVEL');mod.width=bev;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(material);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT');groups[g].append(o)
# 0.90m clear jamb opening, two offset tracks, solid casing, floor origin.
for x in (-.485,.485):
 box('Jamb',(x,0,1.075),(.07,.14,2.15),paint,'Frame')
 for y in (-.078,.078):box('Vertical casing',(x,y,1.075),(.083,.018,2.15),paint,'Frame')
box('Head jamb',(0,0,2.175),(1.04,.14,.05),paint,'Frame')
for y in (-.078,.078):box('Head casing',(0,y,2.20),(1.06,.025,.075),paint,'Frame')
box('Head cap',(0,-.079,2.245),(1.08,.04,.025),paint,'Frame')
for y in (-.028,.028):
 box('Top guide track',(0,y,2.126),(.9,.026,.012),track,'Frame',.001)
 box('Bottom guide track',(0,y,.014),(.9,.026,.012),track,'Frame',.001)
# Left front and right back slabs overlap at center by 2cm; y spacing .056 keeps trim clear.
for group,x,y in [('LeftPanel',-.22,-.028),('RightPanel',.22,.028)]:
 box('Door slab',(x,y,1.0725),(.46,.024,2.105),paint,group)
 for s in (-1,1):
  face=y+s*.013
  for z in (.55,1.57):
   for dx in (-.152,.152):box('Field bead',(x+dx,face+s*.003,z),(.012,.006,.86),paint,group,.001)
   for dz in (-.43,.43):box('Field bead',(x,face+s*.003,z+dz),(.314,.006,.012),paint,group,.001)
  hx=x+(.13 if group=='LeftPanel' else -.13)
  box('Recessed pull bezel',(hx,face+s*.005,1.02),(.033,.006,.095),brass,group,.002)
  box('Pull inset shadow',(hx,face+s*.009,1.02),(.019,.002,.069),dark,group,.0003)
  box('Pull lower lip',(hx,face+s*.011,.992),(.022,.003,.006),brass,group,.0005)
objs={}
for group,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='ARC_Sliding_'+group;objs[group]=o
 origin={'Frame':(0,0,0),'LeftPanel':(-.22,-.028,0),'RightPanel':(.22,.028,0)}[group];bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 orig=o.location.copy();o.location=(0,0,0);bpy.ops.export_scene.fbx(filepath=os.path.join(R,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO');o.location=orig
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(3.1,-5,2.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.9;sc.camera=cam
for loc,power,size in [((2,-4,5),350,4),((-3,-1,3.5),180,3),((0,3,4),220,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.rotation_euler=(Vector((0,0,1.1))-a.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.render.resolution_x=900;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
def render(n):sc.render.filepath=os.path.join(R,'previews',n+'.png');bpy.ops.render.render(write_still=True)
render('closed-perspective');objs['LeftPanel'].location.x+=.44;render('open-perspective');objs['LeftPanel'].location.x-=.44
cam.location=(0,-6,1.1);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();render('closed-front');objs['LeftPanel'].location.x+=.44;render('open-front');objs['LeftPanel'].location.x-=.44
cam.location=(0,6,1.1);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();render('closed-back');objs['LeftPanel'].location.x+=.44;render('open-back');objs['LeftPanel'].location.x-=.44
for img in bpy.data.images:
 if img.source=='FILE':img.pack()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'model','ARC-SLIDING-CLOSET-01.blend'))
