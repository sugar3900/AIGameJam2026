"""FIX010: fitted entry door hardware and strikes. Preserve02 hinge/frame/slab.
Blender metres, Z up, source front/interior -Y. Builds new03 only.
"""
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent.parent;OLD=R.parent/'ARC-ENTRY-DOOR-02'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
audit={'cause':'Source fit, not Rev02 mirroring','old_knob_and_deadbolt_x_m':.382,'old_panel_bead_x_range_m':[.367,.383],'old_molding_back_to_slab_gap_m':.0075,'old_knob_plate_back_to_slab_gap_m':.0035,'old_deadbolt_plate_gap_m':.004,'old_strikes':'None authored','engine_frame_world_cm':[1200,452.5,0],'engine_frame_yaw':90,'engine_leaf_world_cm':[1196.5,403,0],'engine_leaf_yaw':90,'engine_scale':[1,1,1],'hinge_offset_source_m':[-.495,-.035,0],'hinge_offset_world_cm_after_Yflip_and_yaw90':[-3.5,-49.5,0],'placement_verdict':'Exactly matches fitted02 source hinge; no negative-scale mirror needed','original_source_sha256':hashlib.sha256((OLD/'model/ARC-ENTRY-DOOR-02.blend').read_bytes()).hexdigest()}
(R/'source-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
def mat(n,c,metal=0,rough=.78,img=None,mix=False):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if img:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures'/img),check_existing=True);t.image.pack()
  if mix:
   node=m.node_tree.nodes.new('ShaderNodeMixRGB');node.inputs[0].default_value=.35;node.inputs[2].default_value=(.85,.79,.68,1);m.node_tree.links.new(t.outputs['Color'],node.inputs[1]);m.node_tree.links.new(node.outputs[0],p.inputs['Base Color'])
  else:m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
paint=mat('Painted warm ivory',(.77,.69,.56),img='paint-selected.png',mix=True);brass=mat('Muted aged brass',(.31,.205,.075),.68,.46);wood=mat('Edge rub, warm timber',(.43,.29,.16),rough=.9);walnut=mat('Aged walnut entrance leaf',(.28,.13,.07),rough=.82,img='walnut-aged.png');dark=mat('Recess darkness',(.025,.018,.012),rough=.95)
groups={'Frame':[],'Leaf':[]}
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def uv(o):
 activate(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
def box(n,loc,dim,material,group,bevel=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;activate(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Eased edge','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 if material:o.data.materials.append(material)
 if group:groups[group].append(o)
 return o
def cylinder(n,loc,r,depth,material,group,axis='Z'):
 rot={'X':(0,math.pi/2,0),'Y':(math.pi/2,0,0),'Z':(0,0,0)}[axis];bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 groups[group].append(o);return o
def sphere(n,loc,r,material,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=r,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 groups[group].append(o);return o
def cut(o,loc,size):
 tool=box('CUTTER',loc,size,None,None,0);activate(o);mod=o.modifiers.new('Machined recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def screw_hole(o,loc):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0027,depth=.006,location=loc,rotation=(0,math.pi/2,0));tool=bpy.context.object;activate(o);mod=o.modifiers.new('Countersunk mounting hole','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def panel_molding(cx,z,h,s):
 # A continuous mitered ring replaces overlapping beveled strips at each corner.
 v=[]
 for yy,ww,hh in [(s*.034,.1755,h/2+.008),(s*.034,.1595,h/2-.008),(s*.025,.1755,h/2+.008),(s*.025,.1595,h/2-.008)]:
  v += [(cx-ww,yy,z-hh),(cx+ww,yy,z-hh),(cx+ww,yy,z+hh),(cx-ww,yy,z+hh)]
 f=[]
 for i in range(4):
  j=(i+1)%4;f += [(i,j,4+j,4+i),(8+i,12+i,12+j,8+j),(i,8+i,8+j,j),(4+i,4+j,12+j,12+i)]
 me=bpy.data.meshes.new('Mitered panel ring');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new('Continuous seated panel molding',me);bpy.context.collection.objects.link(o);o.data.materials.append(walnut);activate(o);mod=o.modifiers.new('Eased molding edges','BEVEL');mod.width=.0015;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);groups['Leaf'].append(o)
positive_jamb=None
for x in (-.51,.51):
 o=box('Jamb',(x,0,1.055),(.03,.12,2.11),paint,'Frame')
 if x>0:positive_jamb=o
 for y in (-.072,.072):box('Vertical casing',(x+(.03 if x>0 else -.03),y,1.06125),(.09,.025,2.1225),paint,'Frame',.002)
box('Top jamb',(0,0,2.125),(1.05,.12,.03),paint,'Frame')
for y in (-.072,.072):
 box('Head casing',(0,y,2.16),(1.17,.028,.075),paint,'Frame');box('Head crown',(0,y,2.208),(1.19,.038,.022),paint,'Frame')
slab=box('Unchanged walnut leaf slab',(0,0,1.047),(.976,.05,2.094),walnut,'Leaf',.004)
HX=.435
for s in (-1,1):
 # Applied moldings now seated against ±25mm faces, not hovering7.5mm away.
 for z,h in ((.375,.45),(1.37,1.18)):
  for cx in (-.2075,.2075):
   panel_molding(cx,z,h,s)
 box('Seated knob escutcheon',(HX,s*.0305,1),(.048,.011,.13),brass,'Leaf',.004)
 cylinder('Connected knob stem',(HX,s*.0495,1.025),.012,.029,brass,'Leaf','Y')
 sphere('Round brass knob',(HX,s*.069,1.025),.025,brass,'Leaf')
 for z in (.946,1.057):
  cylinder('Escutcheon screw',(HX,s*.0363,z),.0025,.001,brass,'Leaf','Y')
  box('Screw slot',(HX,s*.03685,z),(.0035,.0003,.0005),dark,'Leaf',.0001)
 cylinder('Seated deadbolt rose',(HX,s*.0305,1.20),.023,.011,brass,'Leaf','Y')
 if s<0:
  cylinder('Thumbturn shaft',(HX,-.038,1.20),.007,.010,brass,'Leaf','Y')
  box('Interior deadbolt thumbturn',(HX,-.046,1.20),(.034,.014,.010),brass,'Leaf',.0035)
 else:
  cap=cylinder('Exterior key cylinder',(HX,.038,1.20),.012,.004,brass,'Leaf','Y')
  cut(cap,(HX,.039,1.20),(.002,.012,.007))
  box('Recessed keyway darkness',(HX,.0362,1.20),(.0019,.0003,.0068),dark,'Leaf',.0002)
  # Keyhole below knob, centered on same latch stile.
  cylinder('Mortise keyhole eye',(HX,.0364,.972),.0023,.0005,dark,'Leaf','Y')
  box('Mortise keyhole slot',(HX,.0364,.9685),(.0028,.0005,.006),dark,'Leaf',.0002)
 cylinder('Seated peephole',(0,s*.030,1.57),.009,.010,brass,'Leaf','Y')
 cylinder('Peephole lens',(0,s*.0352,1.57),.004,.0006,dark,'Leaf','Y')
 for z,w in ((.06,.018),(.41,.015),(1.28,.013),(1.92,.02)):box('Subtle worn corner',(.477,s*.0255,z),(.003,.001,w),wood,'Leaf',.0003)
for z in (.28,1.05,1.82):
 cylinder('Unchanged hinge barrel',(-.495,-.035,z),.007,.075,brass,'Leaf');box('Static hinge plate',(-.510,-.066,z),(.03,.006,.065),brass,'Frame',.001)
# Latch and deadbolt share the exact leaf edge / jamb socket axis, source +X.
align=[]
for name,z,holeheight,holewidth,plateheight,throw in [('Latch',1.025,.022,.019,.085,.012),('Deadbolt',1.20,.026,.022,.078,.025)]:
 # Leaf faceplate sunk into a real edge recess, at X=.488 flush with the leaf.
 cut(slab,(.4875,0,z),(.006,.038,plateheight+.002))
 edgeplate=box(name+' edge faceplate',(.487,0,z),(.002,.036,plateheight),brass,'Leaf',.0007)
 cut(edgeplate,(.487,0,z),(.006,holewidth-.003,holeheight-.004))
 # Depiction defaults unlocked/retracted, preserving old swept envelope.
 box(name+' retracted tongue',(.482,0,z),(.012,holewidth-.005,holeheight-.006),brass,'Leaf',.001)
 for zz in (z-plateheight*.36,z+plateheight*.36):
  screw_hole(edgeplate,(.487,0,zz));cylinder(name+' edge screw',(.4876,0,zz),.0023,.0004,brass,'Leaf','X')
  box(name+' edge screw slot',(.48785,0,zz),(.0001,.0032,.0005),dark,'Leaf',0)
 # Seat strike plate in jamb and cut the actual pocket behind it.
 cut(positive_jamb,(.496,0,z),(.003,.047,plateheight+.003))
 cut(positive_jamb,(.5075,0,z),(.025,holewidth,holeheight))
 strike=box(name+' strike plate',(.496,0,z),(.002,.045,plateheight),brass,'Frame',.0007)
 cut(strike,(.496,0,z),(.006,holewidth,holeheight))
 box(name+' pocket back',(.5197,0,z),(.0004,holewidth-.001,holeheight-.001),dark,'Frame',0)
 for zz in (z-plateheight*.36,z+plateheight*.36):
  screw_hole(strike,(.496,0,zz))
  cylinder(name+' countersunk strike screw',(.4958,0,zz),.0023,.0004,brass,'Frame','X')
  box(name+' strike screw slot',(.49555,0,zz),(.0001,.0032,.0005),dark,'Frame',0)
 align.append({'identity':name.lower(),'knob_axis_source_frame_m':[HX,0,z],'leaf_edge_source_frame_m':[.488,0,z],'strike_plane_source_frame_m':[.495,0,z],'strike_hole_size_yz_m':[holewidth,holeheight],'edge_gap_m':.007,'default_bolt_state':'flush/retracted','optional_throw_m':throw,'extended_tip_x_m':.488+throw,'jamb_engagement_m':throw-.007,'axis_source':'+X','world_strike_cm_at_current_Rev02':[1200,502,z*100]})
# Full knob/rose footprint stays inside the unbroken latch stile.
assert HX-.025>.383 and HX+.025<.488
objs={};hullrecords={}
for group,parts in groups.items():
 for o in parts:
  old=list(o.data.materials);fallback=next(m for m in old if m is not None);face_materials=[old[p.material_index] or fallback for p in o.data.polygons];unique=list(dict.fromkeys(m for m in old if m is not None));o.data.materials.clear()
  for m in unique:o.data.materials.append(m)
  for p,m in zip(o.data.polygons,face_materials):p.material_index=unique.index(m)
  uv(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='ARC_Entry_Door03_'+group;objs[group]=o
 # Retain existing material slot indices; append new recess material last.
 old=list(o.data.materials);face_materials=[old[p.material_index] for p in o.data.polygons];ordered=[walnut,brass,wood,dark] if group=='Leaf' else [paint,brass,dark];o.data.materials.clear()
 for m in ordered:o.data.materials.append(m)
 for p,m in zip(o.data.polygons,face_materials):p.material_index=ordered.index(m)
 bpy.context.scene.cursor.location=(-.495,-.035,0) if group=='Leaf' else (0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');loc=o.location.copy();o.location=(0,0,0)
 specs=[((.495,.035,1.047),(.976,.05,2.094))] if group=='Leaf' else [((-.51,0,1.055),(.03,.12,2.11)),((.51,0,1.055),(.03,.12,2.11)),((0,0,2.125),(1.05,.12,.03))]
 hulls=[]
 for i,(center,size) in enumerate(specs):co=box(f'UCX_{o.name}_{i:02d}',center,size,None,None,0);co.hide_render=True;hulls.append(co)
 activate(o)
 for co in hulls:co.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(R/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
 vv=[o.matrix_world@v.co for v in o.data.vertices];hullrecords[group]={'name':o.name,'fbx':'model/'+o.name+'.fbx','bounds_pivot_local_m':{'min':[min(v[k] for v in vv) for k in range(3)],'max':[max(v[k] for v in vv) for k in range(3)]},'closed_offset_m':list(loc),'ucx_hulls':len(hulls),'collision_specs_unchanged_from02':specs,'materials':[{'slot':i,'name':m.name,'color_linear':list(m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:3]),'roughness':m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value,'metallic':m.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value} for i,m in enumerate(o.data.materials)]}
 o.location=loc
 for co in hulls:co.hide_set(True)
report={'asset':'ARC-ENTRY-DOOR-03','units':'metres','up':'Z','front_and_interior':'-Y','export_axes':{'forward':'-Z','up':'Y'},'rough_opening_m':[1.05,2.14],'clear_opening_m':[.99,2.11],'leaf_slab_m':[.976,.05,2.094],'leaf_hinge_offset_source_m':[-.495,-.035,0],'new_hardware_x_source_frame_m':HX,'latch_backset_m':.053,'panel_bead_outer_x_m':.383,'hardware_outer_x_m':[HX-.025,HX+.025],'hardware_clearance_to_bead_m':HX-.025-.383,'hardware_clearance_to_leaf_edge_m':.488-HX-.025,'knob_and_plate_mounts':'Flush seated plates and connected stems on both faces; no panel overlap','parts':hullrecords,'lock_alignment':align,'engine_placement':audit,'action_contract':'Replace Door_Entry_Leaf/Frame meshes only, preserve FrontDoor exit actor and existing hinge transforms. Both bolts flush/retracted by default; no new lock action. If a future animated lock is authored, extend/retract before swinging.'}
(R/'assembly.json').write_text(json.dumps(report,indent=2)+'\n')
# Source evidence views; preview lights and state changes are not exported.
sc=bpy.context.scene;sc.world=bpy.data.worlds.new('Preview world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';sc.camera=cam
def camera(pos,target,scale):cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
for loc,power,size in [((2,-4,5),300,4),((-3,-1,3.5),150,3),((0,3,4),240,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.size=size;a.rotation_euler=(Vector((0,0,1.1))-a.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=900;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
def render(name):sc.render.filepath=str(R/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
camera((.5,-4,1.35),(0,0,1.1),2.50);render('closed-interior')
camera((-.5,4,1.35),(0,0,1.1),2.50);render('closed-exterior')
camera((.65,-1,1.14),(.435,0,1.12),.45);render('hardware-mounted-detail')
objs['Frame'].hide_render=True;camera((1.5,-.16,1.15),(.488,0,1.115),.37);render('leaf-edge-detail');objs['Frame'].hide_render=False
objs['Leaf'].hide_render=True;camera((-.2,-.25,1.15),(.495,0,1.115),.37);render('jamb-strike-detail');objs['Leaf'].hide_render=False
objs['Leaf'].rotation_euler.z=math.radians(-80);camera((2.9,-4,2.0),(0,0,1.1),2.8);render('open-hinge-check');objs['Leaf'].rotation_euler.z=0
camera((.5,-4,1.35),(0,0,1.1),2.50);bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/ARC-ENTRY-DOOR-03.blend'))
assert hashlib.sha256((OLD/'model/ARC-ENTRY-DOOR-02.blend').read_bytes()).hexdigest()==audit['original_source_sha256']
print('ENTRY03_COMPLETE',flush=True)
