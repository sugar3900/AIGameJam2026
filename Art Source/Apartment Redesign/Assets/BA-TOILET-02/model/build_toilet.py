"""FIX-023 additive toilet. Source metres, Z up, front -Y. CPU previews only."""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color,rough=.4,metal=0,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
ivory=material('Painted_Ivory_Enamel',(.8,.73,.60),.36,texture=P/'textures/painted-ivory.png')
brass=material('Aged_Brass',(.40,.25,.11),.32,.72)
dark=material('Trap_Interior',(.10,.087,.065),.6)
water=material('Toilet_Standing_Water',(.72,.83,.82),.09)
wp=water.node_tree.nodes.get('Principled BSDF');wp.inputs['Transmission Weight'].default_value=.85;wp.inputs['IOR'].default_value=1.333
rubber=material('Ivory_Rubber_Bumpers',(.57,.54,.46),.8)

def mesh(name,verts,faces,mat,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 if mat:me.materials.append(mat)
 for f in me.polygons:f.use_smooth=smooth
 if faces:
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 return o

def loft(name,rings,mat,cy=0,clip=None,n=64,square=False,closed=False):
 v=[]
 for rx,ry,z in rings:
  for i in range(n):
   t=2*math.pi*i/n;c,s=math.cos(t),math.sin(t)
   if square:c=math.copysign(abs(c)**.45,c);s=math.copysign(abs(s)**.45,s)
   y=cy+ry*s
   if clip is not None:y=min(clip,y)
   v.append((rx*c,y,z))
 f=[]
 for j in range(len(rings)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
 if closed:
  j=len(rings)-1
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(i+1)%n,i))
 else:f.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))])
 return mesh(name,v,f,mat)

