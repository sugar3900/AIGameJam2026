"""FIX030: preserve exact case/fuse/hinge geometry; replace old straight wiring and remove exterior stubs."""
from pathlib import Path
import bpy,bmesh,math,json,random,shutil
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parent;OLD=R.parent/'LV-FUSE-01'
for p in ('models','textures','previews'):(R/p).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'blender/LV-FUSE-01.blend'))
s=bpy.context.scene
shell=bpy.data.objects['LV_FUSE_01_Shell'];shell.name='LV_Fuse02_Shell'
# Remove connected external stubs/clamps and old red/navy wire geometry. Everything else is kept verbatim.
me=shell.data;adj={v.index:set() for v in me.vertices}
for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
unseen=set(adj);remove=set();islands=[]
while unseen:
 seed=unseen.pop();stack=[seed];part={seed}
 while stack:
  for j in adj[stack.pop()]:
   if j in unseen:unseen.remove(j);part.add(j);stack.append(j)
 zs=[me.vertices[i].co.z for i in part]
 if min(zs)<-.00001 or max(zs)>.58001:remove.update(part)
for p in me.polygons:
 if me.materials[p.material_index].name in ('Wire_Brick_Red','Wire_Navy'):remove.update(p.vertices)
kept_faces=[([tuple(me.vertices[i].co) for i in p.vertices],me.materials[p.material_index].name) for p in me.polygons if not any(i in remove for i in p.vertices)]
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(me);bm.free();me.update()
G=[shell]; added=[]
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def mat(n,c,metal=0,rough=.8):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m

def tex(n,base,kind):
 N=512;yy,xx=np.mgrid[0:N,0:N]/N;rng=np.random.default_rng(1937)
 noise=rng.random((N,N))-.5
 value=noise*.018
 for grid,amount in ((6,.035),(19,.018),(61,.008)):
  coarse=rng.random((grid,grid))-.5; gy=np.linspace(0,grid-1,N); gx=np.linspace(0,grid-1,N); tmp=np.array([np.interp(gx,np.arange(grid),row) for row in coarse]); smooth=np.array([np.interp(gy,np.arange(grid),tmp[:,j]) for j in range(N)]).T;value+=smooth*amount
 if kind=='metal':
  # Finger grime at edges, irregular oxide islands, fine dragging scratches.
  edge=np.minimum.reduce([xx,1-xx,yy,1-yy]);value-=.12*np.exp(-edge*16)
  for i in range(40):
   x,y=rng.random(2);rx,ry=rng.uniform(.008,.06,2);value-=rng.uniform(.01,.09)*np.exp(-((xx-x)/rx)**2-((yy-y)/ry)**2)
 else:value+=.035*np.sin((xx+yy*.23)*math.tau*95)*np.sin((yy-xx*.2)*math.tau*80)
 pix=np.ones((N,N,4),dtype=np.float32)
 for j,v in enumerate(base):pix[:,:,j]=np.clip(v+value,0,1)
 im=bpy.data.images.new(n,width=N,height=N);im.pixels.foreach_set(pix.ravel());im.filepath_raw=str(R/'textures'/(n+'.png'));im.file_format='PNG';im.save();return im

def assign_img(m,im):
 p=m.node_tree.nodes.get('Principled BSDF');n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
# Direct image links survive export. Dirty metal back remains distinct from brown bakelite.
interior=bpy.data.materials['Interior_Dark_Brown'];assign_img(interior,tex('T_Fuse02_Interior',(.205,.195,.165),'metal'));interior.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.88

# Localized grime around original ceramic base edges in the retained assembly UVs.
cer=bpy.data.materials['Ivory_Ceramic'];N=512;yy,xx=np.mgrid[0:N,0:N]/N;rng=np.random.default_rng(1928);dirt=np.zeros((N,N))
for cx in ((-.07+.23)/.46,(.07+.23)/.46):
 for cz in (.245/.58,.37/.58):
  d=np.sqrt(((xx-cx)/(.039/.46))**2+((yy-cz)/(.039/.58))**2);dirt+=.20*np.exp(-((d-.92)/.10)**2)*(0.60+.40*np.sin(xx*93+yy*61)**2)
