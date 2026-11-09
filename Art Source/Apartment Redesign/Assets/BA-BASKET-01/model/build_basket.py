import bpy, math, random
from pathlib import Path
from mathutils import Vector
random.seed(7)
D=Path(__file__).resolve().parent.parent; M=D/'model'; T=D/'textures'; P=D/'previews'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,texture,tint=(1,1,1,1),rough=.85):
 m=bpy.data.materials.new(name);m.diffuse_color=tint;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough
 im=m.node_tree.nodes.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(str(T/texture),check_existing=True);im.image.filepath='//../textures/'+texture
 mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=tint
 m.node_tree.links.new(im.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color']);return m
w=mat('Wicker honey','wicker.png',(.90,.78,.64,1)); wd=mat('Wicker shadow','wicker.png',(.70,.57,.45,1)); cream=mat('Towel ivory','terry.png',(.98,.94,.85,1)); rose=mat('Towel rose','terry.png',(.73,.40,.40,1))

def curve(name,points,radius,material,cyclic=False,res=0):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=radius;c.bevel_resolution=res
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
basket=[]
# Nested courses undulate in and out at each stake, suggesting an over-under weave.
for j in range(15):
 z=.017+j*.0092; a=.197+.025*(z/.15);b=.143+.022*(z/.15)
 pts=[]
 for i in range(96):
  t=2*math.pi*i/96;wave=.0025*math.cos(36*t+j*math.pi)
  pts.append(((a+wave)*math.cos(t),(b+wave)*math.sin(t),z))
 basket.append(curve('Weft_%02d'%j,pts,.0037,w,True))
# Vertical structural stakes; little depth modulation produces woven rhythm.
for k in range(36):
 t=2*math.pi*k/36;pts=[]
 for j in range(31):
  z=.014+j*.0045;a=.197+.025*(z/.15);b=.143+.022*(z/.15);wave=.0027*math.cos(math.pi*(z-.017)/.0092+k*math.pi)
  pts.append(((a+wave)*math.cos(t),(b+wave)*math.sin(t),z))
 basket.append(curve('Stake_%02d'%k,pts,.0031,wd))
for z,rad in [(.150,.006),(.013,.005)]:
 a=.197+.025*(z/.15);b=.143+.022*(z/.15)
 basket.append(curve('Bound_rim',[(a*math.cos(2*math.pi*i/160),b*math.sin(2*math.pi*i/160),z) for i in range(160)],rad,w,True,2))
# low oval base surface
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=12,location=(0,0,.015));base=bpy.context.object;base.name='Woven_bottom';base.scale=(.198,.145,.014);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);base.data.materials.append(wd);basket.append(base)
# arched handles at the two ends; stay within 0.50m overall width
for side in [-1,1]:
 pts=[]
 for i in range(41):
  t=math.pi*i/40;pts.append((side*(.219+.008*math.sin(t)),.045*math.cos(t),.145+.075*math.sin(t)))
 basket.append(curve('Handle',pts,.0065,w,False,2))
# towels: soft rounded cylinders and embroidered spiral on the forward end
collections=[]
for idx,(x,y,z,ma) in enumerate([(-.125,.005,.165,cream),(0,.012,.173,cream),(.123,.008,.165,rose)]):
 group=[]
 verts=[]; faces=[]; n=48
 for yy,rx,rz in [(-.090,.054,.056),(-.087,.064,.066),(-.080,.068,.070),(.080,.068,.070),(.087,.064,.066),(.090,.054,.056)]:
  for k in range(n):
   t=2*math.pi*k/n; verts.append((x+rx*math.cos(t),y+yy,z+rz*math.sin(t)))
 for row in range(5):
  for k in range(n): faces.append((row*n+k,row*n+(k+1)%n,(row+1)*n+(k+1)%n,(row+1)*n+k))
 faces.append(tuple(reversed(range(n))));faces.append(tuple(5*n+k for k in range(n)))
 mesh=bpy.data.meshes.new('Towel_mesh');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('Rolled_towel_%d'%idx,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(ma);group.append(obj)
 # End cap as folded spiral on front, subtly raised, in a slightly darker cotton
 points=[]
 for j in range(81):
  t=5.3*math.pi*j/80;radius=.002+.0030*t
  points.append((x+radius*math.cos(t),y-.092,z+radius*math.sin(t)))
 group.append(curve('Rolled_edge_%d'%idx,points,.0022,ma,False,2))
 # cylindrical stitched bands around towel, spaced near ends
 for yy in [y-.06,y+.06]:
  pts=[(x+.067*math.cos(2*math.pi*i/48),yy,z+.070*math.sin(2*math.pi*i/48)) for i in range(48)]
  group.append(curve('Towel_hem_%d'%idx,pts,.0012,ma,True))
 collections.append(group)

def meshify(group,name):
 for o in group:
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  if o.type=='CURVE':bpy.ops.object.convert(target='MESH')
  o.select_set(False)
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 # smart unwrap creates a portable UV map for FBX, unlike procedural object coordinates
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.005);bpy.ops.object.mode_set(mode='OBJECT')
 for f in o.data.polygons:f.use_smooth=True
 return o
b=meshify(basket,'Basket');towels=[meshify(g,'Towel_%d'%i) for i,g in enumerate(collections)]
# Consistent floor-center export origin despite independently movable towels.
for o in [b]+towels:
 bpy.context.scene.cursor.location=(0,0,0);bpy.context.view_layer.objects.active=o;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def export(o,name):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(M/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='AUTO',add_leaf_bones=False)
export(b,'BA_Basket.fbx')
for i,o in enumerate(towels):export(o,'BA_Towel_%d.fbx'%i)
# render
world=bpy.context.scene.world;world.color=(.14,.14,.14)
bpy.ops.object.light_add(type='AREA',location=(1,-1.5,2.5));key=bpy.context.object;key.data.energy=220;key.data.shape='DISK';key.data.size=2
bpy.ops.object.light_add(type='AREA',location=(-1.5,.5,1.8));bpy.context.object.data.energy=140;bpy.context.object.data.size=2
bpy.ops.object.camera_add(location=(.85,-1.05,.72));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.11))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.73;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX';scene.render.filepath=str(P/'basket-perspective.png');bpy.ops.wm.save_as_mainfile(filepath=str(M/'BA-BASKET-01.blend'));bpy.ops.render.render(write_still=True)
