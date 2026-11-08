"""Build LV-RUG-01. Blender --background --python model/build_rug.py.
Metres, +Z up, origin at floor center; albedo maps the full rug top.
"""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Rug_PaintedFloral'); mat.use_nodes=True
nodes=mat.node_tree.nodes; bs=nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.94
tex=nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(ROOT/'textures'/'rug-albedo.png'),check_existing=True); tex.image.pack(); mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
edge=bpy.data.materials.new('Rug_BoundEdge'); edge.diffuse_color=(.30,.12,.09,1); edge.use_nodes=True; edge.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.30,.12,.09,1);edge.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
# Flat textile panel with minute, restrained irregularity; one UV maps entire image.
nx,ny=32,24; verts=[]; faces=[]
for j in range(ny+1):
 for i in range(nx+1):
  x=-1.225+2.45*i/nx; y=-.875+1.75*j/ny
  z=.015+.0015*math.sin(i*.7)*math.sin(j*.6)
  verts.append((x,y,z))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i; faces.append((a,a+1,a+1+nx+1,a+nx+1))
mesh=bpy.data.meshes.new('Woven rug surface'); mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('Woven rug surface',mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
uv=mesh.uv_layers.new(name='RugUV')
for poly in mesh.polygons:
 for li in poly.loop_indices:
  x,y,_=mesh.vertices[mesh.loops[li].vertex_index].co; uv.data[li].uv=((x+1.225)/2.45,(y+.875)/1.75)
# A slim, real binding describes the silhouette; no thick sculpted paint.
def box(name,loc,dims,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Rounded binding','BEVEL');mod.width=.006;mod.segments=3; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);o.data.materials.append(material);return o
for y in (-.8875,.8875): box('Long bound edge',(0,y,.011),(2.5,.025,.022),edge)
for x in (-1.2375,1.2375): box('Short bound edge',(x,0,.011),(.025,1.75,.022),edge)
# Join only authored geometry before building the neutral review studio.
bpy.ops.object.select_all(action='SELECT'); bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();obj=bpy.context.object;obj.name='LV_RUG_01';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/'LV_RUG_01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'LV-RUG-01.blend'))
# Render actual textured model, not the concept image.
world=bpy.context.scene.world;world.color=(.25,.25,.25)
bpy.ops.object.light_add(type='AREA', location=(-1.8,-2.0,4)); lamp=bpy.context.object;lamp.data.energy=500;lamp.data.shape='DISK';lamp.data.size=5
bpy.ops.object.camera_add(location=(3,-4.4,4.2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.5;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.render.filepath=str(ROOT/'previews'/'rug-three-quarter.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,5);cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.05;s.render.filepath=str(ROOT/'previews'/'rug-top.png');bpy.ops.render.render(write_still=True)
