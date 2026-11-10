"""FIX-029. Additive closet pull-chain pendant, metres, floor origin below ceiling mount.
One CPU Blender process; no engine files or original closet kit writes.
"""
from pathlib import Path
import bpy,bmesh,math,json
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
G={k:[] for k in ('Hardware','Glass','Filament','Chain')}
def mat(name,c,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
brass=mat('Closet_AgedBrass',(.17,.105,.046),.75,.40)
edge=mat('Closet_BrassEdge',(.31,.20,.085),.72,.36)
cord=mat('Closet_BraidedCord',(.022,.017,.012),0,.85)
insulator=mat('Closet_Ceramic',(.50,.43,.31),0,.60)
glass=mat('Closet_ClearAmberGlass',(.94,.86,.70),0,.16)
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46
filament=mat('Closet_Filament',(.25,.08,.012),.1,.5)
p=filament.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.36,.075,1);p.inputs['Emission Strength'].default_value=6
wire=mat('Closet_SupportWire',(.09,.075,.055),.7,.48)
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def reg(o,name,m,g):
 o.name=name;o.data.materials.append(m);G[g].append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o

def lathe(name,profile,m,g,n=48):
 verts=[];rings=[];faces=[]
 for z,r in profile:
  ids=[]
  for i in range(n if r else 1):
   ids.append(len(verts));a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
  rings.append(ids)
 for a,b in zip(rings,rings[1:]+rings[:1]):
  if len(a)==len(b)==1:continue
  for i in range(n):
   j=(i+1)%n
   if len(a)==1:faces.append((a[0],b[j],b[i]))
   elif len(b)==1:faces.append((a[i],a[j],b[0]))
   else:faces.append((a[i],a[j],b[j],b[i]))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return reg(o,name,m,g)

def sphere(name,loc,r,m,g,seg=12,rings=8,scale=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=r,location=loc);o=bpy.context.object
 if scale:o.scale=scale
 return reg(o,name,m,g)

def tube(name,points,r,m,g,smooth=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;cu.resolution_u=16;cu.use_fill_caps=True
 sp=cu.splines.new('BEZIER' if smooth else 'POLY')
 if smooth:
  sp.bezier_points.add(len(points)-1)
  for p,c in zip(sp.bezier_points,points):p.co=c;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 else:
  sp.points.add(len(points)-1)
  for p,c in zip(sp.points,points):p.co=(*c,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);activate(o);bpy.ops.object.convert(target='MESH');return reg(o,name,m,g)

def torus(name,loc,major,minor,m,g):
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,major_radius=major,minor_radius=minor,location=loc);return reg(bpy.context.object,name,m,g)

# Ceiling rosette top touches existing 2.75 m ceiling. Short taper, no floating cable.
lathe('Stepped ceiling rose',[(2.75,0),(2.75,.052),(2.743,.054),(2.737,.050),(2.731,.034),(2.725,.015),(2.72,.011),(2.72,0)],brass,'Hardware')
torus('Rose rolled rim',(0,0,2.743),.051,.0015,edge,'Hardware')
for x in (-.038,.038):sphere('Rose screw',(x,0,2.735),.003,edge,'Hardware',scale=(1,1,.45))
# Two fine twisted strands, mesh export retains the braided silhouette.
for phase in (0,math.pi):
 pts=[]
 for i in range(161):
  z=2.72-(2.72-2.674)*i/160;a=phase+i/160*math.tau*13
  pts.append((.0015*math.cos(a),.0015*math.sin(a),z))
 tube('Twisted fabric cable',pts,.0019,cord,'Hardware')
lathe('Cable strain relief',[(2.68,0),(2.68,.006),(2.667,.0075),(2.66,.008),(2.66,0)],brass,'Hardware')
lathe('Socket cap',[(2.668,0),(2.668,.009),(2.659,.013),(2.652,.022),(2.646,.026),(2.64,.026),(2.64,0)],brass,'Hardware')
lathe('Socket barrel',[(2.647,0),(2.647,.024),(2.642,.025),(2.602,.025),(2.593,.0235),(2.59,.022),(2.59,.018),(2.599,.018),(2.599,0)],brass,'Hardware')
for z in (2.643,2.601,2.593):torus('Socket collar bead',(0,0,z),.024,.0013,edge,'Hardware')
# Fine vertical grip flutes on the retaining ring.
for i in range(36):
 a=i*math.tau/36;x=.0257*math.cos(a);y=.0257*math.sin(a)
 tube('Ring knurl',[(x,y,2.638),(x,y,2.647)],.00065,edge,'Hardware')
