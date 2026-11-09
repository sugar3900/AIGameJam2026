import bpy, os, math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for name in ('model','textures','previews'): os.makedirs(os.path.join(ROOT,name),exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
parts={}
def tex(name,file):
 m=bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes; p=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(os.path.join(ROOT,'textures',file),check_existing=True);t.image.pack()
 
 if name=='Cabinet_Sage':
  hsv=n.new('ShaderNodeHueSaturation');hsv.inputs['Value'].default_value=.75;m.node_tree.links.new(t.outputs['Color'],hsv.inputs['Color']);m.node_tree.links.new(hsv.outputs['Color'],p.inputs['Base Color'])
 else:m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 p.inputs['Roughness'].default_value=.78; return m
def simple(name,col,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
sage=tex('Cabinet_Sage','sage-D.png'); ivory=tex('Counter_Ivory','ivory-enamel.png'); wood=tex('Interior_Wood','interior-wood.png'); dark=tex('Toe_Dark','toe-dark.png'); brass=simple('Aged_Brass',(.48,.29,.09),.7,.33); patina=simple('Muted_Edge_Wear',(.38,.29,.13),0,.8)
def add(o,group,material):
 o.data.materials.append(material);parts.setdefault(group,[]).append(o);return o
def box(name,loc,size,mat,group,bevel=.004):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Rounded', 'BEVEL');mod.width=min(bevel,min(size)*.22);mod.segments=3
  o.modifiers.new('Normals','WEIGHTED_NORMAL');bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 return add(o,group,mat)
def cyl(name,loc,r,depth,mat,group,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rotation);o=bpy.context.object;o.name=name;return add(o,group,mat)
def bar(name,a,b,r,mat,group):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,mat,group);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def curve(name,pts,r,mat,group):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=24;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for pt,co in zip(sp.bezier_points,pts): pt.co=co;pt.handle_left_type='AUTO';pt.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');return add(ob,group,mat)
# Overall 0.65 × 0.65 m; Z up, front faces -Y. White enamel countertop is at 0.90 m.
for side in (-1,1):box('Side',(.302*side,.015,.445),(.036,.60,.77),sage,'body')
box('Back',(0,.30,.445),(.57,.03,.77),wood,'body')
box('Lower shelf',(0,.015,.155),(.57,.55,.035),wood,'body')
box('Interior shelf',(0,.015,.40),(.57,.55,.025),wood,'body')
box('Drawer support',(0,.015,.66),(.57,.55,.025),wood,'body')
box('Toe kick',(0,-.012,.055),(.65,.60,.11),dark,'body',.006)
box('Counter',(0,-.005,.875),(.65,.65,.05),ivory,'body',.01)
box('Short rear upstand',(0,.285,.915),(.65,.05,.08),ivory,'body',.01)
for x in (-.292,.292):box('Front stile',(x,-.306,.47),(.028,.025,.75),sage,'body')
box('Divider rail behind front seam',(0,-.302,.652),(.55,.025,.020),sage,'body',.002)
# Front door: separate group, pivot along left edge of the front opening.
box('Door panel',(0,-.326,.383),(.55,.035,.515),sage,'door',.007)
for x in (-.224,.224):box('Door stile',(x,-.349,.383),(.028,.014,.442),sage,'door',.002)
for z in (.170,.596):box('Door rail',(0,-.345,z),(.43,.014,.028),sage,'door',.002)
curve('Door handle',[(.195,-.353,.47),(.20,-.376,.45),(.20,-.376,.35),(.195,-.353,.33)],.008,brass,'door')
for z in (.23,.52):
 cyl('Door hinge barrel',(-.283,-.339,z),.011,.065,brass,'door')
 box('Door hinge leaf',(-.27,-.343,z),(.025,.01,.047),brass,'door',.002)
# Tiny flush wear accents: visible color only, no exaggerated relief.
for x,z,w in [(-.20,.164,.05),(.07,.164,.04),(-.18,.603,.035),(.17,.603,.025)]:box('Edge wear',(x,-.357,z),(w,.0008,.0025),patina,'door',0)
# Fully enclosed drawer cavity with separate pull-out drawer.
box('Drawer front',(0,-.329,.755),(.55,.035,.18),sage,'drawer',.006)
box('Drawer bottom',(0,-.01,.698),(.49,.50,.022),wood,'drawer')
for x in (-.235,.235):box('Drawer side',(x,-.01,.758),(.02,.50,.12),wood,'drawer',.003)
box('Drawer back',(0,.23,.758),(.47,.02,.12),wood,'drawer',.003)
curve('Drawer pull',[(-.105,-.354,.765),(-.085,-.377,.75),(.085,-.377,.75),(.105,-.354,.765)],.008,brass,'drawer')
for x in (-.105,.105):cyl('Pull mount',(x,-.348,.765),.017,.008,brass,'drawer',(math.pi/2,0,0))
# UV-project individual pieces so each uses the complete painted albedo.
for group,objs in parts.items():
 for o in objs:
  if o.type!='MESH':continue
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
# Join each animation group, with origin at hinge for the door, common assembly floor for body and drawer.
joined={};pivots={'body':(0,0,0),'door':(-.283,-.326,0),'drawer':(0,0,0)}
for group,objs in parts.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_Cabinet_'+group;joined[group]=o
 bpy.context.scene.cursor.location=pivots[group];bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'model',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
# Warm directional presentation, camera looks at the front and right side.
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(2.3,-3.3,2.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.48))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.85;sc.camera=cam
for name,loc,power,size in [('Key',(1,-3,3.5),270,4),('Fill',(-2,-2,2.2),100,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.45))-o.location).to_track_quat('-Z','Y').to_euler()
sc.world.color=(.22,.20,.17);sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True
sc.render.filepath=os.path.join(ROOT,'previews','cabinet-closed.png');bpy.ops.render.render(write_still=True)
joined['door'].rotation_euler.z=math.radians(-100);joined['drawer'].location.y-=.30
sc.render.filepath=os.path.join(ROOT,'previews','cabinet-open.png');bpy.ops.render.render(write_still=True)
joined['door'].rotation_euler.z=0;joined['drawer'].location.y+=.30
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','KI-CABINET-01.blend'))
