import bpy, math, os, random
from mathutils import Vector

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
os.makedirs(os.path.join(ROOT,'previews'),exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color,rough=.8,texture=None):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
    if texture:
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(texture,check_existing=True);tex.extension='REPEAT';m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    return m
texture=os.path.join(ROOT,'textures','closet-plaster.png')
sage=material('Plaster_Painterly',(.40,.39,.25),texture=texture if os.path.isfile(texture) else None)
white_tex=os.path.join(ROOT,'textures','closet-white-wood.png')
white=material('Aged_White_Wood',(.79,.75,.65),texture=white_tex if os.path.isfile(white_tex) else None);shadow=material('Panel_Inset',(.72,.68,.58));wood=material('Warm_Oak',(.29,.14,.065));brass=material('Brass',(.46,.30,.11),.5);black=material('Bulb_Cord',(.06,.055,.045)); bulb=material('Warm_Bulb',(.95,.75,.41),.4); bulb.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.65,.30,1); bulb.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=1.5;mold=material('Mold_Dark',(.09,.13,.08));mold2=material('Mold_Olive',(.20,.22,.12))
parts={k:[] for k in ['Body','Door_L','Door_R','Mold']}
def register(o,part,mat):
 o.data.materials.append(mat);parts[part].append(o);return o

def box(name,loc,dim,mat,part='Body',bevel=.005):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('Soft edges','BEVEL');m.width=bevel;m.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 return register(o,part,mat)

def cyl(name,loc,radius,depth,mat,part='Body',rotation=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=depth,location=loc,rotation=rotation);o=bpy.context.object;o.name=name;return register(o,part,mat)
def uv_all(o):
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
# room envelope: X width, front -Y, floor Z=0
box('Back wall',(0,.705,1.375),(1.8,.08,2.75),sage)
for x in (-.86,.86): box('Side wall',(x,0,1.375),(.08,1.45,2.75),sage)
box('Floor substrate',(0,0,-.035),(1.8,1.45,.07),wood)
for n in range(7):
 x=-.765+n*.255
 box('Oak floorboard',(x,0,.003),(.25,1.40,.006),wood,bevel=.001)
box('Ceiling',(0,0,2.72),(1.8,1.45,.06),sage)
# front framing, aperture .90 wide, 2.15 tall
for x in (-.675,.675): box('Front wall',(x,-.705,1.375),(.45,.08,2.75),sage)
box('Header',(0,-.705,2.45),(.9,.08,.60),sage)
for x in (-.47,.47): box('Door jamb',(x,-.758,1.08),(.055,.07,2.16),white)
box('Door casing header',(0,-.758,2.19),(1.08,.07,.08),white)
box('Crown lintel',(0,-.75,2.25),(1.2,.09,.045),white)
for x in (-.72,.72):
 box('Shelf',(x,0,2.14),(.20,1.16,.035),white)
 box('Shelf apron',(x,0,2.10),(.025,1.12,.06),white)
 # slim rails tucked into sides above standing head height
 cyl('Clothes rail',(x,0,2.04),.012,1.1,brass,rotation=(math.pi/2,0,0))
# Small woven boxes on side shelves and hangers tucked against sidewalls.
for x in (-.72,.72):
 for y in (-.34,.12,.43):
  box('Storage box',(x,y,2.24),(.16,.23,.16),wood,bevel=.004)
  box('Box lid',(x,y,2.33),(.17,.24,.018),white,bevel=.002)
 for y in (-.20,.23):
  # shallow hanger silhouettes parallel to side wall, beneath high clothes rail
  cyl('Hanger hook',(x,y,2.01),.006,.08,brass)
  box('Wood hanger rail',(x,y,1.96),(.025,.20,.018),wood,bevel=.003)
for x in (-.80,.80): box('Side skirting',(x,0,.06),(.03,1.25,.12),white)
box('Back skirting',(0,.65,.06),(1.65,.025,.12),white)
# one bulb suspended from ceiling, separately modeled cord, socket and glass
cyl('Ceiling rosette',(0,0,2.67),.055,.025,brass)
cyl('Hanging cable',(0,0,2.43),.007,.48,black)
cyl('Lamp socket',(0,0,2.17),.025,.055,brass)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(0,0,2.11));o=bpy.context.object;o.name='Single bare bulb';o.scale=(.035,.035,.052);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);register(o,'Body',bulb)
# left/right symmetric hinged doors, with material separated and floor origin hinges
for side in (-1,1):
 part='Door_L' if side==-1 else 'Door_R'; cx=side*.225
 box('Door leaf',(cx,-.753,1.075),(.44,.045,2.15),white,part,.006)
 # inset rails on exterior, sufficient visual depth, no thick paint
 for z in (.56,1.59):
  box('Recessed door panel',(cx,-.782,z),(.33,.012,.80),shadow,part,.003)
  box('Panel flat',(cx,-.791,z),(.285,.008,.755),white,part,.002)
 cyl('Door knob',(cx-side*.145,-.816,1.03),.027,.055,brass,part,(math.pi/2,0,0))
 for z in (.22,1.08,1.92): cyl('Hinge pin',(side*.447,-.754,z),.017,.075,brass,part)
