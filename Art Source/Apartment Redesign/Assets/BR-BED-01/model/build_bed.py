"""Generate a painterly vintage double bed. Metres, Z up, +Y=head, origin on floor."""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL=os.path.join(ROOT,'model'); TEX=os.path.join(ROOT,'textures'); PREVIEW=os.path.join(ROOT,'previews')
for p in (MODEL,TEX,PREVIEW): os.makedirs(p,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def image_mat(name,filename,tint=(1,1,1,1),rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=tint;m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF'); p.inputs['Roughness'].default_value=rough
 image=n.new('ShaderNodeTexImage');image.image=bpy.data.images.load(os.path.join(TEX,filename),check_existing=True);image.image.filepath='//../textures/'+filename;l.new(image.outputs['Color'],p.inputs['Base Color'])
 return m
wood=image_mat('Painted_Walnut','walnut-painted.png',(.38,.17,.07,1),.73)
wn=wood.node_tree.nodes; wl=wood.node_tree.links; hue=wn.new('ShaderNodeHueSaturation');hue.inputs['Value'].default_value=.90;hue.inputs['Saturation'].default_value=.85; wl.new(wn.get('Image Texture').outputs['Color'],hue.inputs['Color']);wl.new(hue.outputs['Color'],wn.get('Principled BSDF').inputs['Base Color'])
ivory=image_mat('Ivory_Cotton','ivory-linen.png',(.83,.75,.64,1),.94)
quilt=image_mat('Floral_Patchwork','quilt.png' if os.path.exists(os.path.join(TEX,'quilt.png')) else 'quilt-fallback.png')
rose=image_mat('Dusty_Rose_Throw','rose-knit.png',(.55,.30,.30,1),.95)

def box(name,loc,dims,mat,bevel=.012):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);return o

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);bpy.ops.object.shade_smooth();return o

def cylinder(name,loc,r,depth,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat);bpy.ops.object.shade_smooth();return o

