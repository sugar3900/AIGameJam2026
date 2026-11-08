"""Build the desk lamp in metres; exports share the table-plane origin."""
import bpy, math
from mathutils import Vector, Matrix
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name,color,tex=None,metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(root/'textures'/tex),check_existing=True);m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
brass=mat('Aged_brass',(.34,.26,.14),'brass.png',.65,.48)
sage=mat('Sage_enamel',(.39,.48,.36),'sage.png',.12,.64)
cream=mat('Ivory_inner_enamel',(.79,.75,.61),None,.05,.7)
cord=mat('Dark_woven_cord',(.085,.065,.050),None,0,.85)
bulbmat=mat('Warm_frosted_bulb',(.92,.83,.67),None,0,.42)
body=[];shade=[];bulbs=[]
def add(o,m,g): o.data.materials.append(m);g.append(o);return o
def finish(o):
 for p in o.data.polygons:p.use_smooth=True
 return o
def cyl(name,loc,r,depth,material,group,verts=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name
 b=o.modifiers.new('Soft edges','BEVEL');b.width=min(.002,r*.18,depth*.18);b.segments=3
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return add(finish(o),material,group)
def between(name,a,b,r,material,group):
 d=Vector(b)-Vector(a);o=cyl(name,(Vector(a)+Vector(b))/2,r,d.length,material,group,20);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def sphere(name,loc,scale,material,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return add(finish(o),material,group)
def torus(name,loc,R,r,material,group):
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=10,location=loc,major_radius=R,minor_radius=r);o=bpy.context.object;o.name=name;return add(finish(o),material,group)
# Weighted round foot and collar
cyl('Foot',(0,0,.011),.092,.022,brass,body);cyl('Sage_Base_Inset',(0,0,.026),.078,.012,sage,body);torus('Base_Rim',(0,0,.029),.078,.0025,brass,body)
cyl('SwitchCollar',(-.036,-.038,.036),.008,.009,brass,body);between('Switch',(-.036,-.038,.040),(-.042,-.038,.053),.0025,brass,body)
cyl('StemMount',(0,0,.055),.015,.05,brass,body)
a=(0,0,.077);b=(.058,0,.235);c=(.172,0,.312)
between('Lower_arm',a,b,.007,brass,body);between('Upper_arm',b,c,.007,brass,body)
for i,loc in enumerate((a,b,c)):
 sphere('Hinge',loc,(.014,.013,.014),brass,body)
 for side in (-1,1):
  n=cyl('HingeKnob',Vector(loc)+Vector((0,side*.016,0)),.010,.009,brass,body);n.rotation_euler.x=math.pi/2
# Socket and bulb separately controllable
between('SocketNeck',(.172,0,.312),(.190,0,.321),.009,brass,body)
cyl('Socket',(.192,0,.302),.018,.043,brass,body)
sphere('Bulb',(.192,0,.270),(.024,.024,.031),bulbmat,bulbs)
# A real hollow tapered enamel bell; outer/inner faces use separate materials.
N=64;v=[];f=[]
for z,r in ((.261,.088),(.342,.034),(.339,.031),(.264,.085)):
 for i in range(N):
  t=2*math.pi*i/N;v.append((.192+r*math.cos(t),r*math.sin(t),z))
for k in range(3):
 for i in range(N):
  j=(i+1)%N;f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
mesh=bpy.data.meshes.new('BellMesh');mesh.from_pydata(v,[],f);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
 i=p.index%N;k=p.index//N;p.material_index=1 if k==2 else 0;p.use_smooth=True
 for li,co in zip(p.loop_indices,((i/N,0),((i+1)/N,0),((i+1)/N,1),(i/N,1))): uv.data[li].uv=co
ob=bpy.data.objects.new('EnamelShade',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(sage);ob.data.materials.append(cream);shade.append(ob)
torus('Shade_Lip',(.192,0,.261),.0865,.0025,brass,shade)
cyl('VentedTop',(.192,0,.354),.033,.026,sage,shade)
cyl('TopCap',(.192,0,.370),.019,.007,brass,shade)
for i in range(8):
 t=i*math.tau/8
 between('Vent',(.192+.033*math.cos(t),.033*math.sin(t),.346),(.192+.033*math.cos(t),.033*math.sin(t),.361),.0018,cord,shade)
# Tilt the shade as a unit toward the working surface.
pivot=Vector((.172,0,.312)); rot=Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(-22),4,'Y') @ Matrix.Translation(-pivot)
for ob in shade+bulbs: ob.matrix_world=rot @ ob.matrix_world
# Cloth power lead, curved along the table surface.
wire=[(-.075,.035,.018),(-.105,.054,.008),(-.15,.063,.005),(-.19,.053,.005),(-.225,.041,.005)]
for i in range(len(wire)-1): between('CordSegment',wire[i],wire[i+1],.0025,cord,body)
for p in wire[1:-1]: sphere('CordJoin',p,(.0025,)*3,cord,body)
def combine(objs,name):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objs: ob.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[combine(body,'OF_DeskLamp_Body'),combine(shade,'OF_DeskLamp_Shade'),combine(bulbs,'OF_DeskLamp_Bulb')]
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Preview only, not in FBX.
bpy.ops.mesh.primitive_plane_add(size=4,location=(0,0,-.003));bpy.context.object.data.materials.append(mat('Preview_table',(.22,.14,.09),None,0,.82))
bpy.ops.object.camera_add(location=(.90,-1.45,.83));cam=bpy.context.object;cam.rotation_euler=(Vector((.01,0,.19))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.69;bpy.context.scene.camera=cam
for loc,power,size in [((.2,-.7,1.3),18,1.4),((-.8,.4,.9),8,1.0)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size
bpy.ops.object.light_add(type='POINT',location=(.192,0,.262));light=bpy.context.object;light.data.color=(1,.55,.23);light.data.shadow_soft_size=.04
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False;sc.world.color=(.12,.12,.12);sc.view_settings.view_transform='AgX'
p=bulbmat.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.51,.18,1)
for state in ('off','on'):
 light.data.energy=6 if state=='on' else 0;p.inputs['Emission Strength'].default_value=3 if state=='on' else 0
 sc.render.filepath=str(root/'previews'/('lamp-'+state+'.png'));bpy.ops.render.render(write_still=True)
light.data.energy=0;p.inputs['Emission Strength'].default_value=0
for img in bpy.data.images:
 if img.source=='FILE' and Path(img.filepath).name in ('brass.png','sage.png'):img.filepath='//../textures/'+Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'OF-DESK-LAMP-01.blend'))
