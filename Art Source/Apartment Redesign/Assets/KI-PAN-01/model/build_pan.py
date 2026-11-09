import bpy, math, os
from mathutils import Vector
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model=os.path.join(root,'model'); preview=os.path.join(root,'previews'); tex=os.path.join(root,'textures')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
def material(name,path,metal=0,rough=.6):
 m=bpy.data.materials.new(name);m.diffuse_color=(.5,.5,.5,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(os.path.join(tex,path),check_existing=True);n.image.filepath='//../textures/'+path
 m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color']);return m
iron=material('Seasoned iron','iron.png',.18,.77);wood=material('Aged walnut','wood-selected.png',0,.7)
def select_only(objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
def smart(o):
 select_only([o]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
def bevel(o,amount=.002,segments=3):
 m=o.modifiers.new('Soft edge','BEVEL');m.width=amount;m.segments=segments
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
def cube(name,loc,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
# Continuous lathed cross section: bottom underside up outer rim and down to inside bottom.
profile=[(.012,.002),(.086,.002),(.105,.004),(.116,.010),(.124,.024),(.129,.044),(.130,.052),(.128,.055),(.124,.054),(.123,.047),(.119,.031),(.111,.019),(.101,.014),(.086,.012),(.012,.012)]
n=96; verts=[];faces=[]
for rad,z in profile:
 for i in range(n):
  a=2*math.pi*i/n;verts.append((rad*math.cos(a),rad*math.sin(a),z))
for j in range(len(profile)-1):
 for i in range(n):
  a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
faces.append(tuple(reversed(range(n))));faces.append(tuple((len(profile)-1)*n+i for i in range(n)))
me=bpy.data.meshes.new('Pan bowl');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Bowl',me);bpy.context.collection.objects.link(o);o.data.materials.append(iron)
for poly in me.polygons:poly.use_smooth=True
smart(o);bowl=o
# Wood handle: rounded, bevelled cuboid with a real through hole at its outboard end.
h=cube('Wood handle',(.245,0,.053),(.215,.033,.024),wood);bevel(h,.010,5)
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.006,depth=.08,location=(.331,0,.053));cut=bpy.context.object
bpy.context.view_layer.objects.active=h;mod=h.modifiers.new('Hanging hole','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
bevel(h,.0008,2);smart(h)
# Align the walnut image lengthwise; avoid cross-grain checkerboard UV islands.
uv=h.data.uv_layers.active.data
for poly in h.data.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  v=h.data.vertices[h.data.loops[li].vertex_index].co
  u=(v.x+.1075)/.215*.88+.06
  if abs(poly.normal.x)>.8: uv[li].uv=((v.y+.0165)/.033*.32+.32,(v.z+.012)/.024*.25+.35)
  elif abs(poly.normal.y)>abs(poly.normal.z): uv[li].uv=(u,(v.z+.012)/.024*.25+.35)
  else: uv[li].uv=(u,(v.y+.0165)/.033*.32+.32)

# Bracket is part of iron pan body; rivets make the connection legible.
collar=cube('Iron ferrule',(.144,0,.051),(.055,.037,.030),iron);bevel(collar,.004,3);smart(collar)
parts=[bowl,collar]
for y in (-.011,.011):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=(.119,y,.043));o=bpy.context.object;o.name='Rivet';o.scale=(.004,.004,.003);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(iron);smart(o)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o)
# Export body and handle with common floor-centre origin.
for o in parts+[h]:
 bpy.context.scene.cursor.location=(0,0,0);select_only([o]);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
def export(name,obs):
 select_only(obs);bpy.ops.export_scene.fbx(filepath=os.path.join(model,name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,path_mode='AUTO')
export('KI_Pan_Body',parts);export('KI_Pan_Handle',[h])
# Studio camera; export above excludes studio objects.
world=bpy.context.scene.world;world.color=(.15,.15,.15)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((.07,0,.03))-l.location).to_track_quat('-Z','Y').to_euler()
area((-.3,-.5,.8),35,1.2);area((.2,.4,.7),25,.8)
bpy.ops.object.camera_add(location=(.66,-.74,.70));cam=bpy.context.object;cam.rotation_euler=(Vector((.105,0,.035))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.54
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True
s.view_settings.view_transform='AgX';s.render.filepath=os.path.join(preview,'pan-three-quarter.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(model,'KI-PAN-01.blend'));bpy.ops.render.render(write_still=True)
