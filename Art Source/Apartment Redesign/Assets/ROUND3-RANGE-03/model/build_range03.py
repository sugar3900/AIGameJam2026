"""Range refinement: retain the successful burner layout; develop working parts."""
from pathlib import Path
import bpy,bmesh,math,json,shutil
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent.parent;A=P.parent
bpy.context.preferences.filepaths.save_version=0
ns={'__file__':str(A/'KI-RANGE-02/build_range.py')}
exec((A/'KI-RANGE-02/build_range.py').read_text().split('records=[];joined={}')[0],ns)
ns=ns['ns']
groups=ns['groups'];box=ns['box'];cyl=ns['cyl'];bar=ns['bar'];add=ns['add']
for src,dst in [('KI-RANGE-02/textures/range-enamel-v2.png','range-enamel.png'),('KI-KETTLE-01/textures/steel-selected.png','aged-steel.png'),('KI-PAN-01/textures/iron.png','iron-grain.png')]:shutil.copyfile(A/src,P/'textures'/dst)

def texmat(name,filename,tint,rough,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*tint,1);m.use_nodes=True;m.use_backface_culling=True;ns=m.node_tree.nodes;ln=m.node_tree.links;bs=ns['Principled BSDF'];bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'textures'/filename),check_existing=True);mul=ns.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*tint,1);ln.new(t.outputs['Color'],mul.inputs[1]);ln.new(mul.outputs[0],bs.inputs['Base Color']);return m
steel=texmat('Range03_AgedSteel','aged-steel.png',(.72,.76,.78),.34,.78)
bakelite=texmat('Range03_Bakelite','iron-grain.png',(.42,.34,.28),.36,.04)
mark=texmat('Range03_CeramicMarkings','range-enamel.png',(1.05,1.05,1.01),.40)
# Retain enamel palette and burner material identities. Correct their actual
# texture paths; use distinct textured steel on all retained metal pieces.
enamel=ns['enamel'];iron=ns['iron'];gasket=ns['gasket'];inside=ns['inside'];glass=ns['glass']
for group,obs in groups.items():
 for o in obs:
  for i,m in enumerate(o.data.materials):
   if m==ns['steel']:o.data.materials[i]=steel
for n in enamel.node_tree.nodes:
 if n.type=='TEX_IMAGE':n.image=bpy.data.images.load(str(P/'textures/range-enamel.png'),check_existing=True)
enamel.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.49
# Retained opaque dark glass is replaced by a physically framed pane and a
# tinted window finish. Engine can use a dark translucent material for this slot.
glass.name='Range03_OvenGlass';bs=glass.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.085,.075,.061,1);bs.inputs['Roughness'].default_value=.23;bs.inputs['Metallic'].default_value=.13;bs.inputs['Transmission Weight'].default_value=.38;bs.inputs['IOR'].default_value=1.46

def remove(group,prefixes):
 keep=[]
 for o in groups[group]:
  if any(o.name.startswith(p) for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)
  else:keep.append(o)
 groups[group]=keep
remove('Body',['Toe kick','Knob bezel','Knob indicator','Knob','Enamel dial graduation','Drawer handle'])
# The old flat door slab occluded the window. Rebuild its four frame rails while
# retaining the old hinge at (0,-.363,.23), width, height and handle envelope.
for o in groups['Door']:bpy.data.objects.remove(o,do_unlink=True)
groups['Door']=[]
# Recessed stove structure, rather than a solid black block at the floor line.
box('Body','Recessed lower frame',(0,.015,.045),(.65,.54,.04),iron,.004)
for x in [-.318,.318]:
 for y in [-.265,.265]:
  cyl('Body','Adjustable steel foot',(x,y,.025),.021,.05,steel,verts=32)
  cyl('Body','Foot adjustment collar',(x,y,.047),.025,.009,iron,verts=32)
# Closed fluted knob, axis -Y, 44 mm grip diameter with a little front taper.
def knob(x):
 vs=[];fs=[];N=80;profile=[(-.361,.0195),(-.364,.022),(-.385,.0225),(-.391,.0215),(-.394,.020)]
 for y,r in profile:
  for i in range(N):a=i*2*math.pi/N;rr=r*(1+.035*math.cos(a*20));vs.append((x+rr*math.cos(a),y,.807+rr*math.sin(a)))
 for j in range(len(profile)-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]);me=bpy.data.meshes.new('Fluted bakelite knob');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Fluted bakelite knob',me);bpy.context.collection.objects.link(o);me.materials.append(bakelite);add('Body',o)
 for f in me.polygons:f.use_smooth=True
