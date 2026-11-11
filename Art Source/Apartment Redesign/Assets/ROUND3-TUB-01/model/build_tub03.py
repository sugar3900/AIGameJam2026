"""Additive tub body only. Retain the installed drain, wall plumbing and curtain."""
from pathlib import Path
import bpy, bmesh, math, shutil, json, hashlib
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; A=P.parent
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for src,dst in [('BA-TUB-01/textures/enamel-albedo.png','enamel-albedo.png'),('BA-TUB-01/textures/enamel-brush-v2.png','enamel-brush.png'),('HA-SCONCE-01/textures/aged-brass.png','aged-metal.png')]:
 shutil.copyfile(A/src,P/'textures'/dst)

def material(name,base,rough,metal=0,mix=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*base,1);m.use_backface_culling=True
 ns=m.node_tree.nodes;ln=m.node_tree.links;bs=ns.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'textures'/('aged-metal.png' if metal else 'enamel-albedo.png')))
 out=t.outputs['Color']
 if not metal:
  t2=ns.new('ShaderNodeTexImage');t2.image=bpy.data.images.load(str(P/'textures/enamel-brush.png'))
  blend=ns.new('ShaderNodeMixRGB');blend.inputs[0].default_value=mix;ln.new(out,blend.inputs[1]);ln.new(t2.outputs['Color'],blend.inputs[2]);out=blend.outputs[0]
 mul=ns.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*base,1);ln.new(out,mul.inputs[1]);ln.new(mul.outputs[0],bs.inputs['Base Color'])
 return m
outer=material('Tub03_Exterior_Enamel',(1,1,1),.36,mix=.6)
inner=material('Tub03_Interior_Enamel',(1.08,1.08,1.06),.23,mix=.3)
rim=material('Tub03_Rolled_Rim',(1.05,1.04,1.01),.26,mix=.45)
cast=material('Tub03_Aged_CastMetal',(.38,.42,.42),.48,.68)
edge=material('Tub03_Raised_Metal',(.67,.64,.56),.39,.72)
dark=bpy.data.materials.new('Tub03_Overflow_Dark');dark.diffuse_color=(.035,.027,.018,1);dark.use_nodes=True;dark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.035,.027,.018,1);dark.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.5
parts=[]

def finish(o,mat):
 o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
 if not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name;assert all(e.is_manifold for e in bm.edges),o.name;bm.to_mesh(o.data);bm.free();parts.append(o);return o

def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,mat)

def ellipsoid(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,mat)

def tube(name,coords,radii,mat,seg=12):
 vs=[];fs=[]
 for k,p in enumerate(coords):
  p=Vector(p);t=(Vector(coords[min(k+1,len(coords)-1)])-Vector(coords[max(k-1,0)])).normalized();ref=Vector((1,0,0)) if abs(t.x)<.8 else Vector((0,1,0));u=t.cross(ref).normalized();v=t.cross(u).normalized()
  for i in range(seg):vs.append(p+radii[k]*(u*math.cos(i*2*math.pi/seg)+v*math.sin(i*2*math.pi/seg)))
 for k in range(len(coords)-1):
  for i in range(seg):a=k*seg+i;b=k*seg+(i+1)%seg;fs.append((a,b,b+seg,a+seg))
 fs.extend([tuple(reversed(range(seg))),tuple(range((len(coords)-1)*seg,len(coords)*seg))]);return mesh(name,vs,fs,mat)

def ringcurve(name,rx,ry,z,r,mat):
 coords=[];vs=[];fs=[];N=128;S=12
 for j in range(N):
  a=j*2*math.pi/N;c,s=math.cos(a),math.sin(a);p=Vector((rx*math.copysign(abs(c)**.65,c),ry*math.copysign(abs(s)**.65,s),z));rad=Vector((c/rx,s/ry,0)).normalized()
  for k in range(S):vs.append(p+r*(rad*math.cos(k*2*math.pi/S)+Vector((0,0,1))*math.sin(k*2*math.pi/S)))
 for j in range(N):
  for k in range(S):fs.append((j*S+k,((j+1)%N)*S+k,((j+1)%N)*S+(k+1)%S,j*S+(k+1)%S))
 return mesh(name,vs,fs,mat)
# Preserve the original inner bowl exactly at each original section: water plane
# local x +/- .718, y +/- .229, z .430 and separate drain z .184 remain seated.
profile=[(.65,.22,.12),(.665,.228,.126),(.706,.251,.145),(.75,.28,.17),(.775,.300,.27),(.801,.321,.40),(.82,.33,.48),(.831,.337,.53),(.835,.34,.55),(.834,.339,.561),(.83,.335,.57),(.812,.317,.575),(.786,.29,.575),(.76,.265,.57),(.755,.26,.54),(.74125,.24875,.46),(.7275,.2375,.38),(.71375,.22625,.30),(.70,.215,.22),(.675,.200,.193),(.64,.182,.182),(.61,.17,.18)]
N=128;vs=[];fs=[]
for rx,ry,z in profile:
 for i in range(N):a=i*2*math.pi/N;c,s=math.cos(a),math.sin(a);vs.append((rx*math.copysign(abs(c)**.65,c),ry*math.copysign(abs(s)**.65,s),z))
for j in range(len(profile)-1):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
fs.extend([tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))])
body=mesh('Tub03_Continuous_Bowl',vs,fs,outer);body.data.materials.append(inner);uv=body.data.uv_layers.active
for f in body.data.polygons:
 f.material_index=1 if f.index>=(14*N) else 0
 for li in f.loop_indices:
  v=body.data.vertices[body.data.loops[li].vertex_index].co
  uv.data[li].uv=(.5+v.x/1.67,.5+v.y/.68) if f.material_index else ((math.atan2(v.y/.34,v.x/.835)+math.pi)/(2*math.pi)*2, v.z/.57)
