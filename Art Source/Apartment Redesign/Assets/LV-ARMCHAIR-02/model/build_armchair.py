"""FIX-013: tailored rust reading armchair. Source only; no Unreal changes."""
from pathlib import Path
import bpy, math, json, random, sys
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
random.seed(43)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32
sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
bpy.context.preferences.filepaths.save_version=0
source=bpy.data.collections.new('LV-ARMCHAIR-02_SOURCE');sc.collection.children.link(source)
ctx=bpy.data.collections.new('PREVIEW_ONLY');sc.collection.children.link(ctx)
parts=[];collision=[];contact_report=[]
def register(ob,mat):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 source.objects.link(ob);ob.data.materials.append(mat);parts.append(ob)
 for p in ob.data.polygons:p.use_smooth=True
 return ob

def material(name,col,tex=None,rough=.85):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 if tex:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/tex));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0006;m.node_tree.links.new(t.outputs['Color'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
  tint={'Armchair02_RustJacquard':(.83,.73,.65),'Armchair02_PaintedWalnut':(.36,.28,.20),'Armchair02_IvoryCrochet':(.78,.72,.61)}.get(name)
  if tint:
   mult=n.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(*tint,1);m.node_tree.links.new(t.outputs['Color'],mult.inputs[1]);m.node_tree.links.new(mult.outputs['Color'],p.inputs['Base Color']);m['base_color_multiplier']=tint
 return m
floral=material('Armchair02_RustJacquard',(.40,.16,.07),'rust-jacquard.png')
welt=material('Armchair02_RustWelt',(.23,.075,.026))
wood=material('Armchair02_PaintedWalnut',(.18,.07,.02),'walnut-painted.png',rough=.66)
lace=material('Armchair02_IvoryCrochet',(.72,.65,.50),'ivory-thread.png')

# Surface parameterization keeps face-panel motif scale stable, including arm caps.
def rounded(name,loc,dims,r,mat,mode='',seed=0,rotation=(0,0,0),N=18,full_uv=False):
 half=Vector(dims)/2;verts=[];faces=[];uvs=[];lookup={};rot=Matrix.Rotation(rotation[0],4,'X')@Matrix.Rotation(rotation[1],4,'Y')@Matrix.Rotation(rotation[2],4,'Z')
 def deform(v):
  x,y,z=v;u=x/half.x;v2=y/half.y;w=z/half.z
  if mode=='seat':
   z+=max(0,w)**2*(.055*(1-u**4)*(1-v2**4)-.032*math.exp(-((u-.10)**2/.30+(v2+.1)**2/.32)))
   z+=max(0,w)**2*.015*(1-u*u)*math.exp(-((v2+1)/.20)**2)
   # Small corner folds and front-edge compression, neither symmetric nor periodic.
   if v2<-.35:
    z-=.005*math.exp(-((u+.76)**2/.012+(v2+.83)**2/.05))+.003*math.exp(-((u-.67)**2/.02+(v2+.89)**2/.03))
    y+=.003*math.exp(-((u-.63)**2/.008+(w-.15)**2/.4))
  if mode=='arm':
   z+=.085*((v2+1)*.5)**2
  if mode=='arm_panel':
   z+=.085*((v2+1)*.5)**2*max(0,(w+1)*.5)
  if mode=='frame_back':
   x*=.91+.09*(w+1)*.5
  if mode=='back':
   y*=.55+.45*(1-u**4)*(1-w**4)
   x*=(.90+.10*(w+1)*.5)*(1-.04*(1-w*w))
   if v2<-.2:
    y-=.038*(1-u**4)*(1-w**4)+.009*math.exp(-((u+.28)**2/.18+(w-.18)**2/.3))
    y+=.018*math.exp(-((u+.72-.15*(w+.5))**2/.012+(w+.65)**2/.1))
    y+=.014*math.exp(-((u-.71+.12*(w-.6))**2/.012+(w-.66)**2/.1))
   z-=.021*(1-u*u)*(max(0,w)**2)
   x+=.002*(1-u*u)*w
  if mode=='pillow':
   fill=(1-abs(u)**3)*(1-abs(w)**3)
   y*=.12+1.14*fill
   if v2<-.2:
    y+=.006*math.exp(-((u+.74-.25*w)**2/.013+(w+.60)**2/.15))
    y+=.004*math.exp(-((u-.76+.15*w)**2/.010+(w-.65)**2/.12))
   x*=1-.085*(1-w*w)
   z*=1-.065*(1-u*u)
  q=rot@Vector((x,y,z));return q+Vector(loc)
 for axis in range(3):
  a,b=[i for i in range(3) if i!=axis]
  for sign in (-1,1):
   grid=[]
   for j in range(N+1):
    for i in range(N+1):
     p=Vector((0,0,0));p[axis]=sign*half[axis];p[a]=(-1+2*i/N)*half[a];p[b]=(-1+2*j/N)*half[b]
     core=Vector([max(-half[k]+r,min(half[k]-r,p[k])) for k in range(3)]);v=core+(p-core).normalized()*r
     key=tuple(round(t,7) for t in v)
     if key not in lookup:lookup[key]=len(verts);verts.append(tuple(deform(v)))
     grid.append((lookup[key],(i/N,j/N) if full_uv else (p[a]/.48+.5+seed*.17,p[b]/.48+.5)))
   for j in range(N):
    for i in range(N):
     inds=[j*(N+1)+i,j*(N+1)+i+1,(j+1)*(N+1)+i+1,(j+1)*(N+1)+i]
     face=[grid[k][0] for k in inds];uv=[grid[k][1] for k in inds]
     if len(set(face))<4:continue
     normal=(Vector(verts[face[1]])-Vector(verts[face[0]])).cross(Vector(verts[face[2]])-Vector(verts[face[0]]))
     desired=rot@Vector(tuple(sign if k==axis else 0 for k in range(3)))
     if normal.dot(desired)<0:face.reverse();uv.reverse()
     faces.append(face);uvs.append(uv)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);source.objects.link(ob);register(ob,mat)
 uv=mesh.uv_layers.new(name='PanelUV')
 for p,coords in zip(mesh.polygons,uvs):
  for li,co in zip(p.loop_indices,coords):uv.data[li].uv=co
 return ob

def tube(name,pts,r,mat,closed=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=0 if r<.0014 else 2;c.use_fill_caps=True
 s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 s.use_cyclic_u=closed
 ob=bpy.data.objects.new(name,c);source.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object
 return register(ob,mat)

def perimeter(a,b,r,steps=10):
 pts=[]
 for sx,sy,start in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
  for k in range(steps+1):
   t=math.radians(start+k*90/steps);pts.append((sx*(a-r)+r*math.cos(t),sy*(b-r)+r*math.sin(t)))
 return pts

def fitted_seam(name,ob,targets,mat=welt,r=.0022):
 tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[p.vertices for p in ob.data.polygons],all_triangles=False)
 dense=[]
 for a,b in zip(targets,targets[1:]+targets[:1]):
  a,b=Vector(a),Vector(b);count=max(1,math.ceil((b-a).length/.012))
  dense.extend(a.lerp(b,k/count) for k in range(count))
 pts=[];distances=[]
 for p in dense:
  hit,n,idx,d=tree.find_nearest(Vector(p));pts.append(tuple(hit+n*(r*.30)));distances.append(d)
 seam=tube(name,pts,r,mat,True)
 contact_report.append({'seam':name,'radius':r,'surface_offset':r*.30,'max_target_snap':max(distances)})
 return seam

def hull(loc,dims):collision.append((loc,dims))
def rolled_arm(name,x,seed):
 # Oval upholstered roll; swept along a rising path, with shallow domed end caps.
 verts=[];faces=[];uvs=[];ny=44;nt=64
 def profile(t):return .602+.105*t*t,.075*(1-.15*t**4),.066*(1-.10*t*t)
 for j in range(ny+1):
  t=j/ny;y=-.321+t*.626;zc,rx,rz=profile(t)
  for k in range(nt):
   a=k*math.tau/nt;verts.append((x+rx*math.cos(a),y,zc+rz*math.sin(a)))
 for j in range(ny):
  for k in range(nt):
   a=j*nt+k;b=(j+1)*nt+k;c=(j+1)*nt+(k+1)%nt;d=j*nt+(k+1)%nt
   faces.append((a,b,c,d));uvs.append(((j/ny*.626/.48,k/nt*.443/.48),( (j+1)/ny*.626/.48,k/nt*.443/.48),((j+1)/ny*.626/.48,(k+1)/nt*.443/.48),(j/ny*.626/.48,(k+1)/nt*.443/.48)))
 for end in (0,1):
  t=float(end);zc,rx,rz=profile(t);yy=-.321 if end==0 else .305;sgn=-1 if end==0 else 1;previous=[end*ny*nt+k for k in range(nt)]
  for rho in (.8,.6,.4,.2):
   ring=[]
   for k in range(nt):
    a=k*math.tau/nt;ring.append(len(verts));verts.append((x+rho*rx*math.cos(a),yy+sgn*.015*math.sqrt(1-rho*rho),zc+rho*rz*math.sin(a)))
   for k in range(nt):
    f=(previous[k],previous[(k+1)%nt],ring[(k+1)%nt],ring[k])
    if end:f=tuple(reversed(f))
    faces.append(f);uvs.append(tuple(((verts[i][0]-x)/.48+.5,(verts[i][2]-zc)/.48+.5) for i in f))
   previous=ring
  centre=len(verts);verts.append((x,yy+sgn*.015,zc))
  for k in range(nt):
   f=(centre,previous[k],previous[(k+1)%nt])
   if end:f=tuple(reversed(f))
   faces.append(f);uvs.append(tuple(((verts[i][0]-x)/.48+.5,(verts[i][2]-zc)/.48+.5) for i in f))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);source.objects.link(ob);register(ob,floral)
 uv=mesh.uv_layers.new(name='UnrolledUpholsteryUV')
 for face,coords in zip(mesh.polygons,uvs):
  for li,co in zip(face.loop_indices,coords):uv.data[li].uv=co
 return ob

