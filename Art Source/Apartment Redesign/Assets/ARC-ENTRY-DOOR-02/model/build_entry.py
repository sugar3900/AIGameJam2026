import bpy, math, os
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.context.preferences.filepaths.save_version=0
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
walnut=mat('Aged walnut entrance leaf',(.28,.13,.07),rough=.82,img='walnut-aged.png')
wn=walnut.node_tree.nodes; walnut.node_tree.links.new(next(n for n in wn if n.type=='TEX_IMAGE').outputs['Color'],wn.get('Principled BSDF').inputs['Base Color'])
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
# 0.99m clear opening, 1.05m rough width, 2.14m rough head; two-sided trim with 0.12m partition depth
for x in (-.51,.51):
 box('Jamb', (x,0,1.055),(.03,.12,2.11),paint,'Frame')
 for y in (-.072,.072): box('Vertical casing',(x+(.03 if x>0 else -.03),y,1.055),(.09,.025,2.11),paint,'Frame',.002)
box('Top jamb',(0,0,2.125),(1.05,.12,.03),paint,'Frame')
for y in (-.072,.072):
 box('Head casing',(0,y,2.16),(1.17,.028,.075),paint,'Frame')
 box('Head crown',(0,y,2.208),(1.19,.038,.022),paint,'Frame')
# Solid walnut entrance leaf; applied raised mouldings on both faces, two tall and two low panels.
box('Solid entry door',(0,0,1.047),(.976,.05,2.094),walnut,'Leaf',.004)
for ysign in (-1,1):
 y=ysign*.030
 for z,h in ((.375,.45),(1.37,1.18)):
  for cx in (-.2075,.2075):
   for x in (cx-.1675,cx+.1675):box('Panel side bead',(x,ysign*.037,z),(.016,.009,h),walnut,'Leaf',.002)
   for dz in (-h/2,h/2):box('Panel horizontal bead',(cx,ysign*.037,z+dz),(.345,.009,.016),walnut,'Leaf',.002)
 box('Brass escutcheon',(.382,ysign*.034,1.00),(.048,.011,.13),brass,'Leaf',.004)
 cyl('Knob stem',(.382,ysign*.051,1.025),.012,.028,brass,'Leaf',(math.pi/2,0,0))
 sphere('Door knob',(.382,ysign*.069,1.025),.025,brass,'Leaf')
 cyl('Deadbolt escutcheon',(.382,ysign*.035,1.20),.023,.012,brass,'Leaf',(math.pi/2,0,0))
 cyl('Peephole',(.0,ysign*.033,1.57),.009,.010,brass,'Leaf',(math.pi/2,0,0))
 for z,w in ((.06,.018),(.41,.015),(1.28,.013),(1.92,.02)):
  box('Subtle worn corner',(.477,ysign*.028,z),(.003,.002,w),wood,'Leaf',.0004)
# Hinge barrels remain with moving leaf for export; frame hinge plates static.
for z in (.28,1.05,1.82):
 cyl('Hinge barrel',(-.495,-.035,z),.007,.075,brass,'Leaf')
 box('Hinge plate',(-.510,-.066,z),(.03,.006,.065),brass,'Frame',.001)
objs={}
for group,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='ARC_Entry_Door02_'+group;objs[group]=o
 bpy.context.scene.cursor.location=((-0.495,-.035,0) if group=='Leaf' else (0,0,0));bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 loc=o.location.copy();o.location=(0,0,0)

 # Convex collision pieces are pivot-local; no hull bridges the frame opening.
 hulls=[]
 specs=[((.495,.035,1.047),(.976,.05,2.094))] if group=='Leaf' else [((-.51,0,1.055),(.03,.12,2.11)),((.51,0,1.055),(.03,.12,2.11)),((0,0,2.125),(1.05,.12,.03))]
 bpy.ops.object.select_all(action='DESELECT')
 for i,(center,size) in enumerate(specs):
  bpy.ops.mesh.primitive_cube_add(size=1,location=center);co=bpy.context.object;co.name=f'UCX_{o.name}_{i:02}';co.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);co.hide_render=True;hulls.append(co)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 for co in hulls:co.select_set(True)
 bpy.ops.export_scene.fbx(filepath=os.path.join(R,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
 o.location=loc
 for co in hulls:co.hide_set(True)
# studio setup
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(3.6,-5.5,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.9;sc.camera=cam
for loc,power,size in [((2,-4,5),350,4),((-3,-1,3.5),180,3),((0,3,4),220,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.rotation_euler=(Vector((0,0,1.1))-a.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=900;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
def render(n):sc.render.filepath=os.path.join(R,'previews',n+'.png');bpy.ops.render.render(write_still=True)
render('entry-closed');objs['Leaf'].rotation_euler.z=math.radians(-80);render('entry-open');objs['Leaf'].rotation_euler.z=0
for img in bpy.data.images:
 if img.source=='FILE':img.pack()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'model','ARC-ENTRY-DOOR-02.blend'))