for x in [-.24,-.08,.08,.24]:
 cyl('Body','Stepped steel escutcheon',(x,-.356,.807),.031,.006,steel,(math.pi/2,0,0),64)
 cyl('Body','Escutcheon inset ring',(x,-.360,.807),.027,.003,gasket,(math.pi/2,0,0),64)
 knob(x)
 cyl('Body','Knob ceramic center',(x,-.3945,.807),.014,.0015,mark,(math.pi/2,0,0),48)
 box('Body','Knob dark pointer',(x,-.3957,.812),(.0027,.0009,.015),inside,.0002)
 # Longer off mark and a graded fan remain legible above each knob.
 for j in range(9):
  a=math.radians(-130+j*260/8);r=.036
  o=box('Body','Dial scale tick',(x+r*math.sin(a),-.355,.807+r*math.cos(a)),(.0015,.002,.0058 if j%2==0 else .0035),inside,.0002);o.rotation_euler.y=a
 box('Body','Dial off mark',(x,-.355,.847),(.004,.002,.003),inside,.0003)
# Bowed tubular handles have seated escutcheons, short supports and a shaped grip.
def tube(group,name,points,r,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;cu.resolution_u=16;cu.use_fill_caps=True;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);cu.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');add(group,bpy.context.object);return bpy.context.object
for x in [-.18,.18]:
 box('Body','Drawer handle seated plate',(x,-.353,.16),(.035,.008,.026),steel,.004)
 bar('Body','Drawer handle standoff',(x,-.356,.16),(x,-.368,.16),.006,steel)
tube('Body','Bowed drawer pull',[(-.19,-.364,.16),(-.15,-.369,.166),(0,-.371,.17),(.15,-.369,.166),(.19,-.364,.16)],.0075,steel)
# A single pressed enamel door frame with a real 400 x 250 mm opening. One
# continuous shell avoids four cabinet-like seams at the window corners.
def rectangle_ring(width,height,cz,r,S=8):
 pts=[]
 for cx,zz,start in [(width/2-r,cz+height/2-r,0),(-width/2+r,cz+height/2-r,90),(-width/2+r,cz-height/2+r,180),(width/2-r,cz-height/2+r,270)]:
  for i in range(S):
   a=math.radians(start+90*i/S);pts.append((cx+r*math.cos(a),zz+r*math.sin(a)))
 return pts
out=rectangle_ring(.66,.49,.475,.012);inn=rectangle_ring(.4,.25,.485,.006);N=len(out);vs=[(x,y,z) for y in [-.388,-.338] for ring in [out,inn] for x,z in ring];fs=[]
for i in range(N):
 j=(i+1)%N
 fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
