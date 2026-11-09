import bpy, math, os
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(n,c,metal=0,rough=.78,img=None):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 if img:
  t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(os.path.join(R,'textures',img),check_existing=True)
  mix=m.node_tree.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MIX'; mix.inputs[0].default_value=.35; mix.inputs[2].default_value=(.85,.79,.68,1)
  m.node_tree.links.new(t.outputs['Color'],mix.inputs[1]); m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
 return m
paint=mat('Painted warm ivory',(.77,.69,.56),img='paint-selected.png'); brass=mat('Muted aged brass',(.31,.205,.075),.68,.46); wood=mat('Edge rub, warm timber',(.43,.29,.16),0,.9)
groups={'Frame':[],'Leaf':[]}
def uv(o):
 bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.015); bpy.ops.object.mode_set(mode='OBJECT')
def box(n, loc, dim, mat, group, bevel=.003):
 bpy.ops.object.select_all(action='DESELECT'); bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Subtle eased edges','BEVEL'); mod.width=bevel; mod.segments=2; bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat); uv(o); groups[group].append(o); return o
def cyl(n,loc,r,depth,mat,group,rot=(0,0,0)):
 bpy.ops.object.select_all(action='DESELECT'); bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(mat);bpy.ops.object.shade_smooth();groups[group].append(o);return o
def sphere(n,loc,r,mat,group):
 bpy.ops.object.select_all(action='DESELECT'); bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(mat);bpy.ops.object.shade_smooth();groups[group].append(o);return o
# 0.90m clear opening; two-sided trim with 0.12m partition depth
for x in (-.49,.49):
 box('Jamb', (x,0,1.06),(.08,.12,2.12),paint,'Frame')
 for y in (-.072,.072): box('Vertical casing',(x,y,1.055),(.09,.025,2.11),paint,'Frame',.002)
box('Top jamb',(0,0,2.135),(1.06,.12,.05),paint,'Frame')
for y in (-.072,.072):
 box('Head casing',(0,y,2.16),(1.10,.028,.075),paint,'Frame')
 box('Head crown',(0,y,2.208),(1.12,.038,.022),paint,'Frame')
# 0.89m wide door leaf, clear of jamb. Full solid slab and 5 identical moulded inset fields on each face.
box('Solid door', (0,0,1.047),(.886,.042,2.094),paint,'Leaf',.004)
for ysign in (-1,1):
 y=ysign*.023
 # Raised stiles and rails give the five fields believable panel joinery.
 for x in (-.396,.396):box('Raised outer stile',(x,ysign*.025,1.047),(.09,.012,2.08),paint,'Leaf',.003)
 for z in (.045,.45,.85,1.25,1.65,2.045):box('Raised cross rail',(0,ysign*.025,z),(.72,.012,.07),paint,'Leaf',.003)
 # applied mouldings surround each recessed field on both faces
 for z in (.25,.65,1.05,1.45,1.85):
  for x in (-.33,.33):box('Panel side bead',(x,y,z),(.016,.012,.305),paint,'Leaf',.002)
  for dz in (-.1525,.1525):box('Panel horizontal bead',(0,y,z+dz),(.67,.012,.016),paint,'Leaf',.002)
 # latch plate and knob on each face
 box('Brass escutcheon',(.345,ysign*.028,1.015),(.048,.010,.11),brass,'Leaf',.004)
 cyl('Knob stem',(.345,ysign*.045,1.015),.012,.028,brass,'Leaf',(math.pi/2,0,0))
 sphere('Door knob',(.345,ysign*.064,1.015),.025,brass,'Leaf')
 for z,w in ((.06,.018),(.41,.015),(1.28,.013),(1.92,.02)):
  box('Subtle worn corner',(.432,ysign*.023,z),(.003,.002,w),wood,'Leaf',.0004)
# Hinge barrels remain with moving leaf for export; frame hinge plates static.
for z in (.28,1.05,1.82):
 cyl('Hinge barrel',(-.45,-.035,z),.007,.075,brass,'Leaf')
 box('Hinge plate',(-.465,-.066,z),(.03,.006,.065),brass,'Frame',.001)
objs={}
for group,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='ARC_Door_'+group;objs[group]=o
 bpy.context.scene.cursor.location=((-0.45,0,0) if group=='Leaf' else (0,0,0));bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 loc=o.location.copy();o.location=(0,0,0)
 bpy.ops.export_scene.fbx(filepath=os.path.join(R,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
 o.location=loc
# studio setup
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(3.6,-5.5,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.9;sc.camera=cam
for loc,power,size in [((2,-4,5),350,4),((-3,-1,3.5),180,3),((0,3,4),220,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.rotation_euler=(Vector((0,0,1.1))-a.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=900;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
def render(n):sc.render.filepath=os.path.join(R,'previews',n+'.png');bpy.ops.render.render(write_still=True)
render('door-closed');objs['Leaf'].rotation_euler.z=math.radians(80);render('door-open');objs['Leaf'].rotation_euler.z=0
cam.location=(0,-6,1.1);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();render('door-front')
cam.location=(0,6,1.1);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();render('door-back')
cam.location=(6,0,1.1);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();render('door-side')
for img in bpy.data.images:
 if img.source=='FILE':img.pack()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'model','ARC-DOOR-01.blend'))