ringcurve('Tub03_Rolled_Lip',.795,.302,.565,.018,rim)
ringcurve('Tub03_Cast_Rim_Bead',.823,.332,.523,.0035,rim)
# Each ankle connects into the underside and is dressed with a shield-shaped
# casting and raised leaf ribs. Balls and tapered curled talons replace toy toes.
for xi,x in enumerate([-.62,.62]):
 for yi,sgn in enumerate([-1,1]):
  tag=f'{xi}{yi}';Y=lambda y:sgn*y
  tube('Tub03_Scrolled_Ankle_'+tag,[(x,Y(.215),.172),(x,Y(.218),.143),(x,Y(.234),.112),(x,Y(.251),.086),(x,Y(.255),.057)],[.025,.023,.019,.020,.022],cast,20)
  ellipsoid('Tub03_Ball_'+tag,(x,Y(.259),.043),(.033,.031,.033),edge)
  # Three front claws curl over the ball; a fourth rear claw braces it.
  for q in [-1,0,1]:
   xx=x+q*.023
   tube('Tub03_Curled_Talon_'+tag+'_'+str(q),[(x+q*.017,Y(.237),.103),(xx,Y(.270),.080),(xx,Y(.290),.054),(x+q*.020,Y(.290),.026)],[.009,.009,.007,.0025],cast,12)
  tube('Tub03_Rear_Claw_'+tag,[(x,Y(.233),.096),(x,Y(.226),.054),(x,Y(.239),.021)],[.009,.007,.002],cast)
  outline=[(-.040,.197),(-.035,.218),(-.019,.221),(0,.229),(.019,.221),(.035,.218),(.040,.197),(.028,.166),(0,.123),(-.028,.166)]
  # Shallow top shield follows the changing shell face; bottom tapers onto ankle.
  def shield_y(dx,z):
   for (r0,s0,z0),(r1,s1,z1) in zip(profile[:10],profile[1:11]):
    if z0<=z<=z1:
     t=(z-z0)/(z1-z0);rx=r0+(r1-r0)*t;ry=s0+(s1-s0)*t;break
   c=min(.999,abs((x+dx)/rx)**(1/.65));return Y(ry*(1-c*c)**(.65/2))
  vs=[(x+dx,shield_y(dx,z)+Y(d),z) for d in [-.005,.006] for dx,z in outline];n=len(outline);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  mesh('Tub03_Leaf_Casting_'+tag,vs,fs,cast)
  def leafline(label,coords,r=.0025):tube('Tub03_Leaf_Rib_'+tag+label,[(x+dx,shield_y(dx,z)+Y(.009),z) for dx,z in coords],[r]*len(coords),edge,8)
  leafline('mid',[(0,.135),(0,.173),(0,.211),(0,.225)],.003)
  for side in [-1,1]:
   for z in [.166,.186,.204]:leafline(str(side)+str(z),[(0,z-.010),(side*.015,z-.001),(side*.028,z+.008)],.0022)
  for dx in [-.026,.026]:ellipsoid('Tub03_Casting_Rivet_'+tag,(x+dx,shield_y(dx,.211)+Y(.009),.211),(.004,.0025,.004),edge)
# Overflow escutcheon is on the inner back slope at x -.53. The original tub's
# baked overflow is removed with the old body. Separate drain stays installed.
# At z .39 the preserved inner shell y is ~.204; front surface sits 4 mm inside.
def inner_y(x,z):
 rx=.70+(z-.22)/(.54-.22)*(.755-.70);ry=.215+(z-.22)/(.54-.22)*(.26-.215)
 c=abs(x/rx)**(1/.65);return ry*max(0,1-c*c)**(.65/2)
def conform_plate(name,x,z,rx,rz,front,back,mat):
 # Conform the full oval to the inner shell instead of placing a flat disk on
 # its curved slope, which would leave one edge floating by several mm.
 N=48;vs=[];fs=[]
 for offset in [back,front]:
  for i in range(N):
   a=i*2*math.pi/N;xx=x+rx*math.cos(a);zz=z+rz*math.sin(a);vs.append((xx,inner_y(xx,zz)-offset,zz))
 vs.extend([(x,inner_y(x,z)-back,z),(x,inner_y(x,z)-front,z)])
 for i in range(N):
  j=(i+1)%N;fs.extend([(2*N,j,i),(2*N+1,N+i,N+j),(i,j,N+j,N+i)])
 return mesh(name,vs,fs,mat)
x=-.53;z=.39
conform_plate('Tub03_Overflow_Plate',x,z,.030,.033,.004,-.001,edge)
conform_plate('Tub03_Overflow_Slot',x,z+.003,.019,.004,.0055,.004,dark)
ellipsoid('Tub03_Overflow_Screw',(x,inner_y(x,z-.018)-.005,z-.018),(.003,.002,.003),cast)
# Reproducible floor-origin combined body with explicit six-slot contract.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body=bpy.context.object;body.name='BA_Tub03_Body';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Joining UVMap preserves the meaningful first layer on all parts.
bpy.ops.export_scene.fbx(filepath=str(P/'model/BA_Tub03_Body.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE',axis_forward='-Z',axis_up='Y')
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.33,.36,.39,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for loc,power,size in [((0,-3,4),650,4),((2,2,3),400,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.28))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.1,-2.8,1.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.92;sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'previews/tub03-three-quarter.png');sc.render.film_transparent=True
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/ROUND3-TUB-01.blend'))
bpy.ops.render.render(write_still=True)
(P/'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f.name not in ['file-manifest.json','validation.json']},indent=2)+'\n')
print('TUB03 EXPORTED',len(body.data.vertices),'vertices',len(body.data.polygons),'faces', [m.name for m in body.data.materials])
