"""Build flush ceiling fixture, metres, ceiling mount origin (0,0,0)."""
import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name, color, tex=None, metallic=0, rough=.6):
 m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(str(root/'textures'/tex),check_existing=True); m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
brass=mat('Aged_Brass',(.30,.22,.11),'aged-brass.png',.60,.54)
glass=mat('Ivory_Opal_Glass',(.88,.80,.65),'opal-glass.png',0,.42)
body=[]; shade=[]
def attach(o,name,material,parts):
 o.name=name; o.data.materials.append(material); parts.append(o)
 for p in o.data.polygons: p.use_smooth=True
 return o
def cylinder(name,loc,r,depth,parts=body):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc); o=bpy.context.object
 b=o.modifiers.new('Rounded_edge','BEVEL');b.width=min(.002,r*.2,depth*.2);b.segments=3; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return attach(o,name,brass,parts)
def torus(name,loc,R,r,parts=body):
 bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,location=loc,major_radius=R,minor_radius=r)
 return attach(bpy.context.object,name,brass,parts)
def sphere(name,loc,scale,parts=body):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return attach(o,name,brass,parts)
# Ceiling plane is z=0. Body remains parentable to one origin.
cylinder('CeilingPlate',(0,0,-.008),.100,.016)
torus('PlateRim',(0,0,-.015),.096,.003)
cylinder('Canopy',(0,0,-.026),.078,.020)
torus('CanopyBead',(0,0,-.036),.077,.0025)
cylinder('Neck',(0,0,-.050),.024,.031)
torus('GlassRetainingRim',(0,0,-.070),.164,.0035)
# Fluted opal diffuser: explicit ring topology and UVs; bottom hidden under finial.
N=96; rings=20; vertices=[]; faces=[]
for k in range(rings+1):
 theta=.035+(math.pi/2-.035)*k/rings
 for j in range(N):
  a=2*math.pi*j/N; rib=1+.08*math.cos(12*a)*math.sin(theta)*math.cos(theta)
  radius=.164*math.sin(theta)*rib
  z=-.150+.080*(1-math.cos(theta)) + .004*math.cos(12*a)*math.sin(theta)*math.cos(theta)
  vertices.append((radius*math.cos(a),radius*math.sin(a),z))
for k in range(rings):
 for j in range(N):
  j2=(j+1)%N;faces.append((k*N+j,k*N+j2,(k+1)*N+j2,(k+1)*N+j))
mesh=bpy.data.meshes.new('FlutedOpalMesh');mesh.from_pydata(vertices,[],faces);mesh.update(); uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
 k=p.index//N;j=p.index%N;p.use_smooth=True
 for li,co in zip(p.loop_indices,((j/N,k/rings),((j+1)/N,k/rings),((j+1)/N,(k+1)/rings),(j/N,(k+1)/rings))): uv.data[li].uv=co
ob=bpy.data.objects.new('FlutedOpalDiffuser',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(glass);shade.append(ob)
# Narrow holding clips and screw heads at thirds of the rim.
for i in range(3):
 a=math.tau*i/3; x=.164*math.cos(a);y=.164*math.sin(a)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,-.071));o=bpy.context.object;o.scale=(.009,.018,.018);o.rotation_euler.z=a;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 b=o.modifiers.new('Rounded edges','BEVEL');b.width=.002;b.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name);attach(o,'RetainingClip',brass,body)
 sphere('ClipFastener',(x*1.027,y*1.027,-.075),(.003,)*3)
cylinder('FinialBase',(0,0,-.153),.020,.006)
cylinder('Finial',(0,0,-.160),.011,.012)
sphere('FinialTip',(0,0,-.171),(.009,.009,.009))
def combine(group,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[combine(body,'ARC_CeilingLight_Hardware'),combine(shade,'ARC_CeilingLight_Glass')]
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Preview-only ceiling, camera, and area lights.
ceilingmat=mat('Preview_Ceiling',(.46,.40,.36),None,0,.85)
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0,.003));bpy.context.object.name='PreviewCeiling';bpy.context.object.data.materials.append(ceilingmat)
bpy.ops.object.camera_add(location=(.60,-.94,-.52));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,-.08))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.57;bpy.context.scene.camera=cam
for loc,power,size in [((.2,-.8,-.7),30,1.1),((-.8,.3,-.5),14,.8)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,-.06))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='POINT',location=(0,0,-.14));pt=bpy.context.object;pt.data.color=(1,.52,.22);pt.data.shadow_soft_size=.08
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.image_settings.file_format='PNG';sc.world.color=(.12,.12,.12);sc.view_settings.view_transform='AgX';sc.render.film_transparent=False
bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.38,.10,1)
for state in ('off','on'):
 pt.data.energy=5 if state=='on' else 0;bs.inputs['Emission Strength'].default_value=.85 if state=='on' else 0
 sc.render.filepath=str(root/'previews'/('fixture-'+state+'.png'));bpy.ops.render.render(write_still=True)
pt.data.energy=0;bs.inputs['Emission Strength'].default_value=0
for img in bpy.data.images:
 if img.source=='FILE' and Path(img.filepath).name in ('aged-brass.png','opal-glass.png'):img.filepath='//../textures/'+Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'ARC-CEILING-LIGHT-01.blend'))
