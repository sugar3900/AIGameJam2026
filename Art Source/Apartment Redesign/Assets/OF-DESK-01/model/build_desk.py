"""Build OF-DESK-01 in metres; front is -Y, floor at Z=0."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; O=P/'previews'; T=P/'textures'
for p in (M,O): p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
wood=mat('Desk walnut painted',(.42,.20,.07));s=wood.node_tree.nodes.get('Principled BSDF');tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'desk-walnut-v2-expressive.png'));tex.image.pack();wood.node_tree.links.new(tex.outputs['Color'],s.inputs['Base Color'])
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
   if abs(n.z)>.7: uv=(v.x/1.75+.5,v.y/1.75+.5)
   elif abs(n.y)>.7: uv=(v.x/1.75+.5,v.z/1.75+.5)
   else: uv=(v.y/1.75+.5,v.z/1.75+.5)
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
body.append(box('Top rounded overhang',(0,0,.735),(1.75,.6,.045),wood,.016))
# Apron / carcass: drawer openings remain actual spaces between rails.
body.append(box('Back apron',(0,.255,.62),(1.58,.038,.19),wood))
for x in (-.775,.775): body.append(box('Side apron',(x,0,.62),(.045,.49,.19),wood))
for z in (.526,.713): body.append(box('Front rail',(0,-.255,z),(1.51,.035,.026),wood))
for x in (-.76,-.26,.26,.76): body.append(box('Drawer stile',(x,-.255,.62),(.025,.035,.17),wood))
# Period tapered/turned legs; collars make joints readable.
for x in (-.785,.785):
 for y in (-.225,.225):
  body.append(cyl('Turned leg',(x,y,.275),.033,.45,wood))
  for z,r,h in ((.09,.037,.038),(.51,.044,.042),(.55,.047,.035)):
   body.append(cyl('Turned leg collar',(x,y,z),r,h,wood))
  body.append(ball('Foot',(x,y,.032),(.038,.038,.032),wood))
body=take('OF_DESK_BODY',body)
# Separate hollow drawer boxes, each same world/floor origin and local -Y sliding motion.
drawers=[]
for i,x in enumerate((-.51,0,.51)):
 group=[]; w=.475; dep=.43
 group.append(box('Drawer front',(x,-.285,.62),(w,.035,.15),wood,.003))
 group.append(box('Drawer bottom',(x,-.055,.555),(w-.035,dep,.018),interior,.002))
 for dx in (-w/2+.015,w/2-.015):group.append(box('Drawer side',(x+dx,-.055,.62),(.018,dep,.12),interior,.002))
 group.append(box('Drawer rear',(x,.15,.62),(w-.035,.018,.12),interior,.002))
 # Brass escutcheon and turned knob facing front.
 group.append(cyl('Pull backplate',(x,-.31,.62),.025,.007,brass,(math.pi/2,0,0)))
 group.append(cyl('Pull stem',(x,-.325,.62),.008,.028,brass,(math.pi/2,0,0)))
 group.append(ball('Pull knob',(x,-.344,.62),(.015,.014,.015),brass))
 drawers.append(take('OF_DESK_DRAWER_'+str(i+1),group))
def export(obj):
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(M/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
for o in [body]+drawers:export(o)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.18,.16,.14)
bpy.ops.object.light_add(type='AREA',location=(2,-4,5));l=bpy.context.object;l.data.energy=600;l.data.color=(1,.88,.75);l.data.size=5
bpy.ops.object.light_add(type='AREA',location=(-3,2,3));l=bpy.context.object;l.data.energy=180;l.data.color=(1,.83,.72);l.data.size=3
bpy.ops.object.camera_add(location=(2.5,-3.5,2.1));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.40))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.30;scene.camera=cam
scene.render.filepath=str(O/'desk-closed.png');bpy.ops.render.render(write_still=True)
drawers[1].location.y=-.26;scene.render.filepath=str(O/'desk-open.png');bpy.ops.render.render(write_still=True);drawers[1].location.y=0
bpy.ops.wm.save_as_mainfile(filepath=str(M/'OF-DESK-01.blend'))
print('DESK BUILT',tuple(round(v,3) for v in body.dimensions))