# Masked painted mold patch. Alpha channel is thresholded to eliminate the pale fringe;
# the color comes from a dark olive pigment, rather than the generated pale background.
mold_mask=material('Mold_Alpha',(.16,.20,.09))
shader=mold_mask.node_tree.nodes.get('Principled BSDF');shader.inputs['Specular IOR Level'].default_value=0;shader.inputs['Roughness'].default_value=1
t=mold_mask.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(os.path.join(ROOT,'textures','mold-mask.png'),check_existing=True)
r=mold_mask.node_tree.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.08;r.color_ramp.elements[1].position=.60;r.color_ramp.elements[1].color=(1,1,1,1)
mold_mask.node_tree.links.new(t.outputs['Alpha'],r.inputs[0])
# Break up the center while retaining dark pigment and feathered opacity at edges.
noise=mold_mask.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=55;noise.inputs['Detail'].default_value=4
contrast=mold_mask.node_tree.nodes.new('ShaderNodeMapRange');contrast.inputs['From Min'].default_value=.25;contrast.inputs['From Max'].default_value=.80;contrast.inputs['To Min'].default_value=.42;contrast.inputs['To Max'].default_value=1
multiply=mold_mask.node_tree.nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY'
mold_mask.node_tree.links.new(noise.outputs['Fac'],contrast.inputs['Value']);mold_mask.node_tree.links.new(r.outputs['Color'],multiply.inputs[0]);mold_mask.node_tree.links.new(contrast.outputs['Result'],multiply.inputs[1]);mold_mask.node_tree.links.new(multiply.outputs[0],shader.inputs['Alpha'])
# Retain tonal variation from the painted mask, but tint its bright fringe dark olive.
mix=mold_mask.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.0015,.002,.001,1)
mold_mask.node_tree.links.new(t.outputs['Color'],mix.inputs[1]);mold_mask.node_tree.links.new(mix.outputs['Color'],shader.inputs['Base Color'])
mesh=bpy.data.meshes.new('Mold decal');mesh.from_pydata([(-.53,.66,1.28),(.53,.66,1.28),(.53,.66,2.40),(-.53,.66,2.40)],[],[(0,1,2,3)]);mesh.update()
o=bpy.data.objects.new('Mold decal',mesh);bpy.context.collection.objects.link(o);register(o,'Mold',mold_mask)
uv=mesh.uv_layers.new(name='UVMap')
for loop,coord in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
# UV maps for all faces; use smart unwrapping for editable material slots
for group in parts.values():
 for o in group:
  if o.name != 'Mold decal': uv_all(o)
# keep all original objects separate in master blend for editability
# export each group as joined temporary copy with desired local pivot
for name, objs in parts.items():
 bpy.ops.object.select_all(action='DESELECT'); copies=[]
 for obj in objs:
  c=obj.copy();c.data=obj.data.copy();bpy.context.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='BR_Closet_'+name
 # pivot = hinge at floor for door parts, floor center for static
 pivot={'Door_L':(-.45,-.753,0),'Door_R':(.45,-.753,0)}.get(name,(0,0,0));bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(HERE,o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
 bpy.data.objects.remove(o,do_unlink=True)
# rendering setup
bpy.ops.object.light_add(type='AREA',location=(0,-2.7,3.3));bpy.context.object.data.energy=430;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=3.5
bpy.ops.object.light_add(type='POINT',location=(0,0,1.96));bpy.context.object.data.energy=60;bpy.context.object.data.color=(1,.71,.38)
bpy.ops.object.camera_add(location=(0,-4.4,1.65));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=40;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.world.color=(.29,.24,.18);scene.render.image_settings.file_format='PNG'
# open door as rigid groups about hinge in preview (not exported)
def open_doors():
 for part,pivot,ang in [('Door_L',Vector((-.45,-.753,0)),math.radians(-90)),('Door_R',Vector((.45,-.753,0)),math.radians(90))]:
  from mathutils import Matrix
  rot=Matrix.Rotation(ang,4,'Z')
  for o in parts[part]: o.matrix_world=Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot) @ o.matrix_world
for state in ('closed','open_mold','open_repaired'):
 if state=='closed':
  for o in parts['Mold']: o.hide_render=True
 if state=='open_mold':
  open_doors()
  for o in parts['Mold']: o.hide_render=False
 if state=='open_repaired':
  for o in parts['Mold']: o.hide_render=True
 scene.render.filepath=os.path.join(ROOT,'previews',state+'.png');bpy.ops.render.render(write_still=True)
# Additional oblique interior review view shows the shelving, bulb and clear floor.
for o in parts['Mold']: o.hide_render=False
cam.location=(.32,-1.65,1.62);cam.rotation_euler=(Vector((-.05,.50,1.58))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20
scene.render.filepath=os.path.join(ROOT,'previews','interior_oblique.png');bpy.ops.render.render(write_still=True)
# retain the editable scene open and damaged for inspection
for o in parts['Mold']: o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,'BR-CLOSET-01.blend'))