lathe('Recessed bulb holder',[(2.601,0),(2.601,.0183),(2.587,.0183),(2.585,.0155),(2.585,0)],insulator,'Hardware')
# Side-mounted chain guide exits clear of glass envelope.
tube('Pull switch side spigot',[(.018,-.012,2.642),(.030,-.028,2.642),(.040,-.060,2.64),(.040,-.060,2.622)],.0055,brass,'Hardware',True)
sphere('Guide ferrule',(.040,-.060,2.624),.0059,edge,'Hardware')
# Closed 0.8 mm glass shell, rounded teardrop. Top is hidden in socket holder.
outer=[(2.596,.014),(2.584,.014),(2.574,.017),(2.555,.024),(2.53,.0315),(2.508,.035),(2.489,.033),(2.473,.024),(2.464,.012),(2.46,0)]
inner=[(2.4608,0),(2.4648,.0115),(2.4738,.0233),(2.489,.0322),(2.508,.0342),(2.53,.0307),(2.555,.0232),(2.574,.0162),(2.584,.0132),(2.596,.0132)]
lathe('Amber glass envelope',outer+inner,glass,'Glass',64)
# Dark support conductors and three bent filament loops. Separate emissive mesh for exact off state.
tube('Central glass stem',[(0,0,2.592),(0,0,2.495)],.0028,glass,'Glass')
for k in range(3):
 a=k*math.tau/3
 def xy(r,t,z):return (r*math.cos(t),r*math.sin(t),z)
 tube('Filament hairpin',[xy(.010,a-.13,2.574),xy(.015,a-.13,2.501),xy(.015,a,2.484),xy(.015,a+.13,2.501),xy(.010,a+.13,2.574)],.00055,filament,'Filament',True)
 for da in (-.13,.13):tube('Stem lead',[(0,0,2.591),xy(.010,a+da,2.574)],.00055,wire,'Hardware')
# Straight ball chain is seated 23 mm into guide; 15 mm pull retains contact.
pts=[(.040,-.060,2.645),(.040,-.060,2.042)]
tube('Ball chain connector',pts,.00065,brass,'Chain')
a,b=Vector(pts[0]),Vector(pts[1]);n=round((b-a).length/.0045)
for i in range(n):sphere('Ball chain bead',a.lerp(b,i/n),.00165,edge,'Chain',8,6)
tube('Pull finial neck',[(.040,-.060,2.047),(.040,-.060,2.035)],.0027,brass,'Chain')
sphere('Weighted brass pull',(.040,-.060,2.027075),.0105,brass,'Chain',24,12,scale=(1,1,1.15))
torus('Pull finial belt',(.040,-.060,2.027075),.010,.001,edge,'Chain')

exports={}
for group,objects in G.items():
 for o in objects:
  activate(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='BR_ClosetLight01_'+group
 s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');activate(o)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.005);bpy.ops.object.mode_set(mode='OBJECT')
 # Triangulate for stable counts and import.
 mod=o.modifiers.new('Export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
 exports[group]=o
# Query-only optional convex bounds for easy chain clicking; never pawn-blocking.
coll=[]
for name,loc,dim in [('00',(.040,-.060,2.331),(.026,.026,.632))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='UCX_BR_ClosetLight01_Chain_'+name;o.dimensions=dim;activate(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');coll.append(o)

records=[]
for group,o in exports.items():
 activate(o)
 selected=[o]+(coll if group=='Chain' else [])
 pivot=Vector((.040,-.060,2.645) if group=='Chain' else (0,0,2.75))
 for ob in selected:
  ob.select_set(True)
  for v in ob.data.vertices:v.co-=pivot
 bpy.ops.export_scene.fbx(filepath=str(R/'models'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,path_mode='AUTO')
 for ob in selected:
  for v in ob.data.vertices:v.co+=pivot
 coords=[o.matrix_world@v.co for v in o.data.vertices]
 records.append({'mesh':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.polygons),'min':[min(c[k] for c in coords) for k in range(3)],'max':[max(c[k] for c in coords) for k in range(3)],'slots':[m.name for m in o.data.materials],'file_pivot_m':list(pivot)})
for c in coll:c.hide_render=True;c.hide_set(True)
(R/'geometry.json').write_text(json.dumps(records,indent=2)+'\n')
# Studio evidence only; no lights/camera/backdrop exported.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=1
s.render.resolution_x=720;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('Studio world');s.world.color=(.08,.08,.08);s.view_settings.view_transform='AgX'
def area(name,loc,power,size,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(.4,-.4,2.8),12,.45,(0,0,2.55));area('Rim',(-.25,.2,2.8),18,.3,(0,0,2.55))
bg=mat('Preview neutral',(.045,.04,.034),0,.9)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,.16,2.3),rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.materials.append(bg)
d=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO'
def shot(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;s.render.filepath=str(R/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
shot('assembly',(.45,-1.2,2.7),(0,0,2.385),.87)
shot('socket-chain',(.32,-.85,2.7),(.01,0,2.555),.32)
p=filament.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Strength'].default_value=0
shot('off',(.45,-1.2,2.7),(0,0,2.385),.87)
p.inputs['Emission Strength'].default_value=6
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/BR-CLOSET-LIGHT-01.blend'))
print('FIX029 BUILD COMPLETE')
