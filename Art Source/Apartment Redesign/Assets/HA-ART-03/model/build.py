import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, rough=.75, image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=rough
 if image:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(image),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=material('Aged walnut',(.25,.1,.04),rough=.78,image=p/'textures/walnut_painterly.png')
art=material('Landscape painting',(.8,.7,.5),rough=.93,image=p/'textures/countryside.png')
brass=material('Muted brass',(.36,.24,.07),metallic=.65,rough=.52)
back=material('Backing board',(.22,.13,.08),rough=.9)

def ring(name,xo,zo,xi,zi,y_front,y_back,mat):
 # Ring vertices ordered outer/inner, front/back, diagonal corners give actual mitred joins.
 def rect(x,z,y): return [(-x,y,.325-z),(x,y,.325-z),(x,y,.325+z),(-x,y,.325+z)]
 v=rect(xo,zo,y_front)+rect(xi,zi,y_front)+rect(xo,zo,y_back)+rect(xi,zi,y_back)
 faces=[]
 for i in range(4):
  j=(i+1)%4;faces.extend([(i,j,4+j,4+i),(8+j,8+i,12+i,12+j),(j,i,8+i,8+j),(4+i,4+j,12+j,12+i)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co
   # Project each face along its dominant normal so sides retain UV area.
   n=poly.normal
   if abs(n.y)>=max(abs(n.x),abs(n.z)): u,v=(co.x+.45)/.9,co.z/.65
   elif abs(n.x)>=abs(n.z): u,v=co.y/.035,co.z/.65
   else: u,v=(co.x+.45)/.9,co.y/.035
   uv.data[li].uv=(u,v)
 return o
ring('Mitered walnut moulding',.45,.325,.395,.270,-.030,0,wood)
ring('Raised moulding lip',.444,.319,.432,.307,-.035,-.030,wood)
ring('Brass inner fillet',.397,.272,.389,.264,-.027,-.018,brass)
# Flat picture mesh, front facing -Y with one coherent UV island.
mesh=bpy.data.meshes.new('Picture canvas');mesh.from_pydata([(-.390,-.019,.061),(.390,-.019,.061),(.390,-.019,.589),(-.390,-.019,.589)],[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('Painted landscape',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(art);uv=mesh.uv_layers.new(name='UVMap')
for i,coord in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=coord

def box(name,location,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);obj=bpy.context.object;obj.name=name;obj.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);return obj
box('Backing', (0,-.005,.325),(.79,.009,.54),back)
# Back mounting keyhole has its own geometry, within frame depth.
box('Mount plate', (0,-.001,.575),(.045,.002,.025),brass)
# Resize frame and canvas in actual mesh coordinates, preserving floor origin.
for ob in [obj for obj in bpy.context.scene.objects if obj.type=='MESH']:
 for vert in ob.data.vertices:
  vert.co.x *= .65/.9
  vert.co.z *= .52/.65
 ob.location.x *= .65/.9
 ob.location.z *= .52/.65
# Select only artifact objects for export.
objs=list(bpy.context.scene.objects)
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.fbx(filepath=str(p/'model/HA-ART-03.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='AUTO',embed_textures=False)
# Preview-only objects.
wall=box('STUDIO_WALL',(0,.08,.26),(2,.08,1.6),material('Studio',(.44,.39,.35)))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.color=(.18,.18,.18)
bpy.ops.object.light_add(type='AREA',location=(-1.6,-2,2.2));bpy.context.object.data.energy=190;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=2.4
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.95
scene.render.resolution_x=1200;scene.render.resolution_y=950;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
def render(name,loc):
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.26))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.image_settings.file_format='PNG';scene.render.filepath=str(p/'previews'/name);bpy.ops.render.render(write_still=True)
render('art-front.png',(0,-3,.26));render('art-three-quarter.png',(1.1,-3,1.05))
bpy.data.objects.remove(wall,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'model/HA-ART-03.blend'))