def box(name,loc,dims,mat,bev=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  m=o.modifiers.new('Soft cast edges','BEVEL');m.width=bev;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
 o.data.materials.append(mat);o.select_set(False);return o

def cyl(name,loc,r,depth,mat,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name
 if axis=='X':o.rotation_euler.y=math.pi/2
 elif axis=='Y':o.rotation_euler.x=math.pi/2
 o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 o.select_set(False);return o

def ball(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
 o.select_set(False);return o

def join(name,obs,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.select_set(False);return o

# Floor base extends back beneath tank, within original y=.345 rear datum.
body=[]
body.append(loft('Pedestal foot',[(.16,.265,0),(.18,.287,.018),(.18,.287,.045),(.158,.265,.065)],ivory,cy=.018))
body.append(loft('Front pedestal',[(.137,.158,.045),(.13,.15,.11),(.118,.135,.24),(.17,.20,.35),(.20,.235,.38),(.15,.18,.36),(.08,.10,.24),(.05,.06,.13),(.05,.06,.045)],ivory,cy=-.075,closed=True))
body.append(loft('Rear tank support',[(.125,.104,.045),(.119,.10,.09),(.103,.086,.27),(.118,.092,.43),(.155,.10,.50)],ivory,cy=.225,square=True))
# Bowl: outer shell flows over lip and down into trap throat, not an opaque cap across the basin.
body.append(loft('Bowl shell and trap',[(.11,.13,.19),(.17,.20,.30),(.22,.255,.35),(.251,.286,.415),(.255,.29,.45),(.247,.282,.468),(.205,.237,.468),(.194,.222,.447),(.17,.198,.397),(.12,.146,.32),(.084,.104,.265),(.043,.054,.225),(.035,.045,.17),(.032,.041,.145)],ivory,cy=-.075,closed=True))
# A smaller deep dark terminus belongs to the trap below the water; never floor-visible.
body.append(loft('Shadow in waste passage',[(.032,.041,.146),(.028,.036,.142)],dark,cy=-.075))
seat=loft('Fixed oval seat',[(.226,.26,.469),(.236,.273,.477),(.236,.273,.488),(.228,.264,.496),(.169,.199,.496),(.161,.19,.488),(.161,.19,.478),(.169,.199,.469)],ivory,cy=-.095,clip=.115,closed=True);body.append(seat)
# Tank and plain lift-off lid. No button or finial.
body.append(loft('Cistern',[(.19,.075,.495),(.205,.083,.505),(.214,.09,.53),(.22,.095,.56),(.22,.095,.845),(.214,.092,.88),(.20,.082,.89)],ivory,cy=.235,square=True))
body.append(loft('Plain cistern lid',[(.218,.10,.875),(.237,.11,.885),(.24,.11,.90),(.225,.102,.916),(.20,.09,.921)],ivory,cy=.235,square=True))
# Front-facing flush paddle: escutcheon hugs tank face rather than side peg.
body.append(cyl('Flush rosette',(-.145,.137,.794),.020,.012,brass,'Y'))
lever=box('Front flush paddle',(-.108,.121,.794),(.086,.014,.021),brass,.009);lever.rotation_euler.y=-.07;body.append(lever)
body.append(ball('Lever ivory fingertip',(-.073,.119,.797),(.019,.009,.013),ivory))
for x in (-.13,.13):body.append(ball('Foot fixing',(x,-.10,.063),(.012,.012,.006),brass))
# Connected hinge with moving barrel, fixed cheeks and support posts.
HINGE=(0,.110,.516)
for x in (-.13,.13):
 body.append(box('Hinge anchor',(x,.108,.480),(.044,.045,.027),brass,.006))
 for dx in (-.019,.019):
  body.append(box('Hinge cheek',(x+dx,.110,.500),(.008,.023,.036),brass,.004))
  body.append(cyl('Fixed hinge end',(x+dx,.110,.516),.011,.008,brass,'X'))
lidparts=[]
lidparts.append(loft('Matched oval cover',[(.224,.26,.506),(.233,.271,.513),(.233,.271,.520),(.225,.263,.530),(.205,.243,.534)],ivory,cy=-.095,clip=.108))
for x in (-.13,.13):
 lidparts.append(cyl('Moving hinge barrel',(x,.110,.516),.0105,.028,brass,'X'))
 lidparts.append(box('Connected hinge leaf',(x,.085,.515),(.026,.05,.012),brass,.003))
for x in (-.145,.145):lidparts.append(ball('Lid underside bumper',(x,-.245,.502),(.017,.012,.006),rubber))
base=join('BA_Toilet02_Body',body,(0,0,0));lid=join('BA_Toilet02_Lid',lidparts,HINGE)
# Standing water at z=.275, slightly smaller than inner bowl cross-section. Separate static mesh.
w=loft('BA_Toilet02_Water',[(.088,.109,.2745),(.088,.109,.275)],water,cy=-.075)
w=join('BA_Toilet02_Water',[w],(0,0,0))
# Triangulate with UV preservation; clipped rear profiles have collinear zero-area
# fragments at the straight seat/lid edge. Remove only those fragments.
for obj in [base,lid,w]:
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bad=[f for f in bm.faces if f.calc_area()<1e-12]
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 bm.normal_update();bm.to_mesh(obj.data);bm.free();obj.data.update()
# Explicit simple collision: separate concave bowl sectors, pedestal/tank pieces; water none.
ucx=[]
def hull_box(target,loc,dims):
 o=box('UCX_'+target+'_'+str(sum(x.name.startswith('UCX_'+target) for x in ucx)).zfill(2),loc,dims,ivory,0);ucx.append(o);return o
hull_box(base.name,(0,.018,.035),(.36,.574,.07));hull_box(base.name,(0,-.075,.215),(.27,.31,.35));hull_box(base.name,(0,.225,.27),(.29,.205,.46));hull_box(base.name,(0,.235,.705),(.44,.19,.42));hull_box(base.name,(0,.235,.90),(.48,.22,.042))
for i in range(16):
 a=2*math.pi*i/16;v=[]
 for z,rx,ry,ix,iy in [(.32,.19,.225,.12,.146),(.488,.256,.291,.16,.19)]:
  for t,rrx,rry in [(a,rx,ry),(a+2*math.pi/16,rx,ry),(a+2*math.pi/16,ix,iy),(a,ix,iy)]:v.append((rrx*math.cos(t),-.075+rry*math.sin(t),z))
 o=mesh('UCX_'+base.name+'_'+str(5+i).zfill(2),v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],None,False);ucx.append(o)
# One convex collision hull over cover and its hinge gives trace reach throughout the animation.
verts=[tuple(lid.matrix_world@v.co) for v in lid.data.vertices]
o=mesh('UCX_'+lid.name+'_00',verts,[],None,False)
bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.convex_hull();bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
bpy.context.scene.cursor.location=HINGE;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.select_set(False);ucx.append(o)
# Bounds and sampled geometric sweep. Tank begins y>=.140 at relevant height.
def bounds(obj):
 vs=[obj.matrix_world@v.co for v in obj.data.vertices];return {'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]}
report={'units':'metres','source_front':'-Y','body_origin':[0,0,0],'lid_pivot':list(HINGE),'lid_axis':'local X','closed_degrees':0,'open_degrees':-85,'water_z':.275,'bounds':{o.name:bounds(o) for o in [base,lid,w]},'ucx_counts':{'body':21,'lid':1,'water':0},'sweep':[]}
for deg in range(86):
 R=Matrix.Rotation(math.radians(-deg),4,'X');world=[Vector(HINGE)+R@v.co for v in lid.data.vertices]
 hits=[v for v in world if v.y>=.14 and v.z>=.495 and abs(v.x)<.22 and v.z<.89]
 assert not hits,(deg,'tank overlap',len(hits))
 report['sweep'].append({'degrees':-deg,'tank_aabb_hits':len(hits),'max_y':max(v.y for v in world)})
# Save and export assembly-space FBX, collision naming recognized by legacy importer.
for obj in [base,lid,w]:
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
 for h in ucx:
  if h.name.startswith('UCX_'+obj.name+'_'):h.select_set(True)
 bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/f'{obj.name}.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,path_mode='RELATIVE')
for h in ucx:h.hide_render=True;h.hide_set(True)
(P/'validation/build-report.json').write_text(json.dumps(report,indent=2)+'\n')
# Modest CPU render, no GPU context or editor.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=3
scene.render.resolution_x=720;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.32,.32,.32,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
floor=box('Preview ground',(0,0,-.025),(200,200,.04),material('Preview floor',(.16,.14,.12),.9),0)
for loc,energy,size in [((1,-2,2.5),110,2.5),((-1,-.5,1.8),65,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.35,-1.8,1.4));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=1.22;scene.camera=cam
cam.rotation_euler=(Vector((0,0,.45))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-TOILET-02.blend'))
if '--no-render' not in sys.argv:
 for name,deg,loc,target in [('closed',0,(1.35,-1.8,1.4),(0,0,.45)),('open',-85,(1.1,-1.65,1.65),(0,0,.45)),('side-open',-85,(2,-.1,1.1),(0,0,.45)),('top-open',-85,(.3,-.9,2.1),(0,-.05,.4))]:
  lid.rotation_euler.x=math.radians(deg);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(P/'previews'/f'toilet-{name}.png');bpy.ops.render.render(write_still=True)
print('BUILD COMPLETE',P)
