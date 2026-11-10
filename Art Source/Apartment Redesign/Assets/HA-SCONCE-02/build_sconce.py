"""FIX008 source audit + corrected opaque opal fixture. Metres, plate center origin.
Read old01 only; write new02 only. Headless Blender -b -t 2 --python build_sconce.py.
"""
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'HA-SCONCE-01/model/HA-SCONCE-01.blend'
def components(me):
 adj=[[] for _ in me.vertices]
 for e in me.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();out=[]
 for i in range(len(adj)):
  if i in seen:continue
  q=[i];seen.add(i);c=[]
  while q:
   a=q.pop();c.append(a)
   for b in adj[a]:
    if b not in seen:seen.add(b);q.append(b)
  out.append(c)
 return out
def bvh(o,faceids=None):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons if faceids is None or p.index in faceids])
def bounds(o):
 v=[o.matrix_world@x.co for x in o.data.vertices];return {'min':[min(x[k] for x in v) for k in range(3)],'max':[max(x[k] for x in v) for k in range(3)]}
bpy.ops.wm.open_mainfile(filepath=str(OLD))
oldshade=bpy.data.objects['HA_Sconce_Shade'];oldhardware=bpy.data.objects['HA_Sconce_Hardware'];oldbulb=bpy.data.objects['HA_Sconce_Bulb']
shellcomp=max(components(oldshade.data),key=len);shellset=set(shellcomp);shellfaces={p.index for p in oldshade.data.polygons if set(p.vertices)<=shellset}
dot=[]
for p in oldshade.data.polygons:
 if p.index in shellfaces:
  c=p.center;rad=Vector((c.x,c.y+.080,0)).normalized();dot.append(p.normal.dot(rad))
bm=bmesh.new();bm.from_mesh(oldshade.data);boundary=sum(e.is_boundary for e in bm.edges);bm.free()
overlap=bvh(oldhardware).overlap(bvh(oldshade,shellfaces))
crossfaces={a for a,b in overlap};crossrange=[]
for ids in components(oldhardware.data):
 s=set(ids);polys=[p for p in oldhardware.data.polygons if set(p.vertices)<=s]
 hits=[p for p in polys if p.index in crossfaces]
 if hits:
  verts=[oldhardware.matrix_world@oldhardware.data.vertices[i].co for p in hits for i in p.vertices];crossrange.append({'component_vertices':len(ids),'crossing_faces':len(hits),'z_range':[min(v.z for v in verts),max(v.z for v in verts)],'y_range':[min(v.y for v in verts),max(v.y for v in verts)]})
