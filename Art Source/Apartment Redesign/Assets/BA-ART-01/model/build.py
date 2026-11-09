import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,metallic=0,rough=.8,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=rough
 if image:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(image),check_existing=True);tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=mat('Aged ivory painted frame',(.83,.79,.69),rough=.85,image=p/'textures/ivory_frame.png')
art=mat('Botanical print',(.8,.7,.5),rough=.94,image=p/'textures/fern_print.png')
brass=mat('Muted brass',(.36,.24,.07),metallic=.65,rough=.52)
back=mat('Backing board',(.22,.13,.08),rough=.9)
# Rectangular ring with true corner mitres. Portrait frame, 0.45 x 0.55 m.
def ring(name,xo,zo,xi,zi,yfront,yback,material):
 def rect(x,z,y):return [(-x,y,.275-z),(x,y,.275-z),(x,y,.275+z),(-x,y,.275+z)]
 verts=rect(xo,zo,yfront)+rect(xi,zi,yfront)+rect(xo,zo,yback)+rect(xi,zi,yback)
 faces=[]
 for i in range(4):
  j=(i+1)%4;faces.extend([(i,j,4+j,4+i),(8+j,8+i,12+i,12+j),(j,i,8+i,8+j),(4+i,4+j,12+j,12+i)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material);uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co; side=poly.index//4
   uv.data[li].uv=(co.z/.55,(abs(co.x)-.17)/.05) if side in (1,3) else ((co.x+.225)/.45,(abs(co.z-.275)-.22)/.05)
 return obj
ring('Mitered walnut frame',.225,.275,.190,.240,-.030,0,wood)
ring('Raised frame lip',.221,.271,.213,.263,-.035,-.030,wood)
ring('Brass inner fillet',.192,.242,.187,.237,-.027,-.018,brass)
mesh=bpy.data.meshes.new('Picture surface');mesh.from_pydata([(-.188,-.019,.037),(.188,-.019,.037),(.188,-.019,.513),(-.188,-.019,.513)],[],[(0,1,2,3)]);mesh.update();obj=bpy.data.objects.new('Botanical artwork',mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(art);uv=mesh.uv_layers.new(name='UVMap')
for i,coord in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=coord
def box(name,location,dimensions,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
box('Backing',(0,-.005,.275),(.38,.009,.48),back)
box('Mount plate',(0,-.001,.475),(.035,.002,.025),brass)
# Adapt the existing period-frame structure to 0.30 × 0.36 m.
# Scale object locations and local mesh vertices, preserving pivot and UVs.
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':
  o.location.x *= 2/3; o.location.z *= 36/55
  for v in o.data.vertices: v.co.x *= 2/3; v.co.z *= 36/55
objs=list(bpy.context.scene.objects);bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.fbx(filepath=str(p/'model/BA-ART-01.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='AUTO',embed_textures=False)
wall=box('STUDIO_WALL',(0,.08,.18),(1.4,.08,1.4),mat('Studio',(.61,.56,.51)))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.18,.18,.18)
bpy.ops.object.light_add(type='AREA',location=(-1.4,-2,2.0));bpy.context.object.data.energy=140;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=2.4
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.56
scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
def render(name,loc):
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.18))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.image_settings.file_format='PNG';scene.render.filepath=str(p/'previews'/name);bpy.ops.render.render(write_still=True)
render('art-front.png',(0,-3,.18));render('art-three-quarter.png',(1.1,-3,.95));render('art-side.png',(2,-1,.4))
bpy.data.objects.remove(wall,do_unlink=True);bpy.ops.wm.save_as_mainfile(filepath=str(p/'model/BA-ART-01.blend'))
