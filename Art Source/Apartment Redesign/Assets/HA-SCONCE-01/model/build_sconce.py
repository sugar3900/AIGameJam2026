"""Hall sconce: metre units, wall plane Y=0, visible towards -Y, origin at plate centre."""
import bpy, math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,col,tex=None,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(root/'textures'/tex),check_existing=True);m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
brass=mat('AgedBrass',(.30,.20,.09),'aged-brass.png',.60,.54)
glass=mat('WarmOpalGlass',(.87,.79,.65),'opal-glass.png',0,.43)
bulbmat=mat('BulbIvory',(.92,.82,.68),None,0,.4)
hardware=[];shade=[];bulb=[]
def register(o,name,material,group):
 o.name=name;o.data.materials.append(material);group.append(o)
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def cyl(name,loc,r,depth,axis='Z',material=brass,group=hardware):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc);o=bpy.context.object
 if axis=='Y':o.rotation_euler.x=math.pi/2
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Rounded edge','BEVEL');mod.width=min(.0015,r*.15,depth*.18);mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return register(o,name,material,group)
def torus(name,loc,major,minor,axis='Z'):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=10,major_radius=major,minor_radius=minor,location=loc);o=bpy.context.object
 if axis=='Y':o.rotation_euler.x=math.pi/2
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return register(o,name,brass,hardware)
def sphere(name,loc,scale,material,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return register(o,name,material,group)
# Mounting plate with concentric rim, fasteners, and wall arm socket.
cyl('MountingPlate',(0,-.007,0),.042,.014,'Y');torus('PlateRim',(0,-.015,0),.038,.0022,'Y');cyl('ArmSocket',(0,-.022,.002),.014,.020,'Y')
for x in (-.026,.026):
 sphere('Fastener',(x,-.016,0),(.0035,.0017,.0035),brass,hardware)
# Curved gooseneck extends above the shade, down to its fitting.
curve=bpy.data.curves.new('GooseneckCurve','CURVE');curve.dimensions='3D';curve.resolution_u=24;curve.bevel_depth=.006;curve.bevel_resolution=4;sp=curve.splines.new('BEZIER');sp.bezier_points.add(3)
for bp,co in zip(sp.bezier_points,[(0,-.030,.005),(0,-.045,.112),(0,-.070,.159),(0,-.080,.096)]):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
o=bpy.data.objects.new('Gooseneck',curve);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);register(o,'Gooseneck',brass,hardware)
cyl('ShadeSocket',(0,-.080,.090),.018,.022);torus('SocketRim',(0,-.080,.079),.019,.0018)
for angle in (0,math.pi):
 x=.020*math.cos(angle);sphere('ShadeThumbscrew',(x,-.080,.088),(.004,.0035,.0035),brass,hardware)
# Bell glass: top radius .020 at z=.077, flares softly to .060 at z=-.005.
N=64;R=24;v=[];f=[]
for k in range(R+1):
 t=k/R;z=.077-.082*t;r=.020+.040*(t**1.75)+.002*math.sin(math.pi*t)
 for j in range(N):
  a=2*math.pi*j/N;v.append((r*math.cos(a),-.080+r*math.sin(a),z))
for k in range(R):
 for j in range(N):
  j2=(j+1)%N;f.append((k*N+j,k*N+j2,(k+1)*N+j2,(k+1)*N+j))
me=bpy.data.meshes.new('BellGlassMesh');me.from_pydata(v,[],f);me.update();uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 k=poly.index//N;j=poly.index%N
 for li,co in zip(poly.loop_indices,((j/N,k/R),((j+1)/N,k/R),((j+1)/N,(k+1)/R),(j/N,(k+1)/R))):uv.data[li].uv=co
ob=bpy.data.objects.new('OpalBell',me);bpy.context.collection.objects.link(ob);register(ob,'OpalBell',glass,shade)
bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=10,major_radius=.059,minor_radius=.002,location=(0,-.080,-.005));register(bpy.context.object,'GlassRolledLip',glass,shade)
sphere('Bulb',(0,-.080,.025),(.017,.017,.026),bulbmat,bulb)
# Join groups, preserve common wall plate origin to make assembly straightforward.
def combine(group,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[combine(hardware,'HA_Sconce_Hardware'),combine(shade,'HA_Sconce_Shade'),combine(bulb,'HA_Sconce_Bulb')]
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(root/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Preview wall, camera and nonexported lights.
wall=mat('Preview_Warm_Plaster',(.45,.37,.33),rough=.85)
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,.002,0),rotation=(math.pi/2,0,0));bpy.context.object.name='PreviewWall';bpy.context.object.data.materials.append(wall)
bpy.ops.object.camera_add(location=(.39,-.69,.24));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.07,.055))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.33;bpy.context.scene.camera=cam
for loc,power,size in [((.2,-.6,.65),18,.8),((-.55,-.35,.15),10,.6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,-.05,.04))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='POINT',location=(0,-.080,.012));light=bpy.context.object;light.data.color=(1,.45,.18);light.data.shadow_soft_size=.035
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.image_settings.file_format='PNG';sc.world.color=(.12,.12,.12);sc.view_settings.view_transform='AgX'
gbs=glass.node_tree.nodes.get('Principled BSDF');bbs=bulbmat.node_tree.nodes.get('Principled BSDF')
for bs in (gbs,bbs):bs.inputs['Emission Color'].default_value=(1,.42,.15,1)
for state in ('off','on'):
 light.data.energy=7 if state=='on' else 0;gbs.inputs['Emission Strength'].default_value=1.7 if state=='on' else 0;bbs.inputs['Emission Strength'].default_value=3 if state=='on' else 0
 sc.render.filepath=str(root/'previews'/('sconce-'+state+'.png'));bpy.ops.render.render(write_still=True)
light.data.energy=0;gbs.inputs['Emission Strength'].default_value=0;bbs.inputs['Emission Strength'].default_value=0
for img in bpy.data.images:
 if img.source=='FILE' and Path(img.filepath).name in ('aged-brass.png','opal-glass.png'):img.filepath='//../textures/'+Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'HA-SCONCE-01.blend'))
