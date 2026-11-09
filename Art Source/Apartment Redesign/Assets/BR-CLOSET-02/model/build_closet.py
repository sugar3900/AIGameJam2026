"""Fitted hall-end closet kit. All exports in local metres; see assembly.json.
No shared room wall/floor/ceiling is exported. Preview shell is a separate collection.
"""
from pathlib import Path
import bpy, math, json
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc.render.engine='CYCLES';sc.cycles.samples=32
sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.world.color=(.18,.15,.11)
sc.view_settings.view_transform='AgX'
sc.render.film_transparent=False

def material(name,color,texture=None,metal=0,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/texture),check_existing=True);t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
white=material('Aged_White_Wood',(.79,.75,.65),'closet-white-wood.png')
plaster=material('Plaster_Painterly',(.40,.39,.25),'closet-plaster.png')
shadow=material('Panel_Inset',(.54,.50,.42));brass=material('Aged_Brass',(.34,.23,.09),metal=.65,rough=.42)
wood=material('Shelf_End_Grain',(.32,.20,.10));cord=material('Bulb_Cord',(.045,.038,.030));oak=material('Preview_Oak',(.23,.105,.042));bulb=material('Warm_Bulb',(.94,.77,.47),rough=.36)
bulb.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.71,.38,1)
bulb.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2
parts={};collision={};proxy=[]
def reg(o,group,mat):
 o.data.materials.append(mat)
 if group=='PROXY':proxy.append(o)
 else:parts.setdefault(group,[]).append(o)
 return o

def box(name,loc,dim,mat=white,group='Trim',bevel=.003,collide=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Worn softened edges','BEVEL');b.width=min(bevel,min(dim)*.24);b.segments=3;bpy.ops.object.modifier_apply(modifier=b.name)
  b=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=b.name)
 reg(o,group,mat)
 if collide:collision.setdefault(group,[]).append((loc,dim))
 return o

