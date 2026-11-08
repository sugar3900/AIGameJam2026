"""KI-POTTERY-01: metres, +Z up, decorative front -Y, tabletop/floor origin."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; M=P/'model'; T=P/'textures'; R=P/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name, color, roughness, image=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness
 if image:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/image),check_existing=True);tex.image.filepath='//../textures/'+image;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 return m
outer=mat('Painted_Honey_Glaze',(.65,.42,.20),.6,'botanical-glaze.png');inner=mat('Interior_Warm_Ceramic',(.46,.25,.13),.62);rim=mat('Terracotta_Rim',(.48,.22,.10),.58)
# Outer and inner continuous profile: rises outer surface, rolls across lip, descends to floor.
profile=[(.040,0),(.049,.001),(.055,.005),(.061,.013),(.068,.026),(.074,.044),(.078,.065),(.080,.087),(.078,.109),(.072,.132),(.064,.154),(.056,.174),(.052,.193),(.052,.210),(.056,.224),(.060,.230),(.059,.235),(.055,.239),(.049,.239),(.046,.235),(.047,.229),(.047,.214),(.047,.197),(.051,.179),(.058,.157),(.066,.135),(.072,.112),(.074,.089),(.072,.068),(.068,.047),(.061,.031),(.050,.021),(.035,.016),(.008,.015)]
n=80;verts=[];faces=[]
for r,z in profile:
 for i in range(n):
  a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
for j in range(len(profile)-1):
 for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
faces.append(tuple(reversed(range(n))));faces.append(tuple((len(profile)-1)*n+i for i in range(n)))
mesh=bpy.data.meshes.new('VesselMesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('KI_Pottery_01',mesh);bpy.context.collection.objects.link(o)
for m in (outer,inner,rim):o.data.materials.append(m)
uv=o.data.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 if poly.index < (len(profile)-1)*n:
  j=poly.index//n;i=poly.index%n;poly.material_index=0 if j<14 else (2 if j<20 else 1);poly.use_smooth=True
  u0=((i/n)+.75)%1;u1=(((i+1)/n)+.75)%1
  if u1<u0:u1+=1
  z0=profile[j][1]/.239;z1=profile[j+1][1]/.239
  if abs(z1-z0)<1e-9:z1=z0+0.001
  for loop_id,uvval in zip(poly.loop_indices,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)]):uv.data[loop_id].uv=uvval
 else:
  poly.material_index=1
  for li in poly.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(.5+v.x*4,.5+v.y*4)
# Shift origin remains tabletop centre, geometry stays positive Z.
bpy.context.view_layer.objects.active=o;o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(M/'KI_Pottery_01.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,axis_forward='-Z',axis_up='Y')
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.camera_add(location=(.39,-.55,.38));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.12))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.36;bpy.context.scene.camera=cam
for loc,pow,size in [((-.4,-.6,.7),8,.65),((.45,.2,.5),3,.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=pow;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.12))-l.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.14,.12,.1)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'KI-POTTERY-01.blend'));sc.render.filepath=str(R/'vessel-perspective.png');bpy.ops.render.render(write_still=True)
