import bpy, math
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
root=here.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
# 2 m module, room-facing normals down. Mirror baked into UVs means opposing boundaries match.
verts=[(x,y,0) for y in range(3) for x in range(3)]
faces=[]
for y in range(2):
 for x in range(2):
  a=y*3+x; faces.append((a,a+3,a+4,a+1))
mesh=bpy.data.meshes.new('Ceiling_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
 for li in p.loop_indices:
  v=mesh.vertices[mesh.loops[li].vertex_index].co
  uv.data[li].uv=(1-abs(v.x-1),1-abs(v.y-1))
obj=bpy.data.objects.new('Ceiling_2m',mesh); bpy.context.collection.objects.link(obj)
mat=bpy.data.materials.new('Ceiling_Plaster_C'); mat.use_nodes=True
nodes=mat.node_tree.nodes; links=mat.node_tree.links
bs=nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.9
tex=nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(root/'textures/plaster-candidate-c.png')); tex.image.pack(); links.new(tex.outputs['Color'],bs.inputs['Base Color']); obj.data.materials.append(mat)
bpy.context.view_layer.objects.active=obj; obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(here/'ARC_Ceiling_Module_2m.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',add_leaf_bones=False)
# Four modules joined visually for repeat preview, using the exact exported material and UVs.
for x,y in [(2,0),(0,2),(2,2)]:
 cp=obj.copy(); cp.data=obj.data; bpy.context.collection.objects.link(cp); cp.location=(x,y,0)
world=bpy.context.scene.world; world.color=(.18,.18,.18)
bpy.ops.object.light_add(type='AREA',location=(2,2,-4)); light=bpy.context.object; light.data.energy=650; light.data.shape='DISK'; light.data.size=6; light.rotation_euler=(Vector((2,2,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2,2,-6)); camera=bpy.context.object; camera.rotation_euler=(Vector((2,2,0))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=4.65
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.resolution_x=1050; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(root/'previews/repeat-4m.png')
bpy.ops.wm.save_as_mainfile(filepath=str(here/'ARC-CEILING-PLASTER-01.blend'))
bpy.ops.render.render(write_still=True)
