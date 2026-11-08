"""KI-KETTLE-01: floor-origin, metres, Z up. Blender 5.x background build."""
import bpy, math, os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parents[1]; MODEL=P/'model'; PRE=P/'previews'; TEX=P/'textures'
for p in (MODEL,PRE,TEX): p.mkdir(exist_ok=True,parents=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(n,c,rough=.6,metal=0,texture=None):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(TEX/texture),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
ivory=material('Painted_Ivory_Enamel',(.78,.64,.46),.48,0,'enamel-selected.png')
metal=material('Aged_Steel',(.24,.20,.15),.43,.48,'steel-selected.png');dark=material('Dark_Interior',(.045,.035,.025),.8);wood=material('Warm_Wood_Grip',(.26,.09,.035),.52,0,'wood-selected.png')

def mesh_lathe(name,profile,mat,n=64):
 verts=[];faces=[]
 for r,z in profile:
  for i in range(n):
   a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  for li in poly.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=((math.atan2(co.y,co.x)/(2*math.pi))%1,co.z/.16)
 for p in me.polygons:p.use_smooth=(len(p.vertices)==4)
 return o

def torus(name,R,r,z,mat):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=(0,0,z),major_radius=R,minor_radius=r);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def tube(name,points,radius,mat,res=10):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16;curve.bevel_depth=radius;curve.bevel_resolution=3
 s=curve.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,c in zip(s.bezier_points,points):p.co=c;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
 for p in o.data.polygons:p.use_smooth=True
 return o

def ball(name,xyz,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=xyz);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def ring_spout():
 # hollow tapered spout, local axis from body outward/upward
 start=Vector((-.080,0,.070));end=Vector((-.157,0,.135));axis=(end-start).normalized();v=Vector((0,1,0));w=axis.cross(v).normalized();n=40
 verts=[];faces=[]
 for t,r in [(0,.026),(.58,.019),(1,.016),(1,.012),(.58,.015),(0,.022)]:
  c=start.lerp(end,t)
  for i in range(n):
   a=2*math.pi*i/n;verts.append(tuple(c+r*(v*math.cos(a)+w*math.sin(a))))
 for j in range(5):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 me=bpy.data.meshes.new('Spout');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Hollow enamel spout',me);bpy.context.collection.objects.link(o);o.data.materials.append(ivory);o.data.materials.append(dark)
 for p in me.polygons: p.material_index = 1 if p.index >= 3*n else 0
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 for p in me.polygons:p.use_smooth=True
 return o

# Turned body follows the concept's squat dome and has an actual open neck.
body=[]
body.append(mesh_lathe('Kettle hollow body',[(.085,.004),(.096,.010),(.101,.025),(.102,.055),(.098,.080),(.089,.103),(.076,.118),(.063,.125),(.058,.125),(.058,.117),(.065,.111),(.076,.100),(.083,.079),(.086,.055),(.085,.025),(.079,.014)],ivory))
body.append(torus('Aged base rim',.094,.004,.009,metal));body.append(torus('Neck rolled rim',.060,.003,.125,metal));body.append(ring_spout())
# Short inner throat makes the mouth dark and visibly hollow.
body.append(ball('Spout recessed shadow',(-.129,0,.111),(.010,.010,.010),dark))
# Metal arch mounts and separate wooden grip, hollow mouth remains visible.
body.append(tube('Left metal handle',[(-.079,0,.108),(-.085,0,.142),(-.078,0,.175),(-.056,0,.195)],.004,metal))
body.append(tube('Right metal handle',[(.079,0,.108),(.085,0,.142),(.078,0,.175),(.056,0,.195)],.004,metal))
body.append(tube('Turned wooden handgrip',[(-.057,0,.195),(-.029,0,.207),(0,0,.211),(.029,0,.207),(.057,0,.195)],.009,wood))
for x in [-.079,.079]:
 body.append(ball('Riveted handle mount',(x,0,.110),(.010,.006,.012),metal));body.append(ball('Mount rivet',(x,-.006,.110),(.003,.002,.003),metal))
# Removable lid as an independent part with matching world/floor origin.
lid=[];lid.append(mesh_lathe('Domed metal lid',[(.058,.126),(.056,.131),(.049,.139),(.036,.145),(.018,.149),(.006,.149)],metal));lid.append(torus('Lid rim',.056,.0025,.127,metal));lid.append(ball('Lid knob',(0,0,.157),(.012,.012,.009),wood))
# Export each named mesh group with a shared world origin.
def export(name,group):
 for obj in group:
  if not obj.data.uv_layers:
   bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
   bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0]
 bpy.ops.export_scene.fbx(filepath=str(MODEL/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
export('KI_Kettle_Body',body);export('KI_Kettle_Lid',lid)
# Render an isolated 3/4 with warm diffuse light.
def camera():
 bpy.ops.object.camera_add(location=(-.38,-.48,.32));o=bpy.context.object;o.name='PreviewCamera';o.rotation_euler=((Vector((0,0,.10))-o.location).to_track_quat('-Z','Y')).to_euler();o.data.type='ORTHO';o.data.ortho_scale=.44;bpy.context.scene.camera=o
 for pos,power,size in [((-.32,-.42,.60),5.0,.48),((.4,.05,.4),1.5,.40)]:
  bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.1))-l.location).to_track_quat('-Z','Y').to_euler()
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.14,.12,.10)
 return scene
scene=camera();bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/'KI-KETTLE-01.blend'))
scene.render.filepath=str(PRE/'kettle-closed.png');bpy.ops.render.render(write_still=True)
for o in lid:
 o.location.x += .085
 o.location.y -= .03
 o.location.z += .055
a=scene.render.filepath=str(PRE/'kettle-lid-off.png');bpy.ops.render.render(write_still=True)
