"""Build BA-TOILET-01; metres, Z up, basin front -Y. Blender 5.2."""
import bpy, math, os
from mathutils import Vector
P=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

def material(name,color,rough=.6,metal=0,image=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 if image and os.path.isfile(image):
  tex=m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(image,check_existing=True)
  m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 return m
ivory=material('Painted_Ivory_Enamel',(.78,.66,.51),.4,image=os.path.join(P,'textures','porcelain-candidate-d.png'))
chrome=material('Aged_Brass',(.55,.32,.12),.36,.7); dark=material('Drain_Holes',(.07,.057,.043),.7)

def mesh(name, verts, faces, mat):
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); me.materials.append(mat)
 bpy.context.view_layer.objects.active=o; o.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)
 for poly in me.polygons: poly.use_smooth=True
 return o

def rings_mesh(name,rings,mat,n=64,rounded=False,caps=True):
 verts=[]
 for rx,ry,z in rings:
  for i in range(n):
   t=2*math.pi*i/n + math.pi/2; c,s=math.cos(t),math.sin(t)
   if rounded: c=math.copysign(abs(c)**.45,c); s=math.copysign(abs(s)**.45,s)
   verts.append((rx*c,ry*s,z))
 faces=[]
 for j in range(len(rings)-1):
  for i in range(n): a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 if caps:
  faces.append(tuple(reversed(range(n))));faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
 o=mesh(name,verts,faces,mat)
 # Continuous ring unwrap places the unavoidable seam at the rear (+Y).
 uv=o.data.uv_layers.active.data
 for k,poly in enumerate(o.data.polygons[:(len(rings)-1)*n]):
  j,i=divmod(k,n); coords=[(i/n,j/(len(rings)-1)),((i+1)/n,j/(len(rings)-1)),((i+1)/n,(j+1)/(len(rings)-1)),(i/n,(j+1)/(len(rings)-1))]
  for li,co in zip(poly.loop_indices,coords): uv[li].uv=co
 return o

def box(name,loc,dims,mat,bevel=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); mod=o.modifiers.new('edge softness','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);o.data.materials.append(mat);return o

def cyl(name,loc,radius,depth,mat,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def tube(name,points,radius,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=18;cu.bevel_depth=radius;cu.bevel_resolution=4
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for bp,co in zip(sp.bezier_points,points):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat); bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

# Vintage floor-mounted toilet, front -Y. Separate body and lid; bowl truly hollow.
body=[]
ped=rings_mesh('Pedestal and bowl base',[(.165,.195,.012),(.18,.21,.025),(.18,.21,.05),(.15,.17,.07),(.125,.145,.13),(.12,.14,.28),(.17,.205,.36),(.20,.24,.38)],ivory,rounded=False)
ped.location.y=-.055;body.append(ped)
# Side porcelain trap curves blend into the pedestal, adding vintage cast-ceramic contours.
for x in (-.115,.115):
 body.append(tube('Curved porcelain trap',[(x*.55,.105,.35),(x*1.30,.045,.29),(x*1.25,-.015,.21),(x*.50,-.04,.12)],.038,ivory))
bowl=rings_mesh('Hollow porcelain bowl',[(.16,.20,.31),(.22,.255,.345),(.255,.29,.40),(.255,.29,.45),(.245,.28,.465),(.205,.24,.466),(.195,.225,.45),(.18,.21,.405),(.145,.17,.345),(.095,.12,.315),(.045,.055,.305)],ivory,n=64)
bowl.location.y=-.075;body.append(bowl)
rim=rings_mesh('Rolled bowl rim',[(.24,.275,.444),(.255,.29,.45),(.258,.293,.461),(.25,.285,.47),(.218,.25,.47),(.198,.225,.463),(.195,.22,.45)],ivory,n=64,caps=False)
rim.location.y=-.075;body.append(rim)
# Ceramic seat ring is fixed to bowl; opens clear when the cover rotates.
seat=rings_mesh('Oval seat with opening',[(.225,.265,.468),(.235,.275,.475),(.235,.275,.488),(.225,.265,.495),(.17,.205,.495),(.16,.195,.487),(.16,.195,.475),(.17,.205,.468)],ivory,n=64,caps=False)
seat.location.y=-.075;body.append(seat)
# Decorative pedestal flange bolts and a thin base plate.
flange=rings_mesh('Rounded ceramic mounting flange',[(.16,.195,.008),(.18,.215,.015),(.18,.215,.035),(.165,.20,.045)],ivory,n=64); flange.location.y=-.055;body.append(flange)
for x in (-.12,.12):
 for y in (-.20,.09):body.append(sphere('Brass base bolt',(x,y,.049),(.012,.012,.007),chrome))
# Cistern: softly rounded body and lid, behind bowl.
tank=rings_mesh('Rounded cistern body',[(.19,.075,.495),(.205,.083,.505),(.214,.09,.53),(.22,.095,.56),(.22,.095,.845),(.214,.092,.88),(.20,.082,.89)],ivory,rounded=True);tank.location.y=.235;body.append(tank)
tank_lid=rings_mesh('Soft cistern lid',[(.218,.10,.875),(.237,.11,.885),(.24,.11,.90),(.225,.102,.916),(.20,.09,.921)],ivory,rounded=True);tank_lid.location.y=.235;body.append(tank_lid)
body.append(sphere('Cistern lid finial',(0,.235,.924),(.03,.025,.008),ivory))
body.append(box('Cistern neck',(0,.235,.48),(.18,.15,.09),ivory,.015))
# Brass left-side lever with pin and grip.
body.append(cyl('Flush lever base',(-.214,.20,.79),.022,.018,chrome));body[-1].rotation_euler[1]=math.pi/2
body.append(tube('Flush arm',[(-.225,.20,.79),(-.25,.20,.79),(-.30,.20,.79)],.008,chrome))
body.append(sphere('Flush handle',(-.306,.20,.79),(.014,.012,.012),chrome))
# Cover is a flattened ellipsoid shaped like an oval; pivot at rear horizontal X axis.
cover=sphere('Lid cover',(0,-.100,.506),(.228,.225,.024),ivory)
# Brass pivot hinge knuckles stay attached to the lid, anchored at rear.
lids=[cover]
for x in (-.135,.135):
 h=cyl('Hinge knuckle',(x,.125,.505),.015,.035,chrome,24); h.rotation_euler[1]=math.pi/2;lids.append(h)
# Reuse stable grouping/export setup with separate hinge origin.
def combine(name,objs,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
base=combine('BA_ToiletBody',body,(0,0,0));lid=combine('BA_ToiletLid',lids,(0,.125,.505));parts=[base,lid]
for obj in parts:
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=os.path.join(P,'model',obj.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,bake_space_transform=False)
# Preview, neutral but warmly lit, same camera for open and closed states.
bpy.context.scene.world.color=(.22,.18,.14)
bpy.ops.object.camera_add(location=(1.55,-2.2,1.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.49))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.48;bpy.context.scene.camera=cam
for loc,energy,size in [((1,-2,2.5),175,3),((-1,-.5,1.8),80,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.5))-l.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.view_settings.view_transform='AgX'
s.render.filepath=os.path.join(P,'previews','toilet-closed.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(P,'model','BA-TOILET-01.blend'));bpy.ops.render.render(write_still=True)
lid.rotation_euler.x=-math.radians(68);s.render.filepath=os.path.join(P,'previews','toilet-open.png');bpy.ops.render.render(write_still=True)