dirt+=rng.random((N,N))*.035
pix=np.ones((N,N,4),dtype=np.float32)
for j,c in enumerate((.63,.59,.49)):pix[:,:,j]=np.clip(c-dirt*(1 if j<2 else .8),0,1)
im=bpy.data.images.new('T_Fuse02_AgedCeramic',width=N,height=N);im.pixels.foreach_set(pix.ravel());im.filepath_raw=str(R/'textures/T_Fuse02_AgedCeramic.png');im.file_format='PNG';im.save();assign_img(cer,im);cer.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.56
assign_img(bpy.data.materials['Bakelite_Dark_Brown'],tex('T_Fuse02_Bakelite',(.105,.074,.043),'metal'))

cloth=mat('Fuse02_AgedCloth',(.42,.34,.22));assign_img(cloth,tex('T_Fuse02_Cloth',(.43,.35,.24),'cloth'))
darkcloth=mat('Fuse02_DarkCloth',(.12,.105,.08));thread=mat('Fuse02_ClothBraid',(.30,.25,.17),0,.95)
tarnish=mat('Fuse02_TarnishedTerminal',(.22,.17,.085),.55,.65);grime=mat('Fuse02_Oxide',(.11,.075,.037),.08,.96)

def tube(name,points,r,material,braid=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;cu.resolution_u=12;cu.use_fill_caps=True
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,v in zip(sp.bezier_points,points):p.co=v;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);active(ob);bpy.ops.object.convert(target='MESH');ob.data.materials.append(material);G.append(ob);added.append(ob)
 for p in ob.data.polygons:p.use_smooth=True
 # Texture is the cloth weave; thin staggered wrap marks add tactile detail without a huge braided mesh.
 if braid:
  # Sample original control-path segments; short wraps stay embedded in insulation.
  for k,(a,b) in enumerate(zip(points,points[1:])):
   a,b=Vector(a),Vector(b);d=b-a
   for i in range(1,max(2,int(d.length/.012))):
    t=i/max(2,int(d.length/.012));c=a+d*t
    if k%2:continue
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=r*1.015,location=c);o=bpy.context.object;o.name='Cloth binding';o.scale=(1,1,.15);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(thread);G.append(o);added.append(o)
 return ob
# Leads enter through back knockouts; no wire above/below the exterior case.
# Loops leave the four central fuse faces readable and retain the right-hand repair route untouched.
paths=[
 ('Upper left cloth loop',[(-.055,-.047,.558),(-.115,-.066,.525),(-.17,-.080,.51),(-.183,-.081,.46),(-.146,-.084,.43),(-.10,-.080,.448),(-.07,-.072,.426)],.0065,cloth),
 ('Dark upper return',[(0,-.045,.557),(.045,-.059,.522),(.10,-.077,.515),(.124,-.083,.475),(.105,-.078,.444),(.07,-.072,.426)],.0055,darkcloth),
 ('Left perimeter feed',[(-.055,-.047,.552),(-.16,-.061,.525),(-.185,-.071,.38),(-.176,-.077,.265),(-.18,-.070,.14),(-.135,-.066,.10),(-.082,-.071,.14),(-.07,-.072,.180)],.006,cloth),
 ('Lower dark loop',[(0,-.046,.025),(-.08,-.064,.049),(-.15,-.076,.065),(-.159,-.079,.112),(-.119,-.078,.154),(-.07,-.072,.180)],.0055,darkcloth),
 ('Lower cloth loop',[(.015,-.045,.026),(.065,-.074,.055),(.105,-.086,.092),(.062,-.082,.135),(.025,-.072,.12),(-.01,-.072,.166),(.07,-.072,.180)],.0058,cloth),
 ('Right perimeter return',[(.055,-.047,.554),(.16,-.055,.531),(.184,-.072,.45),(.184,-.079,.25),(.18,-.077,.12),(.145,-.085,.067),(.092,-.07,.075),(.055,-.052,.025)],.0053,darkcloth),
 ('Left inter-carrier',[(-.07,-.072,.314),(-.12,-.08,.32),(-.145,-.087,.298),(-.12,-.08,.283),(-.07,-.072,.301)],.0048,cloth),
 ('Right inter-carrier',[(.07,-.072,.314),(.12,-.082,.327),(.13,-.087,.297),(.108,-.08,.281),(.07,-.072,.301)],.0048,darkcloth)]
