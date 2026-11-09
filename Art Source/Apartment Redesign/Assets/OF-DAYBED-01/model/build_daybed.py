import bpy, math, os, mathutils
from mathutils import Vector
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name, image=None, color=(.5,.3,.2,1), rough=.8):
 m=bpy.data.materials.new(name); m.diffuse_color=color; m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=color; p.inputs['Roughness'].default_value=rough; p.inputs['Specular IOR Level'].default_value=.18
 if image:
  t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(os.path.join(D,'textures',image),check_existing=True); m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
wood=mat('Walnut painted','walnut-aged.png'); linen=mat('Ivory linen','ivory-linen.png'); quilt=mat('Floral quilt','quilt-floral.png'); rose=mat('Rose knit','rose-knit.png'); sage=mat('Sage cloth',color=(.27,.34,.22,1))
frame=[]; bedding=[]
def box(name,loc,dim,material,bevel=.015, group=frame, rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if rot:o.rotation_euler=rot
 if bevel:
  mod=o.modifiers.new('Softened edges','BEVEL'); mod.width=bevel; mod.segments=3; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(material); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.03); bpy.ops.object.mode_set(mode='OBJECT'); group.append(o); return o
def post(name,x,y,z,height,radius):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=radius,depth=height,location=(x,y,z)); o=bpy.context.object; o.name=name; o.data.materials.append(wood); frame.append(o)
 for f in o.data.polygons:f.use_smooth=True
 return o
def sphere(name,loc,scale,material,group=frame):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material); group.append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
# rails and crosspieces
for y in (-.35,.35):box('Long walnut apron', (0,y,.29),(1.73,.06,.16),wood)
for x in (-.88,.88):
 box('End lower rail',(x,0,.32),(.07,.70,.09),wood)
 box('End top rail',(x,0,.77),(.075,.70,.075),wood,.025)
 for y in (-.34,.34):
  post('Turned corner post',x,y,.43,.78,.027)
  for z,r,h in [(.14,.039,.055),(.70,.038,.04),(.78,.038,.035)]: post('Post collar',x,y,z,h,r)
  sphere('Round finial',(x,y,.825),(.045,.045,.045),wood)
 for y in (-.23,-.115,0,.115,.23):
  post('End spindle',x,y,.55,.40,.012)
  sphere('Spindle turning',(x,y,.55),(.019,.019,.07),wood)
box('Mattress',(0,0,.405),(1.68,.64,.19),linen,.06,bedding)
# seam piping along mattress exposed sides
for y in (-.32,.32):box('Mattress piping',(0,y,.475),(1.56,.012,.012),linen,.005,bedding)
box('Sage cushion',(.63,.09,.585),(.33,.39,.13),sage,.065,bedding,rot=(0,-.29,.08))
box('Rose cushion',(.42,-.15,.57),(.27,.25,.115),rose,.055,bedding,rot=(.08,-.09,-.17))
# continuous quilt across mattress and down front, with gentle irregular folds
verts=[]; faces=[]; nx=32; ny=32
for j in range(ny+1):
 v=j/ny
 if v<.72:
  y=.30-v/.72*.65; z=.515
 else:
  t=(v-.72)/.28; y=-.35-.055*min(1,t*4); z=.515-.27*t
 for i in range(nx+1):
  u=i/nx; x=-.80+1.03*u+.015*math.sin(v*8+u*3)*(u**5)
  fold=.012*math.sin(u*math.pi*5+v*3)+.008*math.sin(v*19+u*5)+.007*math.sin(u*12-v*10)
  # An irregular softened hem and hanging fabric that gathers gently at the front.
  sag=(max(0,(v-.72)/.28))**2 * (.025*math.sin(u*5*math.pi)+.012*math.sin(u*13))
  verts.append((x,y+.008*math.sin(u*8+v*4),z+fold-sag))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i; faces.append((a,a+1,a+nx+2,a+nx+1))
mesh=bpy.data.meshes.new('Quilt drape mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('Floral quilt drape',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(quilt); bedding.append(o)
uv=mesh.uv_layers.new(name='Cloth UV')
for p in mesh.polygons:
 p.use_smooth=True
 for li in p.loop_indices:
  idx=mesh.loops[li].vertex_index; uv.data[li].uv=(idx%(nx+1)/nx,idx//(nx+1)/ny)
mod=o.modifiers.new('Fabric thickness','SOLIDIFY'); mod.thickness=.008; bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); o.select_set(False)
# A slim stitched hem follows the irregular front edge of the quilt.
def seam(points,name,material,radius=.003):
 curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'; curve.resolution_u=2; curve.bevel_depth=radius; curve.bevel_resolution=2
 spline=curve.splines.new('POLY'); spline.points.add(len(points)-1)
 for p,co in zip(spline.points,points):p.co=(*co,1)
 ob=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(ob); ob.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.convert(target='MESH'); bedding.append(bpy.context.object)
seam([(x,y-.004,z+.002) for x,y,z in verts[ny*(nx+1):(ny+1)*(nx+1)]], 'Quilt stitched hem', linen)
# export selected mesh sets
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for obj in objects:obj.select_set(True)
 bpy.ops.export_scene.fbx(filepath=os.path.join(D,'model',name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',path_mode='AUTO')
export('OF_DAYBED_Assembly',frame+bedding); export('OF_DAYBED_Frame',frame); export('OF_DAYBED_Bedding',bedding)
bpy.ops.object.select_all(action='DESELECT')
# studio preview
world=bpy.context.scene.world; world.color=(.22,.22,.22)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc); ob=bpy.context.object; ob.data.energy=power; ob.data.shape='DISK'; ob.data.size=size; ob.rotation_euler=(Vector((0,0,.4))-ob.location).to_track_quat('-Z','Y').to_euler()
area((0,-3,4),600,4); area((-3,2,2.5),400,3)
bpy.ops.object.camera_add(location=(3,-4,2.5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.4))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.7
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1100; scene.render.resolution_y=850; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D,'model','OF_DAYBED_Source.blend'))
scene.render.filepath=os.path.join(D,'previews','daybed-perspective.png'); bpy.ops.render.render(write_still=True)
