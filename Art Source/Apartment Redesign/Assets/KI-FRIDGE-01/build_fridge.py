"""Build KI-FRIDGE-01. Run Blender --background --python build_fridge.py.
Metres, Z up, front -Y; left/front hinge. Body at floor origin, door at hinge."""
import bpy, math, os
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__))
for d in ('models','textures','previews'): os.makedirs(os.path.join(R,d),exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name, color, rough=.6, metal=0, image=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if image:
  img=bpy.data.images.load(os.path.join(R,'textures',image),check_existing=True);img.pack()
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=img
  m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
ivory=material('Painted_Ivory_Enamel',(.82,.72,.54),.72,0,'ivory-enamel-v2.png')
inner=material('Porcelain_Interior',(.74,.68,.55),.68,0,'ivory-enamel-v2.png')
age=material('Painted_Edge_Patina',(.49,.31,.16),.86)
chrome=material('Aged_Chrome',(.62,.59,.52),.38,.55)
seal=material('Rubber_Gasket',(.36,.34,.30),.86)
shadow=material('Drawer_Recess',(.48,.43,.34),.8)
groups={'body':[],'door':[]}
def add(o,group,mat):
 o.data.materials.append(mat);groups[group].append(o);return o
def box(name, loc, dim, mat, group, bevel=.006):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  # Never exceed half-thickness: avoids degenerate bevel faces.
  b=o.modifiers.new('Rounded enamel edges','BEVEL');b.width=min(bevel,min(dim)*.35);b.segments=4
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return add(o,group,mat)
def cyl(name,loc,r,depth,mat,group,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name
 return add(o,group,mat)
def bar(name,a,b,r,mat,group):
 a,b=Vector(a),Vector(b);d=b-a;o=cyl(name,(a+b)*.5,r,d.length,mat,group);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
# A rounded rectangular hollow cabinet shell with real wall thickness. Its
# large XZ corner radii are independent of the wall's thickness.
def cabinet_shell():
 def outline(hx,lo,hi,r):
  pts=[]
  for cx,cz,a in [(hx-r,hi-r,0),(-hx+r,hi-r,90),(-hx+r,lo+r,180),(hx-r,lo+r,270)]:
   for i in range(13):
    t=math.radians(a+90*i/12);pts.append((cx+r*math.cos(t),cz+r*math.sin(t)))
  return pts
 outer=outline(.375,.095,1.68,.115);inside=outline(.304,.19,1.58,.073);n=len(outer)
 verts=[(x,y,z) for pts,y in [(outer,-.275),(outer,.345),(inside,-.275),(inside,.30)] for x,z in pts]
 faces=[]
 for a,b in [(0,1),(2,3),(0,2),(1,3)]:
  for i in range(n):faces.append((a*n+i,a*n+(i+1)%n,b*n+(i+1)%n,b*n+i))
 mesh=bpy.data.meshes.new('Rounded hollow cabinet');mesh.from_pydata(verts,[],faces);mesh.update()
 import bmesh
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 for face in mesh.polygons: face.use_smooth=face.index<2*n
 obj=bpy.data.objects.new('Rounded hollow cabinet',mesh);bpy.context.collection.objects.link(obj);add(obj,'body',ivory)
 # A narrow bevel gives the molded edge soft highlights without inflated geometry.
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 mod=obj.modifiers.new('Rolled enamel rim','BEVEL');mod.width=.007;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
cabinet_shell()
box('Back wall',(0,.315,.89),(.60,.03,1.38),inner,'body',.009)
box('Cavity floor',(0,.035,.19),(.60,.55,.04),inner,'body',.012)
box('Metal plinth',(0,.02,.045),(.72,.64,.075),chrome,'body',.013)
box('Plinth apron',(0,-.31,.048),(.63,.018,.038),inner,'body',.005)
# Inner lining, shelf supports and genuine open wire racks.
box('Interior rear lining',(0,.278,.86),(.60,.012,1.37),inner,'body',.003)
for x in [-.297,.297]:
 box('Interior side lining',(x,.035,.88),(.012,.52,1.38),inner,'body',.003)
 for z in [.49,.73,.97,1.20]: box('Shelf ledge',(x-(.015 if x>0 else -.015),.03,z),(.028,.47,.018),inner,'body',.005)
for z in [.53,.79,1.05]:
 for x in [i*.065 for i in range(-4,5)]:bar('Shelf wire',(x,-.20,z),(x,.23,z),.004,chrome,'body')
 for y in [-.20,.02,.23]:bar('Shelf rail',(-.27,y,z),(.27,y,z),.005,chrome,'body')
# Freezer box: inset face and chrome pull.
box('Ice box surround',(0,.08,1.37),(.53,.39,.24),inner,'body',.022)
box('Ice box panel',(0,-.127,1.37),(.46,.025,.18),ivory,'body',.008)
box('Ice box handle',(.14,-.151,1.37),(.09,.018,.018),chrome,'body',.005)
# Vegetable bin in cavity, inset panel and ridges.
box('Crisper tub',(0,.035,.30),(.54,.44,.19),inner,'body',.015)
box('Crisper front',(0,-.198,.30),(.50,.020,.16),ivory,'body',.006)
for x in [-.20,-.14,-.08,-.02,.04,.10,.16,.22]:box('Crisper rib',(x,-.211,.30),(.009,.008,.11),inner,'body',.002)
box('Crisper pull',(0,-.222,.34),(.13,.018,.014),chrome,'body',.004)
# Rounded door slab, front enamel; inside edge seals and three door bins.
def rounded_door():
 # Rounded rectangle in the XZ plane, extruded through Y. Unlike a box bevel,
 # corner radius is independent of sheet thickness.
 hx=.36; lo=.14; hi=1.65; radius=.095; points=[]
 for cx,cz,a in [(hx-radius,hi-radius,0),(-hx+radius,hi-radius,90),(-hx+radius,lo+radius,180),(hx-radius,lo+radius,270)]:
  for i in range(13):
   t=math.radians(a+90*i/12); points.append((cx+radius*math.cos(t),cz+radius*math.sin(t)))
 n=len(points); verts=[(x,y,z) for y in [-.35,-.28] for x,z in points]
 faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
 faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
 mesh=bpy.data.meshes.new('Rounded door panel'); mesh.from_pydata(verts,[],faces);mesh.update()
 import bmesh
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 
 for face in mesh.polygons: face.use_smooth=face.index>=2
 obj=bpy.data.objects.new('Rounded door',mesh);bpy.context.collection.objects.link(obj);add(obj,'door',ivory)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 mod=obj.modifiers.new('Soft rolled edge','BEVEL');mod.width=.009;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
rounded_door()
# Flat, sparse irregular color marks at working edges: these are painted color,
# not protruding flakes or simulated paint buildup.
import random
rng=random.Random(26)
for i in range(22):
 x=rng.choice([rng.uniform(-.33,-.305),rng.uniform(.305,.33)])
 z=rng.uniform(.24,1.57);w=rng.uniform(.002,.006);h=rng.uniform(.007,.022)
 mesh=bpy.data.meshes.new('Edge wear mark');mesh.from_pydata([(x,-.3505,z),(x+w,-.3505,z+h*.3),(x+w*.65,-.3505,z+h),(x-w*.35,-.3505,z+h*.72)],[],[(0,1,2,3)]);mesh.update()
 o=bpy.data.objects.new('Painted wear mark',mesh);bpy.context.collection.objects.link(o);add(o,'door',age)
box('Inner door panel',(0,-.271,.895),(.63,.025,1.39),inner,'door',.008)
for x in [-.32,.32]:box('Vertical gasket',(x,-.253,.895),(.018,.014,1.39),seal,'door',.004)
for z in [.205,1.585]:box('Horizontal gasket',(0,-.253,z),(.64,.014,.018),seal,'door',.004)
for z in [.48,.83,1.19]:
 box('Door shelf base',(0,-.205,z),(.54,.13,.025),inner,'door',.006)
 box('Door shelf lip',(0,-.137,z+.072),(.54,.018,.15),ivory,'door',.006)
 for x in [-.26,.26]:box('Door shelf end',(x,-.205,z+.072),(.018,.13,.15),inner,'door',.006)
 bar('Shelf chrome trim',(-.25,-.149,z+.14),(.25,-.149,z+.14),.004,chrome,'door')
# External hinges on viewer-left, chrome vintage horizontal lever on right.
for z in [.36,1.42]:
 cyl('Hinge pin',(-.38,-.335,z),.012,.16,chrome,'body')
 for offset in [-.052,0,.052]: cyl('Hinge barrel',(-.38,-.335,z+offset),.017,.045,chrome,'body')
 box('Hinge body plate',(-.384,-.31,z),(.020,.035,.145),chrome,'body',.004)
 box('Hinge door plate',(-.345,-.356,z),(.032,.015,.14),chrome,'door',.004)
 for dz in [-.045,.045]:cyl('Hinge screw',(-.345,-.366,z+dz),.004,.005,shadow,'door',(math.pi/2,0,0))
box('Handle escutcheon',(.235,-.358,1.10),(.075,.022,.07),chrome,'door',.007)
box('Handle bar',(.185,-.386,1.10),(.24,.035,.035),chrome,'door',.011)
for x in [.075,.29]:box('Handle standoff',(x,-.371,1.10),(.025,.035,.027),chrome,'door',.007)
# Iconic small emblem.
cyl('Oval badge',(.0,-.359,1.44),.035,.008,chrome,'door',(math.pi/2,0,0))
box('Badge wing',(0,-.364,1.44),(.20,.008,.008),chrome,'door',.002)
# Transform and unwrap per component; retain painted material UVs in FBX.
for objects in groups.values():
 for obj in objects:
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
# Join and export independently. Door origin is physical hinge axis.
joined={}
for name,objs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for obj in objs:obj.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();obj=bpy.context.object;obj.name='KI_FRIDGE_'+name.upper()
 bpy.context.scene.cursor.location= (0,0,0) if name=='body' else (-.38,-.335,0)
 bpy.ops.object.origin_set(type='ORIGIN_CURSOR');joined[name]=obj
 bpy.ops.export_scene.fbx(filepath=os.path.join(R,'models',obj.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
# Render closed and open at identical camera. Negative Z rotation swings left leaf outward.
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(3,-5,2.8));camera=bpy.context.object
camera.rotation_euler=(Vector((-.08,0,.84))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=2.45;bpy.context.scene.camera=camera
for loc,power,size in [((3,-4,5),520,4),((-3,-2,3.4),320,3.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=(1,.87,.72);o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.world.color=(.21,.19,.17);s.render.resolution_x=1152;s.render.resolution_y=1152;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.film_transparent=True
s.render.filepath=os.path.join(R,'previews','fridge-closed.png');bpy.ops.render.render(write_still=True)
joined['door'].rotation_euler.z=-math.radians(105);s.render.filepath=os.path.join(R,'previews','fridge-open.png');bpy.ops.render.render(write_still=True)
joined['door'].rotation_euler.z=0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'models','KI-FRIDGE-01.blend'))
