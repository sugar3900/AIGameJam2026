import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name,color,rough=.8,metallic=0,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=rough
 if image:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(image),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=material('Aged walnut',(.3,.15,.08),.8,image=p/'textures/walnut_painterly.png')
art=material('Coastal painting',(.8,.7,.5),.93,image=p/'textures/coastal_landscape.png')
brass=material('Aged brass',(.36,.24,.07),.55,.6)
back=material('Backing board',(.22,.13,.08),.9)
def ring(name,xo,zo,xi,zi,y_front,y_back,mat):
 def rect(x,z,y):return [(-x,y,.225-z),(x,y,.225-z),(x,y,.225+z),(-x,y,.225+z)]
 verts=rect(xo,zo,y_front)+rect(xi,zi,y_front)+rect(xo,zo,y_back)+rect(xi,zi,y_back)
 faces=[]
 for i in range(4):
  j=(i+1)%4;faces.extend([(i,j,4+j,4+i),(8+j,8+i,12+i,12+j),(j,i,8+i,8+j),(4+i,4+j,12+j,12+i)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  side=poly.index//4; face=poly.index%4
  for li in poly.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co
   if face in (0,1):
    # Mitered front/back rings: along strip and across its width.
    u,v=(co.z/.45,abs(co.x)) if side in (1,3) else ((co.x+.275)/.55,abs(co.z-.225))
   elif side in (1,3): u,v=co.z/.45,co.y
   else:u,v=(co.x+.275)/.55,co.y
   uv.data[li].uv=(u,v)
 return o
ring('Mitered walnut frame',.275,.225,.238,.188,-.030,0,wood)
ring('Raised walnut lip',.271,.221,.263,.213,-.035,-.030,wood)
ring('Brass fillet',.240,.190,.234,.184,-.027,-.018,brass)
mesh=bpy.data.meshes.new('Picture canvas');mesh.from_pydata([(-.235,-.019,.040),(.235,-.019,.040),(.235,-.019,.410),(-.235,-.019,.410)],[],[(0,1,2,3)]);mesh.update();obj=bpy.data.objects.new('Coastal landscape',mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(art);uv=mesh.uv_layers.new(name='UVMap')
# 1672x941 source (aspect 1.777), image opening .470/.370=1.270: crop U to preserve image proportions.
ratio=(.470/.370)/(1672/941);left=(1-ratio)/2
for i,coord in enumerate([(left,0),(1-left,0),(1-left,1),(left,1)]):uv.data[i].uv=coord
def box(name,loc,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
box('Backing',(0,-.005,.225),(.478,.009,.378),back)
box('Mount plate',(0,-.001,.405),(.04,.002,.025),brass)
objs=list(bpy.context.scene.objects);bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.fbx(filepath=str(p/'model/OF-ART-LANDSCAPE-01.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='AUTO',embed_textures=False)
wall=box('STUDIO_WALL',(0,.08,.225),(1.5,.08,1.2),material('Studio',(.44,.39,.35)))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.18,.18,.18)
bpy.ops.object.light_add(type='AREA',location=(-1.2,-2,1.7));bpy.context.object.data.energy=150;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=2
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.86
scene.render.resolution_x=1200;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
def render(name,loc):
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.225))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.image_settings.file_format='PNG';scene.render.filepath=str(p/'previews'/name);bpy.ops.render.render(write_still=True)
render('art-front.png',(0,-3,.225));render('art-three-quarter.png',(1.1,-3,.9))
bpy.data.objects.remove(wall,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'model/OF-ART-LANDSCAPE-01.blend'))
