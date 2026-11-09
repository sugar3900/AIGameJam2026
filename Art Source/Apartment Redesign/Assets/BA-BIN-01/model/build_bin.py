import bpy, math, os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name, tex, rough=.7, metallic=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(.8,.75,.65,1);m.use_nodes=True
 n=m.node_tree.nodes; p=n.get('Principled BSDF'); p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metallic
 if tex:
  im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(P/'textures'/tex),check_existing=True); im.image.pack(); im.image.filepath='//../textures/'+tex
  m.node_tree.links.new(im.outputs['Color'],p.inputs['Base Color'])
 return m
enamel=mat('Painted ivory enamel','enamel.png',.72);brass=mat('Muted aged brass','brass.png',.62,.75);inner=mat('Dark interior metal','brass.png',.78,.4)
def uv(o):
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
def finish(o,m):
 o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 uv(o);return o
def lathe(name,profile,m):
 N=64;v=[];faces=[]
 for rad,z in profile:
  for i in range(N):
   a=2*math.pi*i/N;v.append((rad*math.cos(a),rad*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,m)
def cube(name,loc,scale,m, bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,m)
def cyl(name,loc,radius,depth,m,rotation=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=rotation or (0,0,0));o=bpy.context.object;o.name=name;return finish(o,m)
def torus(name,loc,major,minor,m):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=loc,major_radius=major,minor_radius=minor);o=bpy.context.object;o.name=name;return finish(o,m)
def join(name,obs,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
body=[]
body.append(lathe('Hollow bin',[(.105,.012),(.111,.02),(.112,.267),(.111,.279),(.104,.28),(.103,.03),(.001,.03)],enamel))
body.append(torus('Brass top lip',(0,0,.279),.109,.0023,brass));body.append(torus('Base trim',(0,0,.018),.109,.003,brass))
body.append(cube('Hinge base',(0,.112,.263),(.050,.012,.031),brass))
body.append(cyl('Hinge barrel',(0,.119,.292),.006,.055,brass,(0,math.pi/2,0)))
body.append(cube('Pedal housing',(0,-.114,.039),(.056,.017,.028),brass))
for x in [-.017,.017]:body.append(cyl('Hinge screw',(x,.12,.263),.0025,.004,brass,(math.pi/2,0,0)))
body=join('Bin_body',body,(0,0,0))
lid=[]
lid.append(lathe('Lid',[(.001,.302),(.06,.302),(.108,.297),(.112,.292),(.112,.283),(.105,.282),(.103,.287),(.001,.291)],enamel))
lid.append(torus('Lid brass rim',(0,0,.287),.109,.002,brass))
lid.append(cube('Lid hinge strap',(0,.104,.296),(.032,.035,.006),brass))
lid=join('Bin_lid',lid,(0,.119,.292))
ped=[]
ped.append(cube('Pedal',(0,-.14,.028),(.052,.054,.012),brass,.004))
for x in [-.018,-.009,0,.009,.018]:ped.append(cube('Grip',(x,-.145,.035),(.002,.028,.0015),inner,.0005))
ped=join('Bin_pedal',ped,(0,-.112,.028))
for obj in [body,lid,ped]:
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',bake_space_transform=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.25,.25,.25)
# ground is preview only
floor=cube('Preview ground',(0,0,-.006),(6,6,.01),mat('Preview ground',None),.0)
floor.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.22,.2,.19,1)
def light(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.14))-o.location).to_track_quat('-Z','Y').to_euler()
light((-.9,-1.2,1.6),180,1.8);light((1,.3,1.2),90,1.4)
bpy.ops.object.camera_add(location=(.65,-.9,.67));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.24))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.76;scene.camera=cam
scene.view_settings.view_transform='AgX'
lid.rotation_euler.x=0;scene.render.filepath=str(P/'previews/bin-closed.png');bpy.ops.render.render(write_still=True)
lid.rotation_euler.x=math.radians(-105);scene.render.filepath=str(P/'previews/bin-open.png');bpy.ops.render.render(write_still=True)
lid.rotation_euler.x=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-BIN-01.blend'))
