"""Headless slipper pair with hollow sewn uppers, quilt lining and surface embroidery."""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
random.seed(16)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,tex=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.88
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(R/'textures'/tex));n.image.pack();m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
velvet=mat('Slipper_WornBurgundy',(1,1,1),'T_Slipper_Velvet.png');lining=mat('Slipper_QuiltedOatmeal',(1,1,1),'T_Slipper_Quilt.png');binding=mat('Slipper_RoseBinding',(.29,.12,.10));sole=mat('Slipper_LeatherSole',(.13,.065,.03));thread=mat('Slipper_FadedFlaxThread',(.53,.36,.19));emb=mat('Slipper_Embroidery',(.63,.47,.27))
def mesh(name,v,f,m):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(m)
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   x,y,z=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(.5+x/.18,.5-y/(.18 if m==lining else .28))
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 return o

def cord(name,pts,r,m):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=1;c.resolution_u=1;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,q in zip(s.points,pts):p.co=(*q,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(m);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False);o.data.uv_layers.new(name='UVMap');return o

def w(s):return (.041+.014*s)*(max(0,math.sin(math.pi*s))**.42)
def shift(s,hand):return hand*(.004*math.sin(math.pi*s)-.003*math.sin(2*math.pi*s))
def upper(s,t,hand):
 y=.14-.28*s;ww=w(s);x=shift(s,hand)+ww*math.cos(t)
 height=.057*max(0,math.sin(math.pi/2*(1-s)/.57))**.55
 z=.014+height*math.sin(t)**.8
 z+=.0012*math.sin(s*72+t*7)*math.sin(t)**2*math.sin(math.pi*(s-.43)/.57)**2
 return (x,y,z)
def surface_z(x,y,hand):
 s=(.14-y)/.28;xx=(x-shift(s,hand))/w(s);return upper(s,math.acos(max(-.999,min(.999,xx))),hand)[2]+.00055

parts=[]
for hand in [-1,1]:
 before=set(bpy.context.scene.objects)
 # Continuous foot outline. Longitudinal profile includes a slightly broader ball and shaped inner arch.
 outline=[]
 for i in range(160):
  th=2*math.pi*i/160;s=(1-math.cos(th))/2
  outline.append((shift(s,hand)+math.copysign(w(s),math.sin(th)),.14-.28*s))
 for name,z0,z1,material,inset in [('Leather outsole',.001,.008,sole,1),('Quilted footbed',.008,.014,lining,.96)]:
  v=[(x*inset,y,z) for z in [z0,z1] for x,y in outline];f=[];N=len(outline)
  f.append(tuple(reversed(range(N))));f.append(tuple(range(N,2*N)))
  for i in range(N):j=(i+1)%N;f.append((i,j,j+N,i+N))
  o=mesh(name,v,f,material);b=bpy.context.view_layer.objects.active=o;be=o.modifiers.new('Soft sewn sole edge','BEVEL');be.width=.0015;be.segments=3;bpy.ops.object.modifier_apply(modifier=be.name)
 # Hollow vamp, with a thick lined opening at the instep. Separate inner material is built into shell.
 ns,nt=55,40;v=[];f=[]
 for i in range(ns+1):
  s=.43+(.9999-.43)*i/ns
  for j in range(nt+1):v.append(upper(s,math.pi*j/nt,hand))
 for i in range(ns):
  for j in range(nt):a=i*(nt+1)+j;f.append((a,a+nt+1,a+nt+2,a+1))
 o=mesh('Hollow velvet upper',v,f,velvet);o.data.materials.append(lining);bpy.context.view_layer.objects.active=o;so=o.modifiers.new('Lined fabric thickness','SOLIDIFY');so.thickness=.002;so.offset=-1;so.material_offset=1;bpy.ops.object.modifier_apply(modifier=so.name)
 opening=[upper(.43,math.pi*j/100,hand) for j in range(101)];cord('Instep seam binding',opening,.0018,binding)
 cord('Footbed welt',[(x*.98,y,.013) for x,y in outline+[outline[0]]],.0013,binding)
 # Tiny interrupted stitches around outsole: genuine short thread marks, not floating decorations.
 for i in range(0,len(outline),2):
  x,y=outline[i];xx,yy=outline[(i+1)%len(outline)];cord('Welt stitching',[(x*1.002,y,.0092),(xx*1.002,yy,.0092)],.00028,thread)
 # Embroidered branching sprig on vamp, conforming to its actual surface.
 def stitch(points,r=.00035):cord('Botanical embroidery',[(x,y,surface_z(x,y,hand)) for x,y in points],r,emb)
 stem=[(-.009+.018*t,-.042-.070*t) for t in [i/24 for i in range(25)]];stitch(stem,.00045)
 for j in range(6):
  t=.12+j*.135;cx=-.009+.018*t;cy=-.042-.070*t;sgn=1 if j%2 else -1
  tip=(cx+sgn*.015,cy-.010);stitch([(cx,cy),((cx+tip[0])/2,cy-.006),tip])
  for k in range(3):
   q=.4+k*.2;bx=cx+(tip[0]-cx)*q;by=cy+(tip[1]-cy)*q
   leaf=[]
   for n in range(17):
    a=2*math.pi*n/16;leaf.append((bx+sgn*.0035*math.cos(a),by+.0018*math.sin(a)))
   stitch(leaf,.00035)
 # Pair is casually splayed, no shared tray; transforms are baked to pair-local space.
 created=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH'];angle=math.radians(hand*5);dx=hand*.070;dy=.008 if hand==1 else -.008
 for o in created:
  for p in o.data.vertices:
   x,y,z=p.co;p.co=(x*math.cos(angle)-y*math.sin(angle)+dx,x*math.sin(angle)+y*math.cos(angle)+dy,z)
 bpy.ops.object.select_all(action='DESELECT')
 for o in created:o.select_set(True)
 bpy.context.view_layer.objects.active=created[0];bpy.ops.object.join();o=bpy.context.object;o.name='HA_Slipper_Left' if hand<0 else 'HA_Slipper_Right';parts.append(o);bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(R/'model/HA_SLIPPERS_01.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/HA-SLIPPERS-01.blend'))
