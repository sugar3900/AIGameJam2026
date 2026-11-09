import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,tex,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
 im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(P/'textures'/tex),check_existing=True);im.image.pack();im.image.filepath='//../textures/'+tex
 m.node_tree.links.new(im.outputs['Color'],p.inputs['Base Color']);return m
ceramic=mat('Warm floral glazed ceramic','floral-ceramic.png',.56)
ivory=mat('Warm ivory ceramic ribs','ceramic-ivory.png',.58)
soapmat=mat('Painterly dusty rose soap','soap-rose.png',.8)
def finish(o,m):
 o.data.materials.append(m)
 for poly in o.data.polygons:poly.use_smooth=True
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT');return o
def join(name,obs,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
# Continuous thick ceramic bowl profile: bottom -> exterior -> scalloped lip -> interior -> floor.
N=96
prof=[(.001,.004),(.60,.004),(.78,.006),(.90,.011),(.97,.020),(1.0,.028),(.976,.030),(.94,.025),(.86,.017),(.74,.012),(.001,.012)]
verts=[];faces=[]
for frac,z in prof:
 for i in range(N):
  a=2*math.pi*i/N;scallop=1+.025*math.cos(12*a)*(frac**4)
  verts.append((.073*frac*scallop*math.cos(a),.052*frac*scallop*math.sin(a),z+.0013*math.cos(12*a)*(frac**6)))
for j in range(len(prof)-1):
 for i in range(N): faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
mesh=bpy.data.meshes.new('Dish mesh');mesh.from_pydata(verts,[],faces);mesh.update()
dish=bpy.data.objects.new('Dish',mesh);bpy.context.collection.objects.link(dish);finish(dish,ceramic)
# Map the floral wrap around the exterior instead of relying on smart-project islands.
uv=mesh.uv_layers.active.data
for j in range(5):
 for i in range(N):
  poly=mesh.polygons[j*N+i];u0=i/N;u1=(i+1)/N;v0=.08+.29*j/5;v1=.08+.29*(j+1)/5
  for li,xy in zip(poly.loop_indices,[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]):uv[li].uv=xy
parts=[dish]
# Three raised smooth drainage beads inside, aligned front-to-back.
for x in [-.025,0,.025]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(x,0,.0145));o=bpy.context.object;o.name='Drainage rib';o.scale=(.0025,.027,.0025);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,ivory);parts.append(o)
dish=join('BA_SoapDish',parts,(0,0,0))
# Rounded bar sits on ribs. Center at placement origin for independent handling.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.029));bar=bpy.context.object;bar.name='Bar';bar.dimensions=(.095,.060,.024);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
b=bar.modifiers.new('Soft rounded soap','BEVEL');b.width=.011;b.segments=6;bpy.context.view_layer.objects.active=bar;bpy.ops.object.modifier_apply(modifier=b.name);finish(bar,soapmat)
bar=join('BA_SoapBar',[bar],(0,0,0))
for o in [dish,bar]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',bake_space_transform=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.25,.25,.25)
def light(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.015))-o.location).to_track_quat('-Z','Y').to_euler()
light((-.55,-.8,1.1),20,1.3);light((.7,.3,.8),10,1.0)
bpy.ops.object.camera_add(location=(.35,-.49,.37));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.015))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.235;scene.camera=cam
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(P/'previews/soap-on-dish.png');bpy.ops.render.render(write_still=True)
bar.hide_render=True;scene.render.filepath=str(P/'previews/dish-empty.png');bpy.ops.render.render(write_still=True);bar.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-SOAP-01.blend'))
