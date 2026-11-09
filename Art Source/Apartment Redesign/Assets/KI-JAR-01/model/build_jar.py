"""KI-JAR-01: metres, +Z up, jar front -Y. Background Blender build."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; MOD=P/'model'; PRE=P/'previews'; TEX=P/'textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.55,img=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
 if img:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(TEX/img),check_existing=True);m.node_tree.links.new(n.outputs['Color'],b.inputs['Base Color'])
 return m
ivory=mat('Ivory_Ceramic',(.82,.73,.61),.55,'ivory-ceramic.png');floral=mat('Painted_Floral',(.82,.73,.61),.6,'floral-ceramic.png');rose=mat('Faded_Rose_Glaze',(.46,.20,.16),.56)
def lathe(name,profile,m,n=96,cap=True):
 verts=[];faces=[]
 for r,z in profile:
  for i in range(n):
   a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 if cap:faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(m)
 for p in me.polygons:p.use_smooth=len(p.vertices)==4
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 return o
profile=[(.068,0),(.074,.001),(.078,.005),(.079,.012),(.079,.18),(.078,.192),(.079,.198),(.078,.201),(.073,.202),(.069,.199),(.069,.19),(.070,.17),(.070,.022),(.067,.012),(.060,.008),(.004,.008)]
body=lathe('Hollow_Canister',profile,ivory);body.data.materials.append(floral)
uv=body.data.uv_layers.active
for p in body.data.polygons:
 j=p.index//96
 if p.index<96*7:
  p.material_index=1
  for li in p.loop_indices:
   vi=body.data.loops[li].vertex_index;v=body.data.vertices[vi];col=vi%96
   u=((col/96)+.25)%1
   if p.index%96==71 and u<.1:u=1
   uv.data[li].uv=(u,max(0,min(1,v.co.z/.20)))
# Closed lid with integral locating lip underneath, softly domed top and separate colored finial.
lid=lathe('Lid',[(.067,.192),(.069,.192),(.070,.196),(.077,.196),(.080,.199),(.080,.203),(.076,.207),(.070,.213),(.058,.220),(.044,.226),(.027,.230),(.012,.231),(.004,.231)],ivory)
band=lathe('Lid_Rose_Band',[(.0798,.200),(.0802,.2025)],rose,cap=False)
knob=lathe('Lid_Rose_Knob',[(.006,.230),(.013,.232),(.018,.235),(.018,.239),(.015,.242),(.010,.244),(.004,.245)],rose)
# Join lid parts, set a meaningful lid-centre pivot at the closed seating height.
bpy.ops.object.select_all(action='DESELECT')
for o in [lid,band,knob]:o.select_set(True)
bpy.context.view_layer.objects.active=lid;bpy.ops.object.join();lid.name='KI_Jar_Lid';bpy.context.scene.cursor.location=(0,0,.196);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
body.name='KI_Jar_Body';bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
for ob,name in [(body,'KI_Jar_Body.fbx'),(lid,'KI_Jar_Lid.fbx')]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(MOD/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(.38,-.56,.36));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.12))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.36;bpy.context.scene.camera=cam
for pos,power,size in [((-.32,-.4,.50),4,.45),((.34,.15,.35),2,.40)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.10))-o.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=40;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.14,.12,.1)
bpy.ops.wm.save_as_mainfile(filepath=str(MOD/'KI-JAR-01.blend'))
sc.render.filepath=str(PRE/'jar-closed.png');bpy.ops.render.render(write_still=True)
lid.location.x=.14;lid.location.z+=.03;lid.rotation_euler[1]=math.radians(25)
cam.data.ortho_scale=.46;cam.rotation_euler=(Vector((.055,0,.12))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(PRE/'jar-open.png');bpy.ops.render.render(write_still=True)
