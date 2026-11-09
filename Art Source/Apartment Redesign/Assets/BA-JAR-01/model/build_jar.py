"""BA-JAR-01 in metres, +Z up, front -Y. Run with Blender --background --python."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];MOD=P/'model';PRE=P/'previews';TEX=P/'textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,c,tex):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.59
 n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(TEX/tex),check_existing=True);m.node_tree.links.new(n.outputs['Color'],b.inputs['Base Color']);return m
rose=mat('Dusty_Rose_Glaze',(.55,.27,.25),'rose-ceramic.png');cream=mat('Ivory_Glaze',(.82,.73,.61),'ivory-ceramic.png')
def lathe(name,profile,material,n=80,cap=True):
 v=[];f=[]
 for r,z in profile:
  for i in range(n):
   a=math.tau*i/n;v.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(n): f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 if cap: f.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(material)
 for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False);return ob
# Continuous body cross-section, descending into a genuinely hollow interior.
body=lathe('JarBody',[(.039,0),(.047,.001),(.050,.004),(.055,.012),(.059,.025),(.061,.040),(.060,.056),(.056,.071),(.052,.080),(.052,.084),(.055,.086),(.055,.089),(.052,.091),(.047,.091),(.045,.088),(.045,.082),(.048,.074),(.052,.057),(.052,.040),(.050,.025),(.046,.014),(.038,.009),(.003,.009)],rose)
# A restrained cream glaze stripe around the shoulder; integral surface just above body.
stripe=lathe('Cream_Stripe',[(.0596,.058),(.059,.061),(.058,.064)],cream,cap=False)
# Raised ceramic rim and foot rings echo the concept.
foot=lathe('Foot_Ring',[(.048,.003),(.051,.004),(.051,.006),(.049,.007)],rose,cap=False)
lid=lathe('Lid',[(.044,.086),(.046,.086),(.047,.089),(.053,.089),(.055,.091),(.055,.094),(.052,.098),(.047,.103),(.039,.108),(.029,.112),(.017,.115),(.005,.116)],cream)
knob=lathe('Knob',[(.005,.115),(.009,.116),(.011,.119),(.011,.123),(.009,.127),(.005,.129),(.002,.129)],cream)
def join(objs,name,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();ob=objs[0];ob.name=name;bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return ob
body=join([body,stripe,foot],'BA_Jar_Body',(0,0,0));lid=join([lid,knob],'BA_Jar_Lid',(0,0,.089))
for ob,name in [(body,'BA_Jar_Body.fbx'),(lid,'BA_Jar_Lid.fbx')]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(MOD/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(.25,-.38,.25));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.065))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.225;bpy.context.scene.camera=cam
for pos,power,size in [((-.32,-.4,.50),4,.45),((.34,.15,.35),2,.40)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.065))-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.world.color=(.14,.12,.1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(MOD/'BA-JAR-01.blend'))
s.render.filepath=str(PRE/'jar-closed.png');bpy.ops.render.render(write_still=True)
lid.location.x=.09;lid.location.z+=.025;lid.rotation_euler[1]=math.radians(25);cam.data.ortho_scale=.285;cam.rotation_euler=(Vector((.025,0,.07))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(PRE/'jar-open.png');bpy.ops.render.render(write_still=True)
