"""FIX-005: fitted, structured vintage sofa. Source only; no Unreal changes."""
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
source=bpy.data.collections.new('LV-SOFA-03_SOURCE');sc.collection.children.link(source)
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
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT.parent/'LV-SOFA-02/textures'/tex));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0006;m.node_tree.links.new(t.outputs['Color'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
floral=material('Sofa02_PaintedFloral',(.32,.29,.18),'sofa-floral.png')
welt=material('Sofa02_OliveWelt',(.18,.155,.085))
wood=material('Sofa02_WornWalnut',(.18,.075,.025),rough=.62)
teal=material('Sofa02_TealNeedlepoint',(.10,.24,.23),'pillow-teal-needlepoint.png')
rose=material('Sofa02_CoralEmbroidery',(.47,.20,.15),'pillow-coral-embroidery.png')
gold=material('Sofa02_AgedGoldCord',(.43,.31,.13))
cream=material('Sofa02_WovenThrow',(.58,.49,.36),'throw-wool.png')
n=cream.node_tree.nodes;links=cream.node_tree.links;p=n.get('Principled BSDF');image=next(t for t in n if t.type=='TEX_IMAGE');mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.58,.49,.36,1);links.new(image.outputs['Color'],mix.inputs[1]);links.new(mix.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.90

# Surface parameterization keeps face-panel motif scale stable, including arm caps.
def rounded(name,loc,dims,r,mat,mode='',seed=0,rotation=(0,0,0),N=18,full_uv=False):
 half=Vector(dims)/2;verts=[];faces=[];uvs=[];lookup={};rot=Matrix.Rotation(rotation[0],4,'X')@Matrix.Rotation(rotation[1],4,'Y')@Matrix.Rotation(rotation[2],4,'Z')
 def deform(v):
  x,y,z=v;u=x/half.x;v2=y/half.y;w=z/half.z
  if mode=='seat':
   if w>.4:z+=.045*(1-u*u)*(1-v2*v2)-.018*math.exp(-((u-.10*seed)**2/.35+(v2+.08)**2/.55))
   if w>.3:z+=.007*(1-u*u)*math.exp(-((v2+1)/.20)**2)
   # Small corner folds and front-edge compression, neither symmetric nor periodic.
   if v2<-.35:
    z-=.005*math.exp(-((u+.76)**2/.012+(v2+.83)**2/.05))+.003*math.exp(-((u-.67)**2/.02+(v2+.89)**2/.03))
    y+=.003*math.exp(-((u-.63)**2/.008+(w-.15)**2/.4))
  if mode=='back':
   y*=.55+.45*(1-u**4)*(1-w**4)
   x*=1-.027*(1-w*w)
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
     grid.append((lookup[key],(i/N,j/N) if full_uv else (p[a]/.72+.5+seed*.17,p[b]/.72+.5)))
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
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2;c.use_fill_caps=True
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
# Quiet rectilinear vintage frame, short turned feet, controlled arm cap.
rounded('Upholstered lower frame',(0,0,.225),(1.94,.78,.21),.018,floral,N=10);hull((0,0,.225),(1.94,.78,.21))
front=rounded('Front apron',(0,-.405,.23),(1.56,.035,.205),.008,floral,N=8)
fitted_seam('Front apron sewn welt',front,[(x,-.426,z+.23) for x,z in perimeter(.77,.095,.013)])
backframe=rounded('Continuous upholstered back',(0,.315,.625),(1.77,.15,.60),.025,floral,N=16);hull((0,.315,.625),(1.77,.15,.60))
for side in (-1,1):
 x=side*.875
 panel=rounded(('Left' if side<0 else 'Right')+' arm panel',(x,-.005,.421),(.215,.79,.542),.022,floral,seed=side,N=20)
 hull((x,-.005,.421),(.215,.79,.542))
 cap=rounded(('Left' if side<0 else 'Right')+' compact arm cap',(x,-.01,.710),(.235,.80,.142),.051,floral,seed=side,N=24)
 hull((x,-.01,.710),(.235,.80,.142))
 fitted_seam(('Left' if side<0 else 'Right')+' inset arm face welt',cap,[(x+u,-.412,.710+v) for u,v in perimeter(.110,.063,.045)])
 # Front panel seam connects visually to the compact arm cap.
 fitted_seam(('Left' if side<0 else 'Right')+' panel seam',panel,[(x+u,-.405,.421+v) for u,v in perimeter(.097,.259,.018)],r=.0018)
# Slightly varied seat cushions and back cushions retain fitted box construction.
for i,x in enumerate((-.535,0,.535)):
 loc=(x,-.07,.402);dims=(.526,.584,.148)
 ob=rounded(f'Seat cushion {i+1}',loc,dims,.026,floral,'seat',i,N=28)
 hull(loc,(.52,.58,.145))
 for z in (.402+.069,.402-.064):
  fitted_seam(f'Seat {i+1} '+('upper' if z>.4 else 'lower')+' welt',ob,[(x+u,-.07+v,z) for u,v in perimeter(.257,.286,.028)])
 loc=(x,.218,[.713,.720,.710][i]);dims=(.52,.19,[.495,.505,.500][i]);ang=[-.145,-.09,-.125][i];lean=[-.016,.011,-.012][i]
 ob=rounded(f'Back cushion {i+1}',loc,dims,.043,floral,'back',i,rotation=(ang,0,lean),N=32)
 rotation=Matrix.Rotation(ang,4,'X')@Matrix.Rotation(lean,4,'Z')
 fitted_seam(f'Back {i+1} front welt',ob,[tuple(rotation@Vector((u,-.086,v))+Vector(loc)) for u,v in perimeter(.253,dims[2]/2-.007,.031)])
# Lathed walnut feet: collar, taper and worn rings, real floor origin.
for x in (-.80,.80):
 for y in (-.30,.29):
  rings=[(0,.043),(.009,.047),(.025,.048),(.038,.055),(.052,.061),(.073,.064),(.091,.051),(.107,.056),(.123,.060),(.134,.055)]
  verts=[];faces=[];M=24
  for z,r in rings:
   for k in range(M):
    a=k*math.tau/M;verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
  for j in range(len(rings)-1):
   for k in range(M):faces.append((j*M+k,j*M+(k+1)%M,(j+1)*M+(k+1)%M,(j+1)*M+k))
  faces.append(tuple(reversed(range(M))));faces.append(tuple((len(rings)-1)*M+k for k in range(M)))
  mesh=bpy.data.meshes.new('Turned foot');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Walnut turned foot',mesh);source.objects.link(o);register(o,wood);hull((x,y,.067),(.12,.12,.134))
# Decorative pillows use a flat front-panel texture, modest depth, pinched corners and welt.
for name,loc,dims,mat,angles in [('Teal needlepoint pillow',(-.54,.015,.647),(.345,.145,.352),teal,(-.20,.11,-.075)),('Coral embroidered lumbar',(.18,-.032,.595),(.425,.145,.237),rose,(-.19,-.06,.045))]:
 ob=rounded(name,loc,dims,.027,mat,'pillow',rotation=angles,N=30,full_uv=True)
 rot=Matrix.Rotation(angles[0],4,'X')@Matrix.Rotation(angles[1],4,'Y')@Matrix.Rotation(angles[2],4,'Z')
 fitted_seam(name+' antique cord',ob,[tuple(rot@Vector((u,-dims[1]/2+.008,v))+Vector(loc)) for u,v in perimeter(dims[0]/2-.007,dims[2]/2-.007,.026)],gold,.0025)
# Throw: contact-supported surface over right arm with nonperiodic gravity folds.
# Along U travel from the seat, rise up the inside arm, over its top, then hang outside.
# Height contact is queried from the actual sofa mesh (excludes pillows / seams).
support=[o for o in parts if any(t in o.name for t in ('arm panel','arm cap','Seat cushion','Back cushion','pillow','lumbar'))]
sv=[];sf=[]
for o in support:
 off=len(sv);sv += [v.co.copy() for v in o.data.vertices];sf += [tuple(off+i for i in p.vertices) for p in o.data.polygons]
tree=BVHTree.FromPolygons(sv,sf,all_triangles=False)
profile=[(.59,.485),(.65,.488),(.704,.53),(.741,.665),(.776,.754),(.83,.788),(.90,.790),(.958,.775),(.994,.731),(.998,.64),(1.001,.50),(1.003,.37),(1.004,.24)]
def catmull(t):
 k=min(int(t*(len(profile)-1)),len(profile)-2);f=t*(len(profile)-1)-k
 a=Vector(profile[max(k-1,0)]);b=Vector(profile[k]);c=Vector(profile[k+1]);d=Vector(profile[min(k+2,len(profile)-1)])
 return .5*((2*b)+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f*f*f)
verts=[];faces=[];uvs=[];Nu=100;Nv=44
folds=[(-.205,.055,.028),(-.065,.044,.032),(.115,.052,.039)]
for j in range(Nv+1):
 v=j/Nv;y0=-.380+v*.38
 for i in range(Nu+1):
  u=i/Nu;x,z=catmull(u)
  # Unequal ridges narrow toward hanging edge, with slight diagonal drift and broad contact valleys.
  fold=sum(amp*math.exp(-((y0-c-.014*u*u)/(width*(1-.25*u)))**2) for c,width,amp in folds)
  if u<.58:
   z+=fold*(.35+.65*u/.58)+.040*math.exp(-((y0+.10)/.07)**2-((u-.48)/.16)**2)
  else:
   x+=fold*.85
   z-=.018*(u-.58)/.42*(.3+.7*v)
  hit=tree.ray_cast(Vector((x,y0,1.20)),Vector((0,0,-1)),2)[0]
  if hit:z=max(z,hit.z+.014)
  z+=max(0,(u-.78)/.22)*(.035*math.exp(-((v-.18)/.17)**2)-.018*math.exp(-((v-.64)/.22)**2))
  # The hem is gently uneven, rather than a repeated sine.
  z+=.006*(v-.4)**2*(u*u)
  y=y0*(1-.12*math.exp(-((u-.53)/.16)**2))+.010*u*(v-.35)
  point=Vector((x,y,z));near,normal,idx,d=tree.find_nearest(point)
  if near and (point-near).dot(normal)<.014:point=near+normal*.014
  verts.append(tuple(point))
for j in range(Nv):
 for i in range(Nu):
  a=j*(Nu+1)+i;faces.append((a,a+Nu+1,a+Nu+2,a+1));uvs.append(((i/Nu,j/Nv),(i/Nu,(j+1)/Nv),((i+1)/Nu,(j+1)/Nv),((i+1)/Nu,j/Nv)))
mesh=bpy.data.meshes.new('Contact draped woven cloth');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Woven throw with gravity folds',mesh);source.objects.link(ob);register(ob,cream)
uv=mesh.uv_layers.new(name='ClothUV')
for p,co in zip(mesh.polygons,uvs):
 for li,xy in zip(p.loop_indices,co):uv.data[li].uv=xy
bpy.context.view_layer.objects.active=ob;sol=ob.modifiers.new('Woven cloth thickness','SOLIDIFY');sol.thickness=.003;sol.offset=0;bpy.ops.object.modifier_apply(modifier=sol.name)
for j in (0,Nv):tube('Throw side hem',[verts[j*(Nu+1)+i] for i in range(Nu+1)],.0022,cream)
tube('Throw hanging hem',[verts[j*(Nu+1)+Nu] for j in range(Nv+1)],.0023,cream)
for j in range(0,Nv+1,2):
 x,y,z=verts[j*(Nu+1)+Nu];length=.038+random.uniform(0,.017)
 for k in (-1,0,1):tube('Throw twisted fringe',[(x,y+k*.0017,z),(x+.002,y+k*.0015,z-length*.55),(x-.003,y+k*.002,z-length)],.0009,cream)
# UV for narrow trims / feet; all texture-bearing panels already have dedicated mappings.
for o in parts:
 if not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
# All parts must share the first UV layer name before joining. Blender's per-object active maps
# otherwise become separate joined channels (PanelUV/ClothUV), leaving throw UV0 collapsed.
for ob in parts:
 ob.data.uv_layers.active.name='UVMap'
# Export one static assembly; source members remain editable.
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();source.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='LV_Sofa03'
sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
hulls=[]
for i,(loc,dims) in enumerate(collision):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=f'UCX_LV_Sofa03_{i:02d}';o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);hulls.append(o)
bpy.ops.object.select_all(action='DESELECT');joined.select_set(True)
for o in hulls:o.select_set(True)
bpy.context.view_layer.objects.active=joined
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/LV-SOFA-03.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE',bake_anim=False)
vs=[v.co for v in joined.data.vertices]
manifest={'asset':'LV-SOFA-03','units':'metres','up':'+Z','front':'-Y','origin':'existing sofa floor centre; preserve actor transform','bounds':{'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]},'render_vertices':len(vs),'ucx_hulls':len(hulls),'materials':[m.name for m in joined.data.materials],'seam_contact':contact_report,'throw_material_contract':{'base_color_multiplier':[.58,.49,.36],'roughness':.90,'texture':'LV-SOFA-02/textures/throw-wool.png','normal_strength':.12},'throw':'hand-modeled nonperiodic contact drape; raycast-supported upper surface; gravity drop outside right arm; no cloth simulation claimed'}
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
for o in [joined]+hulls:bpy.data.objects.remove(o,do_unlink=True)
# Render context is deliberately separate from exported source geometry.
def context_box(name,loc,dims,col):
 m=material('PREVIEW '+name,col);bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='PREVIEW '+name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 ctx.objects.link(o);return o
context_box('warm plank floor',(0,0,-.035),(6,5,.06),(.24,.115,.043))
context_box('ochre plaster wall',(0,.91,1.5),(6,.08,3),(.51,.37,.20))
context_box('ivory skirting',(0,.855,.065),(6,.025,.13),(.70,.65,.53))
context_box('quiet woven rug',(0,-1.10,.002),(2.25,1.40,.006),(.32,.17,.10))
world=bpy.data.worlds.new('Warm neutral studio');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.38,.33,.27,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
for loc,power,size,color in [((-2.7,-3.2,3.4),420,3.0,(1,.86,.68)),((2.3,-1,2.4),170,2.2,(.82,.9,1)),((0,1.5,3),200,2,(1,.88,.72))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam

def camera(loc,target,scale):cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
camera((2.7,-4.3,2.15),(0,0,.48),2.65)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/LV-SOFA-03.blend'))
if '--no-render' not in sys.argv:
 sc.render.filepath=str(ROOT/'previews/sofa-context.png');bpy.ops.render.render(write_still=True)
print('Sofa02 source and export built.')
