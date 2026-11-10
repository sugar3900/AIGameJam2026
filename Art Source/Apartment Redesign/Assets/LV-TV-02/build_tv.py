"""FIX031. Exact original stand-only rebuild plus tabletop walnut television. Source metres, -Y front."""
from pathlib import Path
import bpy,bmesh,math,json,shutil,sys
RENDER="--skip-render" not in sys.argv
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parent;OLD=R.parent/'LV-TV-01'
for d in ('models','textures','previews'):(R/d).mkdir(exist_ok=True)
# Execute only original stand and door construction, no TV body, rendering or original writes.
original=(OLD/'model/build_tv.py').read_text();prefix=original.split('# TV case is a solid rounded shell')[0]
ns={'__file__':str(OLD/'model/build_tv.py')};exec(compile(prefix,str(OLD/'model/build_tv.py'),'exec'),ns)
for group in ns['COL'].values():
 for o in group:ns['plane_uv'](o)
stand_parts=list(ns['COL']['body']);doors=ns['COL']['left']+ns['COL']['right']
G={'Stand':stand_parts,'Housing':[],'Screen':[]}
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
# Bake old wood's documented linear tint into a reusable direct albedo image. Do not rely on FBX node translation.
raw=bpy.data.images.load(str(OLD/'textures/walnut-painted.png'),check_existing=True)
a=np.array(raw.pixels[:],dtype=np.float32).reshape(-1,4);rgb=a[:,:3];linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)*np.array([.25,.23,.14]);a[:,:3]=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055);im=bpy.data.images.new('T_TV02_Walnut',width=raw.size[0],height=raw.size[1]);im.pixels.foreach_set(a.ravel());im.filepath_raw=str(R/'textures/T_TV02_Walnut.png');im.file_format='PNG';im.save();im.pack()
shutil.copyfile(OLD/'textures/walnut-painted.png',R/'textures/walnut-painted.png')

def mat(n,c,rough=.5,metal=0,image=None):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if image:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
wood=mat('TV02_WalnutVeneer',(.23,.10,.034),.55,image=im)
edge=mat('TV02_EndGrainTrim',(.15,.065,.025),.59,image=im)
black=mat('TV02_Bakelite',(.029,.026,.022),.50)
gasket=mat('TV02_CRTSeal',(.012,.015,.012),.85)
brass=mat('TV02_AgedChampagneMetal',(.39,.30,.17),.40,.65)
letter=mat('TV02_DialIvory',(.64,.60,.46),.58)
cloth=mat('TV02_SpeakerCloth',(.14,.125,.085),.95)
back=mat('TV02_BackBoard',(.065,.044,.027),.9)
vent=mat('TV02_VentDark',(.009,.010,.008),.95)
screenmat=mat('TV02_CRTGlass',(.035,.048,.042),.19,.08)
# Small woven albedo for speaker; true dark recessed panel under slats.
N=256;yy,xx=np.mgrid[0:N,0:N];v=.018*np.sin(xx*math.tau/4)*np.sin(yy*math.tau/4)+.012*np.sin((xx+yy)*math.tau/17)
pix=np.ones((N,N,4),dtype=np.float32)
for j,c in enumerate((.17,.15,.105)):pix[:,:,j]=c+v
ci=bpy.data.images.new('T_TV02_SpeakerWeave',width=N,height=N);ci.pixels.foreach_set(pix.ravel());ci.filepath_raw=str(R/'textures/T_TV02_SpeakerWeave.png');ci.file_format='PNG';ci.save();ci.pack();node=cloth.node_tree.nodes.new('ShaderNodeTexImage');node.image=ci;cloth.node_tree.links.new(node.outputs['Color'],cloth.node_tree.nodes['Principled BSDF'].inputs['Base Color'])

def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def reg(o,n,m,g='Housing'):
 o.name=n;o.data.materials.append(m);G[g].append(o);return o

