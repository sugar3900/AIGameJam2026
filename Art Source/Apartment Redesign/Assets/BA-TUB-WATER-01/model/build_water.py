import bpy, math, os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
T=P.parent/'BA-TUB-01/model/BA_Tub.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(T))
shell=bpy.data.objects.get('Tub_shell_hollow')
assert shell is not None, 'Tub shell missing from FBX'
bpy.context.view_layer.update()
verts_world=[shell.matrix_world@v.co for v in shell.data.vertices]
polys=[tuple(p.vertices) for p in shell.data.polygons]
tree=BVHTree.FromPolygons(verts_world,polys,all_triangles=False)
# Sample the imported basin interior, not the visual bounding box. Waterline is 14 cm below rim.
N=128; rings=20; level=.430; inset=.018
boundary=[]
for i in range(N):
 a=math.tau*i/N; direction=Vector((math.cos(a),math.sin(a),0))
 hit,normal,index,dist=tree.ray_cast(Vector((0,0,level)),direction,2.0)
 if hit is None or dist<=inset: raise RuntimeError('No inner-basin ray hit at '+str(i))
 boundary.append((hit.x,hit.y,dist))
vertices=[(0,0,level)];uv=[(.5,.5)]
for j in range(1,rings+1):
 q=j/rings
 for i,(x,y,dist) in enumerate(boundary):
  scale=(dist-inset)/dist*q
  px,py=x*scale,y*scale
  # Microscopic wave rises only in the interior: perfectly level edge preserves clearance.
  ripple=.0015*math.sin(px*13+py*17)*math.cos(px*5-py*19)*(1-q)**2
  vertices.append((px,py,level+ripple));uv.append((.5+px/1.50,.5+py/.52))
faces=[]
for i in range(N): faces.append((0,1+i,1+(i+1)%N))
for j in range(rings-1):
 start=1+j*N; nxt=start+N
 for i in range(N): faces.append((start+i,nxt+i,nxt+(i+1)%N,start+(i+1)%N))
me=bpy.data.meshes.new('Basin_water_surface_mesh');me.from_pydata(vertices,[],faces);me.update();obj=bpy.data.objects.new('Basin_water_surface',me);bpy.context.collection.objects.link(obj)
uvlayer=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 poly.use_smooth=True
 for loop_i in poly.loop_indices: uvlayer.data[loop_i].uv=uv[me.loops[loop_i].vertex_index]
mat=bpy.data.materials.new('Water_painterly');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.30,.49,.49,1);bs.inputs['Roughness'].default_value=.19;bs.inputs['Metallic'].default_value=.03;bs.inputs['Transmission Weight'].default_value=.08;bs.inputs['Alpha'].default_value=.92
texture=P/'textures/water-cool-b.png'
if texture.exists():
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture));mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
obj.data.materials.append(mat)
# floor-centered assembly origin matches the existing tub; export selected surface only.
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(P/'model/BA_TUB_WATER_Surface.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
# report geometry derived from basin hits, usable by non-Blender integration.
with (P/'model/fit-report.txt').open('w') as f:
 f.write(f'Imported basin: {T}\nWater level: {level:.3f} m; radial inset: {inset:.3f} m; samples: {N}\n')
 f.write(f'Basin radial hit min/max: {min(v[2] for v in boundary):.6f}/{max(v[2] for v in boundary):.6f} m\n')
 f.write(f'Water bounds x/y: {min(v[0] for v in vertices):.6f}..{max(v[0] for v in vertices):.6f}, {min(v[1] for v in vertices):.6f}..{max(v[1] for v in vertices):.6f} m\n')
# Studio render with the exact imported tub assembly, rather than a stand-in.
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.25,.20,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
bpy.ops.object.light_add(type='AREA',location=(-2,-3,4));light=bpy.context.object;light.data.energy=550;light.data.color=(1,.79,.60);light.data.shape='DISK';light.data.size=4
bpy.ops.object.camera_add(location=(2.7,-3.1,2.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.33))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.2;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
# Keep fixture geometry only as an inspection reference; export is explicitly water-only.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-TUB-WATER-01.blend'))
scene.render.filepath=str(P/'previews/tub-filled.png');bpy.ops.render.render(write_still=True)
obj.hide_render=True;scene.render.filepath=str(P/'previews/tub-empty.png');bpy.ops.render.render(write_still=True)
