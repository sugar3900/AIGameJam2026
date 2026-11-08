"""BA-MIRROR-01: 0.52 x 0.84 m arched mirror and two globe sconces.
Run Blender -b --python build_mirror.py. Coordinates metres, X horizontal, Z up,
fixture front faces -Y; common wall datum at (0,0,0)."""
import bpy,math,os
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'model';tex=root/'textures';prev=root/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,col,metal=0,rough=.6, texture=None, emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture and (tex/texture).exists():
  im=bpy.data.images.load(str(tex/texture),check_existing=True);n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color']);im.pack()
 if emission:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emission
 return m
brass=material('Painted_Aged_Brass',(.48,.26,.09),.82,.40,'brass-candidate-b.png');mirror=material('Mirror_Glass',(.82,.84,.80),1.0,.045);back=material('Dark_Backing',(.17,.12,.09),.2,.8);opal=material('Opal_Globe',(.94,.83,.68),0,.32);wall=material('Preview_Pink_Tile',(.51,.27,.26),0,.9); grout=material('Preview_Grout',(.77,.62,.56),0,.9)
# Mesh names denote export grouping, preserve actual individual meshes in source.
groups={'mirror':[],'sconce':[],'globe':[]}
def record(o,group):groups[group].append(o);return o
def cube(name,loc,dim,mat,group=None,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=4; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 if group:record(o,group)
 return o
def curve(name,points,radius,mat,group,closed=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=radius;c.bevel_resolution=4;p=c.splines.new('POLY');p.points.add(len(points)-1)
 for q,v in zip(p.points,points):q.co=(*v,1)
 p.use_cyclic_u=closed;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return record(o,group)
def sphere(name,loc,scale,mat,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.shade_smooth();o.data.materials.append(mat);return record(o,group)
def cyl(name,loc,r,depth,mat,group,rot=(math.pi/2,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(mat);bpy.ops.object.shade_smooth();return record(o,group)
# Dome arch: straight sides + a shallow elliptical curved top.
def outline(w,bottom,spring,rise,y):
 r=.045; pts=[]
 for i in range(9):
  a=-math.pi/2 + (math.pi/2)*i/8; pts.append((w/2-r+r*math.cos(a),y,bottom+r+r*math.sin(a)))
 pts.append((w/2,y,spring))
 for i in range(1,33):
  a=math.pi*i/32;pts.append((w/2*math.cos(a),y,spring+rise*math.sin(a)))
 for i in range(9):
  a=math.pi+(math.pi/2)*i/8;pts.append((-w/2+r+r*math.cos(a),y,bottom+r+r*math.sin(a)))
 return pts
# flat glass face with perimeter inset, no hardcoded reflected scene
pts=outline(.49,1.20,1.87,.15,-.040); verts=pts; faces=[tuple(range(len(pts)))]; mesh=bpy.data.meshes.new('Arch glass geometry');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Mirrored glass',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mirror);record(o,'mirror')
# arched back board and continuous double brass rim
pts_back=outline(.515,1.19,1.87,.16,.0);me=bpy.data.meshes.new('Back plate');me.from_pydata(pts_back,[],[tuple(range(len(pts_back)))]);me.update();o=bpy.data.objects.new('Back plate',me);bpy.context.collection.objects.link(o);o.data.materials.append(back);record(o,'mirror')
curve('Outer brass molding',outline(.525,1.185,1.87,.165,-.035),.009,brass,'mirror',True)
curve('Inner brass bead',outline(.497,1.205,1.865,.145,-.048),.004,brass,'mirror',True)
for x in (-.27,.27):
 cyl('Side round mount',(x,-.006,1.59),.019,.025,brass,'mirror');sphere('Mount cap',(x,-.023,1.59),(.012,.006,.012),brass,'mirror')
# Rear mounting plate, keyhole and four fasteners. Dark inset suggests the
# keyhole while maintaining simple, robust geometry for game use.
cube('Rear keyhole plate',(0,.008,1.95),(.055,.012,.082),brass,'mirror',.004)
sphere('Keyhole round',(0,.016,1.963),(.007,.002,.007),back,'mirror')
cube('Keyhole slot',(0,.017,1.95),(.006,.002,.018),back,'mirror')
for x in (-.205,.205):
 for z in (1.25,1.865):
  sphere('Rear screw',(x,.010,z),(.009,.004,.009),brass,'mirror')
  cube('Rear screw slot',(x,.014,z),(.011,.002,.0015),back,'mirror')
# each sconce is a reusable component, group both mounts and bulbs separately
for x in (-.43,.43):
 cyl('Circular wall plate',(x,-.023,1.65),.065,.026,brass,'sconce');cyl('Plate inset',(x,-.042,1.65),.050,.013,brass,'sconce')
 for dx in (-.038,.038):
  sphere('Plate screw',(x+dx,-.051,1.65),(.006,.003,.006),brass,'sconce')
  cube('Plate screw slot',(x+dx,-.055,1.65),(.007,.001,.0012),back,'sconce')
 curve('Curved stem',[(x,-.045,1.65),(x,-.090,1.65),(x,-.130,1.655),(x,-.150,1.675),(x,-.150,1.715)],.011,brass,'sconce')
 cyl('Globe collar',(x,-.150,1.735),.035,.025,brass,'sconce',rot=(0,0,0));cyl('Collar trim',(x,-.150,1.75),.038,.009,brass,'sconce',rot=(0,0,0))
 sphere('Opal glass globe',(x,-.150,1.825),(.077,.077,.077),opal,'globe')
# auto UV for generated geometry; curve conversions also need UVs.
for objs in groups.values():
 for o in objs:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  if o.type=='MESH':
   bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
   if not o.data.uv_layers:
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
# preview wall and contrasting wainscot, not exported
cube('Preview backdrop',(0,.08,1.6),(2.2,.08,2.75),wall,bevel=.001)
# Preview-only reflected architecture: visible in reflections, invisible to camera.
# Provides honest environmental reflections instead of painting a fake image onto glass.
reflection_wall=material('Preview_Reflection_Cream',(.55,.47,.34),0,.8)
reflection_window=material('Preview_Reflection_Window',(.85,.71,.49),0,.7,emission=.35)
reflection_wood=material('Preview_Reflection_Frame',(.20,.13,.075),0,.7)
def reflect_only(o):
 o.visible_camera=False
 return o
reflect_only(cube('Reflection wall',(0,-3.4,1.8),(4,.06,3),reflection_wall))
reflect_only(cube('Reflection window',(-1.35,-3.36,1.15),(.85,.02,1.25),reflection_window))
for x in (-1.775,-1.35,-.925):
 reflect_only(cube('Window vertical', (x,-3.34,1.15),(.025,.018,1.30),reflection_wood))
for z in (.525,1.15,1.775):
 reflect_only(cube('Window rail',(-1.35,-3.34,z),(.87,.018,.025),reflection_wood))
# Camera and warm studio lighting.
world=bpy.context.scene.world;world.color=(.18,.18,.18)
def area(loc,energy,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.65))-o.location).to_track_quat('-Z','Y').to_euler()
area((-.8,-2.5,3.0),75,3.0);area((1.5,-2,2.4),45,2)
bpy.ops.object.camera_add(location=(1.65,-4.1,2.35));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.8;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
# export selected meshes in each logical part, keeping wall datum
for group,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(out/('BA_Mirror_'+group+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Preview off and on; globe uses an editable emission input; point lights only for preview.
for state in ('off','on'):
 p=opal.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.94,.83,.68,1) if state=='off' else (1,.56,.18,1);p.inputs['Emission Color'].default_value=(1,.30,.035,1);p.inputs['Emission Strength'].default_value=0 if state=='off' else 2.5
 lights=[]
 if state=='on':
  for x in (-.43,.43):
   bpy.ops.object.light_add(type='POINT',location=(x,-.17,1.825));o=bpy.context.object;o.data.energy=18;o.data.color=(1,.66,.35);o.data.shadow_soft_size=.16;lights.append(o)
 scene.render.filepath=str(prev/('mirror-sconces-'+state+'.png'));bpy.ops.render.render(write_still=True)
 for o in lights:bpy.data.objects.remove(o,do_unlink=True)
# Return source to off; on is runtime controllable.
p.inputs['Emission Strength'].default_value=0
p.inputs['Base Color'].default_value=(.94,.83,.68,1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'BA-MIRROR-01.blend'))
