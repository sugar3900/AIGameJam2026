import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name, color, metal=0, rough=.72, image=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if image:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(os.path.join(ROOT,'textures',image),check_existing=True);m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
paint=mat('Sage painted wood',(.42,.48,.30),image='sage-B.png'); inside=mat('Warm interior timber',(.42,.26,.12),image='interior-wood.png'); brass=mat('Aged brass',(.35,.24,.08),.65,.48); ivory=mat('Ivory ceramic knob',(.80,.73,.57),0,.38); rub=mat('Small wood wear',(.37,.24,.12),0,.85)
# Combine independent light and olive candidates for a restrained warm sage.
p=paint.node_tree.nodes.get('Principled BSDF'); texture=next(n for n in paint.node_tree.nodes if n.type=='TEX_IMAGE'); olive=paint.node_tree.nodes.new('ShaderNodeTexImage');olive.image=bpy.data.images.load(os.path.join(ROOT,'textures','sage-A.png'),check_existing=True)
mix=paint.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.28;paint.node_tree.links.new(texture.outputs['Color'],mix.inputs[1]);paint.node_tree.links.new(olive.outputs['Color'],mix.inputs[2]);paint.node_tree.links.new(mix.outputs['Color'],p.inputs['Base Color'])
# Neutralize the reused orange wood while preserving its brushy texture.
p=inside.node_tree.nodes.get('Principled BSDF');texture=next(n for n in inside.node_tree.nodes if n.type=='TEX_IMAGE');mix=inside.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.48;mix.inputs[2].default_value=(.36,.26,.18,1);inside.node_tree.links.new(texture.outputs['Color'],mix.inputs[1]);inside.node_tree.links.new(mix.outputs['Color'],p.inputs['Base Color'])
groups={'Body':[],'LeftDoor':[],'RightDoor':[]}
def box(name,loc,dim,material,group,bevel=.004):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(material);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');groups[group].append(o);return o
def sphere(name,loc,r,material,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=r,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);bpy.ops.object.shade_smooth();groups[group].append(o)
def cylinder(name,loc,r,depth,material,group):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);groups[group].append(o)
# Front is -Y, width X = 1.00 m, depth Y = 0.67 m; front is 1.00 m plan axis.
for x in (-.455,.455):
 box('side',(x,0,1.005),(.04,.60,1.67),paint,'Body')
 for y in (-.27,.27):box('foot',(x,y,.105),(.07,.07,.21),paint,'Body')
 box('side inset',(x*1.045,0,1.02),(.012,.46,1.35),paint,'Body',.002)
box('back',(0,.282,1.005),(.87,.035,1.67),inside,'Body')
for z in (.19,.54,.89,1.24,1.59,1.83):box('shelf',(0,-.012,z),(.88,.56,.032),inside,'Body',.003)
# Shaped lower apron: concave upper edge in front, with individually modeled foot clearance.
profile=[(-.42,.20),(.42,.20),(.42,.06),(.32,.06),(.29,.095),(.24,.115),(-.24,.115),(-.29,.095),(-.32,.06),(-.42,.06)]
verts=[(x,y,z) for y in (-.304,-.272) for x,z in profile];n=len(profile); faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('scalloped apron');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('scalloped apron',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(paint);groups['Body'].append(o)
bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
box('lower crown',(0,0,1.855),(.96,.62,.05),paint,'Body');box('crown lip',(0,0,1.905),(1.00,.67,.05),paint,'Body');box('top cap',(0,0,1.953),(.99,.655,.046),paint,'Body')
box('crown bead front',(0,-.335,1.908),(.98,.012,.014),paint,'Body',.003)
box('apron rail bead',(0,-.307,.185),(.82,.009,.012),paint,'Body',.002)
for x,z,w in [(-.43,1.91,.034),(-.26,1.91,.019),(.20,1.91,.028),(.43,1.91,.024),(-.39,.186,.024),(.37,.186,.018)]:box('crown and apron worn edge',(x,-.342 if z>1 else -.314,z),(w,.002,.003),rub,'Body',.0005)
# Pair of doors. Each leaf has a genuine inset and two raised panels.
for name,center,side in [('LeftDoor',-.235,-1),('RightDoor',.235,1)]:
 box('door slab',(center,-.31,1.02),(.454,.035,1.65),paint,name)
 for dx in (-.205,.205):box('stile',(center+dx,-.335,1.02),(.044,.035,1.65),paint,name,.003)
 for z in (.22,.99,1.81):box('rail',(center,-.335,z),(.37,.035,.045),paint,name,.003)
 for z,h in ((.61,.68),(1.40,.72)):
  for dx in (-.159,.159):box('panel beading',(center+dx,-.355,z),(.012,.015,h),paint,name,.002)
  for dz in (-h/2,h/2):box('panel beading',(center,-.355,z+dz),(.33,.015,.012),paint,name,.002)
 knobx=center-side*.135
 sphere('ivory knob',(knobx,-.375,1.03),.019,ivory,name)
 # Hinges turn with the leaf for export, and narrow wear marks are deliberately sparse.
 for z in (.42,1.02,1.61):
  x=center+side*.233;box('hinge plate',(x,-.353,z),(.025,.014,.055),brass,name,.002);cylinder('hinge barrel',(x+side*.012,-.36,z),.006,.063,brass,name)
 for dx,z,h in [(-.20,.34,.032),(.20,1.71,.024),(.20,.26,.019),(-.20,1.30,.026),(.20,.90,.014),(-.20,1.76,.019)]:box('rubbed edge',(center+dx,-.356,z),(.003,.002,h),rub,name,.0005)
 for dx,z,w in [(-.12,.20,.022),(.09,.20,.018),(-.13,1.83,.025),(.08,1.83,.016),(.13,1.00,.014)]:box('rubbed rail',(center+dx,-.356,z),(w,.002,.003),rub,name,.0005)
pivots={'Body':(0,0,0),'LeftDoor':(-.472,-.335,1.02),'RightDoor':(.472,-.335,1.02)};objs={}
for group,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_Pantry_'+group;objs[group]=o
 bpy.context.scene.cursor.location=pivots[group];bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(3.3,-5,2.85));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.98))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.65;sc.camera=cam
for loc,power,size in [((2,-4,5),350,4),((-3,-1,3.5),180,3),((0,3,4),210,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.rotation_euler=(Vector((0,0,.9))-a.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
sc.render.filepath=os.path.join(ROOT,'previews','pantry-closed.png');bpy.ops.render.render(write_still=True)
objs['LeftDoor'].rotation_euler.z=math.radians(-100);objs['RightDoor'].rotation_euler.z=math.radians(100)
sc.render.filepath=os.path.join(ROOT,'previews','pantry-open.png');bpy.ops.render.render(write_still=True)
objs['LeftDoor'].rotation_euler.z=0;objs['RightDoor'].rotation_euler.z=0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','KI-PANTRY-01.blend'))
