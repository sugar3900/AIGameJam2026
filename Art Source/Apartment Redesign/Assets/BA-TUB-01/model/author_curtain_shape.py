"""Run with Blender -b --python; edits only the moving curtain and adds preview context."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parents[2]; D=A/'BA-TUB-01'; M=D/'model'; P=D/'previews'
# Optional source path after -- permits rebuilding from the original pre-morph blend.
source=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else M/'BA-TUB-01.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
o=bpy.data.objects['Curtain_panel_sliding']
if o.data.shape_keys: raise RuntimeError('Already authored; restore original before rebuilding')
# Preserve every original loop UV and polygon material assignment.
old=o.data; original=[o.matrix_world@v.co for v in old.vertices]
faces=[tuple(p.vertices) for p in old.polygons]; mats=[p.material_index for p in old.polygons]; uvs=[tuple(x.uv) for x in old.uv_layers.active.data]
# Solidified original cloth: two 65x33 grids; seven independent 128-vertex tori.
assert len(original)==5186
cloth=65*33*2
assert cloth==4290
# Discover ring components rather than depending on join ordering.
adj={i:[] for i in range(cloth,len(original))}
for e in old.edges:
 a,b=e.vertices
 if a in adj and b in adj: adj[a].append(b);adj[b].append(a)
components=[]; unseen=set(adj)
while unseen:
 stack=[unseen.pop()]; group=[]
 while stack:
  q=stack.pop();group.append(q)
  for n in adj[q]:
   if n in unseen: unseen.remove(n);stack.append(n)
 components.append(group)
components.sort(key=lambda c:sum(original[i].x for i in c)/len(c))
assert len(components)==7 and all(len(c)==128 for c in components)
FABRIC_WIDTH=2.10
# Solve the actual 64-edge polyline, including its fixed return overlap.
def row_points(v,closed,amp):
 z=2.13-1.905*v
 # Outward lean, rounded into a vertical drop over Z 58--72 cm.
 depth=2.13-z;start=2.13-.72;stop=2.13-.58;knee=(start+stop)/2
 travel=depth if depth<=start else (knee if depth>=stop else depth-(depth-start)**2/(2*(stop-start)))
 center=-.385-.010*closed-.055*(1-closed)*travel/knee
 points=[]
 for i in range(65):
  u=i/64;tail=max(0,1-u/.0625)**2
  x=-.82+(.40+1.32*closed)*u-.145*tail
  y=center+amp*math.sin(u*math.pi*14)+(-.21-center)*tail
  zz=z+.005*math.sin(u*math.pi*6)*v
  points.append(Vector((x,y,zz)))
 return points
def solve_row(v,w):
 lo,hi=0,.15
 for _ in range(45):
  amp=(lo+hi)/2;pts=row_points(v,w,amp)
  length=sum((b-a).length for a,b in zip(pts,pts[1:]))
  if length<FABRIC_WIDTH:lo=amp
  else:hi=amp
 return row_points(v,w,(lo+hi)/2)
rows={(w,j):solve_row(j/32,w) for w in (0,.5,1) for j in range(33)}
def clothco(index,closed):
 q=index%(65*33);p=rows[closed,q//65][q%65].copy()
 if index>=2145:p.y+=.002
 return p
def coords(closed):
 out=[clothco(i,closed) for i in range(cloth)] + [Vector() for _ in range(896)]
 for k,c in enumerate(components):
  center=sum((original[i] for i in c),Vector())/len(c)
  u=(k+.5)/7; target=Vector((-.82+(.40+1.32*closed)*u,-.35,2.17))
  for i in c: out[i]=original[i]-center+target
 return out
basis=coords(0);closed=coords(1);midway=coords(.5)
# Small rigid metal header clips, one per ring, connecting its front/lower quadrant to cloth.
for k in range(7):
 u=(k+.5)/7
 def clip(w):
  x=-.82+(.40+1.32*w)*u
  y=-.385-.010*w
  start=Vector((x,-.370,2.150));end=Vector((x,y,2.128));axis=(end-start).normalized();a=Vector((1,0,0));b=axis.cross(a).normalized()
  return [p+.0022*(math.cos(t*math.tau/8)*a+math.sin(t*math.tau/8)*b) for p in (start,end) for t in range(8)]
 off=len(basis);basis+=clip(0);closed+=clip(1);midway+=clip(.5)
 for t in range(8):
  faces.append((off+t,off+(t+1)%8,off+8+(t+1)%8,off+8+t));mats.append(1);uvs.extend([(0,0)]*4)
mesh=bpy.data.meshes.new('Curtain_authored_open_closed');mesh.from_pydata(basis,[],faces);mesh.update()
for mat in old.materials:mesh.materials.append(mat)
uv=mesh.uv_layers.new(name=old.uv_layers.active.name)
for i,p in enumerate(mesh.polygons): p.material_index=mats[i];p.use_smooth=True
for i,v in enumerate(uvs):uv.data[i].uv=v
o.data=mesh;o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
o.shape_key_add(name='Basis');key=o.shape_key_add(name='Closed')
for v,c in zip(key.data,closed):v.co=c
# Relative key stores Basis + residual, not an absolute halfway pose.
mid=o.shape_key_add(name='Closed_Mid')
for v,b,c,m in zip(mid.data,basis,closed,midway):v.co=b+m-(b+c)*.5
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0));arm=bpy.context.object;arm.name=o.name+'_Rig';bone=arm.data.edit_bones[0];bone.name='CurtainRoot';bone.head=(0,0,0);bone.tail=(0,0,.3);bpy.ops.object.mode_set(mode='OBJECT')
g=o.vertex_groups.new(name='CurtainRoot');g.add(list(range(len(mesh.vertices))),1,'REPLACE');mod=o.modifiers.new('Skin','ARMATURE');mod.object=arm;o.parent=arm
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(M/'BA_Curtain_Animated.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
# Preserve the original assembly in a hidden reference collection; export only moving mesh/rig.
legacy=bpy.data.collections.new('Original tub and fixtures (preserved)');bpy.context.scene.collection.children.link(legacy)
for ob in list(bpy.context.scene.objects):
 if ob not in (o,arm):
  for collection in list(ob.users_collection):collection.objects.unlink(ob)
  legacy.objects.link(ob)
legacy.hide_render=True;legacy.hide_viewport=True
context=bpy.data.collections.new('Preview assembly (not exported)');bpy.context.scene.collection.children.link(context)
for file in [A/'FEEDBACK-ROOM-03/model/CurvedL_Rod_ReturnCurtain.blend',A/'ROUND3-TUB-01/model/ROUND3-TUB-01.blend']:
 with bpy.data.libraries.load(str(file),link=False) as (src,dst): dst.objects=[n for n in src.objects if not n.startswith(('Camera','Area','Light'))]
 for ob in dst.objects:
  if ob and ob.type=='MESH':context.objects.link(ob)
# Textures resolve locally; pack for dependable preview and review.
for im in bpy.data.images:
 if im.source=='FILE':
  candidate=D/'textures'/Path(bpy.path.abspath(im.filepath)).name
  if candidate.exists():im.filepath=str(candidate);im.reload();im.pack();im.filepath='//../textures/'+candidate.name
world=bpy.data.worlds.new('Curtain preview studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.17,.20,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
bpy.ops.object.camera_add(location=(-2.8,-5.5,2.85));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.02,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.85;bpy.context.scene.camera=cam
for loc,power,size in [((-1,-4,4),650,4),((3,-1,3),350,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1100;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
for w,name in [(0,'open'),(.5,'halfway'),(1,'closed')]:
 key.value=w;mid.value=4*w*(1-w);s.render.filepath=str(P/f'curtain-{name}.png');bpy.ops.render.render(write_still=True)
key.value=0;mid.value=0
oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldscale=cam.data.ortho_scale
cam.location=(-2.5,-3.7,1.6);cam.rotation_euler=(Vector((-.65,-.32,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.35
s.render.filepath=str(P/'curtain-open-clearance.png');bpy.ops.render.render(write_still=True)
cam.location=oldloc;cam.rotation_euler=oldrot;cam.data.ortho_scale=oldscale
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(M/'BA-TUB-01.blend'))
