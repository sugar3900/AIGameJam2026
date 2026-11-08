import bpy, math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
def mat(name,path,tint,metal=0,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*tint,1);n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures'/path),check_existing=True)
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*tint,1);l.new(t.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color']);return m
brass=mat('Patinated Brass','aged-brass.png',(.8,.75,.56),.68,.45)
paper=mat('Ivory paper','paper.png',(.96,.94,.88),0,.92)
core=mat('Cardboard core','paper.png',(.54,.44,.32),0,.95)
rollcenter=Vector((0,-.071,-.014))
def apply_uv(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if o.type=='CURVE':
  bpy.ops.object.convert(target='MESH');o=bpy.context.object
  while o.data.uv_layers:o.data.uv_layers.remove(o.data.uv_layers[0])
 if not o.data.uv_layers:
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 return o
def cylinder(name,r,depth,loc,rot,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(material);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 
 if name!='Fastener':
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=.0006;mod.segments=2
 for p in o.data.polygons:p.use_smooth=True
 return o
def tube(name,coords,r):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(coords)-1)
 for p,v in zip(sp.bezier_points,coords):p.co=v;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.data.materials.append(brass);return apply_uv(ob)
parts=[]
for x in (-.069,.069):
 parts += [cylinder('Round mounting rosette',.021,.006,(x,-.003,0),(math.pi/2,0,0),brass),cylinder('Rosette collar',.011,.008,(x,-.009,0),(math.pi/2,0,0),brass)]
 parts.append(tube('Curved support',[(x,-.012,0),(x,-.025,-.001),(x,-.049,-.010),(x,-.071,-.014)],.0043))
 for a in (math.pi/2,math.pi*7/6,math.pi*11/6):
  parts.append(cylinder('Fastener',.0015,.001,(x+.014*math.cos(a),-.0065,.014*math.sin(a)),(math.pi/2,0,0),brass))
parts.append(cylinder('Spindle',.006,.142,rollcenter,(0,math.pi/2,0),brass))
for x in (-.062,.062):parts.append(cylinder('Spindle collar',.010,.006,(x,rollcenter.y,rollcenter.z),(0,math.pi/2,0),brass))
# Genuine hollow annular paper cylinder, X axis. Four quad surfaces, shared UVs.
N=64; vertices=[]
for x,r in [(-.052,.047),(.052,.047),(-.052,.013),(.052,.013)]:
 for i in range(N):
  a=2*math.pi*i/N;vertices.append((x,rollcenter.y+r*math.sin(a),rollcenter.z+r*math.cos(a)))
faces=[]
for i in range(N):
 j=(i+1)%N
 faces.extend([(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(i,2*N+i,2*N+j,j),(N+j,3*N+j,3*N+i,N+i)])
mesh=bpy.data.meshes.new('Hollow paper roll');mesh.from_pydata(vertices,[],faces);mesh.update();roll=bpy.data.objects.new('Paper roll',mesh);bpy.context.collection.objects.link(roll);roll.data.materials.append(paper);roll.data.materials.append(core)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 typ=poly.index%4; idx=poly.index//4;poly.material_index=1 if typ==1 else 0;poly.use_smooth=typ in (0,1)
 for li in poly.loop_indices:
  v=mesh.vertices[mesh.loops[li].vertex_index].co
  if typ in (2,3):uv.data[li].uv=((v.y-rollcenter.y)/.11+.5,(v.z-rollcenter.z)/.11+.5)
  else:
   ang=math.atan2(v.y-rollcenter.y,v.z-rollcenter.z)%(2*math.pi);u=ang/(2*math.pi)
   if idx==N-1 and u<.1:u=1
   uv.data[li].uv=(u,(v.x+.052)/.104)
# paper tail gracefully leaves front underside; tiny transverse curvature
verts=[];faces=[];nx=12;ny=18
for j in range(ny+1):
 t=j/ny
 for i in range(nx+1):
  u=i/nx;x=(u-.5)*.104; y=rollcenter.y-.046+.004*t+.001*math.sin(u*math.pi*2)*t;z=rollcenter.z-.009-.065*t+.001*math.sin(u*math.pi*2)*t
  verts.append((x,y,z))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Paper tail');me.from_pydata(verts,[],faces);me.update();tail=bpy.data.objects.new('Paper tail',me);bpy.context.collection.objects.link(tail);tail.data.materials.append(paper);uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  vi=me.loops[li].vertex_index;uv.data[li].uv=((vi%(nx+1))/nx,(vi//(nx+1))/ny)
# Tail is a zero-thickness sheet; use a two-sided Unreal paper material.
# Thin inset rings hint at paper layers on the visible roll ends.
layers=mat('Paper layer edges','paper.png',(.84,.81,.74),0,.95)
ring_objects=[]
for x in (-.05215,.05215):
 for rad in (.020,.028,.036,.043):
  bpy.ops.mesh.primitive_torus_add(major_radius=rad,minor_radius=.00012,major_segments=48,minor_segments=6,location=(x,rollcenter.y,rollcenter.z),rotation=(0,math.pi/2,0))
  ob=bpy.context.object;ob.name='Paper layer edge';ob.data.materials.append(layers);ring_objects.append(ob)
# Join all paper pieces; origin at roll axis, allowing optional roll rotation.
bpy.ops.object.select_all(action='DESELECT');roll.select_set(True);tail.select_set(True)
for o in ring_objects:o.select_set(True)
bpy.context.view_layer.objects.active=roll;bpy.ops.object.convert(target='MESH');bpy.ops.object.join();roll=bpy.context.object
bpy.context.scene.cursor.location=rollcenter;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
def export(name,obs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.export_scene.fbx(filepath=str(R/'model'/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False)
export('BA_Roll_Holder.fbx',parts);export('BA_Roll_Paper.fbx',[roll])
# preview wall only
m=bpy.data.materials.new('Preview warm plaster');m.diffuse_color=(.53,.43,.41,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.025,-.035));wall=bpy.context.object;wall.name='Preview wall';wall.dimensions=(.50,.045,.38);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.data.materials.append(m)
bpy.ops.object.camera_add(location=(.38,-.63,.22));camera=bpy.context.object;camera.rotation_euler=(Vector((0,-.05,-.025))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.33;bpy.context.scene.camera=camera
for loc,power,size in [((.3,-.7,.8),28,1.1),((-.5,-.4,.3),18,.8)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,-.04,-.02))-light.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world.color=(.2,.2,.2);s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'previews'/'roll-perspective.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model'/'BA-ROLL-01.blend'));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(R/'model'/'BA-ROLL-01.blend'));bpy.ops.render.render(write_still=True)
