"""1 m repeatable kitchen linoleum, front surface z=0; 0.25 m squares."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; O=P/'previews'; T=P/'textures'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('KI_LINOLEUM_generated_checker');mat.use_nodes=True
p=mat.node_tree.nodes.get('Principled BSDF'); p.inputs['Roughness'].default_value=.72
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'checker-selected.png'));tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
base=bpy.data.materials.new('KI_LINOLEUM_fine_seams');base.diffuse_color=(.32,.24,.17,1);base.use_nodes=True;base.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.32,.24,.17,1)
# Draw 16 slightly inset UV islands. Sampling inside each quadrant excludes any baked borders.
verts=[]; faces=[]; uvmap=[]
for y in range(4):
 for x in range(4):
  x0=x*.25-.5; y0=y*.25-.5; eps=.00045
  verts.extend([(x0+eps,y0+eps,0),(x0+.25-eps,y0+eps,0),(x0+.25-eps,y0+.25-eps,0),(x0+eps,y0+.25-eps,0)])
  faces.append(tuple(range(len(verts)-4,len(verts))))
  # top-left quadrant is cream and top-right is terracotta, using v=0.5..1 in Blender
  cream=(x+y)%2==0
  # Two independent source quadrants per color reduce repeated brush marks.
  alt=((x//2+y//2+x*y)%2)==1
  if cream: u0,u1,v0,v1=(.54,.96,.04,.46) if alt else (.04,.46,.54,.96)
  else: u0,u1,v0,v1=(.04,.46,.04,.46) if alt else (.54,.96,.54,.96)
  corners=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
  rot=(x*3+y*5)%4; corners=corners[rot:]+corners[:rot]
  uvmap.append(corners)
mesh=bpy.data.meshes.new('Checker top mesh');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat)
uv=mesh.uv_layers.new(name='UVMap')
for f,coords in zip(mesh.polygons,uvmap):
 for li,coord in zip(f.loop_indices,coords):uv.data[li].uv=coord
obj=bpy.data.objects.new('KI_TILE_TOP',mesh);bpy.context.collection.objects.link(obj)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.0152)); slab=bpy.context.object;slab.name='KI_TILE_SUBSTRATE';slab.dimensions=(1,1,.03);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);slab.data.materials.append(base)
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(M/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
for o in (obj,slab):export(o)
# Repeat test uses the actual same top mesh: checker parity must match across module boundaries.
for x in range(-2,2):
 for y in range(-1,2):
  if x==0 and y==0:continue
  for original in (obj,slab):
   copy=original.copy();copy.data=original.data;bpy.context.collection.objects.link(copy);copy.location.x+=x;copy.location.y+=y
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1300;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.25,.23,.20)
bpy.ops.object.light_add(type='AREA',location=(0,-2,5));l=bpy.context.object;l.data.energy=600;l.data.size=6
bpy.ops.object.camera_add(location=(2.7,-4.4,4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.5;scene.camera=cam
scene.render.filepath=str(O/'checker-repeat.png');bpy.ops.render.render(write_still=True)
# Save the editable source with the repeat-test context; export files remain single modules.
bpy.ops.wm.save_as_mainfile(filepath=str(M/'KI-TILE-01.blend'))