def cyl(name,loc,r,depth,mat,group,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name
 b=o.modifiers.new('Edge fillet','BEVEL');b.width=.0012;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
 return reg(o,group,mat)
def sphere(name,loc,scale,mat,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return reg(o,group,mat)
def bar(name,a,b,r,mat,group):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,mat,group);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
# Rough opening 1.10w x2.14h. Jamb insides exactly +/-0.50.
for side in (-1,1):
 box('Jamb lining',(side*.525,-.90,1.055),(.05,.12,2.11),collide=True)
 box('Front casing',(side*.580,-.980,1.0775),(.11,.038,2.155))
 box('Casing outer bead',(side*.628,-1.002,1.075),(.014,.016,2.15),bevel=.003)
 box('Casing inner fillet',(side*.535,-1.003,1.075),(.013,.014,2.15),bevel=.002)
 box('Plinth block',(side*.580,-.990,.075),(.124,.055,.15))
box('Head lining',(0,-.90,2.125),(1.10,.12,.03),collide=True)
box('Casing lintel',(0,-.982,2.165),(1.27,.042,.11))
box('Lintel bead',(0,-1.009,2.199),(1.30,.019,.018))
box('Lintel cap',(0,-.985,2.231),(1.35,.068,.025))
# Separate leaves. Local floor hinges, no shared solid collider across aperture.
PIVOTS={'Door_L':(-.5,-.978,0),'Door_R':(.5,-.978,0)}
for side,group in [(-1,'Door_L'),(1,'Door_R')]:
 cx=side*.2525
 box('Door leaf',(cx,-.978,1.0575),(.495,.038,2.085),group=group,bevel=.005,collide=True)
 # Shaker-like raised frames: preserve source profile width rather than stretching.
 for z,h in [(.51,.78),(1.55,.83)]:
  box('Recessed field',(cx,-1.001,z),(.378,.010,h),shadow,group,.002)
  box('Painted inset',(cx,-1.008,z),(.340,.008,h-.038),white,group,.002)
  for sx in (-1,1):box('Inset stile bead',(cx+sx*.183,-1.014,z),(.012,.012,h+.014),white,group,.002)
  for sz in (-1,1):box('Inset rail bead',(cx,-1.014,z+sz*(h/2+.001)),(.378,.012,.012),white,group,.002)
 # Back face inset panels makes open-door reveal equally complete.
 for z,h in [(.51,.78),(1.55,.83)]:box('Interior inset',(cx,-.953,z),(.365,.012,h),white,group,.003)
 knobx=side*.10
 for yy in (-1.028,-.93):
  cyl('Knob escutcheon',(knobx,yy,1.04),.032,.007,brass,group,(math.pi/2,0,0))
  cyl('Knob spindle',(knobx,yy+(-.018 if yy<-.978 else .018),1.04),.009,.034,brass,group,(math.pi/2,0,0))
  sphere('Round brass knob',(knobx,yy+(-.04 if yy<-.978 else .04),1.04),(.024,.023,.024),brass,group)
 for z in (.20,1.055,1.91):
  cyl('Hinge barrel',(side*.500,-.978,z),.010,.065,brass,group)
  box('Hinge leaf',(side*.480,-1.000,z),(.030,.006,.052),brass,group,.001)
 # Subtle colored wear: texture remains the principal painterly treatment.
 for dx,z in [(-.13,.115),(.10,.115),(.14,2.065)]:box('Sparse rubbed edge',(cx+dx,-.998,z),(.028,.0006,.002),wood,group,0)
# High shelf only on west side; approved bounds x=-1.04..-.74 y=-.37..+.68.
box('West high shelf',(-.89,.155,2.2325),(.30,1.05,.035),group='Shelf',collide=True)
box('Shelf front apron',(-.752,.155,2.19),(.024,1.05,.085),group='Shelf')
for yy in (-.27,.58):
 box('Shelf wall cleat',(-1.017,yy,2.17),(.045,.11,.10),group='Shelf')
 bar('Triangular shelf bracket',(-1.015,yy,2.11),(-.78,yy,2.215),.012,brass,'Shelf')
cyl('West hanging rail',(-.89,.155,2.102),.012,1.00,brass,'Shelf',(math.pi/2,0,0))
for yy in (-.15,.22,.52):
 # Small hangers, parallel to side wall, entirely west of x=-.80.
 bar('Hanger hook',(-.89,yy,2.10),(-.89,yy,2.04),.005,brass,'Shelf')
 for y2 in (yy-.11,yy+.11):bar('Hanger shoulder',(-.89,yy,2.04),(-.89,y2,1.98),.007,wood,'Shelf')
 bar('Hanger bar',(-.89,yy-.11,1.98),(-.89,yy+.11,1.98),.007,wood,'Shelf')
# Bulb position follows approved plan rect centre (1.14,4.68).
bx,by=.04,.02
cyl('Ceiling rosette',(bx,by,2.735),.055,.03,brass,'Bulb')
cyl('Single black cable',(bx,by,2.455),.005, .53,cord,'Bulb')
cyl('Pendant socket',(bx,by,2.165),.024,.055,brass,'Bulb')
sphere('Single bare bulb',(bx,by,2.112),(.035,.035,.052),bulb,'Bulb')
# Painted mold uses exact source mask. Plane is 3mm in front of north wall face.
mold=material('Mold_Alpha',(.045,.062,.025));shader=mold.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=1;shader.inputs['Specular IOR Level'].default_value=0
n=mold.node_tree.nodes;t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures/mold-mask.png'));t.image.pack()
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.08;r.color_ramp.elements[1].position=.60;mold.node_tree.links.new(t.outputs['Alpha'],r.inputs[0]);mold.node_tree.links.new(r.outputs['Color'],shader.inputs['Alpha'])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.12,.15,.07,1);mold.node_tree.links.new(t.outputs['Color'],mix.inputs[1]);mold.node_tree.links.new(mix.outputs['Color'],shader.inputs['Base Color'])
mesh=bpy.data.meshes.new('Mold decal');mesh.from_pydata([(-.45,.837,.75),(.45,.837,.75),(.45,.837,1.85),(-.45,.837,1.85)],[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('Mold decal',mesh);bpy.context.collection.objects.link(o);reg(o,'Mold',mold)
u=mesh.uv_layers.new(name='UVMap')
for l,v in zip(u.data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=v
# Multiply masked alpha by subtle pigment breakup so the patch retains painted texture.
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=3
remap=n.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=.20;remap.inputs['From Max'].default_value=.80;remap.inputs['To Min'].default_value=.62;remap.inputs['To Max'].default_value=1
multiply=n.new('ShaderNodeMath');multiply.operation='MULTIPLY';mold.node_tree.links.new(noise.outputs['Fac'],remap.inputs['Value']);mold.node_tree.links.new(r.outputs['Color'],multiply.inputs[0]);mold.node_tree.links.new(remap.outputs['Result'],multiply.inputs[1]);mold.node_tree.links.new(multiply.outputs[0],shader.inputs['Alpha'])
# No floor/room wall/ceiling geometry in the exports below.
for group,objs in parts.items():
 for ob in objs:
  if ob.data.uv_layers:continue
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
manifest={'asset':'BR-CLOSET-02','units':'metres','up':'+Z','front':'-Y','plan_origin':[1.1,4.7,0],'plan_mapping':'plan x=1.1+local x; plan y=4.7-local y; plan z=local z; map handedness through existing Unreal importer','opening':{'rough_width':1.1,'rough_head':2.14,'finished_clear_width':1.0,'finished_clear_head':2.11},'exports':[]}
for group,objs in parts.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for ob in objs:
  c=ob.copy();c.data=ob.data.copy();bpy.context.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='BR_Closet02_'+group
 pivot=PIVOTS.get(group,(0,0,0));sc.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');ob.location=(0,0,0)
 meshname=ob.name;collision_objects=[]
 for idx,(loc,dim) in enumerate(collision.get(group,[])):
  bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(loc)-Vector(pivot));c=bpy.context.object;c.name=f'UCX_{meshname}_{idx:02d}';c.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);collision_objects.append(c)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
 for c in collision_objects:c.select_set(True)
 bpy.context.view_layer.objects.active=ob
 path=ROOT/'model'/f'{meshname}.fbx';bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE')
 manifest['exports'].append({'file':'model/'+path.name,'mesh':meshname,'assembly_offset':list(pivot),'export_object_origin':[0,0,0],'collision_hulls':len(collision_objects),'opens_about_local_Z_degrees':(-95 if group=='Door_L' else 95 if group=='Door_R' else None)})
 for c in [ob]+collision_objects:bpy.data.objects.remove(c,do_unlink=True)
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Preview-only shell exactly follows nominal centerline geometry. Not exported.
box('PREVIEW north wall',(0,.90,1.375),(2.32,.12,2.75),plaster,'PROXY',0)
for x in (-1.10,1.10):box('PREVIEW side wall',(x,0,1.375),(.12,1.80,2.75),plaster,'PROXY',0)
for x in (-.825,.825):box('PREVIEW front pier',(x,-.9,1.375),(.55,.12,2.75),plaster,'PROXY',0)
box('PREVIEW header',(0,-.9,2.445),(1.10,.12,.61),plaster,'PROXY',0)
box('PREVIEW floor',(0,-.25,-.045),(2.32,2.55,.08),oak,'PROXY',0)
for i in range(9):box('PREVIEW floor board',(-1.0+i*.25,-.25,-.002),(.246,2.5,.005),oak,'PROXY',.001)
box('PREVIEW ceiling',(0,0,2.78),(2.32,1.92,.06),plaster,'PROXY',0)
for side in (-1,1):box('PREVIEW skirting',(side*1.02,0,.06),(.035,1.68,.12),white,'PROXY')
box('PREVIEW back skirting',(0,.823,.06),(2.08,.034,.12),white,'PROXY')
preview_col=bpy.data.collections.new('PREVIEW ONLY — NOT EXPORTED');sc.collection.children.link(preview_col)
for ob in proxy:
 for col in list(ob.users_collection):col.objects.unlink(ob)
 preview_col.objects.link(ob)
# Empty standing proxy is disabled for beauty renders but available for measurement.
proxy_mat=material('Clearance proxy',(.13,.45,.42));human=box('CLEARANCE man 0.60 x0.60 x1.80',(0,.15,.90),(.60,.60,1.80),proxy_mat,'PROXY',0);human.hide_render=True;human.display_type='WIRE'
# Lighting/camera.
def area(name,loc,energy,size,target):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm outside window',(2,-3,4),450,3,(0,0,1.2));area('Soft fill',(-2,-3,2),120,3,(0,0,1.3))
bpy.ops.object.light_add(type='POINT',location=(bx,by,2.04));bpy.context.object.data.energy=35;bpy.context.object.data.color=(1,.72,.42);bpy.context.object.data.shadow_soft_size=.08
bpy.ops.object.camera_add(location=(.15,-4.7,1.55));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.02,1.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=40;sc.camera=cam
matrices={o.name:o.matrix_world.copy() for g in ('Door_L','Door_R') for o in parts[g]}
def pose(opened):
 for g,angle in [('Door_L',-95),('Door_R',95)]:
  p=Vector(PIVOTS[g]);R=Matrix.Translation(p)@Matrix.Rotation(math.radians(angle if opened else 0),4,'Z')@Matrix.Translation(-p)
  for ob in parts[g]:ob.matrix_world=R@matrices[ob.name]
def render(name):sc.render.filepath=str(ROOT/'previews'/name);bpy.ops.render.render(write_still=True)
pose(False);render('closet-closed.png')
pose(True);render('closet-open-mold.png')
for o in parts['Mold']:o.hide_render=True
render('closet-open-repaired.png')
for o in parts['Mold']:o.hide_render=False
cam.location=(.35,-1.9,1.6);cam.rotation_euler=(Vector((-.08,.4,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20;render('closet-interior.png')
pose(False);sc.cursor.location=(0,0,0);cam.location=(.15,-4.7,1.55);cam.rotation_euler=(Vector((0,-.02,1.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=40
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/BR-CLOSET-02.blend'))
print('BR-CLOSET-02 completed; closed-pose exports and assembly manifest saved.')
