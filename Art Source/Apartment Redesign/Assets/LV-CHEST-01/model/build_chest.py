"""Rebuild LV-CHEST-01; metres, front -Y, lid origin at back hinge."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; O=P/'previews'; T=P/'textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.8,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
wood=mat('Aged walnut',(.3,.14,.07));s=wood.node_tree.nodes.get('Principled BSDF');tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'walnut-muted-b.png'));tex.image.pack();h=wood.node_tree.nodes.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=.68;h.inputs['Value'].default_value=1.35;wood.node_tree.links.new(tex.outputs['Color'],h.inputs['Color']);wood.node_tree.links.new(h.outputs['Color'],s.inputs['Base Color']);s.inputs['Roughness'].default_value=.86
wear=mat('Worn light walnut',(.39,.27,.15),.93)
inside=mat('Interior wood',(.31,.19,.10));brass=mat('Patinated brass',(.36,.20,.075),.54,.62)
def box(name,loc,dim,material,b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  m=o.modifiers.new('Rounded edges','BEVEL');m.width=b;m.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 o.data.materials.append(material)
 layer=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for poly in o.data.polygons:
  n=poly.normal
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if abs(n.z)>.7: uv=(v.x/.90+.5,v.y/.9+.5)
   elif abs(n.y)>.7:uv=(v.x/.90+.5,v.z/.9+.5)
   else:uv=(v.y/.90+.5,v.z/.9+.5)
   layer.data[li].uv=uv
 return o
def cylinder(name,loc,r,depth,material,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(material);return o
def join(name,objects,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
body=[]
body.append(box('Base board',(0,0,.072),(.87,.35,.028),wood,.005))
for x in (-.422,.422):body.append(box('Side wall',(x,0,.210),(.026,.35,.26),wood,.003))
for y in (-.162,.162):body.append(box('Front or back wall',(0,y,.21),(.824,.026,.26),wood,.003))
body.append(box('Interior bottom',(0,0,.091),(.817,.29,.015),wood,.001))
# Framed inset front face, modeled rails and panels.
for z in (.105,.315):body.append(box('Front rail',(0,-.178,z),(.83,.012,.025),wood,.003))
for x in (-.40,0,.40):body.append(box('Front stile',(x,-.178,.21),(.022,.012,.20),wood,.003))
for x in (-.2,.2):body.append(box('Inset panel',(x,-.177,.21),(.36,.008,.17),wood,.002))
for x in (-.355,.355):
 for y in (-.125,.125):body.append(box('Short foot',(x,y,.032),(.095,.075,.064),wood,.006))
body.append(box('Latch lower plate',(0,-.187,.307),(.035,.008,.046),brass,.003))
body.append(cylinder('Latch stud',(0,-.194,.307),.006,.009,brass,(math.pi/2,0,0)))
# Back hinge barrels remain attached to the case, two separate metal details.
for x in (-.30,.30):body.append(cylinder('Hinge barrel',(x,.175,.35),.009,.08,brass,(0,math.pi/2,0)))
# Small exposed patches on corners and front rails; geometry follows the worn surface.
for x,z,length in [(-.36,.118,.038),(.32,.118,.050),(-.27,.321,.030),(.35,.321,.045)]:
 body.append(box('Fine edge rub',(x,-.185,z),(length,.001,.002),wear,.0003))
for x,z in [(-.413,.145),(.413,.25),(-.413,.282)]:
 body.append(box('Corner rub',(x,-.185,z),(.002,.001,.018),wear,.0003))
body=join('LV_CHEST_BODY',body,(0,0,0))
lid=[]
lid.append(box('Thick overhanging lid',(0,0,.37),(.90,.38,.045),wood,.006))
lid.append(box('Lid bottom lip',(0,0,.345),(.84,.32,.008),wood,.002))
lid.append(box('Latch upper plate',(0,-.194,.354),(.035,.008,.027),brass,.002))
for x in (-.30,.30):lid.append(box('Hinge leaf',(x,.160,.346),(.08,.03,.005),brass,.001))
for x,length in [(-.39,.045),(-.17,.035),(.37,.040)]:
 lid.append(box('Lid edge rub',(x,-.1908,.386),(length,.001,.0025),wear,.0003))
lid=join('LV_CHEST_LID',lid,(0,.175,.35))
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(M/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
for o in (body,lid):export(o)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.18,.16,.14)
for loc,power,size,col in [((2,-4,5),550,4,(1,.87,.72)),((-3,2,3),160,3,(1,.83,.72))]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.size=size;l.data.color=col
bpy.ops.object.camera_add(location=(2,-3,1.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.20))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.58;sc.camera=cam
sc.render.filepath=str(O/'chest-closed.png');bpy.ops.render.render(write_still=True)
lid.rotation_euler.x=math.radians(-100);sc.render.filepath=str(O/'chest-open.png');bpy.ops.render.render(write_still=True);lid.rotation_euler.x=0
bpy.ops.wm.save_as_mainfile(filepath=str(M/'LV-CHEST-01.blend'))