audit={'source_blend_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'old_shell_radial_normal_dot_mean':sum(dot)/len(dot),'old_open_boundary_edges':boundary,'old_hardware_shell_triangle_intersections':len(overlap),'old_crossing_components':crossrange,'old_bulb_max_z':bounds(oldbulb)['max'][2],'old_socket_bottom_z':.079,'old_bulb_socket_unsupported_gap_m':.079-bounds(oldbulb)['max'][2]}
(ROOT/'source-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def material(name,color,tex=None,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/tex),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
brass=material('HA_Sconce02_AgedBrass',(.30,.20,.09),'aged-brass.png',.60,.54)
opal=material('HA_Sconce02_OpalOpaque',(.87,.79,.65),'opal-glass.png',0,.43)
bulbmat=material('HA_Sconce02_BulbIvory',(.92,.82,.68),None,0,.4)
ceramic=material('HA_Sconce02_PorcelainHolder',(.74,.69,.58),None,0,.57)
hardware=[];shade=[];bulbs=[]
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def add(o,name,mat,group):
 o.name=name;o.data.materials.append(mat);group.append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
def smart(o):
 activate(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
def cylinder(name,loc,r,depth,mat=brass,group=hardware,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc);o=bpy.context.object
 if axis=='Y':o.rotation_euler.x=math.pi/2
 m=o.modifiers.new('Soft manufactured edge','BEVEL');m.width=min(.0012,depth*.16);m.segments=3;activate(o);bpy.ops.object.modifier_apply(modifier=m.name);return add(o,name,mat,group)
def sphere(name,loc,size,mat,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.scale=size;activate(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return add(o,name,mat,group)
def torus(name,loc,major,minor,axis='Z'):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=10,major_radius=major,minor_radius=minor,location=loc);o=bpy.context.object
 if axis=='Y':o.rotation_euler.x=math.pi/2
 return add(o,name,brass,hardware)
def lathe(name,profile,mat,group):
 N=96;v=[(r*math.cos(i*math.tau/N),-.08+r*math.sin(i*math.tau/N),z) for z,r in profile for i in range(N)];f=[]
 for j in range(len(profile)):
  k=(j+1)%len(profile)
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,k*N+(i+1)%N,k*N+i))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return add(o,name,mat,group)
# Original plate datum, size and profile. Base spigot retracts, leaving the bell clear.
cylinder('Mounting plate',(0,-.007,0),.042,.014,axis='Y');torus('Plate rim',(0,-.015,0),.038,.0022,'Y')
cylinder('Short recessed arm spigot',(0,-.014,.008),.009,.008,axis='Y')
for x in (-.026,.026):sphere('Plate screw',(x,-.016,0),(.0035,.0017,.0035),brass,hardware)
cu=bpy.data.curves.new('Wall hugging gooseneck','CURVE');cu.dimensions='3D';cu.resolution_u=32;cu.bevel_depth=.0045;cu.bevel_resolution=4;sp=cu.splines.new('BEZIER');sp.bezier_points.add(3)
for bp,co in zip(sp.bezier_points,[(0,-.020,.008),(0,-.024,.095),(0,-.052,.158),(0,-.080,.096)]):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
o=bpy.data.objects.new('Gooseneck',cu);bpy.context.collection.objects.link(o);activate(o);bpy.ops.object.convert(target='MESH');arm=add(o,'Gooseneck',brass,hardware)
# Real hollow cup accepts cylindrical opal neck; holder remains inside the hollow.
lathe('Hollow shade retaining cup',[(.071,.023),(.094,.023),(.096,.020),(.096,.007),(.090,.007),(.090,.0192),(.071,.0192)],brass,hardware)
torus('Arm seated collar',(0,-.080,.096),.0062,.0015)
for x in (-.024,.024):sphere('Retaining thumbscrew',(x,-.080,.080),(.003,.003,.003),brass,hardware)
cylinder('Ceramic bulb holder',(0,-.08,.075),.010,.020,ceramic)
cylinder('Bulb threaded neck',(0,-.08,.062),.007,.014,brass)
# Closed opal shell. Original outer width/projection retained; cylindrical mounting neck.
outer=[(.079,.0185),(.069,.0185)]
for i in range(1,33):
 t=i/32;outer.append((.069-.074*t,.0185+.0415*t**1.65+.0015*math.sin(math.pi*t)))
profile=outer+[(-.0065,.0605),(-.007,.0595),(-.0065,.058),(-.005,.0575)]+[(z,r-.0025) for z,r in reversed(outer[:-1])]
glass=lathe('Closed opal bell',profile,opal,shade)
sphere('Connected frosted bulb',(0,-.08,.034),(.014,.014,.024),bulbmat,bulbs)
cylinder('Bulb glass neck',(0,-.08,.056),.006,.014,bulbmat,bulbs)
# Validate the geometry before joining. Intentional holder/bulb seating is internal.
cross=bvh(glass).overlap(bvh(arm));assert not cross,('New arm crosses glass',len(cross))
allhits=[]
for o in hardware:
 overlap=bvh(glass).overlap(bvh(o))
 if overlap:allhits.append((o.name,len(overlap)))
assert not allhits,('Glass/hardware intersections',allhits)
assert not bvh(glass).overlap(bvh(bulbs[0])),'Bulb crosses glass'
bm=bmesh.new();bm.from_mesh(glass.data);newboundary=sum(e.is_boundary for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert newboundary==0 and volume>0
gap=min(bvh(arm).find_nearest(glass.matrix_world@v.co)[3] for v in glass.data.vertices)
def join(group,name):
 for o in group:smart(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[join(hardware,'HA_Sconce02_Hardware'),join(shade,'HA_Sconce02_Shade'),join(bulbs,'HA_Sconce02_Bulb')]
# Wall-mounted fixture: simple box for optional ray selection, shade/bulb no collision.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.071,.061));ucx=bpy.context.object;ucx.name='UCX_HA_Sconce02_Hardware_00';ucx.dimensions=(.123,.142,.207);activate(ucx);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ucx.hide_render=True
for o in parts:
 activate(o)
 if o==parts[0]:ucx.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'models'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
materials={}
for o in parts:
 slots=[]
 for i,m in enumerate(o.data.materials):
  p=m.node_tree.nodes.get('Principled BSDF');r={'slot':i,'name':m.name,'base_color_linear':list(p.inputs['Base Color'].default_value[:3]),'roughness':p.inputs['Roughness'].default_value,'metallic':p.inputs['Metallic'].default_value,'opacity':1,'blend_mode':'Opaque','two_sided':False,'transmission':0}
  if p.inputs['Base Color'].links:r['base_color_texture']='textures/'+Path(p.inputs['Base Color'].links[0].from_node.image.filepath).name
  slots.append(r)
 materials[o.name]=slots
report={'origin_m':[0,0,0],'front':'-Y','up':'+Z','units':'metres','replaces':{'HA_Sconce_Hardware':'HA_Sconce02_Hardware','HA_Sconce_Shade':'HA_Sconce02_Shade','HA_Sconce_Bulb':'HA_Sconce02_Bulb'},'component_bounds':{o.name:bounds(o) for o in parts},'material_contracts':materials,'shade_boundary_edges':newboundary,'shade_volume_m3':volume,'shade_arm_triangle_intersections':len(cross),'shade_hardware_triangle_intersections':allhits,'shade_arm_nearest_vertex_gap_m':gap,'shade_wall_minimum_clearance_m':.0195,'shade_thickness_m':.0025,'bulb_holder_seating_overlap_m':.008,'light_preview_position_m':[0,-.08,-.012],'toggle_contract':'Same transform for all3 meshes. Existinglight toggle actor controls unchanged lamp identity; shade/bulb emission + previewlight only change on/off. Hardware remains fixed.','original_source_sha256':audit['source_blend_sha256']}
report['assembly_bounds_m']={'min':[min(b['min'][i] for b in report['component_bounds'].values()) for i in range(3)],'max':[max(b['max'][i] for b in report['component_bounds'].values()) for i in range(3)]}
report['assembly_dimensions_m']=[report['assembly_bounds_m']['max'][i]-report['assembly_bounds_m']['min'][i] for i in range(3)]
(ROOT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
# Studio front/side and on/off. Opal is opaque; no transmission or fake transparency.
wallmat=material('PREVIEW chalk wall',(.38,.32,.24),None,0,.9)
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,.001,0),rotation=(math.pi/2,0,0));wall=bpy.context.object;wall.name='PREVIEW_WALL';wall.data.materials.append(wallmat)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.31;sc.camera=cam
def camera(pos):cam.location=pos;cam.rotation_euler=(Vector((0,-.065,.061))-cam.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((-.3,-.5,.55),12,.7),((.5,-.3,.25),6,.7)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,-.05,.05))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='POINT',location=(0,-.08,-.012));local=bpy.context.object;local.data.color=(1,.66,.36);local.data.shadow_soft_size=.022;local.data.energy=0
sc.world=bpy.data.worlds.new('Preview world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.25
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
camera((.25,-.55,.17));sc.render.filepath=str(ROOT/'previews/sconce-off.png');bpy.ops.render.render(write_still=True)
for m,e in [(opal,.65),(bulbmat,3.5)]:p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.66,.36,1);p.inputs['Emission Strength'].default_value=e
local.data.energy=1.3;sc.render.filepath=str(ROOT/'previews/sconce-on.png');bpy.ops.render.render(write_still=True)
local.data.energy=0
for m in (opal,bulbmat):m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=0
camera((.7,-.065,.08));sc.render.filepath=str(ROOT/'previews/sconce-side.png');bpy.ops.render.render(write_still=True)
camera((0,-.6,.061));sc.render.filepath=str(ROOT/'previews/sconce-front.png');bpy.ops.render.render(write_still=True)
camera((.16,-.35,-.13));sc.render.filepath=str(ROOT/'previews/sconce-underside.png');bpy.ops.render.render(write_still=True)
camera((.25,-.55,.17));wall.hide_render=True;wall.hide_set(True);ucx.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/HA-SCONCE-02.blend'))
assert hashlib.sha256(OLD.read_bytes()).hexdigest()==audit['source_blend_sha256']
print('SCONCE02_COMPLETE',json.dumps(report),flush=True)