# Compact frame remains inside original LV-CHAIR-01 envelope.
base=rounded('Rust upholstered base',(0,0,.215),(.675,.61,.23),.025,floral,N=16);hull((0,0,.215),(.675,.61,.23))
apron=rounded('Tailored front apron',(0,-.318,.221),(.55,.024,.20),.012,floral,N=12)
fitted_seam('Apron inset seam',apron,[(x,-.332,.221+z) for x,z in perimeter(.266,.092,.022)],r=.0017)
frame=rounded('Shaped sloping back frame',(0,.255,.609),(.60,.13,.60),.048,floral,'frame_back',rotation=(-.07,0,0),N=28);hull((0,.255,.610),(.58,.17,.61))
padloc=(0,.165,.640);padangle=-.14
back=rounded('Stuffed tailored back',padloc,(.535,.135,.535),.052,floral,'back',rotation=(padangle,0,-.012),N=40)
rot=Matrix.Rotation(padangle,4,'X')@Matrix.Rotation(-.012,4,'Z')
fitted_seam('Back fitted edge welt',back,[tuple(rot@Vector((x,-.061,z))+Vector(padloc)) for x,z in perimeter(.257,.256,.055)],r=.0018)
seat=rounded('Compressed crowned seat',(0,-.057,.401),(.505,.49,.15),.032,floral,'seat',N=40);hull((0,-.057,.402),(.50,.49,.145))
for z in (.469,.335):fitted_seam('Seat '+('upper' if z>.4 else 'lower')+' fitted welt',seat,[(x,-.057+y,z) for x,y in perimeter(.244,.236,.035)],r=.0018)
for side in (-1,1):
 x=side*.295;tag='Left' if side<0 else 'Right'
 panel=rounded(tag+' shaped arm panel',(x,-.010,.350),(.135,.62,.48),.025,floral,'arm_panel',seed=side,N=28);hull((x,-.010,.365),(.132,.62,.51))
 cap=rolled_arm(tag+' rising arm cap',x,side)
 for yy,zz,dd,hh in [(-.22,.608,.20,.13),(0,.628,.24,.14),(.22,.686,.20,.15)]:hull((x,yy,zz),(.145,dd,hh))
 fitted_seam(tag+' arm front welt',cap,[(x+.06975*math.cos(k*math.tau/64),-.3265,.602+.06138*math.sin(k*math.tau/64)) for k in range(64)],r=.0018)
 fitted_seam(tag+' arm panel sewn outline',panel,[(x+u,-.323,.350+z) for u,z in perimeter(.060,.228,.027)],r=.0015)
