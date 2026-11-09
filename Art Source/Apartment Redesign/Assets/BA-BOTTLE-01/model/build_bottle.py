"""BA-BOTTLE-01: metres, Z up, front -Y; source/FBX and studio previews."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; M=P/'model'; T=P/'textures'; R=P/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,rough=.55,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough
 if image:
  img=m.node_tree.nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(T/image),check_existing=True);m.node_tree.links.new(img.outputs['Color'],n.inputs['Base Color'])
 return m
sage=material('Sage_Glaze',(.51,.54,.36),.58,'sage-glaze.png');ivory=material('Ivory_Stopper',(.78,.72,.58),.49);panel=material('Painted_Floral_Panel',(.56,.56,.35),.63,'floral-panel.png')
def surface(name,profile,mat,n=96,cap_top=False):
 verts=[]; faces=[]
 for radius,z,exp in profile:
  for i in range(n):
   a=2*math.pi*i/n;c=math.cos(a);s=math.sin(a);verts.append((radius*math.copysign(abs(c)**exp,c),radius*math.copysign(abs(s)**exp,s),z))
 for j in range(len(profile)-1):
  for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.append(tuple(reversed(range(n))))
 if cap_top: faces.append(tuple((len(profile)-1)*n+i for i in range(n)))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 uv=me.uv_layers.new(name='UVMap')
 for face in me.polygons:
  face.use_smooth=len(face.vertices)==4
  for li in face.loop_indices:
   idx=me.loops[li].vertex_index;col=idx%n;row=idx//n;u=col/n
   if face.index < (len(profile)-1)*n and face.index%n==n-1 and col==0:u=1.0
   uv.data[li].uv=((me.vertices[idx].co.x/.11+.5, me.vertices[idx].co.y/.11+.5) if face.index >= (len(profile)-1)*n else (u,row/(len(profile)-1)))
 return o
# Rounded-square reservoir transitions into a round neck; the inward rings are a real open mouth.
body=surface('Bottle_body',[(.041,0,.30),(.047,.002,.30),(.050,.007,.30),(.050,.112,.30),(.049,.122,.32),(.045,.132,.38),(.036,.142,.52),(.023,.151,.8),(.016,.157,1),(.016,.168,1),(.019,.169,1),(.020,.172,1),(.019,.175,1),(.012,.175,1),(.011,.171,1),(.011,.151,1),(.005,.145,1)],sage)
body.name='BA_Bottle_Body'
# Painted panel uses the body's actual front-facing quads, so it has no overlay depth.
# Front faces local -Y. Per-loop planar UVs keep the floral image readable and integrated.
body.data.materials.append(panel)
uv=body.data.uv_layers.active.data
for face in body.data.polygons:
 ring=face.index//96
 if face.index >= 96*16 or ring not in (1,2,3): continue
 mid=sum((body.data.vertices[v].co for v in face.vertices),Vector())/len(face.vertices)
 if mid.y < -abs(mid.x):
  face.material_index=1
  for li in face.loop_indices:
   v=body.data.vertices[body.data.loops[li].vertex_index].co
   uv[li].uv=(max(0,min(1,v.x/.10+.5)),max(0,min(1,(v.z-.002)/.120)))
# Stopper with shallow insert and an ivory rounded finial.
stop=surface('BA_Bottle_Stopper',[(.008,.160,1),(.010,.160,1),(.010,.173,1),(.013,.175,1),(.019,.179,1),(.023,.185,1),(.023,.190,1),(.020,.195,1),(.014,.198,1),(.004,.199,1)],ivory,cap_top=True)
bpy.ops.object.select_all(action='DESELECT');stop.select_set(True);bpy.context.view_layer.objects.active=stop;bpy.context.scene.cursor.location=(0,0,.175);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
for o,name in [(body,'BA_Bottle_Body.fbx'),(stop,'BA_Bottle_Stopper.fbx')]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(M/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(.28,-.46,.30));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.28;bpy.context.scene.camera=cam
for pos,power,size in [((-.30,-.35,.48),4,.45),((.28,.14,.35),2,.38)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.10))-o.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.14,.12,.1)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'BA-BOTTLE-01.blend'));sc.render.filepath=str(R/'bottle-closed.png');bpy.ops.render.render(write_still=True)
stop.location.x=.10;stop.location.z+=.025;cam.data.ortho_scale=.34;cam.rotation_euler=(Vector((.04,0,.10))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(R/'bottle-open.png');bpy.ops.render.render(write_still=True)
