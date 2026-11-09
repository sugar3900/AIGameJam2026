"""KI-MUG-01: meters, Z up, floor-centered origin, front -Y; background Blender."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; MOD=P/'model'; PRE=P/'previews'; TEX=P/'textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.58,img=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
 if img:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(TEX/img),check_existing=True);m.node_tree.links.new(n.outputs['Color'],b.inputs['Base Color'])
 return m
ceramic=mat('Ivory_Painted_Ceramic',(.8,.68,.5),.43,'ivory-ceramic.png'); rose=mat('Dusty_Rose',(.53,.22,.19),.62); leaf=mat('Muted_Sage',(.28,.33,.19),.7); pollen=mat('Ochre',(.59,.42,.19),.65)
parts=[]
def lathe(name,profile,material,n=64,caps=True):
 verts=[]; faces=[]
 for r,z in profile:
  for i in range(n):
   a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 
 if caps: faces.append(tuple(reversed(range(n)))); faces.append(tuple((len(profile)-1)*n+i for i in range(n)))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
 for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
 parts.append(obj);return obj
# Profile rises outer surface, rounds over the lip, and returns down the actual inner cavity.
profile=[(.029,0),(.034,.001),(.038,.006),(.041,.018),(.043,.038),(.042,.058),(.040,.078),(.042,.099),(.044,.105),(.0438,.107),(.041,.108),(.039,.106),(.037,.100),(.035,.078),(.037,.058),(.038,.038),(.036,.020),(.032,.011),(.026,.008),(.004,.008)]
body=lathe('Hollow ceramic body',profile,ceramic)
def tube(name,points,r,material):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=20;c.bevel_depth=r;c.bevel_resolution=4
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for q,co in zip(s.bezier_points,points):q.co=co;q.handle_left_type='AUTO';q.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(ob);ob.data.materials.append(material);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
 for p in ob.data.polygons:p.use_smooth=True
 parts.append(ob);return ob
# Loop is ceramic, reaches approx 0.12m overall width; attachments overlap the wall.
tube('Loop handle',[(.038,0,.083),(.049,0,.086),(.060,0,.077),(.062,0,.059),(.056,0,.044),(.040,0,.035)],.005,ceramic)
# Raised rose band remains visually thin, not chunky paint.
lathe('Rose rim stripe',[(.04305,.097),(.0436,.1015)],rose,caps=False)
def ellipsoid(name,loc,scale,material,rot=0):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.rotation_euler[1]=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o);return o
# UVs for each mesh. Smart projection protects against degenerate loops on poles/caps.
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
# Cylindrical painted decoration on the exterior; inner wall and handle stay plain ivory.
floral=mat('Floral_Ceramic',(.8,.68,.5),.43,'floral-ceramic.png')
body.data.materials.append(floral)
uv=body.data.uv_layers.active
n=64
for poly in body.data.polygons:
 j=poly.index//n
 if poly.index < n*8:
  poly.material_index=1
  for li in poly.loop_indices:
   v=body.data.vertices[body.data.loops[li].vertex_index]
   idx=body.data.loops[li].vertex_index
   col=idx%n
   # Unwrap once around, keeping seam on the back, and use full motif height.
   u=((col/n)+.5)%1
   if poly.index%n==31 and u<.1:u=1
   uv.data[li].uv=(u,max(0,min(1,v.co.z/.105)))
# Common floor datum: join after resetting all origins to world cursor.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body.name='KI_Mug_01';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(MOD/'KI_Mug_01.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.camera_add(location=(.23,-.34,.24));cam=bpy.context.object;cam.rotation_euler=(Vector((.009,0,.053))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.18;bpy.context.scene.camera=cam
for pos,power,size in [((-.28,-.35,.48),3,.4),((.32,.1,.32),1,.35)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.05))-o.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.14,.12,.1)
bpy.ops.wm.save_as_mainfile(filepath=str(MOD/'KI-MUG-01.blend'));sc.render.filepath=str(PRE/'mug-perspective.png');bpy.ops.render.render(write_still=True)
