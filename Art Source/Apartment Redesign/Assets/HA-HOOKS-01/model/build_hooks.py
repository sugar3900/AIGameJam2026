import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent; R=P.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name, path, metal=0, rough=.75):
 m=bpy.data.materials.new(name);m.diffuse_color=(.6,.5,.35,1);m.use_nodes=True
 n=m.node_tree.nodes; b=n.get('Principled BSDF');b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures'/path),check_existing=True);tex.image.pack()
 m.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color']);return m
wood=mat('Warm muted walnut','walnut.png');brass=mat('Aged brass','brass.png',.60,.54)
asset=[]
def cube(name,loc,dim,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft worn edges','BEVEL');mod.width=bevel;mod.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(material);asset.append(o);return o

def sphere(name,loc,r,material,scale=(1,1,1)):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 asset.append(o);return o

def curved(name,x,points,r):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3;c.resolution_u=16
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for b,(y,z) in zip(s.bezier_points,points):b.co=(x,y,z);b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
 o.data.materials.append(brass)
 for p in o.data.polygons:p.use_smooth=True
 asset.append(o);return o
board=cube('Walnut backboard',(0,-.009,0),(.72,.018,.12),wood,.004)
# Map broad front/back faces along the board's long axis, preserving UVs on edges.
uv=board.data.uv_layers.active
for poly in board.data.polygons:
 if abs(poly.normal.y)>.9:
  for li in poly.loop_indices:
   co=board.data.vertices[board.data.loops[li].vertex_index].co
   uv.data[li].uv=(co.x/.72+.5, .5+co.z/.72)
# Match the other reviewed walnut furniture's muted color treatment.
n=wood.node_tree.nodes; h=n.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=.68;h.inputs['Value'].default_value=1.35
tex=next(x for x in n if x.type=='TEX_IMAGE');wood.node_tree.links.new(tex.outputs['Color'],h.inputs['Color']);wood.node_tree.links.new(h.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
for i,x in enumerate([-.27,-.09,.09,.27],1):
 # Oval mounting plate sits on wood, with screw heads.
 sphere('Hook %d backplate'%i,(x,-.020,0),.020,brass,(.55,.14,1.65))
 for z in (-.023,.023):sphere('Hook %d screw'%i,(x,-.023,z),.0026,brass,(1,.48,1))
 curved('Hook %d upper'%i,x,[(-.022,-.010),(-.033,.012),(-.046,.032),(-.055,.050)],.0037)
 sphere('Hook %d upper tip'%i,(x,-.055,.050),.006,brass)
 curved('Hook %d lower'%i,x,[(-.023,-.012),(-.032,-.035),(-.049,-.043),(-.061,-.025)],.0037)
 sphere('Hook %d lower tip'%i,(x,-.061,-.025),.006,brass)
# Ensure per-mesh UVs after converting curves.
for o in asset:
 if not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
# Shared wall-centre pivot, preserve assembly in a single FBX.
bpy.ops.object.select_all(action='DESELECT')
for o in asset:o.select_set(True)
bpy.context.view_layer.objects.active=board
bpy.ops.export_scene.fbx(filepath=str(P/'HA_Hooks.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,path_mode='AUTO')
# Preview wall omitted from FBX.
wallmat=bpy.data.materials.new('Preview wall');wallmat.use_nodes=True;wallmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.38,.32,1);wall=cube('Preview wall',(0,.024,0),(1.6,.045,.9),wallmat)
asset.remove(wall)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.18,.18,.18)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area((-.8,-1.3,1.5),38,1.8);area((1,-.8,.5),18,1.4)
bpy.ops.object.camera_add(location=(1.1,-2.1,.85));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.01,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.05;scene.camera=cam
scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/'previews'/'hooks-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-2.5,0);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.9;scene.render.filepath=str(R/'previews'/'hooks-front.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'HA-HOOKS-01.blend'))
