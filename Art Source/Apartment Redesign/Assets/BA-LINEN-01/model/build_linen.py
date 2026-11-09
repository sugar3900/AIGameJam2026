import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in ('model','previews'): os.makedirs(os.path.join(ROOT,d),exist_ok=True)

def mat(name,color,metallic=0,rough=.65,img=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=rough
 if img:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(img,check_existing=True)
  mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.56;mix.inputs[2].default_value=(.94,.91,.82,1);m.node_tree.links.new(n.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs['Color'],p.inputs['Base Color'])
 return m
paint=mat('Painterly warm ivory',(0.73,.55,.34),img=os.path.join(ROOT,'textures','ivory-paint-C.png'))
brass=mat('aged brass',(.42,.23,.07),.72,.38)
inner=paint
wear=mat('small exposed ochre wood',(.31,.19,.095),0,.85)
groups={'Body':[],'UpperDoor':[],'LowerDoor':[]}
def box(n,loc,dim,ma,grp,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft crafted edges','BEVEL');mod.width=bevel;mod.segments=2; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(ma);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');groups[grp].append(o);return o

def ball(n,loc,r,ma,grp):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=r,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(ma);bpy.ops.object.shade_smooth();groups[grp].append(o);return o
# body: front points negative Y; interior is real and open.
for x in (-.265,.265):
 box('side',(x,0,.93),(.045,.54,1.45),paint,'Body')
 for y in (-.235,.235): box('leg',(x,y,.095),(.065,.065,.19),paint,'Body')
 # side inset and applied bead; layered joinery
 box('side field',(x*1.09,0,.94),(.013,.40,1.15),paint,'Body',.003)
box('back',(0,.253,.93),(.50,.035,1.45),inner,'Body')
for z in (.21,.57,.92,1.27,1.63): box('shelf',(0,-.005,z),(.50,.51,.035),paint,'Body',.004)
# Concave lower apron cut from a shaped plate, raised at the middle.
profile=[(-.24,.23),(.24,.23),(.24,.055),(.18,.055),(.16,.085),(.13,.11),(.10,.12),(-.10,.12),(-.13,.11),(-.16,.085),(-.18,.055),(-.24,.055)]
verts=[(x,y,z) for y in (-.283,-.248) for x,z in profile];k=len(profile)
faces=[tuple(reversed(range(k))),tuple(range(k,k*2))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
mesh=bpy.data.meshes.new('shaped apron mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('shaped apron',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(paint);groups['Body'].append(o)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
box('crown lower',(0,0,1.655),(.58,.58,.05),paint,'Body')
box('crown lip',(0,0,1.702),(.60,.60,.045),paint,'Body')
box('crown cap',(0,0,1.733),(.59,.59,.017),paint,'Body')
# individual framed doors, left-mounted hinges and right pulls
for grp,z,h in [('LowerDoor',.565,.68),('UpperDoor',1.295,.68)]:
 box('inset panel',(0,-.287,z),(.455,.028,h-.09),paint,grp,.003)
 for x in (-.249,.249): box('door stile',(x,-.304,z),(.047,.055,h),paint,grp,.004)
 for dz in (-h/2+.025,h/2-.025): box('door rail',(0,-.304,z+dz),(.45,.055,.05),paint,grp,.004)
 # inner applied narrow raised trim
 for x in (-.193,.193): box('panel moulding',(x,-.32,z),(.012,.018,h-.14),paint,grp,.002)
 for dz in (-h/2+.07,h/2-.07):box('panel moulding',(0,-.32,z+dz),(.39,.018,.012),paint,grp,.002)
 ball('brass backplate',(.19,-.336,z),.021,brass,grp)
 ball('brass knob',(.19,-.357,z),.022,brass,grp)
 # local, narrow rubbed highlights along handled edges, not a uniform damage overlay
 for dx,dz,w in [(.235,-.29,.014),(.234,.12,.012),(.237,.25,.01),(-.236,-.19,.012),(-.232,.27,.009)]:
  box('small rubbed edge',(dx,-.333,z+dz),(.0025,.002,w),wear,grp,.0004)
 for dx,dz,w in [(-.10,-.322,.024),(.07,-.322,.014),(.15,.322,.018),(-.16,.322,.012)]:
  box('small rubbed rail',(dx,-.333,z+dz),(w,.002,.0025),wear,grp,.0004)
 for dz in (-.22,.22):
  box('hinge plate',(-.263,-.336,z+dz),(.030,.012,.075),brass,grp,.003)
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.008,depth=.083,location=(-.278,-.343,z+dz));o=bpy.context.object;o.name='hinge barrel';o.data.materials.append(brass);groups[grp].append(o)
# Join animation groups and export at actual intended pivots
pivots={'Body':(0,0,0),'UpperDoor':(-.274,-.31,1.295),'LowerDoor':(-.274,-.31,.565)}
objs={}
for group,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='BA_Linen_'+group;objs[group]=o
 bpy.context.scene.cursor.location=pivots[group];bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
# Neutral warm review light
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(3.2,-4.7,2.65));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.88))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.45;sc.camera=cam
for loc,power,size in [((2,-4,5),300,4),((-3,-1,3.5),160,3),((0,3,4),180,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.rotation_euler=(Vector((0,0,.8))-a.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.film_transparent=True
sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.join(ROOT,'previews','linen-closed.png');bpy.ops.render.render(write_still=True)
for n in ('UpperDoor','LowerDoor'):objs[n].rotation_euler.z=math.radians(-100)
sc.render.filepath=os.path.join(ROOT,'previews','linen-open.png');bpy.ops.render.render(write_still=True)
for n in ('UpperDoor','LowerDoor'):objs[n].rotation_euler.z=0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','BA-LINEN-01.blend'))