# Four lathed timber feet actually touch floor and support the frame.
for x in (-.268,.268):
 for y in (-.235,.235):
  rings=[(0,.025),(.006,.029),(.020,.034),(.036,.036),(.049,.029),(.074,.028),(.082,.040),(.096,.040),(.111,.032)]
  M=28;verts=[];faces=[]
  for z,r in rings:
   for k in range(M):
    a=k*math.tau/M;verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
  for j in range(len(rings)-1):
   for k in range(M):faces.append((j*M+k,j*M+(k+1)%M,(j+1)*M+(k+1)%M,(j+1)*M+k))
  faces.append(tuple(reversed(range(M))));faces.append(tuple((len(rings)-1)*M+k for k in range(M)))
  mesh=bpy.data.meshes.new('Turned walnut foot');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Supported walnut foot',mesh);source.objects.link(ob);register(ob,wood);hull((x,y,.0555),(.08,.08,.111))
# Real geometric openwork wraps the visible front, crown and rear.
# Each sample is ray-projected from outside onto the actual combined back surfaces.
sv=[];sf=[]
for ob in (frame,back):
 off=len(sv);sv.extend(v.co.copy() for v in ob.data.vertices);sf.extend(tuple(off+i for i in p.vertices) for p in ob.data.polygons)
