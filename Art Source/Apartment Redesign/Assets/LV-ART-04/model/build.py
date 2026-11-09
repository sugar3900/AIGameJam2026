import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color,metallic=0,rough=.75,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=rough
 if image:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(image),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=material('Aged walnut',(.25,.1,.04),rough=.78,image=p/'textures/walnut_painterly.png')
art=material('Garden landscape',(.8,.7,.5),rough=.93,image=p/'textures/garden_landscape.png')
brass=material('Muted brass',(.36,.24,.07),metallic=.65,rough=.52)
back=material('Backing board',(.22,.13,.08),rough=.9)

def ring(name,xo,zo,xi,zi,y_front,y_back,mat):
 def rect(x,z,y): return [(-x,y,.26-z),(x,y,.26-z),(x,y,.26+z),(-x,y,.26+z)]
 verts=rect(xo,zo,y_front)+rect(xi,zi,y_front)+rect(xo,zo,y_back)+rect(xi,zi,y_back); faces=[]
 for i in range(4):
  j=(i+1)%4;faces.extend([(i,j,4+j,4+i),(8+j,8+i,12+i,12+j),(j,i,8+i,8+j),(4+i,4+j,12+j,12+i)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co
   side=poly.index//4
   if side in (1,3): u=co.z/.52;v=(abs(co.x)-.28)/.08
   else: u=(co.x+.36)/.72;v=(abs(co.z-.26)-.18)/.08
   uv.data[li].uv=(u,v)
  # Front frame faces use the artwork-facing projection above. Thin edge
  # faces need a second projection axis to avoid zero-area UV islands.
  points=[mesh.vertices[mesh.loops[i].vertex_index].co for i in poly.loop_indices]
  coords=[uv.data[i].uv.copy() for i in poly.loop_indices]
  area=sum(coords[i].x*coords[(i+1)%len(coords)].y-coords[(i+1)%len(coords)].x*coords[i].y for i in range(len(coords)))
  if abs(area)<1e-9:
   spans=[max(q[k] for q in points)-min(q[k] for q in points) for k in range(3)]
   axes=sorted(range(3),key=lambda k:spans[k],reverse=True)[:2]
   for li,q in zip(poly.loop_indices,points):uv.data[li].uv=(q[axes[0]]/.3,q[axes[1]]/.3)
 return o
ring('Mitered walnut moulding',.36,.26,.314,.214,-.030,0,wood)
ring('Raised moulding lip',.355,.255,.345,.245,-.035,-.030,wood)
ring('Brass inner fillet',.316,.216,.308,.208,-.027,-.018,brass)
# Front-facing artwork. Plane normal points toward -Y.
mesh=bpy.data.meshes.new('Picture canvas');mesh.from_pydata([(-.309,-.019,.051),(.309,-.019,.051),(.309,-.019,.469),(-.309,-.019,.469)],[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('Painted garden landscape',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(art);uv=mesh.uv_layers.new(name='UVMap')
for i,coord in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=coord

def box(name,location,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);obj=bpy.context.object;obj.name=name;obj.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);return obj
box('Backing',(0,-.005,.26),(.627,.009,.427),back)
box('Mount plate',(0,-.001,.455),(.045,.002,.025),brass)
objs=list(bpy.context.scene.objects)
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.fbx(filepath=str(p/'model/LV-ART-04.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='AUTO',embed_textures=False)
wall=box('STUDIO_WALL',(0,.04,.26),(1.7,.08,1.4),material('Studio',(.44,.39,.35)))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.18,.18,.18)
bpy.ops.object.light_add(type='AREA',location=(-1.3,-1.8,1.8));bpy.context.object.data.energy=130;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=2
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.98
scene.render.resolution_x=1200;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
def render(name,loc):
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.26))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.image_settings.file_format='PNG';scene.render.filepath=str(p/'previews'/name);bpy.ops.render.render(write_still=True)
render('art-front.png',(0,-3,.26));render('art-three-quarter.png',(.9,-3,.8));render('art-side.png',(3,-.08,.35))
bpy.data.objects.remove(wall,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'model/LV-ART-04.blend'))