for n,pts,r,m in paths:tube(n,pts,r,m)
# Age the backs and terminals; very shallow spots sit on metal surfaces, not floating over fuses.
random.seed(1971)
for i in range(0):
 x=random.uniform(-.19,.19);z=random.uniform(.04,.54)
 if abs(x)<.143 and .187<z<.425:continue
 rad=random.uniform(.0015,.008)
 verts=[(x+math.cos(a*math.tau/9)*rad*random.uniform(.6,1),-.0368,z+math.sin(a*math.tau/9)*rad*.6*random.uniform(.6,1)) for a in range(9)]
 mesh=bpy.data.meshes.new('Oxide smear');mesh.from_pydata(verts,[],[tuple(range(9))]);mesh.update();o=bpy.data.objects.new('Localized oxide',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(grime);G.append(o);added.append(o)
for x in (-.07,.07):
 for z in (.426,.314,.301,.189):
  bpy.ops.mesh.primitive_torus_add(major_radius=.0077,minor_radius=.0008,major_segments=20,minor_segments=6,location=(x,-.072,z+.0091));o=bpy.context.object;o.name='Tarnish terminal ring';o.data.materials.append(tarnish);G.append(o);added.append(o)
# Original UVs stay untouched. UV only added elements, using assembly-space projection.
for o in added:
 active(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 for p in o.data.polygons:
  for li in p.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=((v.x+.23)/.46,v.z/.58)
# Geometric source invariants before joining.
extra=[tuple(o.matrix_world@v.co) for o in added for v in o.data.vertices]
assert min(p[1] for p in extra)>-.120
assert all(not (abs(p[0])<.11 and .206<p[2]<.409 and p[1]<-.112) for p in extra)
assert min(p[2] for p in extra)>0 and max(p[2] for p in extra)<.58
active(shell)
for o in G:o.select_set(True)
bpy.ops.object.join();shell=bpy.context.object;shell.name='LV_Fuse02_Shell';s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Preserve source textures with direct paths in the new package.
for m in shell.data.materials:
 if not m or not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   im=n.image;dest=R/'textures'/Path(im.filepath).name
   if not dest.exists():
    orig=Path(bpy.path.abspath(im.filepath))
    if orig.exists():shutil.copyfile(orig,dest)
    else:im.filepath_raw=str(dest);im.file_format='PNG';im.save()
   im.filepath=str(dest);im.pack()
active(shell);bpy.ops.export_scene.fbx(filepath=str(R/'models/LV_Fuse02_Shell.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,path_mode='RELATIVE')
report={'mesh':shell.name,'triangles':sum(len(p.vertices)-2 for p in shell.data.polygons),'slots':[m.name for m in shell.data.materials],'retained_original_faces':len(kept_faces),'removed_old_wire_vertices':len(remove),'added_bounds':[[min(p[i] for p in extra) for i in range(3)],[max(p[i] for p in extra) for i in range(3)]],'case_and_hinge':'original non-wire faces/UVs retained; unchanged','repair_wires':'use original LV_FUSE_01_Wire_Damaged/Repaired unchanged','external_stubs':'removed'}
(R/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
# Neutral previews, actual original door and repair parts retained for fit reference only.
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for o in s.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.19,.19,1)
door=bpy.data.objects['LV_FUSE_01_Door'];door.rotation_euler.z=math.radians(-105)
cam=s.camera;cam.location=(.85,-2.2,1.05);cam.rotation_euler=(Vector((0,-.05,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.95
s.render.filepath=str(R/'previews/open-damaged.png');bpy.ops.render.render(write_still=True)
bpy.data.objects['LV_FUSE_01_Wire_Damaged'].hide_render=True;bpy.data.objects['LV_FUSE_01_Wire_Repaired'].hide_render=False
s.render.filepath=str(R/'previews/open-repaired.png');bpy.ops.render.render(write_still=True)
door.hide_render=True;cam.location=(0,-2.2,.37);cam.rotation_euler=(Vector((0,-.05,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.69
s.render.filepath=str(R/'previews/interior.png');bpy.ops.render.render(write_still=True)
door.hide_render=False;door.rotation_euler.z=0;bpy.data.objects['LV_FUSE_01_Wire_Damaged'].hide_render=False;bpy.data.objects['LV_FUSE_01_Wire_Repaired'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/LV-FUSE-02.blend'))
print('FIX030 BUILT',report)
