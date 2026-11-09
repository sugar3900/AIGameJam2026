import bpy, math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name, color, rough=.6, image=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if image:
  t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(root/'textures'/image),check_existing=True); m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
floral=mat('Floral_Ceramic',(.8,.75,.66),.47,'floral-ceramic.png'); ivory=mat('Ivory_Ceramic',(.85,.8,.7),.47,'ivory-ceramic.png');rose=mat('Rose_Band',(.51,.27,.25),.57);sage=mat('Sage_Handle',(.30,.36,.22),.65);cream=mat('Ivory_Handle',(.76,.68,.5),.65);bristle=mat('Warm_Bristles',(.9,.87,.76),.82)
# Closed cross-section of a genuinely hollow cup; rings start at outer bottom, go up and back down inner wall.
profile=[(.028,0),(.031,.002),(.034,.008),(.038,.090),(.0382,.096),(.036,.099),(.033,.099),(.0325,.095),(.029,.012),(.027,.009),(.001,.009)]
n=64; verts=[]
for radius,z in profile:
 for j in range(n):
  a=2*math.pi*j/n;verts.append((radius*math.cos(a),radius*math.sin(a),z))
faces=[]
for k in range(len(profile)-1):
 for j in range(n): faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
faces.append(tuple(reversed(tuple(range(n))))); faces.append(tuple((len(profile)-1)*n+j for j in range(n)))
mesh=bpy.data.meshes.new('CupMesh');mesh.from_pydata(verts,[],faces);mesh.update();cup=bpy.data.objects.new('Cup',mesh);bpy.context.collection.objects.link(cup);cup.data.materials.append(floral);cup.data.materials.append(ivory)
uv=mesh.uv_layers.new(name='UVMap')
for i,poly in enumerate(mesh.polygons):
 if i < (len(profile)-1)*n:
  k=i//n;j=i%n;poly.material_index=0 if k<=3 else 1
  coords=[(j/n,profile[k][1]/.099),((j+1)/n,profile[k][1]/.099),((j+1)/n,profile[k+1][1]/.099),(j/n,profile[k+1][1]/.099)]
  for li,coord in zip(poly.loop_indices,coords):uv.data[li].uv=coord
 else:
  poly.material_index=1
  for li in poly.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((v.x/.08)+.5,(v.y/.08)+.5)
for f in mesh.polygons:f.use_smooth=True
# decorative band atop cup wall, UV unwrapped by native primitives
bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=(0,0,.087),major_radius=.0378,minor_radius=.0011);band=bpy.context.object;band.name='RoseBand';band.data.materials.append(rose)
for p in band.data.polygons:p.use_smooth=True
# Helpers to create rounded primitives and combine by assembly.
def cube(name,loc,dim,material,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('soft edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def join_parts(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
cup=join_parts('BA_Cup',[cup,band]);bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
def brush(name,x,tilt,handle):
 parts=[]
 parts.append(cube(name+'_handle',(0,0,.085),(.009,.006,.140),handle,.002))
 parts.append(cube(name+'_neck',(0,0,.160),(.006,.005,.022),handle,.0014))
 parts.append(cube(name+'_head',(0,0,.178),(.010,.005,.030),handle,.002))
 # Curated tuft shapes protrude toward -Y, real geometry, grouped as bristle clusters.
 for z in [.168,.174,.180,.186]:
  for x0 in [-.003,0,.003]:
   parts.append(cube('bristles',(x0,-.0048,z),(.0022,.0048,.0042),bristle,.0007))
 obj=join_parts(name,parts)
 # all points initially world assembled about x=0, object origin at first piece's center
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');obj.rotation_euler[1]=tilt;obj.location=(x,0,0)
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # bake location in mesh so exports share common tabletop datum
 bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
 return obj
b1=brush('BA_Brush_Ivory',-.012,-.11,cream);b2=brush('BA_Brush_Sage',.012,.13,sage)
# Export each mesh with consistent origin; image textures saved alongside the source.
for ob,filename in [(cup,'BA_Cup.fbx'),(b1,'BA_Brush_Ivory.fbx'),(b2,'BA_Brush_Sage.fbx')]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/filename),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True)
# Studio preview set only: export above excludes ground.
ground=cube('PreviewGround',(0,0,-.008),(.7,.7,.015),mat('Ground',(.31,.27,.25)),.001)
world=bpy.context.scene.world;world.color=(.16,.16,.16)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.09))-o.location).to_track_quat('-Z','Y').to_euler()
area((-.25,-.4,.55),7,.48);area((.35,-.1,.3),3,.35)
bpy.ops.object.camera_add(location=(.30,-.48,.30));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.095))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.31;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'
for img in bpy.data.images:
 if img.source == 'FILE' and img.filepath:
  img.filepath='//../textures/'+Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'BA-CUP-01.blend'));scene.render.filepath=str(root/'previews'/'cup-perspective.png');bpy.ops.render.render(write_still=True)
