"""Build KI-BUCKET-01 with Blender 5.x background. Dimensions in metres; Z up."""
import bpy, math, os
from mathutils import Vector
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M=os.path.join(D,'model'); P=os.path.join(D,'previews'); T=os.path.join(D,'textures')
os.makedirs(P,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
def material(name,col,metal=0,rough=.55,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(texture,check_existing=True);n.interpolation='Linear';m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
zinc=material('Painted_Zinc',(.45,.43,.40),.55,.47,os.path.join(T,'zinc-candidate-a.png'))
edge=material('Aged_Metal',(.29,.25,.19),.7,.35);water=material('Water',(.67,.76,.72),0,.12)
wp=water.node_tree.nodes.get('Principled BSDF');wp.inputs['Transmission Weight'].default_value=.88;wp.inputs['IOR'].default_value=1.333
ripple_mat=material('Water_Ripple',(.32,.40,.38),.12,.25)
def uv(o):
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
def mesh(name,verts,faces,mat):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.data.materials.append(mat);uv(o);return o
def torus(name,major,minor,z,mat):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=(0,0,z),major_radius=major,minor_radius=minor);o=bpy.context.object;o.name=name;o.data.materials.append(mat);uv(o);return o
def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);uv(o);return o
def path(name,pts,radius,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=4;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);uv(o);return o
# Tapered hollow shell: four loops top/bottom and inner/outer, with floor.
n=64;verts=[]
for r,z in [(.120,.012),(.160,.252),(.154,.246),(.114,.020)]:
 for i in range(n):
  a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
faces=[]
for k in range(3):
 for i in range(n):j=(i+1)%n;faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
faces.append(tuple(reversed(range(n))));faces.append(tuple(3*n+i for i in range(n)))
body=[mesh('Hollow tapered zinc shell',verts,faces,zinc),torus('Rolled upper rim',.158,.004,.251,edge),torus('Bottom rolled seam',.121,.0035,.014,edge),torus('Raised upper rib',.149,.0022,.190,edge)]
# Riveted handle mounting plates at either side.
for sign in (-1,1):
 a=sign*.157;body.append(sphere('Handle lug',(a,0,.225),(.012,.012,.019),edge));body.append(sphere('Rivet',(a+sign*.008,-.004,.226),(.0035,.0035,.0035),edge))
# Wire bail lies in XZ plane. Its origin is the axle midpoint, to rotate about X.
pts=[]
for i in range(65):
 a=math.pi*i/64;pts.append((-.165*math.cos(a),0,.225+.184*math.sin(a)))
handle=path('Pivoted wire handle',pts,.0033,edge);bpy.context.scene.cursor.location=(0,0,.225);bpy.context.view_layer.objects.active=handle;handle.select_set(True);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');handle.select_set(False)
# Water is separately switchable; not inside bucket in repaired state.
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.133,depth=.002,location=(0,0,.17));wet=bpy.context.object;wet.name='Optional water level';wet.data.materials.append(water);uv(wet)
water_objects=[wet]
for k,radius in enumerate((.027,.048,.069)):
 angles=[(.25+k*.64)+(4.1-0.2*k)*i/48 for i in range(49)]
 points=[(radius*math.cos(a),radius*(.88+.04*k)*math.sin(a),.1712) for a in angles]
 ripple=path('Subtle water ripple',points,.00023,ripple_mat);water_objects.append(ripple)
# The asset files retain distinct pivots, dimensions and material names.
def export_group(name,objects,pivot):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.duplicate();objs=list(bpy.context.selected_objects);bpy.context.view_layer.objects.active=objs[0]
 if len(objs)>1:bpy.ops.object.join()
 o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(M,name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
 bpy.ops.object.delete(use_global=False)
export_group('KI_Bucket_Body',body,(0,0,0));export_group('KI_Bucket_Handle',[handle],(0,0,.225));export_group('KI_Bucket_Water',water_objects,(0,0,0))
# Studio camera and warm neutral illumination.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.18,.18,.18)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.color=(1.0,.83,.67);o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.19))-o.location).to_track_quat('-Z','Y').to_euler()
area((1.0,-1.2,1.4),75,1.7);area((-.9,.4,1.0),40,1.2)
bpy.ops.object.camera_add(location=(.75,-1.05,1.05));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=.72;camera.rotation_euler=(Vector((0,0,.22))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
# Stage renders show empty/upright and filled/lowered without changing exports.
[setattr(o,'hide_render',True) for o in water_objects];scene.render.filepath=os.path.join(P,'bucket-empty-handle-up.png');bpy.ops.render.render(write_still=True)
[setattr(o,'hide_render',False) for o in water_objects];handle.rotation_euler.x=math.radians(-72);scene.render.filepath=os.path.join(P,'bucket-water-handle-down.png');bpy.ops.render.render(write_still=True)
handle.rotation_euler.x=0;[setattr(o,'hide_render',True) for o in water_objects]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(M,'KI-BUCKET-01.blend'))
print('BUCKET COMPLETE')
