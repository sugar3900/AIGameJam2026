import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent; R=P.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Painted iron');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.32;bs.inputs['Roughness'].default_value=.7
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures'/'iron.png'),check_existing=True);tex.image.pack();pat=mat.node_tree.nodes.new('ShaderNodeTexImage');pat.image=bpy.data.images.load(str(R/'textures'/'brass-patina.png'),check_existing=True);pat.image.pack();mix=mat.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.45;mat.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(pat.outputs['Color'],mix.inputs[2]);mat.node_tree.links.new(mix.outputs['Color'],bs.inputs['Base Color'])
asset=[]; hooks=[]
def cyl(name,loc,r,depth,axis,verts=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name
 o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 o.data.materials.append(mat)
 bev=o.modifiers.new('Soft metal edges','BEVEL');bev.width=min(.0015,depth*.18,r*.25);bev.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bev.name)
 for f in o.data.polygons:f.use_smooth=True
 asset.append(o);return o
def hook(x,i):
 c=bpy.data.curves.new('Hook curve','CURVE');c.dimensions='3D';c.resolution_u=8;c.bevel_depth=.0028;c.bevel_resolution=2
 s=c.splines.new('BEZIER');pts=[(-.044,-.018),(-.061,-.012),(-.063,.006),(-.053,.017),(-.039,.017),(-.027,.006),(-.029,-.009),(-.038,-.023),(-.048,-.045),(-.048,-.066),(-.037,-.076),(-.026,-.069),(-.024,-.057)]
 s.bezier_points.add(len(pts)-1)
 for b,(y,z) in zip(s.bezier_points,pts):b.co=(x,y,z);b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new('Hook %d'%i,c);bpy.context.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object
 o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
 asset.append(o);hooks.append(o)
rod=cyl('Crossbar',(0,-.045,0),.006,.56,(1,0,0))
for i,x in enumerate([-.27,.27],1):
 cyl('Wall plate %d'%i,(x,-.004,0),.026,.008,(0,1,0));cyl('Standoff %d'%i,(x,-.025,0),.008,.042,(0,1,0))
 for z in [-.016,.016]:cyl('Screw %d'%i,(x,-.009,z),.0025,.002,(0,1,0),16)
for i,x in enumerate([-.225,-.075,.075,.225],1):hook(x,i)
for o in asset:
 if not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
# Export each object with common wall datum, so all pieces assemble without offsets.
for o in asset:
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
def export(name,parts):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.fbx(filepath=str(P/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,path_mode='AUTO')
export('KI_Pan_Rail_Assembly.fbx',asset);export('KI_Pan_Rail_Body.fbx',[o for o in asset if o not in hooks]);export('KI_Pan_Rail_Hooks.fbx',hooks)
# Preview wall excluded from exports.
w=bpy.data.materials.new('Preview plaster');w.use_nodes=True;w.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.55,.48,.40,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.025,0));wall=bpy.context.object;wall.name='Preview wall';wall.dimensions=(1.1,.05,.5);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.data.materials.append(w)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.18,.18,.18)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area((-.8,-1.3,1.5),38,1.8);area((1,-.8,.5),18,1.4)
bpy.ops.object.camera_add(location=(1.1,-2.1,.65));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.035,-.018))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.85;scene.camera=cam
scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/'previews'/'rail-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-2.5,0);cam.rotation_euler=(Vector((0,-.035,-.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.78;scene.render.filepath=str(R/'previews'/'rail-front.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'KI-PAN-RAIL-01.blend'))
