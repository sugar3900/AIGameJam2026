"""Build LV-LAMP-01, metres, Z up, floor origin. Run Blender --background --python."""
import bpy, os, math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
def material(name,color,texture=None,metal=0,rough=.6):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(str(root/'textures'/texture),check_existing=True); m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
brass=material('Brass_Painted',(0.48,.31,.12),'brass.png',.28,.48)
cloth=material('Linen_Painted',(.8,.73,.59),'linen.png',0,.86)
# Subtle pleat-aware emission: the lit side stays golden without flattening the folds.
nt=cloth.node_tree; p=nt.nodes.get('Principled BSDF'); image_node=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
uvnode=nt.nodes.new('ShaderNodeTexCoord'); separate=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uvnode.outputs['UV'],separate.inputs[0])
freq=nt.nodes.new('ShaderNodeMath');freq.operation='MULTIPLY';freq.inputs[1].default_value=24*2*math.pi;nt.links.new(separate.outputs['X'],freq.inputs[0])
sine=nt.nodes.new('ShaderNodeMath');sine.operation='SINE';nt.links.new(freq.outputs[0],sine.inputs[0])
contrast=nt.nodes.new('ShaderNodeMath');contrast.operation='MULTIPLY_ADD';contrast.inputs[1].default_value=.22;contrast.inputs[2].default_value=.72;nt.links.new(sine.outputs[0],contrast.inputs[0])
glow=nt.nodes.new('ShaderNodeValue');glow.name='LampGlow';glow.outputs[0].default_value=0
strength=nt.nodes.new('ShaderNodeMath');strength.operation='MULTIPLY';nt.links.new(contrast.outputs[0],strength.inputs[0]);nt.links.new(glow.outputs[0],strength.inputs[1]);nt.links.new(strength.outputs[0],p.inputs['Emission Strength'])
color=nt.nodes.new('ShaderNodeMixRGB');color.blend_type='MULTIPLY';color.inputs[0].default_value=1;color.inputs[2].default_value=(1,.70,.08,1);nt.links.new(image_node.outputs['Color'],color.inputs[1]);nt.links.new(color.outputs[0],p.inputs['Emission Color'])

bulb=material('Bulb_Glass',(.95,.85,.65),None,0,.48)
cordmat=material('Cord',(.13,.11,.08),None,0,.9)
body=[]; shade=[]; lampbulb=[]
def add(obj,mat,collection):
 obj.data.materials.append(mat); collection.append(obj); return obj
def cyl(name,loc,r,depth,mat=brass,verts=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name
 b=o.modifiers.new('Rounded edges','BEVEL'); b.width=min(.002,r*.10,depth*.18); b.segments=3
 o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
 for f in o.data.polygons: f.use_smooth=True
 return add(o,mat,body)
def sphere(name,loc,scale,mat,coll):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc); o=bpy.context.object; o.name=name;o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return add(o,mat,coll)
# Layered, weighted 28cm base and slender metal shaft, total height ~1.56m
cyl('WeightedBase',(0,0,.018),.14,.036); cyl('BaseRim',(0,0,.040),.126,.012); cyl('BaseRise',(0,0,.054),.082,.018)
cyl('Stem',(0,0,.69),.009,1.27); cyl('LowerCollar',(0,0,.16),.019,.036); cyl('UpperCollar',(0,0,1.19),.018,.045)
cyl('Socket',(0,0,1.255),.027,.060); cyl('FinialStem',(0,0,1.50),.008,.055)
sphere('Finial',(0,0,1.545),(.018,.018,.018),brass,body)
# Pull chain small bead geometry; attached at socket edge.
for i in range(14): sphere('PullBead',(.16,-.13,1.22-i*.008),(.0025,)*3,brass,body)
sphere('PullWeight',(.16,-.13,1.098),(.006,)*3,brass,body)
# Pleated conical shade with thickness and nonzero surface polygons.
N=96; vertices=[]; faces=[]; uvs=[]
for z,r in [(1.22,.245),(1.49,.145)]:
 for i in range(N):
  a=2*math.pi*i/N; rr=r+(.004 if i%4 in (0,1) else -.004); vertices.append((rr*math.cos(a),rr*math.sin(a),z))
for i in range(N):
 j=(i+1)%N;faces.append((i,j,N+j,N+i))
mesh=bpy.data.meshes.new('PleatedLinen');mesh.from_pydata(vertices,[],faces);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 i=poly.index
 for li,(u,v) in zip(poly.loop_indices,[(i/N,0),((i+1)/N,0),((i+1)/N,1),(i/N,1)]): uv.data[li].uv=(u,v)
o=bpy.data.objects.new('Shade',mesh);bpy.context.collection.objects.link(o);add(o,cloth,shade)
sol=o.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.002;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=sol.name);o.select_set(False)
# Smooth trim rings around the cloth.
for z,r in [(1.22,.245),(1.49,.145)]:
 bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=8,location=(0,0,z),major_radius=r,minor_radius=.003); o=bpy.context.object;o.name='ShadeBinding'; add(o,brass,shade)
sphere('Bulb',(0,0,1.31),(.030,.030,.048),bulb,lampbulb)
# Join each group keeping a shared floor origin. Separate parts allow screen light swapping.
def combine(objs,name):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objs: ob.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[combine(body,'LV_LampBody'),combine(shade,'LV_LampShade'),combine(lampbulb,'LV_LampBulb')]
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Ground and camera used only for previews.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.008));ground=bpy.context.object;ground.name='PreviewGround'; ground.data.materials.append(material('Preview_Backdrop',(.32,.27,.22),None,0,1))
def point_camera(loc,target):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=2.00;return o
camera=point_camera((2.7,-4,1.55),(0,0,.79));bpy.context.scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(1,-3,3)); key=bpy.context.object;key.data.energy=180;key.data.shape='DISK';key.data.size=4
bpy.ops.object.light_add(type='AREA',location=(-2,1,2)); fill=bpy.context.object;fill.data.energy=60;fill.data.size=3
bpy.ops.object.light_add(type='POINT',location=(0,0,1.31)); point=bpy.context.object;point.data.color=(1,.62,.30);point.data.shadow_soft_size=.08
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world.color=(.18,.18,.18)
for state in ('off','on'):
 on=state=='on';point.data.energy=30 if on else 0
 glow.outputs[0].default_value=3.0 if on else 0
 p=bulb.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.47,.12,1);p.inputs['Emission Strength'].default_value=3 if on else 0
 scene.render.filepath=str(root/'previews'/('lamp-'+state+'.png'));bpy.ops.render.render(write_still=True)
# Save with light off; remove preview-only geometry from production blend.
point.data.energy=0
glow.outputs[0].default_value=0
bulb.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=0
for img in bpy.data.images:
 if img.source == 'FILE' and Path(img.filepath).name in ('brass.png','linen.png'):
  img.filepath = '//../textures/' + Path(img.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/'LV-LAMP-01.blend'))
