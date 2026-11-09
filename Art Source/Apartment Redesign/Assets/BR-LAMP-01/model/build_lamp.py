"""Create bedroom lamp, metres/Z-up; exports use a shared tabletop origin."""
import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
def mat(name, texture=None, color=(.8,.7,.6), metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(root/'textures'/texture),check_existing=True);m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
brass=mat('AgedBrass','brass.png',metal=.55,rough=.48)
ceramic=mat('IvoryCeramic','ceramic-floral.png',rough=.43)
cloth=mat('FloralShade','floral-linen.png',rough=.85)
binding=mat('DustyRoseBinding',None,(.49,.29,.27),rough=.8)
bulb=mat('Bulb',None,(.9,.79,.62),rough=.48)
# The powered state warms the existing texture rather than replacing the floral print.
nt=cloth.node_tree;p=nt.nodes.get('Principled BSDF');img=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(1,.68,.32,1);nt.links.new(img.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Emission Color'])
glow=nt.nodes.new('ShaderNodeValue');glow.name='LampGlow';glow.outputs[0].default_value=0;nt.links.new(glow.outputs[0],p.inputs['Emission Strength'])
body=[];shade=[];lampbulb=[]
def add(o,m,group): o.data.materials.append(m);group.append(o);return o
def cylinder(name,z,r,depth,material=brass):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=(0,0,z));o=bpy.context.object;o.name=name
 bevel=o.modifiers.new('Soft edges','BEVEL');bevel.width=min(.0015,r*.08,depth*.15);bevel.segments=3
 o.modifiers.new('Normals','WEIGHTED_NORMAL');bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 for poly in o.data.polygons:poly.use_smooth=True
 return add(o,material,body)
def sphere(name,loc,scale,material,group):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return add(o,material,group)
def lathe(name, profile, material,group):
 n=64; verts=[]; faces=[]
 for z,r in profile:
  for i in range(n):
   a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  i=poly.index%n;j=poly.index//n
  coords=((i/n,j/(len(profile)-1)),((i+1)/n,j/(len(profile)-1)),((i+1)/n,(j+1)/(len(profile)-1)),(i/n,(j+1)/(len(profile)-1)))
  for li,co in zip(poly.loop_indices,coords):uv.data[li].uv=co
  poly.use_smooth=True
 ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);return add(ob,material,group)
# Brass plinth and rounded vase-shaped ceramic body.
cylinder('Foot',.008,.056,.016);cylinder('FootRing',.020,.052,.009)
profile=[(.023,.043),(.030,.047),(.044,.051),(.060,.058),(.078,.067),(.100,.072),(.123,.073),(.146,.068),(.164,.058),(.180,.045),(.189,.034),(.193,.031)]
lathe('CeramicVase',profile,ceramic,body)
cylinder('NeckCollar',.197,.034,.010);cylinder('NeckPlate',.205,.026,.010);cylinder('Stem',.236,.008,.055);cylinder('Socket',.265,.017,.028)
cylinder('FinialStem',.457,.006,.014);sphere('Finial',(0,0,.467),(.008,.008,.008),brass,body)
# A delicate soft cloth shade with vertical fabric-panel ribs and rose piping.
N=96;verts=[];faces=[]
for z,r in [(.274,.145),(.454,.082)]:
 for i in range(N):
  a=2*math.pi*i/N; rr=r + (.0013 if i%8==0 else 0);verts.append((rr*math.cos(a),rr*math.sin(a),z))
for i in range(N):faces.append((i,(i+1)%N,N+(i+1)%N,N+i))
mesh=bpy.data.meshes.new('FloralShade');mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 i=poly.index
 for li,coord in zip(poly.loop_indices,[(i/N,0),((i+1)/N,0),((i+1)/N,1),(i/N,1)]):uv.data[li].uv=coord
ob=bpy.data.objects.new('Shade',mesh);bpy.context.collection.objects.link(ob);add(ob,cloth,shade)
sol=ob.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.0015;bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=sol.name);ob.select_set(False)
for z,r in [(.274,.145),(.454,.082)]:
 bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=10,location=(0,0,z),major_radius=r,minor_radius=.0027);o=bpy.context.object;o.name='RosePiping';add(o,binding,shade)
sphere('Bulb',(0,0,.350),(.018,.018,.028),bulb,lampbulb)
def combine(objs,name):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objs:ob.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[combine(body,'BR_LampBody'),combine(shade,'BR_LampShade'),combine(lampbulb,'BR_LampBulb')]
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Presentation only.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));ground=bpy.context.object;ground.data.materials.append(mat('Backdrop',None,(.30,.26,.23),rough=1))
bpy.ops.object.camera_add(location=(.9,-1.3,.64));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.235))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.64;bpy.context.scene.camera=cam
for loc,energy,size in [((1,-1.5,2),70,2),((-1,.5,1),18,1.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=size
bpy.ops.object.light_add(type='POINT',location=(0,0,.35));point=bpy.context.object;point.data.color=(1,.62,.30);point.data.shadow_soft_size=.08
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world.color=(.18,.18,.18)
for state in ('off','on'):
 on=state=='on';point.data.energy=3 if on else 0;glow.outputs[0].default_value=.65 if on else 0
 p=bulb.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.47,.12,1);p.inputs['Emission Strength'].default_value=3 if on else 0
 scene.render.filepath=str(root/'previews'/('lamp-'+state+'.png'));bpy.ops.render.render(write_still=True)
point.data.energy=0;glow.outputs[0].default_value=0;bulb.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=0
for img in bpy.data.images:
 if img.source=='FILE':img.filepath='//../textures/'+Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'BR-LAMP-01.blend'))
