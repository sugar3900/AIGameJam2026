import bpy, math, os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(n,c,rough=.55,metal=0,texture=None):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
tex=P/'textures'/'range-enamel-v2.png'
enamel=mat('Enamel_Painted',(0.82,.7,.49),.72,texture=tex if tex.exists() else None)
inside=mat('Oven_Dark',(.082,.065,.052),.5); iron=mat('Burner_Cast_Iron',(.075,.067,.06),.8,.25);steel=mat('Aged_Steel',(.44,.40,.32),.37,.7); glass=mat('Oven_Window',(.16,.115,.072),.32,.1); gasket=mat('Gasket',(.13,.115,.09),.8)
groups={}
def add(group,o): groups.setdefault(group,[]).append(o);return o

def box(group,n,loc,dims,m,b=.006):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=min(b,min(dims)*.24);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Smooth normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(m);add(group,o);return o

def cyl(group,n,loc,r,depth,m,rot=(0,0,0),verts=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);add(group,o);return o

def bar(group,n,a,b,r,m):
 a,b=Vector(a),Vector(b);d=b-a;o=cyl(group,n,(a+b)*.5,r,d.length,m,verts=12);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o

# Broad casing is made of walls around a real dark hollow oven. -Y faces the room.
box('Body','Left side',(-.35,0,.46),(.05,.66,.88),enamel,.012)
box('Body','Right side',(.35,0,.46),(.05,.66,.88),enamel,.012)
box('Body','Back',(0,.305,.46),(.65,.05,.88),enamel,.008)
box('Body','Oven inner back',(0,.271,.46),(.59,.012,.52),inside,.002)
box('Body','Oven inner left',(-.307,-.01,.48),(.012,.55,.47),inside,.002)
box('Body','Oven inner right',(.307,-.01,.48),(.012,.55,.47),inside,.002)
box('Body','Oven inner top',(0,-.01,.705),(.61,.55,.015),inside,.002)
box('Body','Oven inner floor',(0,-.01,.225),(.61,.55,.018),inside,.002)
box('Body','Enamel cooktop',(0,0,.885),(.75,.7,.055),enamel,.012)
box('Body','Backguard',(0,.30,.985),(.75,.08,.17),enamel,.014)
box('Body','Control fascia',(0,-.329,.805),(.66,.05,.13),enamel,.009)
box('Body','Toe kick',(0,0,.035),(.72,.65,.07),iron,.008)
box('Body','Lower drawer',(0,-.326,.15),(.66,.047,.14),enamel,.008)
bar('Body','Drawer handle',(-.19,-.358,.16),(.19,-.358,.16),.009,steel)
for x in [-.24,-.08,.08,.24]:
 cyl('Body','Knob bezel',(x,-.36,.807),.024,.012,steel,(math.pi/2,0,0));cyl('Body','Knob',(x,-.37,.807),.017,.016,steel,(math.pi/2,0,0));box('Body','Knob indicator',(x,-.38,.812),(.003,.003,.014),iron,.0004)
# Four burner rings and square raised grates.
for x in [-.18,.18]:
 for y in [-.15,.15]:
  cyl('Body','Burner base',(x,y,.922),.057,.012,iron);cyl('Body','Burner cap',(x,y,.930),.038,.008,iron)
  cyl('Body','Burner cap center',(x,y,.936),.024,.004,steel)
  for j in range(12):
   angle=math.tau*j/12; cyl('Body','Gas port',(x+.046*math.cos(angle),y+.046*math.sin(angle),.931),.0027,.003,gasket,verts=8)
  for dx in [-.073,.073]:bar('Body','Grate side',(x+dx,y-.073,.949),(x+dx,y+.073,.949),.007,iron)
  for dy in [-.073,.073]:bar('Body','Grate bar',(x-.073,y+dy,.949),(x+.073,y+dy,.949),.007,iron)
  for a in [0,math.pi/2,math.pi,3*math.pi/2]:
   bar('Body','Grate spoke',(x+math.cos(a)*.024,y+math.sin(a)*.024,.949),(x+math.cos(a)*.073,y+math.sin(a)*.073,.949),.006,iron)
  for a in [math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4]:
   bar('Body','Diagonal grate',(x+math.cos(a)*.036,y+math.sin(a)*.036,.949),(x+math.cos(a)*.103,y+math.sin(a)*.103,.949),.005,iron)
# Oven rack: front/back rails and thin bars
for z in [.39,.55]:
 for y in [-.24,.20]:bar('Body','Rack rail',(-.275,y,z),(.275,y,z),.004,steel)
 for x in [-.25,-.20,-.15,-.10,-.05,0,.05,.10,.15,.20,.25]:bar('Body','Rack wire',(x,-.24,z),(x,.20,z),.002,steel)
# Door pivots around X along its bottom edge. Separate transformable object, origin at hinge.
box('Door','Oven door',(0,-.363,.475),(.66,.05,.49),enamel,.012)
box('Door','Window dark bezel',(0,-.392,.485),(.40,.008,.25),gasket,.005)
box('Door','Window glass',(0,-.397,.485),(.36,.005,.21),glass,.004)
# Inner face: dark metal window rim and glass, visible when the door opens.
box('Door','Inner window surround',(0,-.335,.485),(.44,.008,.29),inside,.006)
box('Door','Inner window rim',(0,-.329,.485),(.39,.004,.24),steel,.003)
box('Door','Inner glass',(0,-.326,.485),(.36,.004,.21),glass,.003)
for x in [-.20,.20]:
 for z in [.36,.61]: cyl('Door','Rim fastener',(x,-.325,z),.004,.003,steel,(math.pi/2,0,0),verts=12)
for x in [-.29,.29]:
 cyl('Door','Hinge barrel',(x,-.363,.23),.014,.055,steel,(0,math.pi/2,0)); box('Body','Hinge mounting plate',(x,-.342,.23),(.065,.018,.045),iron,.003)
bar('Door','Door handle',(-.22,-.414,.665),(.22,-.414,.665),.012,steel)
for x in [-.20,.20]:bar('Door','Handle mount',(x,-.387,.665),(x,-.414,.665),.008,steel)
# Join export groups, preserve exact hinge floor coordinates and packed textures.
for group,objs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_RANGE_'+group
 bpy.context.scene.cursor.location=(0,-.363,.23) if group=='Door' else (0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');groups[group]=o
 for p in o.data.polygons:p.use_smooth=True
# separate export, do not bake transforms
for group,o in groups.items():
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/('KI_RANGE_'+group+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False)
# presentation
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=groups['Body']
bpy.ops.object.camera_add(location=(2.1,-2.8,1.85));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.49))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.8;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(1,-2,3));bpy.context.object.data.energy=290;bpy.context.object.data.color=(1,.87,.72);bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=48;bpy.context.scene.world.color=(.20,.17,.13);bpy.context.scene.render.resolution_x=1024;bpy.context.scene.render.resolution_y=1024;bpy.context.scene.render.resolution_percentage=100;bpy.context.scene.render.film_transparent=True
# Save with door closed. Render open by rotating about hinge.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'KI-RANGE-01.blend'))
bpy.context.scene.render.filepath=str(P/'previews'/'range-closed.png');bpy.ops.render.render(write_still=True)
groups['Door'].rotation_euler.x=math.radians(82)
bpy.context.scene.render.filepath=str(P/'previews'/'range-open.png');bpy.ops.render.render(write_still=True)