support=BVHTree.FromPolygons(sv,sf,all_triangles=False)
lace_parts=[];projection_distances=[]
def drape(u,v):
 x=(u-.5)*.35;theta=v*math.pi;zc=.752+.012*abs(2*u-1)
 start=Vector((x,.22-.5*math.cos(theta),zc+.5*math.sin(theta)));direction=Vector((0,math.cos(theta),-math.sin(theta)))
 hit,normal,idx,dist=support.ray_cast(start,direction,1)
 if hit is None:raise RuntimeError(('Lace projection missed',u,v))
 p=hit-direction*(.0037/max(.25,abs(normal.dot(direction))))
 projection_distances.append(.0037)
 return tuple(p)
def stitch(name,uvs,r=.00072,closed=False):
 ob=tube(name,[drape(u,v) for u,v in uvs],r,lace,closed);lace_parts.append(ob);return ob
# A connected diamond net, with tiny floral rosettes laid over it.
cols=10;rows=16
for row in range(rows):
 for col in range(cols):
  u0=col/cols;u1=(col+1)/cols;v0=row/rows;v1=(row+1)/rows
  # diagonal mesh strands; small holes remain real geometry in every view.
  for a,b in [((u0,v0),(u1,v1)),((u1,v0),(u0,v1))]:
   stitch('Crochet diagonal stitch',[(a[0]+(b[0]-a[0])*t/8,a[1]+(b[1]-a[1])*t/8) for t in range(9)],.00042)
for row in range(7):
 for col in range(5):
  uc=.10+col*.20;vc=.085+row*.138
  # Rounded, bundled crochet petals, not angular star outlines.
  phi=.08*((row+col)%3)
  for petal in range(8):
   angle=petal*math.tau/8+phi;radial=Vector((math.cos(angle),math.sin(angle)));tangent=Vector((-math.sin(angle),math.cos(angle)))
   centre=radial*.0145
   for band in (1.0,.77):
    coords=[]
    for k in range(24):
     t=k*math.tau/24;pt=centre+radial*(.0113*band*math.cos(t))+tangent*(.0052*band*math.sin(t))
     coords.append((uc+pt.x/.35,vc+pt.y/.55))
    stitch('Crochet rounded flower petal',coords,.0010,True)
  for rr in (.0052,.0068):
   stitch('Crochet flower centre',[(uc+rr/.35*math.cos(k*math.tau/28),vc+rr/.55*math.sin(k*math.tau/28)) for k in range(28)],.0009,True)
