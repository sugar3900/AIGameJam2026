"""Build repeatable period backsplash, cap and end caps. Blender background mode."""
import bpy, math, os, random
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD=os.path.join(ROOT,'model'); PRE=os.path.join(ROOT,'previews'); TEX=os.path.join(ROOT,'textures')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name, col, rough=.72, tex=None, tint=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=rough
 if tex:
  im=m.node_tree.nodes.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(os.path.join(TEX,tex),check_existing=True); im.extension='REPEAT'
  mix=m.node_tree.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MIX'; mix.inputs[0].default_value=.30; mix.inputs[2].default_value=(*tint,1)
  m.node_tree.links.new(im.outputs['Color'],mix.inputs[1]); m.node_tree.links.new(mix.outputs['Color'],bs.inputs['Base Color'])
 return m
ivory=mat('Warm ivory ceramic',(.70,.62,.47),.64,'glaze-ivory.png',(.78,.70,.57))
sage=mat('Soft sage ceramic',(.43,.49,.37),.68,'glaze-sage.png',(.49,.55,.43))
grout=mat('Warm cream grout',(.76,.70,.59),.89)
capmat=mat('Cream glazed cap',(.74,.68,.57),.69,'glaze-ivory.png',(.78,.70,.57))
def block(name,loc,dims,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
# X along wall, -Y facing room, +Z up. Field includes top/bottom caps; 1 m repeat, 0.56 m tall.
parts=[block('Grout substrate',(.5,-.007,.28),(1,.014,.56),grout)]
verts=[];faces=[];uvs=[];slots=[];random.seed(187)
for row in range(5):
 for col in range(10):
  x=col*.1+.002; z=.03+row*.1+.002; w=.096; y=-.017; i=len(verts)
  verts += [(x,y,z),(x+w,y,z),(x+w,y,z+w),(x,y,z+w),(x,-.007,z),(x+w,-.007,z),(x+w,-.007,z+w),(x,-.007,z+w)]
  fs=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
  # sample an interior patch and rotate UVs on individual tiles to vary the painterly swatch
  ox=.05+random.random()*.46; oz=.05+random.random()*.46; s=.42
  uv=[(ox,oz),(ox+s,oz),(ox+s,oz+s),(ox,oz+s)]; n=random.randrange(4); uv=uv[n:]+uv[:n]
  for f in fs:faces.append(tuple(i+j for j in f)); uvs.append(uv); slots.append((col+row)%2)
mesh=bpy.data.meshes.new('Ceramic checker mesh');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Individual checker tiles',mesh);bpy.context.collection.objects.link(ob);mesh.materials.append(ivory);mesh.materials.append(sage)
uv=mesh.uv_layers.new(name='UVMap')
for p,coords,slot in zip(mesh.polygons,uvs,slots):
 p.material_index=slot
 for li,c in zip(p.loop_indices,coords):uv.data[li].uv=c
parts.append(ob)
parts.append(block('Lower horizontal cap',(.5,-.012,.015),(1,.034,.03),capmat,.002))
parts.append(block('Upper horizontal cap',(.5,-.012,.545),(1,.034,.03),capmat,.002))
# Separate left/right edge caps, applied only at the physical ends of the run.
left=block('Left end cap',(-.015,-.012,.28),(.03,.034,.56),capmat,.002)
right=block('Right end cap',(1.015,-.012,.28),(.03,.034,.56),capmat,.002)
def originzero(objects):
 bpy.context.scene.cursor.location=(0,0,0)
 for o in objects:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
def export(name,objects):
 originzero(objects);bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.fbx(filepath=os.path.join(MOD,name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
export('KI_Backsplash_Module_1m',parts);export('KI_Backsplash_End_Left',[left]);export('KI_Backsplash_End_Right',[right])
# Three repeated modules, including one pair of end caps, show seams and material cadence.
right.location.x+=2
for i in (1,2):
 for o in parts:
  d=o.copy();d.data=o.data.copy();bpy.context.collection.objects.link(d);d.location.x+=i
plaster=mat('Preview plaster',(.62,.54,.44));cab=mat('Preview sage cabinet',(.31,.36,.26)); counter=mat('Preview cream counter',(.79,.72,.59))
block('Context plaster',(1.5,.01,.9),(3.3,.04,1.25),plaster)
block('Context counter',(1.5,-.22,-.03),(3.25,.45,.06),counter,.003)
block('Context cabinet',(1.5,-.19,-.31),(3.1,.39,.55),cab)
bpy.ops.object.camera_add(location=(3.2,-5.5,1.9));cam=bpy.context.object;cam.rotation_euler=(Vector((1.5,0,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.85;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(.5,-3,3.2));l=bpy.context.object;l.data.energy=500;l.data.shape='DISK';l.data.size=4;l.data.color=(1,.84,.73);l.rotation_euler=(Vector((1.5,0,.3))-l.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.world.color=(.28,.25,.21);s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1400;s.render.resolution_y=800;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(PRE,'backsplash-repeat.png');bpy.ops.render.render(write_still=True)
cam.location=(.55,-3,.32);cam.rotation_euler=(Vector((.55,0,.28))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.filepath=os.path.join(PRE,'backsplash-detail.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(MOD,'KI-BACKSPLASH-01.blend'));print('BACKSPLASH_BUILD_OK')