me=bpy.data.meshes.new('One-piece pressed enamel door');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('One-piece pressed enamel door',me);bpy.context.collection.objects.link(o);me.materials.append(enamel);add('Door',o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
mod=o.modifiers.new('Pressed enamel eased edges','BEVEL');mod.width=.003;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);mod=o.modifiers.new('Pressed sheet normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
# The sharper pressed frame needs rear clearance over the two retained fixed
# hinge mounting plates. The old 12mm slab bevel cleared them earlier; the new
# 3mm bevel otherwise extended plate/frame penetration from 21.25 to 29.75deg
# on the installed rig (source hinge 0,-.38,.22). Keep the front skin and its UV
# mapping intact and pocket only the concealed rear-bottom hinge seats.
frame=o
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
def front_uv_signature(mesh):
 from collections import Counter
 uv=mesh.uv_layers.active
 return Counter((tuple(round(float(c),7) for c in mesh.vertices[mesh.loops[li].vertex_index].co),tuple(round(float(c),7) for c in uv.data[li].uv)) for p in mesh.polygons if all(mesh.vertices[i].co.y<-.38 for i in p.vertices) for li in p.loop_indices)
front_uv_before=front_uv_signature(frame.data)
for x in [-.29,.29]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-.337,.239));cut=bpy.context.object;cut.name='Temporary concealed hinge seat cutter';cut.dimensions=(.070,.040,.038);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cut.data.materials.append(enamel)
 bpy.ops.object.select_all(action='DESELECT');frame.select_set(True);bpy.context.view_layer.objects.active=frame
 mod=frame.modifiers.new('Concealed rear hinge pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cut,do_unlink=True)
assert front_uv_signature(frame.data)==front_uv_before,'hinge pockets altered visible front UV'
hinge_relief_proof={'front_uv_corners_unchanged':sum(front_uv_before.values()),'source_live_hinge_m':[0,-.38,.22],
 'pockets':[{'center_m':[x,-.337,.239],'size_m':[.070,.040,.038]} for x in [-.29,.29]],
 'minimum_front_skin_thickness_m':.031,'hinge_plate_lateral_clearance_each_side_m':.0025}
(P/'hinge-relief-source.json').write_text(json.dumps(hinge_relief_proof,indent=2)+'\n')
def window_frame(group,name,cy,width,height,barwidth,depth,mat):
 for x in [-width/2,width/2]:box(group,name+' upright',(x,cy,.485),(barwidth,depth,height+barwidth),mat,.002)
 for z in [.485-height/2,.485+height/2]:box(group,name+' crossrail',(0,cy,z),(width-barwidth,depth,barwidth),mat,.002)
window_frame('Door','Outer window gasket',-.390,.402,.252,.012,.009,gasket)
window_frame('Door','Pressed steel window trim',-.392,.402,.252,.004,.003,steel)
box('Door','Recessed tinted oven pane',(0,-.353,.485),(.395,.004,.245),glass,.004)
window_frame('Door','Inner window frame',-.329,.404,.254,.014,.008,inside)
for x in [-.20,.20]:
 for z in [.36,.61]:cyl('Door','Inner frame screw',(x,-.3245,z),.0037,.002,steel,(math.pi/2,0,0),16)
for x in [-.29,.29]:cyl('Door','Hinge barrel',(x,-.363,.23),.014,.055,steel,(0,math.pi/2,0))
for x in [-.20,.20]:
 box('Door','Handle escutcheon',(x,-.391,.665),(.038,.010,.027),steel,.004)
 bar('Door','Handle support',(x,-.391,.665),(x,-.410,.671),.007,steel)
tube('Door','Bowed steel oven pull',[(-.22,-.410,.665),(-.18,-.415,.674),(0,-.415,.679),(.18,-.415,.674),(.22,-.410,.665)],.009,steel)
# Dark central grip is a restrained heat-safe insert, with metal visible at ends.
tube('Door','Bakelite pull grip',[(-.13,-.415,.676),(0,-.415,.679),(.13,-.415,.676)],.0095,bakelite)
for x in [i*.031 for i in range(-7,8)]:box('Door','Door lower ventilation',(x,-.389,.275),(.018,.0018,.005),gasket,.0008)
for x in [-.302,.302]:bar('Door','Vertical heat seal',(x,-.331,.252),(x,-.331,.700),.003,gasket)
for z in [.252,.700]:bar('Door','Horizontal heat seal',(-.302,-.331,z),(.302,-.331,z),.003,gasket)
# All parts have an explicit UV0 before joining. Recalculate geometry winding;
# source primitives and tubes are closed, so no material has to be two-sided.
records=[];joined={}
for group,obs in groups.items():
 for o in obs:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  if not o.data.uv_layers:
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
  o.data.uv_layers.active.name='UVMap'
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name;assert all(e.is_manifold for e in bm.edges),o.name;bm.to_mesh(o.data);bm.free()
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_RANGE03_'+group;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);pv=Vector((0,-.363,.23)) if group=='Door' else Vector((0,0,0));bpy.context.scene.cursor.location=pv;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y')
 vv=[o.matrix_world@v.co for v in o.data.vertices];records.append({'file':o.name+'.fbx','source_pivot_m':list(pv),'source_bounds_m':[[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]],'slots':[m.name for m in o.data.materials]});joined[group]=o
(P/'assembly.json').write_text(json.dumps({'units':'metres','axes':['-Z','Y'],'parts':records,'unchanged':{'body_actor_cm':[382.5,50.03,0],'oven_root_cm':[382.5,88.03,22],'door_source_hinge_m':[0,-.363,.23],'burner_root_cm':[400.5,65.03,93.1],'flame_source_and_light':'unchanged','kettle_root_cm':[367,61.03,91]},'changed':{'knob_front_source_y_m':-.39615,'old_knob_front_source_y_m':-.3815,'reason':'larger fluted 44mm grips; 14.7mm extra projection with unchanged centers'}},indent=2)+'\n')
contract=json.loads((P/'assembly.json').read_text());contract['unchanged']['installed_rotation_pivot_source_m']=[0,-.38,.22];contract['unchanged']['installed_oven_body_relative_cm']=[0,-38,-22];contract['changed']['concealed_hinge_relief']=hinge_relief_proof
(P/'assembly.json').write_text(json.dumps(contract,indent=2)+'\n')
sc=bpy.context.scene
if sc.world is None:sc.world=bpy.data.worlds.new('Studio')
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.28,.31,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
for loc,power,size in [((0,-3,4),550,4),((2,2,3),300,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.5,-2.8,1.7));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.54))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.32;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=900;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/ROUND3-RANGE-03.blend'))
sc.render.filepath=str(P/'previews/range03-closed.png');bpy.ops.render.render(write_still=True)
live_hinge=Vector((0,-.38,.22));joined['Door'].matrix_world=Matrix.Translation(live_hinge)@Matrix.Rotation(math.radians(85),4,'X')@Matrix.Translation(-live_hinge)@joined['Door'].matrix_world;sc.render.filepath=str(P/'previews/range03-open.png');bpy.ops.render.render(write_still=True)
print('RANGE03 EXPORTED',records)