coords=[o.matrix_world@v.co for o in parts for v in o.data.vertices];bounds={'min':[min(v[i] for v in coords) for i in range(3)],'max':[max(v[i] for v in coords) for i in range(3)]}
materials={m.name:{'base_color_linear':list(m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value)[:3],'roughness':.88,'base_color_texture':next(('textures/'+Path(n.image.filepath).name for n in m.node_tree.nodes if n.type=='TEX_IMAGE'),None)} for o in parts for m in o.data.materials}
(R/'assembly.json').write_text(json.dumps({'asset':'HA-SLIPPERS-01','fix':'FIX-016','units':'metres','origin':'pair floor center','up':'+Z','front_toes':'-Y','fbx_forward':'-Y','bounds':bounds,'parts':[{'name':o.name,'materials':[m.name for m in o.data.materials]} for o in parts],'materials':materials,'collision':'none; decorative floor textile','proposed_placement':{'unreal_location_cm':[1170,362,0],'yaw_degrees':90,'scale':[1,1,1],'retire_old_display_parts':['HA_ShoeTray','HA_Oxford_1','HA_Oxford_2','HA_SlipOn_1','HA_SlipOn_2'],'engine_verification':'bench/entry clearance and visual review pending'},'placement':'Replace old shoes and tray with ONE pair near entry; preserve doorway/bench clearance. Source pair center and floor datum, no old shoe-specific pivot offsets.'},indent=2)+'\n')
# Preview only
floor=mat('PREVIEW floor',(.23,.19,.14));bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(floor)
bpy.ops.object.light_add(type='AREA',location=(-.3,-.4,.8));bpy.context.object.data.energy=35;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=.8
bpy.ops.object.camera_add(location=(.36,-.52,.59));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.018))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.47;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1100;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world.color=(.2,.2,.2);s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'previews/pair.png');bpy.ops.render.render(write_still=True)
cam.location=(.02,.52,.30);cam.rotation_euler=(Vector((0,0,.025))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'previews/heel-openings.png');bpy.ops.render.render(write_still=True)
