import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent; R=P.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Aged brass');mat.use_nodes=True
n=mat.node_tree.nodes;b=n.get('Principled BSDF');b.inputs['Metallic'].default_value=.68;b.inputs['Roughness'].default_value=.45
tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures'/'aged-brass.png'),check_existing=True);tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color'])
parts=[]
def finish(o):
 o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o);return o
def sphere(name,loc,r,scale=(1,1,1)):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o)
def disc(name,loc,r,depth):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 mod=o.modifiers.new('soft machined edges','BEVEL');mod.width=.0012;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);return finish(o)
def line(name,points,r):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=4;c.resolution_u=16
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for b,pt in zip(s.bezier_points,points):b.co=pt;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return finish(o)
# Wall plane is Y=0, hook projects toward -Y; datum is plate centre.
disc('backplate',(0,-.004,0),.030,.008)
disc('raised socket',(0,-.010,-.004),.011,.009)
line('hook arm',[(0,-.014,-.004),(0,-.027,-.030),(0,-.049,-.070),(0,-.068,-.063),(0,-.071,-.030)],.0045)
sphere('rounded hook tip',(0,-.071,-.030),.006)
for x in (-.019,.019):
 sphere('slotted screw head',(x,-.0085,0),.003,(1,.36,1))
 # Real dark slot as small inset, not a floating large line.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-.010,0));o=bpy.context.object;o.name='screw slot';o.dimensions=(.0035,.0005,.00055);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 dark=bpy.data.materials.get('Screw recess') or bpy.data.materials.new('Screw recess');dark.diffuse_color=(.07,.045,.02,1);dark.use_nodes=True;dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.07,.045,.02,1);o.data.materials.append(dark);parts.append(o)
for o in parts:
 if not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
# Join asset geometry, preserve origin exactly at wall plane and plate centre.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hook=bpy.context.object;hook.name='BA_Hook_01';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(P/'BA_Hook_01.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
# Unexported preview wall.
wallmat=bpy.data.materials.new('Preview plaster');wallmat.diffuse_color=(.52,.46,.43,1);wallmat.use_nodes=True;wallmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.52,.46,.43,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.015,0));wall=bpy.context.object;wall.name='Preview wall (not exported)';wall.dimensions=(.3,.029,.3);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.data.materials.append(wallmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.18,.18,.18)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area((-.4,-.7,.8),14,1);area((.6,-.6,.2),8,.8)
bpy.ops.object.camera_add(location=(.30,-.70,.24));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.025,-.020))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.19;scene.camera=cam;scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/'previews'/'hook-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-.7,0);cam.rotation_euler=(Vector((0,-.025,-.020))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.18;scene.render.filepath=str(R/'previews'/'hook-front.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'BA-HOOK-01.blend'))