# Bound perimeter: a double cord down sides and scalloped front/back hems.
for u in (0,1):
 for off in (0,.004):stitch('Crochet side bound edge',[(u+off*(1 if u==0 else -1),k/100) for k in range(101)],.0010)
for v in (0,1):
 stitch('Crochet straight hem',[(k/160,v) for k in range(161)],.0010)
 for i in range(14):
  pts=[]
  for k in range(21):
   a=k*math.pi/20;u=(i+.5-.5*math.cos(a))/14;vv=v+(-1 if v==0 else 1)*.019*math.sin(a)
   pts.append((u,vv))
  stitch('Crochet scallop edging',pts,.0010)
# Join lace members into a separately editable source part.
bpy.ops.object.select_all(action='DESELECT')
for ob in lace_parts:ob.select_set(True);parts.remove(ob)
bpy.context.view_layer.objects.active=lace_parts[0];bpy.ops.object.join();lace_mesh=bpy.context.object;lace_mesh.name='Contact draped openwork antimacassar';parts.append(lace_mesh)
for ob in parts:
 if not ob.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
# One static combined export, original component meshes retained in source.
bpy.ops.object.select_all(action='DESELECT');copies=[]
for ob in parts:
 c=ob.copy();c.data=ob.data.copy();source.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='LV_Armchair02';sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
hulls=[]
for i,(loc,dims) in enumerate(collision):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=f'UCX_LV_Armchair02_{i:02d}';ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);hulls.append(ob)
bpy.ops.object.select_all(action='DESELECT');joined.select_set(True)
for ob in hulls:ob.select_set(True)
bpy.context.view_layer.objects.active=joined
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/LV-ARMCHAIR-02.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE',bake_anim=False)
vs=[v.co for v in joined.data.vertices]
manifest={'asset':'LV-ARMCHAIR-02','replaces':'LV-CHAIR-01','units':'metres','up':'+Z','front':'-Y','origin':'same floor centre as LV-CHAIR-01; preserve actor transform','bounds':{'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]},'render_vertices':len(vs),'ucx_hulls':len(hulls),'materials':[{'name':m.name,'base_color_linear':list(m.diffuse_color[:3]),'base_color_multiplier':list(m.get('base_color_multiplier',(1,1,1))),'albedo_texture':next(('textures/'+Path(n.image.filepath).name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image),None),'roughness':m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value,'metallic':0,'blend_mode':'opaque','two_sided':False,'albedo_srgb':True} for m in joined.data.materials],'seam_contact':contact_report,'lace':'opaque geometric openwork, front/crown/rear contact drape projected onto actual back; 3.7mm thread-centre offset; no alpha or cloth simulation'}
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
for ob in [joined]+hulls:bpy.data.objects.remove(ob,do_unlink=True)
# Neutral room context, not exported.
def context_box(name,loc,dims,col):
 m=material('PREVIEW '+name,col);bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name='PREVIEW '+name;ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(m)
 for c in list(ob.users_collection):c.objects.unlink(ob)
 ctx.objects.link(ob)
context_box('warm wood floor',(0,0,-.035),(4,4,.06),(.24,.115,.043))
context_box('painted plaster',(0,.70,1.5),(4,.06,3),(.51,.37,.20))
context_box('ivory skirting',(0,.65,.06),(4,.025,.12),(.70,.65,.53))
world=bpy.data.worlds.new('Warm neutral studio');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.38,.33,.27,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
for loc,power,size,color in [((-2,-2.5,3),340,2.5,(1,.86,.68)),((2,-1,2),90,2,(.82,.9,1)),((0,1.5,3),160,2,(1,.88,.72))]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;ob.data.color=color;ob.rotation_euler=(Vector((0,0,.45))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.location=(1.8,-2.6,1.5);cam.rotation_euler=(Vector((0,0,.46))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.38
sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.cycles.samples=28
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/LV-ARMCHAIR-02.blend'))
if '--no-render' not in sys.argv:
 sc.render.filepath=str(ROOT/'previews/armchair-context.png');bpy.ops.render.render(write_still=True)
print('Armchair source built.')
