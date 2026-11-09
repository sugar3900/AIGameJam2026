"""Build OF-DESK-01 in metres; front is -Y, floor at Z=0."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; O=P/'previews'; T=P/'textures'
for p in (M,O): p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
wood=mat('Console walnut painted',(.42,.20,.07));s=wood.node_tree.nodes.get('Principled BSDF');tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'walnut-muted-b.png'));tex.image.pack();hsv=wood.node_tree.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.68;hsv.inputs['Value'].default_value=1.35;wood.node_tree.links.new(tex.outputs['Color'],hsv.inputs['Color']);wood.node_tree.links.new(hsv.outputs['Color'],s.inputs['Base Color']);s.inputs['Roughness'].default_value=.84
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
# A shallow enclosed vintage gallery cabinet. Front faces -Y.
body=[]
body.append(box('Crown top',(0,0,.702),(1.02,.235,.035),wood,.004))
body.append(box('Base plinth',(0,0,.095),(.97,.224,.035),wood,.003))
body.append(box('Back',(0,.101,.36),(.94,.018,.59),wood,.002))
body.append(box('Shelf',(0,0,.295),(.94,.20,.018),wood,.002))
for x in (-.479,.479):
 body.append(box('Side',(x,0,.38),(.026,.22,.60),wood,.003))
for x in (-.44,.44):
 for y in (-.08,.08):
  leg=box('Foot',(x,y,.055),(.055,.055,.11),wood,.003)
  for v in leg.data.vertices:
   if v.co.z<-.035:v.co.x*=.8;v.co.y*=.8
  body.append(leg)
for z in (.533,.635):body.append(box('Drawer rail',(0,-.106,z),(.94,.020,.016),wood,.002))
body.append(box('Upper apron',(0,-.106,.661),(.94,.020,.050),wood,.002))
body.append(box('Drawer separator',(0,0,.53),(.94,.21,.016),wood,.002))
body=take('HA_CABINET_BODY',body)
# A real shallow box, common floor origin, movable in local -Y.
d=[];w=.89
for n,loc,dim,matl in [('Front',(0,-.112,.584),(w,.018,.084),wood),('Bottom',(0,-.016,.545),(w-.03,.166,.012),interior),('Back',(0,.064,.586),(w-.03,.012,.075),interior)]:d.append(box('Drawer '+n,loc,dim,matl,.0015))
for x in (-.432,.432):d.append(box('Drawer side',(x,-.016,.585),(.013,.166,.075),interior,.001))
for x in (-.28,.28):
 d.append(cyl('Drawer rosette',(x,-.122,.584),.012,.006,brass,(math.pi/2,0,0)))
 d.append(ball('Drawer knob',(x,-.123,.584),(.009,.006,.009),brass))
drawer=take('HA_CABINET_DRAWER',d)
# Independently hinged lower panels, origins at outside edge.
doors=[]
for side in (-1,1):
 x=side*.235
 pieces=[box('Door panel',(x,-.111,.323),(.455,.018,.39),wood,.002)]
 for z in (.16,.486):pieces.append(box('Panel rail',(x,-.121,z),(.39,.006,.016),wood,.001))
 for dx in (-.194,.194):pieces.append(box('Panel stile',(x+dx,-.121,.323),(.016,.006,.31),wood,.001))
 pieces.append(ball('Cabinet knob',(side*.060,-.124,.335),(.010,.006,.010),brass))
 
 for z in (.18,.46):pieces.append(cyl('Door hinge',(side*.462,-.116,z),.004,.037,brass))
 door=take('HA_CABINET_DOOR_'+('L' if side<0 else 'R'),pieces)
 bpy.context.scene.cursor.location=(side*.465,-.11,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');doors.append(door)

def export(obj):
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(M/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
for o in [body,drawer,*doors]:export(o)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.18,.16,.14)
bpy.ops.object.light_add(type='AREA',location=(2,-4,5));l=bpy.context.object;l.data.energy=550;l.data.color=(1,.87,.72);l.data.size=4
bpy.ops.object.light_add(type='AREA',location=(-3,2,3));l=bpy.context.object;l.data.energy=160;l.data.color=(1,.83,.72);l.data.size=3
bpy.ops.object.camera_add(location=(2,-3,1.6));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.5;scene.camera=cam
scene.render.filepath=str(O/'cabinet-closed.png');bpy.ops.render.render(write_still=True)
drawer.location.y=-.13
doors[0].rotation_euler.z=-math.radians(75);doors[1].rotation_euler.z=math.radians(75)
scene.render.filepath=str(O/'cabinet-open.png');bpy.ops.render.render(write_still=True)
drawer.location.y=0
for o in doors:o.rotation_euler.z=0
bpy.ops.wm.save_as_mainfile(filepath=str(M/'HA-CABINET-01.blend'))
print('CABINET BODY',tuple(round(x,4) for x in body.dimensions))
