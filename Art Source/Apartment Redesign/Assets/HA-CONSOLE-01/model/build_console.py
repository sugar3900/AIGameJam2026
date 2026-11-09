"""Build OF-DESK-01 in metres; front is -Y, floor at Z=0."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; O=P/'previews'; T=P/'textures'
for p in (M,O): p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
wood=mat('Console walnut painted',(.42,.20,.07));s=wood.node_tree.nodes.get('Principled BSDF');tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'walnut-b.png'));tex.image.pack();wood.node_tree.links.new(tex.outputs['Color'],s.inputs['Base Color'])
brass=mat('Aged brass',(.49,.30,.11),.48,.65); interior=mat('Drawer wood inside',(.40,.24,.12),.8)
def box(name,loc,dim,material,b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=b;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(material)
 # Project using physical coordinates to avoid smearing broad paint strokes across a wide desktop.
 layer=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for poly in o.data.polygons:
  n=poly.normal
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if abs(n.z)>.7: uv=(v.x/1.05+.5,v.y/1.05+.5)
   elif abs(n.y)>.7: uv=(v.x/1.05+.5,v.z/1.05+.5)
   else: uv=(v.y/1.05+.5,v.z/1.05+.5)
   layer.data[li].uv=uv
 return o
def cyl(name,loc,r,depth,material,rot=(0,0,0),vertices=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(material);return o
def ball(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def take(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
body=[]
body.append(box('Top', (0,0,.765), (1.05,.25,.04), wood,.009))
body.append(box('Shelf',(0,0,.115),(.92,.20,.028),wood,.004))
body.append(box('Back apron',(0,.095,.66),(.90,.025,.16),wood,.002))
for x in (-.475,.475):
 for y in (-.08,.08):
  leg=box('Leg',(x,y,.38),(.045,.045,.75),wood,.004)
  for v in leg.data.vertices:
   if v.co.z < -.25: v.co.x *= .72; v.co.y *= .72
  body.append(leg)
  body.append(box('Capital',(x,y,.66),(.055,.055,.16),wood,.003))
for x in (-.45,.45):body.append(box('Apron end',(x,0,.66),(.04,.18,.16),wood,.002))
for x in (-.43,.43):body.append(box('Drawer stile',(x,-.103,.66),(.018,.025,.16),wood,.002))
for z in (.575,.737):body.append(box('Front rail',(0,-.103,z),(.86,.025,.021),wood,.002))
body=take('HA_CONSOLE_BODY',body)
d=[];w=.82;depth=.16
d.append(box('Drawer front',(0,-.121,.657),(w,.022,.13),wood,.003))
d.append(box('Drawer bottom',(0,-.024,.601),(w-.03,depth,.012),interior,.001))
for x in (-.397,.397):d.append(box('Drawer side',(x,-.024,.655),(.015,depth,.10),interior,.001))
d.append(box('Drawer back',(0,.051,.655),(.78,.012,.1),interior,.001))
# Period bail pull as a curved brass arc with decorative mounts.
for x in (-.065,.065):
 d.append(cyl('Escutcheon',(x,-.14,.665),.015,.006,brass,(math.pi/2,0,0)))
 d.append(ball('Pull end',(x,-.146,.665),(.009,.007,.009),brass))
curve=bpy.data.curves.new('Brass bail','CURVE');curve.dimensions='3D';curve.bevel_depth=.004;curve.bevel_resolution=3;sp=curve.splines.new('POLY');sp.points.add(20)
for i,p in enumerate(sp.points):
 a=math.pi+math.pi*i/20;p.co=(.065*math.cos(a),-.153,.665+.045*math.sin(a),1)
o=bpy.data.objects.new('Bail',curve);bpy.context.collection.objects.link(o);o.data.materials.append(brass);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');d.append(bpy.context.object)
drawer=take('HA_CONSOLE_DRAWER',d)
def export(obj):
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(M/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
for o in [body,drawer]:export(o)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.18,.16,.14)
bpy.ops.object.light_add(type='AREA',location=(2,-4,5));l=bpy.context.object;l.data.energy=550;l.data.color=(1,.87,.72);l.data.size=4
bpy.ops.object.light_add(type='AREA',location=(-3,2,3));l=bpy.context.object;l.data.energy=160;l.data.color=(1,.83,.72);l.data.size=3
bpy.ops.object.camera_add(location=(2,-3,1.6));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.38))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.55;scene.camera=cam
scene.render.filepath=str(O/'console-closed.png');bpy.ops.render.render(write_still=True)
drawer.location.y=-.13;scene.render.filepath=str(O/'console-open.png');bpy.ops.render.render(write_still=True);drawer.location.y=0
bpy.ops.wm.save_as_mainfile(filepath=str(M/'HA-CONSOLE-01.blend'))
print('CONSOLE BODY',tuple(round(x,4) for x in body.dimensions))