def arched_panel(name,y,top,base):
 n=28; verts=[]
 for yy in (y-.035,y+.035):
  for i in range(n+1):
   x=-.66+1.32*i/n; z=top-.12*(abs(x)/.66)**2
   verts.extend([(x,yy,base),(x,yy,z)])
 faces=[]; row=2*(n+1)
 for i in range(n):
  a=2*i;b=a+2; faces.extend([(a,b,b+1,a+1),(row+a,row+a+1,row+b+1,row+b),(a,row+a,row+b,b),(a+1,b+1,row+b+1,row+a+1)])
 faces.extend([(0,1,row+1,row),(2*n,row+2*n,row+2*n+1,2*n+1)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(wood)
 # Continuous arched decorative bead.
 curve=bpy.data.curves.new(name+' rail','CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=.013;curve.bevel_resolution=3
 sp=curve.splines.new('POLY');sp.points.add(n)
 for i,p in enumerate(sp.points):
  x=-.66+1.32*i/n;p.co=(x,y-.04,top-.12*(abs(x)/.66)**2,1)
 obj=bpy.data.objects.new(name+' rail',curve);bpy.context.collection.objects.link(obj);curve.materials.append(wood)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
 return o

# Four turned posts and low side rails; all geometry remains within nominal footprint.
for yy,ht in ((.9,1.13),(-.9,.76)):
 for xx in (-.70,.70):
  cylinder('Turned post',(xx,yy,ht/2),.035,ht-.06,wood)
  sphere('Post finial',(xx,yy,ht),(.049,.049,.049),wood)
  sphere('Post foot',(xx,yy,.07),(.045,.045,.068),wood)
  for zz in (.13,ht-.09): cylinder('Post collar',(xx,yy,zz),.042,.028,wood)
arched_panel('Arched headboard',.9,1.07,.31)
arched_panel('Arched footboard',-.9,.70,.20)
for xx in (-.65,.65):box('Side rail',(xx,0,.25),(.055,1.74,.21),wood,.014)
box('Mattress',(0,0,.48),(1.30,1.73,.26),ivory,.075)
# Sculpted pillows: upper pillow puff, tapered corners through UV-sphere silhouette.
for xx in (-.34,.34):
 o=sphere('Soft pillow',(xx,.60,.72),(.31,.25,.105),ivory)
 for v in o.data.vertices:
  for i,dim in enumerate((.31,.25,.105)):
   a=v.co[i]/dim; v.co[i]=math.copysign(abs(a)**.62,a)*dim if a else 0
 for v in o.data.vertices:
  if v.co.z>0: v.co.z += .008*math.sin(v.co.x*34)*math.sin(v.co.y*23)*(1-abs(v.co.x)/.31)
 o.rotation_euler[0]=.12
 # A narrow sewn welt on the side of each soft pillow; no thick piping.
 curve=bpy.data.curves.new('Pillow seam','CURVE');curve.dimensions='3D';curve.bevel_depth=.0025;curve.bevel_resolution=2
 sp=curve.splines.new('POLY');sp.points.add(63);sp.use_cyclic_u=True
 for k,p in enumerate(sp.points):
  a=2*math.pi*k/64;cx=math.copysign(abs(math.cos(a))**.62,math.cos(a))*.302;cy=math.copysign(abs(math.sin(a))**.62,math.sin(a))*.242
  p.co=(xx+cx,.60+cy,.72+cy*.12,1)
 seam=bpy.data.objects.new('Pillow seam',curve);bpy.context.collection.objects.link(seam);curve.materials.append(ivory)
 bpy.ops.object.select_all(action='DESELECT');seam.select_set(True);bpy.context.view_layer.objects.active=seam;bpy.ops.object.convert(target='MESH')
# Mesh grid draped over sides with gently irregular quilted folds.
def drape(name,y0,y1,mat,kind):
 nx,ny=80,48;verts=[];uvs=[]
 # Arc-length coordinates avoid squashing the pattern down the steep fabric drop.
 xcoords=[-.73+1.46*i/nx for i in range(nx+1)]; arc=[0.0]
 for i in range(1,nx+1):
  def side_z(x): return -.31*(max(0,(abs(x)-.655)/.075)**1.5)
  dx=xcoords[i]-xcoords[i-1]; dz=side_z(xcoords[i])-side_z(xcoords[i-1]); arc.append(arc[-1]+math.hypot(dx,dz))
 for j in range(ny+1):
  v=j/ny;y=y0+(y1-y0)*v
  for i in range(nx+1):
   u=i/nx;x=-.73+1.46*u
   edge=max(0,(abs(x)-.655)/.075)
   z=.635 - .31*(edge**1.5) + .014*math.sin(y*16+x*6)*math.sin(math.pi*u)**2 + .009*math.sin(y*36+x*9)
   if kind=='throw': z+=.035+.028*math.sin(y*42+2*x)+.009*math.sin(y*68-x*5)
   verts.append((x,y,z));uvs.append((.02+arc[i]*.30,.03+(y-y0)*.30))
 faces=[]
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  poly.use_smooth=True
  for k in poly.loop_indices:uv.data[k].uv=uvs[mesh.loops[k].vertex_index]
 solid=o.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.008;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=solid.name);o.select_set(False)
 return o

drape('Floral patchwork quilt',-.83,.43,quilt,'quilt')
drape('Dusty rose throw',-.78,-.39,rose,'throw')
# Knotted fringe at the two draped edges, restrained and modeled separately.
for side in (-1,1):
 for i in range(20):
  y=-.78+i*.39/19;x=side*.724
  cylinder('Throw fringe',(x,y,.285),.0025,.08,rose)
# UV unwrap the custom arched boards, whose mesh had no initial UV layer.
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
# Preserve names, floor origin in the exported whole asset, and source with texture paths packed.
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  bpy.context.scene.cursor.location=(0,0,0);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.select_set(False)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=os.path.join(MODEL,'BR_Bed_Complete.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
soft=('Mattress','Soft pillow','Pillow seam','Floral patchwork quilt','Dusty rose throw','Throw fringe')
for filename,want_soft in (('BR_Bed_Frame.fbx',False),('BR_Bed_Bedding.fbx',True)):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and any(o.name.startswith(n) for n in soft)==want_soft: o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=os.path.join(MODEL,filename),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
bpy.ops.object.select_all(action='DESELECT')
# Warm room-like photographic review, showing frame, quilt, pillow and throw.
world=bpy.context.scene.world;world.color=(.35,.29,.23)
def point_camera(loc,target):
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=3.0;bpy.context.scene.camera=c
point_camera((3,-4,2.65),(0,0,.55))
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
area((1,-3,4),350,4);area((-3,1,3),220,3)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.view_settings.view_transform='AgX';s.render.filepath=os.path.join(PREVIEW,'bed-three-quarter.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(MODEL,'BR-BED-01.blend'));bpy.ops.render.render(write_still=True)