def box(n,loc,dim,m,bev=.003,g='Housing'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  b=o.modifiers.new('Small joinery bevel','BEVEL');b.width=min(bev,min(dim)*.3);b.segments=3;bpy.ops.object.modifier_apply(modifier=b.name)
  w=o.modifiers.new('Face normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=w.name)
 return reg(o,n,m,g)

def cylinder(n,loc,r,d,m,verts=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d,location=loc,rotation=(math.pi/2,0,0));o=bpy.context.object
 b=o.modifiers.new('Turned rim','BEVEL');b.width=.001;b.segments=2;active(o);bpy.ops.object.modifier_apply(modifier=b.name);return reg(o,n,m)

# Flat-bottom stepped plinth rests at64.75cm. Cabinet back <=20.8cm (2.2cm off stand edge).
box('Lower plinth',(0,-.002,.661),(1.015,.418,.027),edge,.005)
box('Plinth upper step',(0,-.002,.682),(1.00,.412,.016),wood,.004)
box('Cabinet left side',(-.477,.003,.978),(.038,.400,.584),wood,.005)
box('Cabinet right side',(.477,.003,.978),(.038,.400,.584),wood,.005)
box('Cabinet roof',(0,.003,1.270),(.992,.400,.035),wood,.005)
box('Crown lower bead',(0,-.002,1.292),(1.018,.416,.015),edge,.004)
box('Crown top',(0,-.002,1.306),(1.035,.424,.016),wood,.004)
box('Lower front rail',(0,-.197,.709),(.956,.032,.042),wood,.004)
for x in (-.456,.456):box('Front stile',(x,-.199,.987),(.022,.030,.52),edge,.003)
# Back cover has physical slots via separated horizontal strips, recessed within the cabinet.
box('Back board lower',(0,.198,.805),(.91,.014,.23),back)
box('Back board upper',(0,.198,1.172),(.91,.014,.15),back)
for i in range(9):box('Back ventilation strip',(0,.198,.932+i*.016),(.91,.014,.008),back,.001)
box('Back inner darkness',(0,.183,1.0),(.90,.006,.25),vent,0)
for x in (-.426,.426):
 for z in (.77,1.21):cylinder('Rear fixing',(x,.207,z),.0045,.002,brass,16)
# TV face: a dark recessed bezel around a curved CRT, never a solid block behind the screen.
def contour(rx,rz,n=96,p=.5,cx=-.105,cz=.992):
 return [(cx+rx*math.copysign(abs(math.cos(i*math.tau/n))**p,math.cos(i*math.tau/n)),cz+rz*math.copysign(abs(math.sin(i*math.tau/n))**p,math.sin(i*math.tau/n))) for i in range(n)]

def ring(n,loops,m):
 # loops[(rx,rz,y)] trace closed annular cross section.
 N=96;vs=[];fs=[]
 for rx,rz,y in loops:vs.extend((x,y,z) for x,z in contour(rx,rz))
 for k in range(len(loops)):
  a=k*N;b=((k+1)%len(loops))*N
  for i in range(N):j=(i+1)%N;fs.append((a+i,a+j,b+j,b+i))
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
 for p in me.polygons:p.use_smooth=True
 return reg(o,n,m)
ring('Recessed Bakelite CRT funnel',[(.341,.255,-.201),(.333,.249,-.208),(.303,.211,-.157),(.301,.209,-.142),(.341,.255,-.14)],black)
ring('Thin champagne bezel inlay',[(.340,.254,-.209),(.337,.251,-.210),(.337,.251,-.207),(.340,.254,-.206)],brass)
ring('CRT rubber edge',[(.305,.213,-.157),(.297,.205,-.151),(.297,.205,-.137),(.305,.213,-.141)],gasket)
# One closed lens. Curved face centre at y-.183, rim y-.143, all behind the front rim y-.210.
N=96;K=12;vs=[(-.105,-.183,.992)];fs=[]
for k in range(1,K+1):
 t=k/K
 for x,z in contour(.299*t,.207*t):vs.append((x,-.143-.040*(1-t*t),z))
for i in range(N):fs.append((0,1+i,1+(i+1)%N))
for k in range(1,K):
 a=1+(k-1)*N;b=1+k*N
 for i in range(N):j=(i+1)%N;fs.append((a+i,b+i,b+j,a+j))
start=len(vs)
for x,z in contour(.299,.207):vs.append((x,-.132,z))
a=1+(K-1)*N
for i in range(N):j=(i+1)%N;fs.append((a+i,start+i,start+j,a+j))
fs.append(tuple(range(start,start+N)))
me=bpy.data.meshes.new('CRT glass');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new('Single curved CRT glass',me);bpy.context.collection.objects.link(o);reg(o,o.name,screenmat,'Screen')
for p in me.polygons:p.use_smooth=True
# Control/speaker section: recess dark face behind narrow metal surround.
box('Control inset',(.344,-.166,1.080),(.185,.018,.332),black,.003)
for x in (.246,.442):box('Control side rim',(x,-.199,.995),(.008,.014,.51),brass,.0015)
for z in (.740,1.25):box('Control rim',(.344,-.199,z),(.204,.014,.008),brass,.0015)
for z,r in ((1.15,.043),(1.018,.034)):
 cylinder('Dial recessed seat',(.344,-.179,z),r+.009,.008,brass)
 cylinder('Knurled dial',(.344,-.195,z),r,.028,black)
 cylinder('Dial metal inset',(.344,-.211,z),r*.69,.003,brass)
 box('Dial bar',(.344,-.217,z),(.012,.012,r*1.2),black,.003)
 for i in range(12):
  a=i*math.tau/12;x=.344+(r+.015)*math.sin(a);zz=z+(r+.015)*math.cos(a)
  o=box('Ivory dial tick',(x,-.178,zz),(.0014,.0015,.004),letter,0);o.rotation_euler.y=a
 for i in range(28):
  a=i*math.tau/28;x=.344+r*math.sin(a);zz=z+r*math.cos(a)
  o=box('Fine knob knurl',(x,-.195,zz),(.002,.020,.002),brass,.0003)
# Two little ancillary controls above woven speaker panel.
for x in (.293,.395):
 cylinder('Small control collar',(x,-.178,.924),.012,.005,brass)
 cylinder('Small control knob',(x,-.193,.924),.008,.025,black)
box('Speaker cloth recessed',(.344,-.149,.825),(.166,.008,.137),cloth,.001)
for i in range(14):box('Inset speaker horizontal louvre',(.344,-.166,.762+i*.0094),(.164,.012,.0028),brass,.0007)
for z in (.749,.900):box('Speaker inset border',(.344,-.180,z),(.17,.008,.004),brass,.001)
# Readable small generic label, no real brand.
cu=bpy.data.curves.new('Television mark','FONT');cu.body='TELEVISION';cu.size=.009;cu.align_x='CENTER';cu.extrude=.00015
ob=bpy.data.objects.new('Television mark',cu);bpy.context.collection.objects.link(ob);ob.location=(.344,-.179,1.222);ob.rotation_euler=(math.pi/2,0,0);active(ob);bpy.ops.object.convert(target='MESH');reg(ob,ob.name,letter)
# UVs orient grain along each board, retain original stand UVs exactly.
for group in ('Housing','Screen'):
 for ob in G[group]:
  active(ob);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
  if not ob.data.uv_layers:ob.data.uv_layers.new(name='UVMap')
  for p in ob.data.polygons:
   ax=max(range(3),key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    v=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co
    if group=='Screen':uv=((v.x+.404)/.598,(v.z-.785)/.414)
    elif ax==0:uv=(v.y*1.7+.5,v.z*1.7)
    elif ax==1:uv=(v.x*1.5+.5,v.z*1.5)
    else:uv=(v.x*1.5+.5,v.y*1.5+.5)
    ob.data.uv_layers.active.data[li].uv=uv
# Export 3 assembled-origin meshes. Existing door FBXs are retained unchanged, not re-exported.
reports=[]
for key,parts in G.items():
 active(parts[0])
 for o in parts:o.select_set(True)
 bpy.ops.object.join();ob=bpy.context.object
 if key=='Housing':
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bad=[f for f in bm.faces if f.calc_area()<=1e-12];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 ob.name='LV_TV02_'+key;s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');G[key]=[ob]
 xyz=[ob.matrix_world@v.co for v in ob.data.vertices];reports.append({'mesh':ob.name,'min':[min(p[i] for p in xyz) for i in range(3)],'max':[max(p[i] for p in xyz) for i in range(3)],'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons),'slots':[m.name for m in ob.data.materials]})
 active(ob);bpy.ops.export_scene.fbx(filepath=str(R/'models'/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,path_mode='RELATIVE')
(R/'geometry.json').write_text(json.dumps(reports,indent=2)+'\n')
assert abs(reports[0]['max'][2]-.6475)<.00001
assert abs(reports[1]['min'][2]-.6475)<.00001
assert reports[1]['max'][2]<1.45 and reports[1]['max'][0]<.55 and reports[1]['min'][0]>-.55
assert reports[1]['max'][1]<.22 and reports[1]['min'][1]>-.23
# Studio renders. On/off use the same screen with soft radial phosphor, off-zero emission.
s.world=bpy.data.worlds.new('Neutral studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
bpy.ops.object.camera_add(location=(2,-3.4,1.9));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=1.68;s.camera=cam

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
aim(cam,(0,0,.70))
for pos,power,size in [((1,-3,3),180,3),((-2,-1,2),120,2),((0,2,3),100,2)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;aim(o,(0,0,.85))
box('Studio ground',(0,0,-.022),(200,200,.04),mat('Studio',(.19,.19,.19),.95),0,g='Housing') # after export, presentation only
s.render.filepath=str(R/'previews/off.png');bpy.ops.render.render(write_still=True) if RENDER else None
t=screenmat.node_tree;p=t.nodes['Principled BSDF'];uv=t.nodes.new('ShaderNodeTexCoord');dist=t.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0);t.links.new(uv.outputs['UV'],dist.inputs[0]);ramp=t.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.10;ramp.color_ramp.elements[0].color=(1,.90,.74,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.16,.19,.15,1);t.links.new(dist.outputs['Value'],ramp.inputs[0]);t.links.new(ramp.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.7
s.render.filepath=str(R/'previews/on.png');bpy.ops.render.render(write_still=True) if RENDER else None
p.inputs['Emission Strength'].default_value=0;cam.location=(1.5,-2.6,1.48);cam.data.ortho_scale=1.20;aim(cam,(0,-.05,.995));s.render.filepath=str(R/'previews/face-depth.png');bpy.ops.render.render(write_still=True) if RENDER else None
cam.location=(0,-3,1.05);cam.data.ortho_scale=1.23;aim(cam,(0,-.04,.98));s.render.filepath=str(R/'previews/front.png');bpy.ops.render.render(write_still=True) if RENDER else None
# Save complete source; ground is presentation-only, existing doors kept in place.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/LV-TV-02.blend'))
print('FIX031 BUILT',reports)
